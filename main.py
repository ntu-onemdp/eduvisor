from services.logger import Logger, configure_logger
import uvicorn
from fastapi import FastAPI, UploadFile
from models.pdf_model import PDFModel
from dotenv import load_dotenv
from models.post import Post

# For fastapi simple cache
from fastapi_simple_cache.backends.inmemory import InMemoryBackend
from fastapi_simple_cache import FastAPISimpleCache

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


# Get response from thread.
@app.get("/response")
def get_response(post: Post):
    log.info(f"Getting response for post: {post.title}")
    return {
        "post_title": post.title,
        "post_content": post.content,
        "response": f"Response for {post.title} with content: {post.content}",
    }


@app.on_event("startup")
async def startup():
    backend = InMemoryBackend()
    FastAPISimpleCache.init(backend=backend)


if __name__ == "__main__":
    configure_logger()

    uvicorn.run(app)
