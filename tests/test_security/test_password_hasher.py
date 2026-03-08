from dataclasses import dataclass

import pytest

from core.security.password_hasher import PasswordHasher


@dataclass(frozen=True)
class PasswordHasherTestCase:
  password: str
  check_against: str
  is_valid: bool


test_cases = [
  pytest.param(
    PasswordHasherTestCase(password="secret", check_against="secret", is_valid=True),
    id="valid-password",
  ),
  pytest.param(
    PasswordHasherTestCase(password="secret", check_against="another-secret", is_valid=False),
    id="diff-password",
  ),
]


@pytest.mark.parametrize("case", test_cases)
def test_password_hasher(case: PasswordHasherTestCase):
  hashed = PasswordHasher.hash(case.password)
  assert hashed != "", "hashed value cannot be empty"

  # validate hashed
  is_valid, _ = PasswordHasher.verify(hashed, case.check_against)
  assert is_valid == case.is_valid
