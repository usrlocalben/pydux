def compose(*funcs):
    """
    chained function composition wrapper

    creates function f, where f(x) = arg0(arg1(arg2(...argN(x))))

    if *funcs is empty, an identity function is returned.

    Args:
        *funcs: list of functions to chain
    
    Returns:
        a new function composed of chained calls to *args
    """
    if not funcs:
        return lambda *args: args
    last = funcs[-1]
    rest = funcs[0:-1]
    return lambda *args: reduce(lambda ax, func: func(ax),
                                reversed(rest), last(*args))
