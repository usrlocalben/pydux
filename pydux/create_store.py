"""
python + redux == pydux

Redux: http://redux.js.org

A somewhat literal translation of Redux.

Closures in Python are over references, as opposed to
names in JavaScript, so they are read-only.  Single-
element arrays are used to create read/write closures.

"""


class ActionTypes(object):
    INIT = '@@redux/INIT'


class StoreDict(dict):
    def get_state(self):
        return self['get_state']()
    def subscribe(self, listener):
        return self['subscribe'](listener)
    def dispatch(self, action):
        return self['dispatch'](action)
    def replace_reducer(self, next_reducer):
        return self['replace_reducer'](next_reducer)


def create_store(reducer, initial_state=None, enhancer=None):
    """
    redux in a nutshell.

    observable has been omitted.

    Args:
        reducer: root reducer function for the state tree
        initial_state: optional initial state data
        enhancer: optional enhancer function for middleware etc.

    Returns:
        a Pydux store
    """
    if enhancer is not None:
        if not hasattr(enhancer, '__call__'):
            raise TypeError('Expected the enhancer to be a function.')
        return enhancer(create_store)(reducer, initial_state)

    if not hasattr(reducer, '__call__'):
        raise TypeError('Expected the reducer to be a function.')

    # single-element arrays for r/w closure
    current_reducer = [reducer]
    current_state = [initial_state]
    current_listeners = [[]]
    next_listeners = [current_listeners[0]]
    is_dispatching = [False]

    def ensure_can_mutate_next_listeners():
        if next_listeners[0] == current_listeners[0]:
            next_listeners[0] = current_listeners[0][:]

    def get_state():
        return current_state[0]

    def subscribe(listener):
        if not hasattr(listener, '__call__'):
            raise TypeError('Expected listener to be a function.')

        is_subscribed = [True]  # r/w closure

        ensure_can_mutate_next_listeners()
        next_listeners[0].append(listener)

        def unsubcribe():
            if not is_subscribed[0]:
                return
            is_subscribed[0] = False

            ensure_can_mutate_next_listeners()
            index = next_listeners[0].index(listener)
            next_listeners[0].pop(index)

        return unsubcribe

    def dispatch(action):
        if not isinstance(action, dict):
            raise TypeError('Actions must be a dict. '
                            'Use custom middleware for async actions.')

        if action.get('type') is None:
            raise ValueError('Actions must have a non-None "type" property. '
                             'Have you misspelled a constant?')

        if is_dispatching[0]:
            raise Exception('Reducers may not dispatch actions.')

        try:
            is_dispatching[0] = True
            current_state[0] = current_reducer[0](current_state[0], action)
        finally:
            is_dispatching[0] = False

        listeners = current_listeners[0] = next_listeners[0]
        for listener in listeners:
            listener()

        return action

    def replace_reducer(next_reducer):
        if not hasattr(next_reducer, '__call__'):
            raise TypeError('Expected next_reducer to be a function')

        current_reducer[0] = next_reducer
        dispatch({'type': ActionTypes.INIT})

    dispatch({'type': ActionTypes.INIT})

    return StoreDict(
        dispatch=dispatch,
        subscribe=subscribe,
        get_state=get_state,
        replace_reducer=replace_reducer,
    )
