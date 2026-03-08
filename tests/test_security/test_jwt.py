from dataclasses import dataclass

from constants import UserRole
from core.security.jwt import AuthJWT, AuthPayload
import pytest


@dataclass(frozen=True)
class AuthJWT_TestCase:
  payload: AuthPayload


authjwt_test_cases = [
  pytest.param(
    AuthJWT_TestCase(payload=AuthPayload(sub="username1", role=UserRole.ADMIN)),
    id="valid-payload",
  ),
  pytest.param(
    AuthJWT_TestCase(payload=AuthPayload(sub="username2", role=UserRole.MEMBER)),
    id="valid-payload",
  ),
]


@pytest.mark.parametrize("case", authjwt_test_cases)
def test_authJwt(case: AuthJWT_TestCase):
  # sign: payload to token
  assert case.payload.exp is None
  token_str = AuthJWT.sign(case.payload)  # should populate exp field
  assert case.payload.exp is not None
  assert token_str != ""

  # validate: token to payload
  validated_payload = AuthJWT.validate(token_str)
  assert validated_payload.sub == case.payload.sub
  assert validated_payload.role == case.payload.role
