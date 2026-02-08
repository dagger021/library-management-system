def skip_n_limit(skip: int | None = None, limit: int | None = None):
  ret = {}
  if skip is not None and skip > 0:
    ret["skip"] = skip
  if limit is not None and limit > 0:
    ret["limit"] = limit
  return ret
