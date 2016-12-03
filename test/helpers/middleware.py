def thunk(store):
	dispatch = store['dispatch']
	get_state = store['get_state']
	
	def apply_middleware(next):
		def apply_action(action):
			if hasattr(action, '__call__'):
				action(dispatch, get_state)
			else:
				next(action)
		return apply_action
	return apply_middleware