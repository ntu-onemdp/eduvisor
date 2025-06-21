import os
import io
from google.cloud import storage
import streamlit as st
from response import response_handler
from io import BytesIO

# Initialize Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = st.secrets['GOOGLE_APPLICATION_CREDENTIALS']

class PDFModel:
    BUCKET_NAME = "vtabucket"

    def upload_pdf_to_gcs(self, uploaded_file, course_id):
        """
        Uploads a PDF file to Google Cloud Storage.

        Args:
            uploaded_file: The uploaded file object from Streamlit.
            course_id: The course ID used to organize PDFs in GCS.
        """
        try:
            file_name = uploaded_file.name
            blob_name = f"pdfs/{course_id}/{file_name}"

            client = storage.Client()
            bucket = client.bucket(self.BUCKET_NAME)
            blob = bucket.blob(blob_name)

            blob.upload_from_file(uploaded_file, content_type="application/pdf")
            return response_handler(201, f"Uploaded {file_name} successfully.", file_name)
        except Exception as e:
            print('upload pdf')
            print(str(e))
            return response_handler(500, "Failed to Upload PDF", str(e))

    def fetch_pdfs_from_gcs_in_memory(self, course_id):
        """
        Fetch all PDFs for a course from GCS as in-memory files.

        Args:
            course_id: The course ID.

        Returns:
            A list of tuples (file_name, file_content), where file_content is a BytesIO object.
        """
        try:
            prefix = f"pdfs/{course_id}/"
            files = []

            client = storage.Client()
            bucket = client.bucket(self.BUCKET_NAME)
            blobs = bucket.list_blobs(prefix=prefix)

            for blob in blobs:
                file_name = blob.name.split("/")[-1]
                file_content = BytesIO()
                blob.download_to_file(file_content)
                file_content.seek(0)
                files.append((file_name, file_content))
    
            return response_handler(200, "PDFs Fetched Successfully", files)
        except Exception as e:
            print('fetch')
            print(str(e))
            return response_handler(500, "Failed to Fetch PDFs", str(e))

    def list_pdfs_for_course(self, course_id):
        """
        List all PDF filenames for a course from GCS.

        Args:
            course_id: The course ID.

        Returns:
            A list of filenames.
        """
        try:
            prefix = f"pdfs/{course_id}/"
            filenames = []

            client = storage.Client()
            bucket = client.bucket(self.BUCKET_NAME)
            blobs = bucket.list_blobs(prefix=prefix)

            for blob in blobs:
                filename = blob.name.split("/")[-1]
                if filename.endswith(".pdf"):
                    filename = filename[:-4]
                filenames.append(filename)

            return response_handler(200, "PDFs Listed Successfully", filenames)
        except Exception as e:
            return response_handler(500, "Failed to List PDFs", str(e))

    def delete_pdf_from_gcs(self, course_id, filename):
        """
        Deletes a specific PDF file from GCS.

        Args:
            course_id: The course ID.
            filename: The file to delete.

        Returns:
            A response dictionary indicating success or failure.
        """
        try:
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            blob_name = f"pdfs/{course_id}/{filename}"

            client = storage.Client()
            bucket = client.bucket(self.BUCKET_NAME)
            blob = bucket.blob(blob_name)

            if not blob.exists():
                return response_handler(404, "File Not Found", f"File '{filename}' does not exist in course '{course_id}'.")

            blob.delete()
            return response_handler(200, "File Deleted Successfully", filename)
        except Exception as e:
            return response_handler(500, "Failed to Delete File", str(e))
