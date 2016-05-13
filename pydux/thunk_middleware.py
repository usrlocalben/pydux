"""
thunks for pydux
original from https://github.com/gaearon/redux-thunk
"""


def thunk_middleware(store):
    dispatch, get_state = store['dispatch'], store['get_state']

    def wrapper(next_):
        def thunk_dispatch(action):
            if hasattr(action, '__call__'):
                return action(dispatch, get_state)
            return next_(action)
        return thunk_dispatch
    return wrapper
