from sqlalchemy import Select


def modify_stmt_for_rate_limit[T](stmt: Select[tuple[T]], **kwargs):
  """Modify select statement for rate limiting by adding *limit* and *skip* parameters.

  Args:
    stmt (Select[tuple[T]]): select statement to modify
    **kwargs (dict): parameters are parsed from *kwargs*.

  Returns:
    Select[tuple[T]]: modified select statement with limit and offset
  """
  if (skip := kwargs.get("skip", 0)) > 0:
    stmt = stmt.offset(skip)
  if (limit := kwargs.get("limit", 0)) > 0:
    stmt = stmt.limit(limit)

  return stmt
