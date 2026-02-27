class UserNotFound(Exception):
  def __init__(self, msg="") -> None:
    self.msg = msg or "user not found"


class PublisherNotFound(Exception):
  def __init__(self, msg=""):
    self.msg = msg or "publisher not found"


class AuthorNotFound(Exception):
  def __init__(self, msg="") -> None:
    self.msg = msg or "author not found"


class BookNotFound(Exception):
  def __init__(self, msg="") -> None:
    self.msg = msg or "book not found"


class BookCategoryNotFound(Exception):
  def __init__(self, msg="") -> None:
    self.msg = msg or "category not found"


class InvalidCreds(Exception):
  def __init__(self, msg="") -> None:
    self.msg = msg or "invalid credentials"
