from models.pdf_store import PdfStore
from models.vector_store import VectorStore
from services.logger import Logger
from fastapi import UploadFile
from response import response_handler

logger = Logger()


class MaterialsController:
    def __init__(self, pdf_store: PdfStore, vector_store: VectorStore):
        self.pdf_store = pdf_store
        self.vector_store = vector_store
        logger.debug("Materials controller initialized")
        pass

    def add(self, files: list[UploadFile]):
        # Upload PDFs onto Google Cloud Storage for retrieval in the future
        upload_res = self.pdf_store.upload(files)
        if upload_res["code"] != 201:
            logger.error("Error uploading files to Google Cloud Storage.")
            return response_handler(500, "Error uploading to Google Cloud Storage")

        # Update vectorstore
        vectorstore_res = self.vector_store.add_documents(files)
        if vectorstore_res["code"] != 201:
            logger.error("Error updating vectorstore")
            return response_handler(500, "Error updating vectorstore")

        return response_handler(201, "Successfully added files into Eduvisor")
