def extend(a, b):
    """shallow dictionary merge

    Args:
        a: dict to extend
        b: dict to apply to a

    Returns:
        new instance of the same type as _a_, with _a_ and _b_ merged.
    """
    if __debug__:
        assert isinstance(a, dict)
        assert isinstance(b, dict)

    out = type(a)(a)
    out.update(b)
    return out
