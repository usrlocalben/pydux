def extend(*items):
    """fold-left shallow dictionary merge"""
    out = {}
    for item in items:
        out.update(item)
    return out
