from __future__ import print_function
"""
logging middleware example
"""

def log_middleware(store):
    """log all actions to console as they are dispatched"""
    def wrapper(next_):
        def log_dispatch(action):
            print('Dispatch Action:', action)
            return next_(action)
        return log_dispatch
    return wrapper
