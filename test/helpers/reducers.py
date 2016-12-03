from test.helpers.action_types import ADD_TODO, DISPATCH_IN_MIDDLE, THROW_ERROR

def id(state = []):
	id = 0
	for item in state:
		id = item.get('id') if item.get('id') > id else id
	return id + 1

def todos(state=None, action={}):
	if state is None:
		state = []
	if action.get('type') == ADD_TODO:
		return list(state) + [{
			'id': id(state),
			'text': action['text']
		}]
	else:
		return state

def todos_reverse(state=None, action={}):
	if state is None:
		state = []
	if action.get('type') == ADD_TODO:
		return [{
			'id': id(state),
			'text': action.get('text')
		}] + list(state)
	else:
		return state

def dispatch_in_middle_of_reducer(state=None, action={}):
	if state is None:
		state = []
	if action.get('type') == DISPATCH_IN_MIDDLE:
		action.get('bound_dispatch_fn')()
		return state
	else:
		return state

def error_throwing_reducer(state=None, action={}):
	if state is None:
		state = []
	if action.get('type') == THROW_ERROR:
		raise Exception()
	else:
		return state

reducers = {
	'todos': todos,
	'todos_reverse': todos_reverse,
	'dispatch_in_middle_of_reducer': dispatch_in_middle_of_reducer,
	'error_throwing_reducer': error_throwing_reducer
}