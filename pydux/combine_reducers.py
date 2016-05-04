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
                      for key, reducer in reducers.iteritems()
                      if hasattr(reducer, '__call__')}

    def combination(state=None, action=None):
        if state is None:
            state = {}

        has_changed = False
        next_state = {}
        for key, reducer in final_reducers.iteritems():
            previous_state_for_key = state.get(key)
            next_state_for_key = reducer(previous_state_for_key, action)
            next_state[key] = next_state_for_key
            has_changed = (has_changed or
                           next_state_for_key != previous_state_for_key)
        return next_state if has_changed else state

    return combination
