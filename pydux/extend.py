def extend(*args):
    """shallow dictionary merge

    Args:
        a: dict to extend
        b: dict to apply to a

    Returns:
        new instance of the same type as _a_, with _a_ and _b_ merged.
    """
    if not args:
        return {}

    first = args[0]
    rest = args[1:]
    out = type(first)(first)
    for each in rest:
        out.update(each)
    return out
