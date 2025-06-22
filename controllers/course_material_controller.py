from models.pdf_model import PDFModel
from models.vectorstore_model import VectorStoreModel


class CourseMaterialController:
    def __init__(self):
        self.pdf_model = PDFModel()
        self.vectorstore_model = VectorStoreModel()

    def list_files(self, course_id):
        """Fetch course materials"""

        return self.pdf_model.list_pdfs_for_course(course_id)

    def delete_file(self, course_id, filename):
        """Delete a course file"""
        return self.pdf_model.delete_pdf_from_gcs(course_id, filename)

    def upload_file(self, uploaded_file, course_id):
        """Upload a new file to GCS"""
        return self.pdf_model.upload_pdf_to_gcs(uploaded_file, course_id)

    def fetch_pdfs_in_memory(self, course_id):
        return self.pdf_model.fetch_pdfs_from_gcs_in_memory(course_id)

    def generate_vectorstore(self, pdfs):
        return self.vectorstore_model.generate_vectorstore_from_memory(pdfs)

    def save_vectorstore(self, vectorstore, course_id):
        return self.vectorstore_model.save_vectorstore_to_gcs_direct(
            vectorstore, course_id
        )
