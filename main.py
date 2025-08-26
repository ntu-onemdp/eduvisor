from services.logger import Logger, configure_logger
import uvicorn
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import JSONResponse
from models.post import Post
from dotenv import load_dotenv
import os
from services.materials import MaterialsController

# For fastapi simple cache
from fastapi_simple_cache.backends.inmemory import InMemoryBackend
from fastapi_simple_cache import FastAPISimpleCache

# LLM related
from models.vector_store import VectorStore
from services.chat_service import ChatService

# Load environment variables
load_dotenv(".env", verbose=True, override=True)
_eduvisor_api_key = os.getenv("EDUVISOR_API_KEY")

app = FastAPI()
configure_logger()

log = Logger()

# Load stores
vector_store = VectorStore()

# Initialize controllers
material_controller = MaterialsController(
    vector_store=vector_store
)
chat_service = ChatService(vector_store=vector_store)


# Simple middleware to ensure that only requests from OneMDP are accepted.
# Set the API key in .env
@app.middleware("http")
async def auth(request: Request, call_next):
    api_key = request.headers.get("x-api-key")

    if api_key != _eduvisor_api_key:
        return JSONResponse(
            content={"error": "unauthorized. check that api key is correctly set"},
            status_code=401,
        )

    response = await call_next(request)
    return response


@app.get("/")
def read_root():
    log.info("Root endpoint accessed")
    return {"message": "Welcome to the Eduvisor API."}


# Upload PDF to Google Cloud Storage
@app.post("/upload")
def upload_pdf(files: list[UploadFile]):
    response = material_controller.add(files)
    log.info(f"Add pdfs response: {response}")
    return response


# Get response from thread.
@app.post("/response")
def get_response(posts: list[Post]):
    log.info(f"Getting response for posts: {posts[0].title}")

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
    You will give the response in a concise and clear manner, without any unnecessary information. Do not prompt the user for any further input or questions. Use HTML tags instead of markdown in your response (e.g. <b></b> to bold text instead of **).
    """

    query = ""
    for index, post in enumerate(posts):
        query += f"Post number: {index + 1}, Post title: {post.title}, Post content: {post.content}, Post author: {post.author} "

    response, token_used, main_topic = chat_service.invoke_response(
        persona, task, conditions, output_style, query
    )

    log.info(f"Response generated: {response}")
    log.info(f"Tokens used: {token_used}")
    log.info(f"Main topic: {main_topic}")

    return JSONResponse(
        status_code=200,
        content={
            "response": response,
        },
    )


@app.on_event("startup")
async def startup():
    backend = InMemoryBackend()
    FastAPISimpleCache.init(backend=backend)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
