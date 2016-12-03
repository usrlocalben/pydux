import unittest
import unittest.mock as mock
import re
from pydux import bind_action_creators, create_store
from test.helpers.reducers import reducers
from test.helpers.action_creators import add_todo, add_todo_if_empty, dispatch_in_middle, unknown_action

todos = reducers['todos']
action_creators = dict(
	add_todo=add_todo,
	add_todo_if_empty=add_todo_if_empty,
	dispatch_in_middle=dispatch_in_middle,
	unknown_action=unknown_action
)

class TestBindActionCreators(unittest.TestCase):
	store = None
	action_creator_functions = None
	def setUp(self):
		self.store = create_store(todos)
		self.action_creator_functions = dict(action_creators)
		for key in self.action_creator_functions:
			if not hasattr(self.action_creator_functions[key], '__call__'):
				del self.action_creator_functions[key]

	def test_wraps_action_creators_with_dispatch_function(self):
		bound_action_creators = bind_action_creators(action_creators, self.store['dispatch'])
		self.assertEqual(bound_action_creators.keys(), self.action_creator_functions.keys())

		action = bound_action_creators['add_todo']('Hello')
		self.assertEqual(action, action_creators['add_todo']('Hello'))

		self.assertEqual(self.store['get_state'](), [dict(id=1, text='Hello')])

	def test_skips_non_function_values_in_the_passed_object(self):
		bound_action_creators = bind_action_creators(dict(
			foo=42,
			bar='baz',
			wow=None,
			much={},
			**action_creators
		), self.store['dispatch'])

		self.assertEqual(bound_action_creators.keys(), self.action_creator_functions.keys())

	def test_supports_wrapping_single_function_only(self):
		action_creator = action_creators['add_todo']
		bound_action_creator = bind_action_creators(action_creator, self.store['dispatch'])

		action = bound_action_creator('Hello')
		self.assertEqual(action, action_creator('Hello'))
		self.assertEqual(self.store['get_state'](), [dict(id=1, text='Hello')])

	def test_throws_for_undefined_action_creator(self):
		with self.assertRaises(Exception) as e:
			bind_action_creators(None, self.store['dispatch'])
		self.assertTrue(re.search(r'bind_action_creators expected an object or a function, instead received None', str(e.exception)))

	def test_throws_for_a_primative_action_creator(self):
		with self.assertRaises(Exception) as e:
			bind_action_creators('string', self.store['dispatch'])
		self.assertTrue(re.search('bind_action_creators expected an object or a function, instead received <class \'str\'>', str(e.exception)))
if __name__ == '__main__':
	unittest.main()
