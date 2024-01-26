def normalize_value(value: int | float | None) -> int | float:
    if not isinstance(value, int) and not isinstance(value, float):
        return 0
    return value
