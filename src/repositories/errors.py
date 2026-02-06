class AlreadyExists(Exception): ...


class NotFound(Exception):
  def __init__(self, msg: str = ""):
    self.msg = msg or "record not found"
