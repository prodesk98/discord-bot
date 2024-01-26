def normalize_value(value: int | float | bytes | str | None, typing: int|float = int) -> int | float:
    if value is None:
        return 0

    if isinstance(value, str) or isinstance(value, bytes):
        if typing is int:
            return int(value)
        else:
            return float(value)

    if typing is float:
        return float(value)

    return int(round(value))
