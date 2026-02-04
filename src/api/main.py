from dotenv import load_dotenv
from fastapi import FastAPI

from src.logger import get_logger
from src.routes import auth_router

load_dotenv()

logger = get_logger()


app = FastAPI(title="Library Management System")


@app.get("/")
async def root():
  return "app is running..."


app.include_router(auth_router)
