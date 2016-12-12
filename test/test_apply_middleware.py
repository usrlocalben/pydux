from __future__ import absolute_import

import unittest

import mock
from pydux import create_store, apply_middleware
from .helpers.reducers import reducers
from .helpers.action_creators import add_todo, add_todo_if_empty
from .helpers.middleware import thunk


class TestApplyMiddleware(unittest.TestCase):
    def test_wraps_dispatch_method_with_middleware_once(self):
        def test(spy_on_methods):
            def apply(methods):
                spy_on_methods(methods)
                return lambda next: lambda action: next(action)
            return apply

        spy = mock.MagicMock()
        store = apply_middleware(test(spy), thunk)(create_store)(reducers['todos'])

        store['dispatch'](add_todo('Use Redux'))
        store['dispatch'](add_todo('Flux FTW!'))

        self.assertEqual(spy.call_count, 1)
        args, kwargs = spy.call_args
        self.assertEqual(sorted(list(args[0].keys())),
                         sorted(['get_state', 'dispatch']))

        self.assertEqual(store['get_state'](),
                         [dict(id=1, text='Use Redux'), dict(id=2, text='Flux FTW!')])


if __name__ == '__main__':
    unittest.main()
