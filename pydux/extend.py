def extend(*items):
    """fold-left shallow dictionary merge"""
    def merge(ax, item):
        ax.update(item)
        return ax
    return reduce(merge, items, {})
