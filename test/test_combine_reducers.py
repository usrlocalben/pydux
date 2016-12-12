import re
import unittest

import mock
from pydux import combine_reducers, create_store

ACTION_TYPES = {
    'INIT': '@@redux/INIT'
}


class TestCombineReducers(unittest.TestCase):
    def test_returns_reducer_that_maps_state_keys_to_given_reducers(self):
        def counter(state=None, action={}):
            if state is None:
                state = 0
            if action.get('type') == 'increment':
                return state + 1
            return state

        def stack(state=None, action={}):
            if state is None: state = []
            if action.get('type') == 'push':
                return list(state) + [action.get('value')]
            return state

        reducer = combine_reducers({
            'counter': counter,
            'stack': stack
        })
        s1 = reducer({}, { 'type': 'increment' })
        self.assertEqual(s1, { 'counter': 1, 'stack': []})
        s2 = reducer(s1, { 'type': 'push', 'value': 'a' })
        self.assertEqual(s2, { 'counter': 1, 'stack': [ 'a' ] })

    def test_ignores_all_props_which_are_not_functions(self):
        reducer = combine_reducers({
            'fake': True,
            'broken': 'string',
            'another': { 'nested': 'object' },
            'stack': lambda state, action: state if state is not None else []
        })

        self.assertEqual(list(reducer({}, { 'type': 'push' }).keys()), [ 'stack' ])

    def test_throws_if_reducer_returns_undefined_handling_an_action(self):
        def counter(state=None, action=None):
            state = 0 if state is None else state
            action = {} if action is None else action
            if action.get('type') == 'increment':
                return state + 1
            if action.get('type') == 'decrement':
                return state - 1
            if action.get('type') in ['decrement', 'whatever', None]:
                return None
            return state

        reducer = combine_reducers({ 'counter': counter })

        with self.assertRaises(Exception) as e:
            reducer({ 'counter': 0}, { 'type': 'whatever' })
        e = str(e.exception)
        self.assertTrue('"whatever"' in e and "counter" in e)

        with self.assertRaises(Exception) as e:
            reducer({ 'counter': 0 }, None)
        e = str(e.exception)
        self.assertTrue('"counter"' in e and 'an action' in e)

        with self.assertRaises(Exception) as e:
            reducer({ 'counter': 0 }, {})
        e = str(e.exception)
        self.assertTrue('"counter"' in e and 'an action' in e)

    def test_throws_error_on_first_call_if_reducer_returns_undefined_initializing(self):
        def counter(state=None, action=None):
            if action.get('type') == 'increment':
                return state + 1
            if action.get('type') == 'decrement':
                return state - 1
            return state

        reducer = combine_reducers({ 'counter': counter })
        with self.assertRaises(Exception) as e:
            reducer({})
        e = str(e.exception)
        self.assertTrue('"counter"' in e and 'initialization' in e)

    def test_catches_error_thrown_in_reducer_when_initializing_and_re_throw(self):
        def throwing_reducer(state=None, action=None):
            raise Exception('Error in reducer')
        reducer = combine_reducers({
            'throwing_reducer': throwing_reducer
        })

        with self.assertRaises(Exception) as e:
            reducer({})
        self.assertTrue('Error in reducer' in str(e.exception))

    def test_maintains_referential_equality_if_reducers_it_combines_does(self):
        def child_1(state=None, action=None):
            state = {} if state is None else state
            return state
        def child_2(state=None, action=None):
            state = {} if state is None else state
            return state
        def child_3(state=None, action=None):
            state = {} if state is None else state
            return state
        reducer = combine_reducers({
            'child_1': child_1,
            'child_2': child_2,
            'child_3': child_3
        })

        initial_state = reducer(None, '@@INIT')
        self.assertEqual(reducer(initial_state, { 'type': 'FOO' }), initial_state)

    def test_does_not_have_referential_equality_if_one_reducer_changes_something(self):
        def child_1(state=None, action=None):
            if state is None:
                state = {}
            return state

        def child_2(state=None, action=None):
            if action is None:
                action = {}
            if state is None:
                state = { 'count': 0 }
            if action.get('type') == 'increment':
                return { 'count': state['count'] + 1}
            return state

        def child_3(state=None, action=None):
            if state is None:
                state = {}
            return state

        reducer = combine_reducers({
            'child_1': child_1,
            'child_2': child_2,
            'child_3': child_3
        })

        initial_state = reducer(None)
        self.assertNotEqual(reducer(initial_state, { 'type': 'increment' }), initial_state)

    def test_throws_error_if_reducer_attempts_to_handle_a_private_action(self):
        def counter(state=None, action=None):
            if action is None:
                action = {}
            if state is None:
                state = 0
            if action.get('type') == 'increment':
                return state + 1
            if action.get('type') == 'decrement':
                return state - 1
            # Never do this
            if action.get('type') == ACTION_TYPES['INIT']:
                return 0
            return None

        reducer = combine_reducers({ 'counter': counter })
        with self.assertRaises(Exception) as e:
            reducer()
        self.assertTrue('counter' in str(e.exception) and 'private' in str(e.exception))

    @mock.patch('logging.warning', new_callable=mock.MagicMock())
    def test_warns_if_no_reducers_passed_to_combine_reducers(self, logging):
        def foo(state=None, action=None):
            if state is None:
                state = { 'bar': 1}
            return state
        def baz(state=None, action=None):
            if state is None:
                state = { 'qux': 3 }
            return state

        reducer = combine_reducers({
            'foo': foo,
            'baz': baz
        })
        reducer()
        self.assertEqual(len(logging.call_args_list), 0)

        reducer({ 'foo': { 'bar': 2 }})
        self.assertEqual(len(logging.call_args_list), 0)

        reducer({
            'foo': { 'bar': 2 },
            'baz': { 'qux': 4 }
        })
        self.assertEqual(len(logging.call_args_list), 0)

        create_store(reducer, { 'bar': 2 })
        m = str(logging.call_args_list[0])
        self.assertTrue(re.search(r'Unexpected key "bar".*create_store.*instead: ("foo"|"baz"), ("foo"|"baz")', m))

        create_store(reducer, { 'bar': 2, 'qux': 4, 'thud': 5 })
        m = str(logging.call_args_list[1])
        self.assertTrue(re.search(r'Unexpected keys ("qux"|"thud"), ("qux"|"thud").*create_store.*instead: ("foo"|"baz"), ("foo"|"baz")', m))

        create_store(reducer, 1)
        m = str(logging.call_args_list[2])
        self.assertTrue(re.search(r'create_store has an unexpected type of <class "int">.*keys: ("foo"|"baz"), ("foo"|"baz")', m))

        reducer({ 'corge': 2 })
        m = str(logging.call_args_list[3])
        self.assertTrue(re.search(r'Unexpected key "corge".*reducer.*instead: ("foo"|"baz"), ("foo"|"baz")', m))

        reducer({ 'rick': 2, 'morty': 4 })
        m = str(logging.call_args_list[4])
        self.assertTrue(re.search(r'Unexpected keys ("rick"|"morty"), ("rick"|"morty").*reducer.*instead: ("foo"|"baz"), ("foo"|"baz")', m))

        reducer(1)
        m = str(logging.call_args_list[5])
        self.assertTrue(re.search(r'reducer has an unexpected type of <class "int">', m))

    @mock.patch('logging.warning', new_callable=mock.MagicMock())
    def test_only_warns_for_unexpected_keys_once(self, logging):
        def foo(state=None, action=None):
            return { 'foo': 1 }
        def bar(state=None, action=None):
            return { 'bar': 2 }

        self.assertEqual(len(logging.call_args_list), 0)
        reducer = combine_reducers(dict(foo=foo, bar=bar))
        state = dict(foo=1, bar=2, qux=3)
        reducer(state, {})
        reducer(state, {})
        reducer(state, {})
        reducer(state, {})
        self.assertEqual(len(logging.call_args_list), 1)
        reducer(dict(baz=5, **state), {})
        reducer(dict(baz=5, **state), {})
        reducer(dict(baz=5, **state), {})
        reducer(dict(baz=5, **state), {})
        self.assertEqual(len(logging.call_args_list), 2)


if __name__ == '__main__':
    unittest.main()
