from sqlalchemy import Select


def _parse_int(val):
  try:
    return int(val)
  except (TypeError, ValueError):
    raise ValueError(f"required int, got {val!r} of type {type(val).__name__}")


def modify_stmt_for_rate_limit[T](stmt: Select[tuple[T]], **kwargs):
  """Modify select statement for rate limiting by adding *limit* and *skip* parameters.

  Args:
    stmt (Select[tuple[T]]): select statement to modify
    **kwargs (dict): parameters are parsed from *kwargs*.

  Returns:
    Select[tuple[T]]: modified select statement with limit and offset

  Raises:
    ValueError: if *limit* or *skip* parameters are not convertible to `int`.
  """
  if (skip := kwargs.get("skip")) is not None:
    stmt = stmt.offset(_parse_int(skip))
  if (limit := kwargs.get("limit")) is not None:
    stmt = stmt.limit(_parse_int(limit))

  return stmt
