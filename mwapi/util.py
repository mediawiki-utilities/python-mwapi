def _normalize_value(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, bool):
        return "" if value else None
    elif hasattr(value, "__iter__"):
        return "|".join(str(v) for v in value)
    else:
        return value


def _normalize_params(params, query_continue=None):
    normal_params = {k: _normalize_value(v) for k, v in params.items()}
    normal_params = {k: v for k, v in normal_params.items() if v is not None}

    if query_continue is not None:
        normal_params.update(query_continue)

    return normal_params
