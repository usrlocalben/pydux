from .compose import compose
from .extend import extend


def apply_middleware(*middlewares):
    """
    creates an enhancer function composed of middleware

    Args:
        *middlewares: list of middleware functions to apply

    Returns:
        an enhancer for subsequent calls to create_store()
    """
    def inner(create_store_):
        def create_wrapper(reducer, enhancer=None):
            store = create_store_(reducer, enhancer)
            dispatch = store['dispatch']
            middleware_api = {
                'get_state': store['get_state'],
                'dispatch': lambda action: dispatch(action),
            }
            chain = [mw(middleware_api) for mw in middlewares]
            dispatch = compose(*chain)(store['dispatch'])

            return extend(store, {'dispatch': dispatch})
        return create_wrapper
    return inner
