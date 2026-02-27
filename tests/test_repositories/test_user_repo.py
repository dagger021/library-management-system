from dataclasses import dataclass

from constants import UserRole
from repositories.errors import AlreadyExists
from schemas import User
from repositories import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

import pytest
import pytest_asyncio

FAKE_USER_DATA = dict(
  email="johndoe@example.com", password="secret", role=UserRole.MEMBER
)


@pytest_asyncio.fixture
async def seed_one_user(async_session: AsyncSession):
  async_session.add(user := User(**FAKE_USER_DATA))
  await async_session.flush()

  return user


@pytest_asyncio.fixture
async def user_repo(async_session: AsyncSession):
  return UserRepository(async_session)


@dataclass(frozen=True)
class GetByEmailTestCase:
  email: str
  expected_none: bool
  expected_email: str | None = None


get_by_email_testcases = [
  pytest.param(
    GetByEmailTestCase(
      email=FAKE_USER_DATA["email"],
      expected_email=FAKE_USER_DATA["email"],
      expected_none=False,
    ),
    id="existing-email",
  ),
  pytest.param(
    GetByEmailTestCase(email="unknown@example.com", expected_none=True),
    id="non-existing-email",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", get_by_email_testcases)
async def test_get_by_email(
  user_repo: UserRepository, case: GetByEmailTestCase, seed_one_user: User
):
  user = await user_repo.get_by_email(email=case.email)
  assert case.expected_none and user is None or user.email == case.expected_email


@dataclass(frozen=True)
class CreateTestCase:
  email: str
  password: str
  role: UserRole
  expected_exception: Exception | None = None


create_test_cases = [
  pytest.param(
    CreateTestCase(
      email="new-email@example.com",
      password="secret",
      role=UserRole.MEMBER,
    ),
    id="with-non-existing-email",
  ),
  pytest.param(
    CreateTestCase(
      **FAKE_USER_DATA,  # same credentials as seeded user
      expected_exception=AlreadyExists,
    ),
    id="with-existing-email",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", create_test_cases)
async def test_create(user_repo: UserRepository, case: CreateTestCase, seed_one_user):
  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      await user_repo.create(email=case.email, password=case.password, role=case.role)
    return

  # create user
  user_id = await user_repo.create(
    email=case.email, password=case.password, role=case.role
  )
  # check by getting user by email
  user = await user_repo.get_by_email(email=case.email)
  assert user is not None  # must get some user
  assert user_id == user.id # id is same
  assert user.email == case.email # email is same
  assert user.password != case.password # password is hashed, i.e., not same
  assert user.role == case.role # role is same
