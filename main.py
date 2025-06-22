from services.logger import Logger
import uvicorn
from fastapi import FastAPI

app = FastAPI()

log = Logger()


@app.get("/")
async def read_root():
    await log.info("Root endpoint accessed")
    return {"message": "Welcome to the Eduvisor API"}


if __name__ == "__main__":
    uvicorn.run(app)
