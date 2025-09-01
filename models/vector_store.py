import os
import io
import pickle
import faiss
import numpy as np
from google.cloud import storage
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from response import response_handler
from PyPDF2 import PdfReader
from services.logger import Logger
from langchain_community.docstore.in_memory import InMemoryDocstore
from fastapi import UploadFile
from dotenv import load_dotenv

logger = Logger()

load_dotenv(".env", verbose=True, override=True)

# Initialize Google Cloud credentials
env = os.getenv("ENV")
if env == "DEV" or env == "DEV_2":
    path = "./secrets/service-account-key"
else:
    path = "/secrets/service-account-key"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path


class VectorStore:
    # Class constants
    BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    if not BUCKET_NAME:
        raise ValueError("GCS_BUCKET_NAME environment variable is not set.")
    logger.debug(f"bucket name: {BUCKET_NAME}")

    # Retrieve env and set model accordingly. Defaults to PROD (will incur OpenAI usage)
    _env = os.getenv("ENV", "PROD")
    logger.debug(f"environment: {_env}")

    if _env == "DEV":
        from langchain_ollama import OllamaEmbeddings

        _embedding_dim = 1024  # bge-m3 uses 1024 dim for embeddings
        _model = "bge-m3:567m"  # retrieve model with ollama pull bge-m3:567m
        embeddings = OllamaEmbeddings(
            model=_model, base_url="http://host.docker.internal:11434"
        )
    elif _env == "PROD" or _env == "DEV_2":
        from langchain_openai import OpenAIEmbeddings

        _embedding_dim = 1536  # OpenAI uses 1536 dim for emmbeddings
        # Embedding model to use. See https://platform.openai.com/docs/models for list of embedding models available
        _model = "text-embedding-3-small"
        embeddings = OpenAIEmbeddings(model=_model)
    else:
        # Invalid environment
        logger.warning(
            "A donkey has set an invalid environment. Valid environment names: DEV,PROD."
        )

    def __init__(self):
        # Retrieve vectorstore from gcs
        response = self._load_vectorstore_from_gcs()
        logger.debug(response)
        if response["code"] != 200:
            logger.warning(
                "error loading vectorstore from gcs - initializing vectorstore"
            )

            # Step 2: Create an empty FAISS index
            index = faiss.IndexFlatL2(self._embedding_dim)

            # Step 3: Prepare the empty docstore and mapping
            docstore = InMemoryDocstore({})
            index_to_docstore_id = {}

            # Step 4: Create the LangChain FAISS vectorstore
            self.vector_store = FAISS(
                embedding_function=self.embeddings,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id,
            )
        else:
            self.vector_store = response["data"]

        logger.info("Vector store initialized")
        pass

    # Add document to vectorstore
    def add_documents(
        self, pdfs: list[UploadFile], chunk_size=3000, chunk_overlap=100
    ) -> dict[str, str]:
        """Add one or more PDF documents to the vector store.

        Each PDF is split into pages, and each page is further split into text chunks
        if it exceeds the specified chunk size. The resulting chunks are stored as
        individual documents in the vector store, along with metadata about the
        document title, page number, and chunk index.

        Args:
            pdfs (list[UploadFile]):
                A list of tuples, where each tuple contains the filename (str) and
                file content as a BytesIO object representing a PDF file.
            chunk_size (int, optional):
                The maximum number of characters in each text chunk.
                If a page's text exceeds this length, it will be split into multiple chunks.
                Defaults to 3000.
            chunk_overlap (int, optional):
                The number of overlapping characters between consecutive chunks.
                This helps preserve context between chunks. Defaults to 100.

        Returns:
            dict[str, any]: 201 if successful.
        """
        documents = []

        try:
            for pdf in pdfs:
                filename = pdf.filename
                file = pdf.file

                pdf = PdfReader(file)
                if filename:
                    title = filename.replace(".pdf", "")
                else:
                    title = "Untitled"

                for page_number, page in enumerate(pdf.pages, start=1):
                    page_content = page.extract_text()

                    if len(page_content) > chunk_size:
                        # Split page content into chunks if length of page content exceeds the chunk size setting.
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=chunk_size, chunk_overlap=chunk_overlap
                        )
                        chunks = text_splitter.split_text(page_content)

                        for i, chunk in enumerate(chunks):
                            doc = Document(
                                page_content=chunk,
                                metadata={
                                    "title": title,
                                    "page": page_number,
                                    "chunk": i + 1,
                                },
                                # id=f"{title}{i}",
                            )
                            documents.append(doc)
                    else:
                        doc = Document(
                            page_content=page_content,
                            metadata={"title": title,
                                      "page": page_number, "chunk": 1},
                            # id=title,
                        )
                        documents.append(doc)

            # Add documents into vectorstore
            self.vector_store.add_documents(documents)

            # Sync vectorstore with gcs
            self._save_vectorstore_to_gcs_direct(self.vector_store)

            logger.info(f"{len(pdfs)} document added to vectorstore")

            return response_handler(201, "Vector store updated")
        except Exception as e:
            logger.error(e)
            return response_handler(
                500, "Error adding document to vectorstore" + str(e)
            )

    def _save_vectorstore_to_gcs_direct(self, vectorstore):
        """
        Saves a FAISS vector store to Google Cloud Storage.

        Args:
            vectorstore: The FAISS vector store object.
            course_id: The course ID.
        """
        try:
            index_blob_name = "vectorstore/index.faiss"
            metadata_blob_name = "vectorstore/metadata.pkl"
            mapping_blob_name = "vectorstore/mapping.pkl"

            faiss_index_buffer = faiss.serialize_index(vectorstore.index)

            metadata_buffer = io.BytesIO()
            pickle.dump(vectorstore.docstore._dict, metadata_buffer)
            metadata_buffer.seek(0)

            mapping_buffer = io.BytesIO()
            pickle.dump(vectorstore.index_to_docstore_id, mapping_buffer)
            mapping_buffer.seek(0)

            client = storage.Client()
            bucket = client.bucket(self.BUCKET_NAME)

            bucket.blob(index_blob_name).upload_from_file(
                io.BytesIO(faiss_index_buffer), content_type="application/octet-stream"
            )
            bucket.blob(metadata_blob_name).upload_from_file(
                metadata_buffer, content_type="application/octet-stream"
            )
            bucket.blob(mapping_blob_name).upload_from_file(
                mapping_buffer, content_type="application/octet-stream"
            )

            return response_handler(201, "Vectorstore updated ")
        except Exception as e:
            return response_handler(500, "Failed to Save Vectorstore", str(e))

    #  @DEPRECATED
    def generate_vectorstore_from_memory(
        self, pdfs, chunk_size=3000, chunk_overlap=100
    ):
        """
        Generates a FAISS vector store from in-memory PDFs.

        Args:
            pdfs: A list of (file_name, file_content) tuples.
        """
        try:
            courseinfo_docs = []
            for file_name, file_content in pdfs:
                pdf_reader = PdfReader(file_content)
                title = file_name.replace(".pdf", "")

                for page_number, page in enumerate(pdf_reader.pages, start=1):
                    page_content = page.extract_text()

                    if len(page_content) > chunk_size:
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=chunk_size, chunk_overlap=chunk_overlap
                        )
                        chunks = text_splitter.split_text(page_content)

                        for i, chunk in enumerate(chunks):
                            doc = Document(
                                page_content=chunk,
                                metadata={
                                    "title": title,
                                    "page": page_number,
                                    "chunk": i + 1,
                                },
                            )
                            courseinfo_docs.append(doc)
                    else:
                        doc = Document(
                            page_content=page_content,
                            metadata={"title": title,
                                      "page": page_number, "chunk": 1},
                        )
                        courseinfo_docs.append(doc)

            vectorstore = FAISS.from_documents(
                courseinfo_docs, self.embeddings)

            return response_handler(
                200, "Vectorstore Generated Successfully", vectorstore
            )

        except Exception as e:
            return response_handler(500, "Failed to Generate Vectorstore", str(e))

    def _load_vectorstore_from_gcs(self):
        try:
            index_blob_name = "vectorstore/index.faiss"
            metadata_blob_name = "vectorstore/metadata.pkl"
            mapping_blob_name = "vectorstore/mapping.pkl"  # New blob for mapping

            # Initialize GCS client
            client = storage.Client()
            bucket = client.bucket(self.BUCKET_NAME)

            # Download FAISS index
            faiss_index_buffer = bucket.blob(
                index_blob_name).download_as_bytes()
            faiss_index = faiss.deserialize_index(
                np.frombuffer(faiss_index_buffer, dtype=np.uint8)
            )

            # Download metadata
            metadata_buffer = bucket.blob(
                metadata_blob_name).download_as_bytes()
            metadata = pickle.loads(metadata_buffer)

            # Download index_to_docstore_id
            mapping_buffer = bucket.blob(mapping_blob_name).download_as_bytes()
            index_to_docstore_id = pickle.loads(mapping_buffer)

            # Reconstruct the docstore
            docstore = InMemoryDocstore(metadata)

            # Reconstruct the FAISS vectorstore
            vectorstore = FAISS(
                embedding_function=self.embeddings,
                index=faiss_index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id,
            )
            return response_handler(200, "Vectorstore Loaded Successfully", vectorstore)
        except Exception as e:
            logger.error(f"failed to load vector store, {str(e)}")
            return response_handler(500, "Failed to Load Vectorstore", str(e))
