from dotenv import load_dotenv
from fastapi import FastAPI

from src.logger import get_logger
from src.routes import auth_router, book_router, author_router

load_dotenv()

logger = get_logger()


app = FastAPI(title="Library Management System")


@app.get("/")
async def root():
  return "app is running 2..."


for router in (auth_router, author_router, book_router):
  app.include_router(router)
