def skip_n_limit(skip: int | None = None, limit: int | None = None):
  if skip is not None and skip <= 0:
    skip = None
  if limit is not None and limit <= 0:
    limit = None
  return dict(skip=skip, limit=limit)
