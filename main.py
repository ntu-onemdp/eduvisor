from services.logger import Logger, configure_logger
import uvicorn
from fastapi import FastAPI, UploadFile
from models.pdf_model import PDFModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

log = Logger()


@app.get("/")
def read_root():
    log.info("Root endpoint accessed")
    return {"message": "Welcome to the Eduvisor API"}


# Upload PDF to Google Cloud Storage
@app.post("/upload")
def upload_pdf(file: UploadFile):
    pdf_model = PDFModel()
    response = pdf_model.upload_pdf_to_gcs(file)
    log.info(f"PDF upload response: {response}")
    return response


# List all PDFs
@app.get("/all")
def list_all_pdfs():
    pdf_model = PDFModel()
    response = pdf_model.list_all()
    log.info(f"List all PDFs response: {response}")
    return response


# Fetch PDFs from Google Cloud Storage
@app.get("/fetch")
def fetch_pdfs():
    pdf_model = PDFModel()
    response = pdf_model.fetch_pdfs_from_gcs_in_memory()
    log.info(f"Fetch PDFs response: {response}")
    return response


# Delete a specific PDF
@app.delete("/{filename}")
def delete_pdf(filename: str):
    pdf_model = PDFModel()
    response = pdf_model.delete_pdf_from_gcs(filename)
    log.info(f"Delete PDF response: {response}")
    return response


if __name__ == "__main__":
    configure_logger()

    uvicorn.run(app)
