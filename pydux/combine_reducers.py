from __future__ import absolute_import

import random
from string import ascii_letters

from .create_store import ActionTypes


def get_undefined_state_error_message(key, action):
    action_type = action and action['type']
    action_name = action_type and str(action_type) or 'an action'
    return ('Given action "%s", reducer "%s" returned None.  '
            'To ignore an action you must return the previous '
            'state.' % (action_name, key))

def assert_reducer_sanity(reducers):
    for key, reducer in reducers.items():
        initial_state = reducer(None, {'type': ActionTypes.INIT})

        if initial_state is None:
            msg = ('Reducer "%s" returned None during initialization. '
                   'If the state passed to the reducer is undefined, '
                   'you must explicitly return the initial state. '
                   'The initial state may not be None.' % (key,))
            raise Exception(msg)
        ty = ('@@redux/PROBE_UNKNOWN_ACTION_%s' %
              ('.'.join(random.choice(ascii_letters) for _ in range(20)),))
        if reducer(None, {'type': ty}) is None:
            msg = ('Reducer "%s" returned None when probed with a random type. '
                   'Don\'t try to handle %s or other actions in the "redux/*" '
                   'namespace. They are considered private. Instead, you must '
                   'return the current state for any unknown actions, unless '
                   'it is None, in which case you must return initial state, '
                   'regardless of the action type. The initial state may not '
                   'be None.' % (key, ActionTypes.INIT))
            raise Exception(msg)




def combine_reducers(reducers):
    """
    composition tool for creating reducer trees.
   
    Args:
        reducers: dict with state keys and reducer functions
                  that are responsible for each key

    Returns:
        a new, combined reducer function
    """
    final_reducers = {key: reducer
                      for key, reducer in reducers.items()
                      if hasattr(reducer, '__call__')}

    sanity_error = None
    try:
        assert_reducer_sanity(final_reducers)
    except Exception as e:
        sanity_error = e

    def combination(state=None, action=None):
        if state is None:
            state = {}
        if sanity_error:
            raise sanity_error

        has_changed = False
        next_state = {}
        for key, reducer in final_reducers.items():
            previous_state_for_key = state.get(key)
            next_state_for_key = reducer(previous_state_for_key, action)
            if next_state_for_key is None:
                msg = get_undefined_state_error_message(key, action)
                raise Exception(msg)
            next_state[key] = next_state_for_key
            has_changed = (has_changed or
                           next_state_for_key != previous_state_for_key)
        return next_state if has_changed else state

    return combination
