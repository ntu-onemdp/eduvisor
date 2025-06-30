import os
import io
import pickle
from fastapi_simple_cache.decorator import cache
import faiss
import numpy as np
from google.cloud import storage
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from response import response_handler
from PyPDF2 import PdfReader
from services.logger import Logger
from langchain_community.docstore.in_memory import InMemoryDocstore
from io import BytesIO

logger = Logger()

# Initialize Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/service-account-key.json"


class VectorStore:
    # Class constants
    BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    if not BUCKET_NAME:
        raise ValueError("GCS_BUCKET_NAME environment variable is not set.")

    # Embedding model to use. See https://platform.openai.com/docs/models for list of embedding models available
    MODEL = "text-embedding-3-small"

    def __init__(self):
        embeddings = OpenAIEmbeddings(model=self.MODEL)

        # Retrieve vectorstore from gcs
        response = load_vectorstore_from_gcs()
        logger.debug(response)
        if response["code"] != 200:
            logger.warning(
                "error loading vectorstore from gcs - initializing vectorstore"
            )

            # Step 1: Get embedding dimension (example: 1536 for many OpenAI models)
            embedding_dim = 1536

            # Step 2: Create an empty FAISS index
            index = faiss.IndexFlatL2(embedding_dim)

            # Step 3: Prepare the empty docstore and mapping
            docstore = InMemoryDocstore({})
            index_to_docstore_id = {}

            # Step 4: Create the LangChain FAISS vectorstore
            self.vector_store = FAISS(
                embedding_function=embeddings,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id,
            )
        else:
            self.vector_store = response["data"]

        logger.info("Vector store initialized")
        pass

    # Add document to vectorstore
    def add_document(
        self, pdfs: list[tuple[str, BytesIO]], chunk_size=3000, chunk_overlap=100
    ) -> None:
        """
        Add document(s) to vectorstore

        Args:
            files (list[Document]): list of pdfs to add to vectorstore
        """
        documents = []

        for filename, content in pdfs:
            pdf = PdfReader(content)
            title = filename.replace(".pdf", "")

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
                        )
                        documents.append(doc)
                else:
                    doc = Document(
                        page_content=page_content,
                        metadata={"title": title, "page": page_number, "chunk": 1},
                    )
                    documents.append(doc)

        logger.info(f"{len(pdfs)} added to vectorstore")

        # @NOTE not working due to api limits
        self.vector_store.add_documents(documents)

    def save_vectorstore_to_gcs_direct(self, vectorstore):
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
                            metadata={"title": title, "page": page_number, "chunk": 1},
                        )
                        courseinfo_docs.append(doc)

            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_documents(courseinfo_docs, embeddings)

            return response_handler(
                200, "Vectorstore Generated Successfully", vectorstore
            )

        except Exception as e:
            return response_handler(500, "Failed to Generate Vectorstore", str(e))


# @cache(expire=3600)
def load_vectorstore_from_gcs():
    try:
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not bucket_name:
            raise ValueError("GCS_BUCKET_NAME environment variable is not set.")

        index_blob_name = "vectorstore/index.faiss"
        metadata_blob_name = "vectorstore/metadata.pkl"
        mapping_blob_name = "vectorstore/mapping.pkl"  # New blob for mapping

        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        # Download FAISS index
        faiss_index_buffer = bucket.blob(index_blob_name).download_as_bytes()
        faiss_index = faiss.deserialize_index(
            np.frombuffer(faiss_index_buffer, dtype=np.uint8)
        )

        # Download metadata
        metadata_buffer = bucket.blob(metadata_blob_name).download_as_bytes()
        metadata = pickle.loads(metadata_buffer)

        # Download index_to_docstore_id
        mapping_buffer = bucket.blob(mapping_blob_name).download_as_bytes()
        index_to_docstore_id = pickle.loads(mapping_buffer)

        # Reconstruct the docstore
        from langchain_community.docstore.in_memory import InMemoryDocstore

        docstore = InMemoryDocstore(metadata)

        # Reconstruct the FAISS vectorstore
        from langchain_community.vectorstores import FAISS

        vectorstore = FAISS(
            embedding_function=OpenAIEmbeddings(),
            index=faiss_index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
        )
        return response_handler(200, "Vectorstore Loaded Successfully", vectorstore)
    except Exception as e:
        print("load  vectorstore ")
        print(str(e))
        return response_handler(500, "Failed to Load Vectorstore", str(e))
