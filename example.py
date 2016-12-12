from __future__ import print_function
import pydux

# This is a reducer, a pure function with (state, action) => state signature.
# It describes how an action transforms the state into the next state.
#
# The shape of the state is up to you: it can be a primitive, an array, an object,
# or even an frozendict data structure [1]. The only important part is that you should
# not mutate the state object, but return a new object if the state changes.
#
# [1]: https://pypi.python.org/pypi/frozendict
#
# In this example, we use a `if` statement and strings, but you can use a
# helper that follows a different convention if it makes sense for your
# project.
def counter(state, action):
    if state is None:
        state = 0
    if action is None:
        return state
    elif action['type'] == 'INCREMENT':
        return state + 1
    elif action['type'] == 'DECREMENT':
        return state - 1
    return state

# Create a Redux store holding the state of your app.
# Its API is { subscribe, dispatch, get_state }.
store = pydux.create_store(counter)

# You can use subscribe() to update the UI in response to state changes.
store.subscribe(lambda: print(store.get_state()))

# The only way to mutate the internal state is to dispatch an action.
# The actions can be serialized, logged or stored and later replayed.
store.dispatch({ 'type': 'INCREMENT' })
# 1
store.dispatch({ 'type': 'INCREMENT' })
# 2
store.dispatch({ 'type': 'DECREMENT' })
# 1
