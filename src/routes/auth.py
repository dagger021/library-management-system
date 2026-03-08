from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from constants import UserRole
from core.dependencies import (
  AuthService,
  SafeUser,
  get_auth_service,
  get_current_user,
)
from src.logger import get_logger
from repositories.errors import AlreadyExists
from services.errors import InvalidCreds, UserNotFound

INTERNAL_SERVER_ERROR = HTTPException(
  status.HTTP_500_INTERNAL_SERVER_ERROR, "internal server error"
)

auth_router = APIRouter(tags=["auth"])
logger = get_logger()


class RegisterRequest(BaseModel):
  email: str
  password: str
  role: UserRole


class LoginRequest(BaseModel):
  email: str
  password: str


class LoginResponse(BaseModel):
  token: str


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
  body: RegisterRequest, auth_svc: AuthService = Depends(get_auth_service)
):
  try:
    await auth_svc.register(email=body.email, password=body.password, role=body.role)

  except AlreadyExists:
    raise HTTPException(status.HTTP_409_CONFLICT, "email already exists")

  except Exception as e:
    logger.error("unexpected error:", e)
    raise INTERNAL_SERVER_ERROR


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(
  body: LoginRequest, auth_svc: AuthService = Depends(get_auth_service)
):
  try:
    token = await auth_svc.login(email=body.email, password=body.password)
    return LoginResponse(token=token)

  except UserNotFound:
    raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")

  except InvalidCreds:
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")

  except Exception as e:
    logger.error("unexpected error:", e)
    raise INTERNAL_SERVER_ERROR
