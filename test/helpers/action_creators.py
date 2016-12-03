from test.helpers.action_types import ADD_TODO, DISPATCH_IN_MIDDLE, THROW_ERROR, UNKNOWN_ACTION

def add_todo(text):
  return {'type': ADD_TODO, 'text': text}

def add_todo_if_empty(text):
  def anon(dispatch, get_state):
    if len(get_state()) == 0:
      add_todo(text)
  return anon

def dispatch_in_middle(bound_dispatch_fn):
  return {
    'type': DISPATCH_IN_MIDDLE,
    'bound_dispatch_fn': bound_dispatch_fn
  }

def throw_error():
  return {
    'type': THROW_ERROR
  }

def unknown_action():
  return {
    'type': UNKNOWN_ACTION
  }