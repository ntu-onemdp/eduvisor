import os
from google.cloud import storage
from response import response_handler
from io import BytesIO
from fastapi import UploadFile
from services.logger import Logger

logger = Logger()

# Initialize Google Cloud credentials
env = os.getenv("ENV")
if env == "DEV":
    path = "credentials/service-account-key.json"
else:
    path = "mnt/secrets/service-account-key.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
if not BUCKET_NAME:
    raise ValueError("GCS_BUCKET_NAME environment variable is not set.")


class PdfStore:
    def __init__(self):
        pass

    def upload(self, files: list[UploadFile]):
        """
        Uploads PDF files to Google Cloud Storage. Returns 201 on success

        Args:
            uploaded_file: The uploaded file object.
        """
        logger.debug("Starting PDF upload to GCS...")
        try:
            for file in files:
                file_name = file.filename
                blob_name = f"pdfs/{file_name}"
                logger.debug(f"Received file: {file_name}, Blob name: {blob_name}")

                client = storage.Client()
                logger.debug(f"Uploading {file_name} to GCS bucket {BUCKET_NAME}")

                bucket = client.bucket(BUCKET_NAME)
                logger.debug(f"Bucket {BUCKET_NAME} accessed successfully")
                blob = bucket.blob(blob_name)
                logger.debug(f"Blob {blob_name} created in bucket {BUCKET_NAME}")

                blob.upload_from_file(file.file, content_type="application/pdf")

            return response_handler(
                201, f"Uploaded {file_name} successfully.", file_name
            )
        except Exception as e:
            logger.error(f"Error uploading PDF: {str(e)}")
            return response_handler(500, "Failed to Upload PDF", str(e))

    def fetch_pdfs_from_gcs_in_memory(self):
        """
        Fetch all PDFs for a course from GCS as in-memory files.

        Currently unused.

        Returns:
            A list of tuples (file_name, file_content), where file_content is a BytesIO object.
        """
        try:
            prefix = "pdfs/"
            files = []

            client = storage.Client()
            bucket = client.bucket(BUCKET_NAME)
            blobs = bucket.list_blobs(prefix=prefix)

            for blob in blobs:
                file_name = blob.name.split("/")[-1]
                file_content = BytesIO()
                blob.download_to_file(file_content)
                file_content.seek(0)
                files.append((file_name, file_content))

            return response_handler(200, "PDFs Fetched Successfully", files)
        except Exception as e:
            logger.error(f"error fetching pdfs, {str(e)}")
            return response_handler(500, "Failed to Fetch PDFs", str(e))

    def list_all(self):
        """
        List all PDF filenames from GCS.

        Returns:
            A list of filenames.
        """
        try:
            prefix = "pdfs/"
            filenames = []

            client = storage.Client()
            bucket = client.bucket(BUCKET_NAME)
            blobs = bucket.list_blobs(prefix=prefix)

            for blob in blobs:
                filename = blob.name.split("/")[-1]
                if filename.endswith(".pdf"):
                    filename = filename[:-4]
                filenames.append(filename)

            return response_handler(200, "PDFs Listed Successfully", filenames)
        except Exception as e:
            return response_handler(500, "Failed to List PDFs", str(e))

    def delete_pdf_from_gcs(self, filename):
        """
        Deletes a specific PDF file from GCS.

        Args:
            filename: The file to delete.

        Returns:
            A response dictionary indicating success or failure.
        """
        try:
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            blob_name = f"pdfs/{filename}"

            client = storage.Client()
            bucket = client.bucket(BUCKET_NAME)
            blob = bucket.blob(blob_name)

            if not blob.exists():
                return response_handler(
                    404,
                    "File Not Found",
                    f"File '{filename}' does not exist in course.",
                )

            blob.delete()
            return response_handler(200, "File Deleted Successfully", filename)
        except Exception as e:
            return response_handler(500, "Failed to Delete File", str(e))
