# pydux

[Redux](https://github.com/reactjs/redux) reimplemented in Python.

[![PyPI version](https://badge.fury.io/py/pydux.svg)](https://badge.fury.io/py/pydux)

To see it in action, try the [todos](https://github.com/usrlocalben/urwid_todos) demo.  (Mouse-click needed, as in the original demo)

```pip install urwid_todos ; python -m urwid_todos```

##### What is it? Why would I want it?

The [Redux Readme](https://github.com/reactjs/redux) is a good place to start.

###### The Gist

>The whole state of your app is stored in an object tree inside a single store.
The only way to change the state tree is to emit an action, an object describing what happened.
To specify how the actions transform the state tree, you write pure reducers.

>That's it!


```python
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

```

##### Further examples of _Python_ usage


[urwid_pydux](https://github.com/usrlocalben/urwid_pydux) provides a [React-Redux](https://github.com/reactjs/react-redux) Component API for text/console GUIs made with [Urwid](https://github.com/urwid/urwid).

[urwid_todos](https://github.com/usrlocalben/urwid_todos) is a reimplementation of the Redux [todos](http://redux.js.org/docs/basics/ExampleTodoList.html) example made with [urwid_pydux](https://github.com/usrlocalben/urwid_pydux).

[canute-ui](https://github.com/Bristol-Braille/canute-ui) is the user interface for a multi-line electronic Braille e-book reader.


##### Acknowledgements

The initial test suite was imported from [python-redux](https://github.com/ebrakke/python-redux), a Redux implementation for Python 3.4+.
