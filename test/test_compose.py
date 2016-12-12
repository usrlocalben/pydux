import unittest

from pydux.compose import compose


class TestComposeMethod(unittest.TestCase):

    def test_composes_from_right_to_left(self):
        double = lambda x: x * 2
        square = lambda x: x * x
        self.assertEqual(compose(square)(5), 25)
        self.assertEqual(compose(square, double)(5), 100)
        self.assertEqual(compose(double, square, double)(5), 200)

    def test_composes_functions_from_right_to_left(self):
        a = lambda next: lambda x: next(x + 'a')
        b = lambda next: lambda x: next(x + 'b')
        c = lambda next: lambda x: next(x + 'c')
        final = lambda x: x

        self.assertEqual(compose(a, b, c)(final)(''), 'abc')
        self.assertEqual(compose(b, c, a)(final)(''), 'bca')
        self.assertEqual(compose(c, a, b)(final)(''), 'cab')

    def test_can_be_seeded_with_multiple_arguments(self):
        square = lambda x: x * x
        add = lambda x, y: x + y

        self.assertEqual(compose(square, add)(1, 2), 9)

    def test_returns_first_given_argument_if_no_given_functions(self):
        self.assertEqual(compose()(1,2), 1)
        self.assertEqual(compose()(3), 3)
        self.assertEqual(compose()(), None)

    def test_returns_first_function_if_only_one(self):
        func = lambda: {}
        self.assertEqual(compose(func), func)


if __name__ == '__main__':
    unittest.main()
