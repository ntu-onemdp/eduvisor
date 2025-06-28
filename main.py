from services.logger import Logger, configure_logger
import uvicorn
from fastapi import FastAPI, UploadFile
from models.pdf_model import PDFModel
from dotenv import load_dotenv
from models.post import Post

# For fastapi simple cache
from fastapi_simple_cache.backends.inmemory import InMemoryBackend
from fastapi_simple_cache import FastAPISimpleCache

# LLM related
from services.chat_service import ChatService
from models.vectorstore_model import (
    load_vectorstore_from_gcs,
    VectorStoreModel,
)

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
    vector_store = VectorStoreModel()
    vector_store.generate_vectorstore_from_memory
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

    # Initialize LLM
    chatService = ChatService()
    llm = chatService.initialize_llm()

    # Load pdfs into memory
    pdf_model = PDFModel()
    pdf_response = pdf_model.fetch_pdfs_from_gcs_in_memory()

    if pdf_response["code"] != 200:
        log.error("error fetching pdfs")
        return pdf_response

    pdfs = pdf_response["data"]

    if not pdfs:
        log.warning("no pdfs found")
        return {"response": "no pdfs found."}

    vector_store = VectorStoreModel()
    vector_store_response = vector_store.generate_vectorstore_from_memory(pdfs)

    if vector_store_response["code"] != 200:
        log.error("error generating vectorstore from memory")

    # Initialize persona etc. (refer to chat_controller.py for reference)
    persona = """
    You are a virtual teaching assistant in Nanyang Technological University, Singapore. You are helpful, knowledgeable, and friendly.
    """

    task = """
    You assist students with their queries related to their courses and provide them with relevant information. 
    Your task is to help students with their multidisciplinary project. 
    """

    conditions = """
    If you do not know the answer, or if you are unsure, you should say "I don't know." instead of making up an answer.
    You are not a chatbot, you will give responses and help only if you know the answer. 
    You should not expect any response from the user, you will just give the response.
    """

    output_style = """
    You will give the response in a concise and clear manner, without any unnecessary information. Do not prompt the user for any further input or questions.
    """

    query = f"Post title: {post.title}, Post content: {post.content}"

    vector_store_response = load_vectorstore_from_gcs()
    if vector_store_response["code"] == 200:
        loaded_faiss_vs = vector_store_response["data"]
    else:
        log.error("Failed to load vectorstore from GCS")
        loaded_faiss_vs = None
    # loaded_faiss_vs = None

    response, token_used, main_topic = chatService.invoke_response(
        llm, persona, task, conditions, output_style, loaded_faiss_vs, query
    )

    log.info(f"Response generated: {response}")
    log.info(f"Tokens used: {token_used}")
    log.info(f"Main topic: {main_topic}")

    return {
        "post_title": post.title,
        "post_content": post.content,
        "response": response,
    }


@app.on_event("startup")
async def startup():
    backend = InMemoryBackend()
    FastAPISimpleCache.init(backend=backend)


if __name__ == "__main__":
    configure_logger()

    uvicorn.run(app)
