from dotenv import load_dotenv
from fastapi import FastAPI

from src.logger import get_logger
from src.routes import ROUTERS

load_dotenv()

logger = get_logger()
app = FastAPI(title="Library Management System")


@app.get("/")
async def root():
  return "app is running..."


for router in ROUTERS:
  app.include_router(router)
