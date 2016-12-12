from __future__ import absolute_import

import unittest

import mock
from pydux import create_store, combine_reducers
from .helpers.action_creators import add_todo, dispatch_in_middle, throw_error, unknown_action
from .helpers.reducers import reducers


class TestCreateStoreMethod(unittest.TestCase):
    def test_exposes_public_API(self):
        store = create_store(combine_reducers(reducers))
        methods = store.keys()

        self.assertEqual(len(methods), 4)
        self.assertTrue('subscribe' in methods)
        self.assertTrue('dispatch' in methods)
        self.assertTrue('get_state' in methods)
        self.assertTrue('replace_reducer' in methods)

    def test_throws_if_reducer_is_not_a_function(self):
        with self.assertRaises(Exception):
            create_store(combine_reducers)
        with self.assertRaises(Exception):
            create_store('test')
        with self.assertRaises(Exception):
            create_store({})
        try:
            create_store(lambda *x: {})
        except Exception as e:
            self.fail('create_store(lambda: {}) should not have failed')

    def test_passes_initial_action_and_initial_state(self):
        store = create_store(reducers['todos'], [
            {
                'id': 1,
                'text': 'Hello'
            }
        ])
        self.assertEqual(store['get_state'](), [{ 'id': 1, 'text': 'Hello' }])

    def test_applies_reducer_to_previous_state(self):
        store = create_store(reducers['todos'])
        self.assertEqual(store['get_state'](), [])

        store['dispatch'](unknown_action())
        self.assertEqual(store['get_state'](), [])

        store['dispatch'](add_todo('Hello'))
        self.assertEqual(store['get_state'](), [
            {
                'id': 1,
                'text': 'Hello'
            }
        ])

        store['dispatch'](add_todo('World'))
        self.assertEqual(store['get_state'](), [
            {
                'id': 1,
                'text': 'Hello'
            },
            {
                'id': 2,
                'text': 'World'
            }
        ])

    def test_applied_reducer_to_initial_state(self):
        store = create_store(reducers['todos'], [
            {
                'id': 1,
                'text': 'Hello'
            }
        ])
        self.assertEqual(store['get_state'](), [
            {
                'id': 1,
                'text': 'Hello'
            }
        ])

        store['dispatch'](unknown_action())
        self.assertEqual(store['get_state'](), [
            {
                'id': 1,
                'text': 'Hello'
            }
        ])

        store['dispatch'](add_todo('World'))
        self.assertEqual(store['get_state'](), [
            {
                'id': 1,
                'text': 'Hello'
            },
            {
                'id': 2,
                'text': 'World'
            }
        ])

    def test_preserves_state_when_replacing_reducer(self):
        store = create_store(reducers['todos'])
        store['dispatch'](add_todo('Hello'))
        store['dispatch'](add_todo('World'))
        self.assertEqual(store['get_state'](), [
            {
                'id': 1,
                'text': 'Hello'
            },
            {
                'id': 2,
                'text': 'World'
            }
        ])

        store['replace_reducer'](reducers['todos_reverse'])
        self.assertEqual(store['get_state'](), [
            {
                'id': 1,
                'text': 'Hello'
            },
            {
                'id': 2,
                'text': 'World'
            }
        ])

        store['dispatch'](add_todo('Perhaps'))
        self.assertEqual(store['get_state'](), [
            {
                'id': 3,
                'text': 'Perhaps'
            },
            {
                'id': 1,
                'text': 'Hello'
            },
            {
                'id': 2,
                'text': 'World'
            }
        ])

        store['replace_reducer'](reducers['todos'])
        self.assertEqual(store['get_state'](), [
            {
                'id': 3,
                'text': 'Perhaps'
            },
            {
                'id': 1,
                'text': 'Hello'
            },
            {
                'id': 2,
                'text': 'World'
            }
        ])

        store['dispatch'](add_todo('Surely'))
        self.assertEqual(store['get_state'](), [
            {
                'id': 3,
                'text': 'Perhaps'
            },
            {
                'id': 1,
                'text': 'Hello'
            },
            {
                'id': 2,
                'text': 'World'
            },
            {
                'id': 4,
                'text': 'Surely'
            }
        ])

    def test_supports_multiple_subscriptions(self):
        store = create_store(reducers['todos'])
        listener_a = mock.MagicMock()
        listener_b = mock.MagicMock()

        unsubscribe_a = store['subscribe'](listener_a)
        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_a.call_args_list), 1)
        self.assertEqual(len(listener_b.call_args_list), 0)

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_a.call_args_list), 2)
        self.assertEqual(len(listener_b.call_args_list), 0)

        unsubscribe_b = store['subscribe'](listener_b)
        self.assertEqual(len(listener_a.call_args_list), 2)
        self.assertEqual(len(listener_b.call_args_list), 0)

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_a.call_args_list), 3)
        self.assertEqual(len(listener_b.call_args_list), 1)

        unsubscribe_a()
        self.assertEqual(len(listener_a.call_args_list), 3)
        self.assertEqual(len(listener_b.call_args_list), 1)

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_a.call_args_list), 3)
        self.assertEqual(len(listener_b.call_args_list), 2)

        unsubscribe_b()
        self.assertEqual(len(listener_a.call_args_list), 3)
        self.assertEqual(len(listener_b.call_args_list), 2)

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_a.call_args_list), 3)
        self.assertEqual(len(listener_b.call_args_list), 2)

        unsubscribe_a = store['subscribe'](listener_a)
        self.assertEqual(len(listener_a.call_args_list), 3)
        self.assertEqual(len(listener_b.call_args_list), 2)

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_a.call_args_list), 4)
        self.assertEqual(len(listener_b.call_args_list), 2)

    def test_only_removes_listener_once_when_unsubscribe_is_called(self):
        store = create_store(reducers['todos'])
        listener_a = mock.MagicMock()
        listener_b = mock.MagicMock()

        unsubscribe_a = store['subscribe'](listener_a)
        store['subscribe'](listener_b)

        unsubscribe_a()
        unsubscribe_a()

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_a.call_args_list), 0)
        self.assertEqual(len(listener_b.call_args_list), 1)

    def test_only_removes_relevant_listener_when_unsubscribe_is_called(self):
        store = create_store(reducers['todos'])
        listener = mock.MagicMock()

        store['subscribe'](listener)
        unsubscribe_second = store['subscribe'](listener)

        unsubscribe_second()
        unsubscribe_second()

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener.call_args_list), 1)

    def test_supports_removing_a_subscription_within_a_subscription(self):
        store = create_store(reducers['todos'])
        listener_a = mock.MagicMock()
        listener_b = mock.MagicMock()
        listener_c = mock.MagicMock()

        store['subscribe'](listener_a)
        unsub_b = store['subscribe'](lambda: [listener_b(), unsub_b()])
        store['subscribe'](listener_c)

        store['dispatch'](unknown_action())
        store['dispatch'](unknown_action())

        self.assertEqual(len(listener_a.call_args_list), 2)
        self.assertEqual(len(listener_b.call_args_list), 1)
        self.assertEqual(len(listener_c.call_args_list), 2)

    def test_delays_unsubscribe_until_the_end_of_current_dispatch(self):
        store = create_store(reducers['todos'])

        unsubscribe_handles = []
        def do_unsubscribe_all():
            for unsubscribe in unsubscribe_handles:
                unsubscribe()

        listener_1 = mock.MagicMock()
        listener_2 = mock.MagicMock()
        listener_3 = mock.MagicMock()

        unsubscribe_handles.append(store['subscribe'](lambda: listener_1()))
        unsubscribe_handles.append(store['subscribe'](lambda: [listener_2(), do_unsubscribe_all()]))
        unsubscribe_handles.append(store['subscribe'](lambda: listener_3()))

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_1.call_args_list), 1)
        self.assertEqual(len(listener_2.call_args_list), 1)
        self.assertEqual(len(listener_3.call_args_list), 1)

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_1.call_args_list), 1)
        self.assertEqual(len(listener_2.call_args_list), 1)
        self.assertEqual(len(listener_3.call_args_list), 1)

    def test_delays_subscribe_until_the_end_of_current_dispatch(self):
        store = create_store(reducers['todos'])

        listener_1 = mock.MagicMock()
        listener_2 = mock.MagicMock()
        listener_3 = mock.MagicMock()

        listener_3_added = [False]
        def maybe_add_third_listener():
            if not listener_3_added[0]:
                listener_3_added[0] = True
                store['subscribe'](lambda: listener_3())

        store['subscribe'](lambda: listener_1())
        store['subscribe'](lambda: [listener_2(), maybe_add_third_listener()])

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_1.call_args_list), 1)
        self.assertEqual(len(listener_2.call_args_list), 1)
        self.assertEqual(len(listener_3.call_args_list), 0)

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_1.call_args_list), 2)
        self.assertEqual(len(listener_2.call_args_list), 2)
        self.assertEqual(len(listener_3.call_args_list), 1)

    def test_uses_last_snapshot_of_subscribers_during_nested_dispatch(self):
        store = create_store(reducers['todos'])

        listener_1 = mock.MagicMock()
        listener_2 = mock.MagicMock()
        listener_3 = mock.MagicMock()
        listener_4 = mock.MagicMock()

        unsubscribe_4 = [None]
        unsubscribe_1 = [None]
        def callback_for_listener_1():
            listener_1()
            self.assertEqual(len(listener_1.call_args_list), 1)
            self.assertEqual(len(listener_2.call_args_list), 0)
            self.assertEqual(len(listener_3.call_args_list), 0)
            self.assertEqual(len(listener_4.call_args_list), 0)

            unsubscribe_1[0]()
            unsubscribe_4[0] = store['subscribe'](listener_4)
            store['dispatch'](unknown_action())

            self.assertEqual(len(listener_1.call_args_list), 1)
            self.assertEqual(len(listener_2.call_args_list), 1)
            self.assertEqual(len(listener_3.call_args_list), 1)
            self.assertEqual(len(listener_4.call_args_list), 1)

        unsubscribe_1[0] = store['subscribe'](callback_for_listener_1)
        store['subscribe'](listener_2)
        store['subscribe'](listener_3)

        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_1.call_args_list), 1)
        self.assertEqual(len(listener_2.call_args_list), 2)
        self.assertEqual(len(listener_3.call_args_list), 2)
        self.assertEqual(len(listener_4.call_args_list), 1)

        unsubscribe_4[0]()
        store['dispatch'](unknown_action())
        self.assertEqual(len(listener_1.call_args_list), 1)
        self.assertEqual(len(listener_2.call_args_list), 3)
        self.assertEqual(len(listener_3.call_args_list), 3)
        self.assertEqual(len(listener_4.call_args_list), 1)

    def test_provides_up_to_date_state_when_subscriber_is_notified(self):
        store = create_store(reducers['todos'])
        def callback():
            state = store['get_state']()
            self.assertEqual(state, [
                {
                    'id': 1,
                    'text': 'Hello'
                }
            ])
        store['dispatch'](add_todo('Hello'))

    def test_only_accepts_plain_objects(self):
        store = create_store(reducers['todos'])

        try:
            store['dispatch'](unknown_action())
        except Exception:
            self.fail('Should not have thrown exception')

        class AwesomeMap:
            def __init__(self):
                self.x = 1

        for non_object in [None, 42, 'hey', AwesomeMap()]:
            with self.assertRaises(Exception):
                store['dispatch'](non_object)

    def test_handles_nested_dispatches_gracefully(self):
        def foo(state, action={}):
            if state is None:
                state = 0
            if action.get('type') == 'foo':
                return 1
            return state

        def bar(state, action={}):
            if state is None:
                state = 0
            if action.get('type') == 'bar':
                return 2
            else:
                return state

        store = create_store(combine_reducers({ 'foo': foo, 'bar': bar }))
        def kinda_component_did_update():
            state = store['get_state']()
            if state.get('bar') == 0:
                store['dispatch']({ 'type': 'bar' })
        store['subscribe'](kinda_component_did_update)
        store['dispatch']({ 'type': 'foo' })

        self.assertEqual(store['get_state'](), {
            'foo': 1,
            'bar': 2
        })

    def test_does_not_allow_dispatch_from_within_reducer(self):
        store = create_store(reducers['dispatch_in_middle_of_reducer'])
        with self.assertRaises(Exception) as e:
            store['dispatch'](dispatch_in_middle(lambda: store['dispatch'](unknown_action())))
        self.assertTrue('may not dispatch' in str(e.exception))

    def test_throws_if_action_type_is_none(self):
        store = create_store(reducers['todos'])

        with self.assertRaises(Exception) as e:
            store['dispatch']({ 'type': None })
        self.assertTrue('Actions must have a non-None "type" property.' in str(e.exception))

    def test_does_not_throw_if_action_type_is_falsy(self):
        store = create_store(reducers['todos'])
        try:
            store['dispatch']({ 'type': False })
            store['dispatch']({ 'type': 0 })
            store['dispatch']({ 'type': '' })
        except Exception:
            self.fail('These should not have raised an exception')

    def test_accepts_enhancer_as_third_argument(self):
        empty_array = []
        def spy_enhancer(vanilla_create_store):
            def enhancer(*args):
                self.assertEqual(args[0], reducers['todos'])
                self.assertEqual(args[1], empty_array)
                self.assertEqual(len(args), 2)
                vanilla_store = vanilla_create_store(*args)
                vanilla_store['dispatch'] = mock.MagicMock(side_effect=vanilla_store['dispatch'])
                return vanilla_store
            return enhancer

        store = create_store(reducers['todos'], empty_array, spy_enhancer)
        action = add_todo('Hello')
        store['dispatch'](action)
        self.assertEqual(store['dispatch'].call_args_list, [mock.call(action)])
        self.assertEqual(store['get_state'](), [{
            'id': 1,
            'text': 'Hello'
        }])

    def test_throws_if_enhancer_is_neither_undefined_or_a_function(self):
        with self.assertRaises(Exception):
            create_store(reducers['todos'], None, {})
        with self.assertRaises(Exception):
            create_store(reducers['todos'], None, [])
        with self.assertRaises(Exception):
            create_store(reducers['todos'], None, False)
        try:
            create_store(reducers['todos'], None, None)
            create_store(reducers['todos'], None, lambda x: x)
            create_store(reducers['todos'], lambda x: x)
            create_store(reducers['todos'], [])
            create_store(reducers['todos'], {})
        except Exception:
            self.fail('Should not have thrown an exception')

    def test_throws_if_next_reducer_is_not_a_function(self):
        store = create_store(reducers['todos'])
        with self.assertRaises(Exception) as e:
            store['replace_reducer']('not a function')
        self.assertTrue('Expected next_reducer to be a function' in str(e.exception))

        try:
            store['replace_reducer'](lambda *x: x)
        except Exception:
            self.fail('Should not have raised an exception')

    def test_throws_if_listener_is_not_a_function(self):
        store = create_store(reducers['todos'])

        with self.assertRaises(Exception):
            store['subscribe']()
        with self.assertRaises(Exception):
            store['subscribe']('')
        with self.assertRaises(Exception):
            store['subscribe'](None)


if __name__ == '__main__':
    unittest.main()
