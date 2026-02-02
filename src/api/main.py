from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db import db_lifespan
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
  async with db_lifespan():
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
  return "app is running..."
