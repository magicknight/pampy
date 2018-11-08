import unittest

import functools
from functools import reduce

from pampy import match, REST, TAIL, HEAD, _, match_value, match_iterable


class PampyElaborateTests(unittest.TestCase):

    def test_fibonacci(self):
        def fib(n):
            return match(n,
                1, 1,
                2, 1,
                _, lambda x: fib(x - 1) + fib(x - 2))

        self.assertEqual(fib(1), 1)
        self.assertEqual(fib(7), 13)

    def test_parser(self):
        def parser(exp):
            return match(exp,
                3,              "the integer 3",
                float,          "any float number",
                int,            "any integer",
                "ciao",         "the string ciao",
                dict,           "any dictionary",
                str,            "any string",
                (int, int),     "a tuple made of two ints",
                [1],            "the list [1]",
                [1, 2, 3],      "the list [1, 2, 3]",
                [1, _, 3],      "the list [1, _, 3]",
                (str, str),     lambda a, b: "%s %s" % (a, b),
                [1, 2, _],      lambda x: "the list [1, 2, _]",
                [1, 2, 4],      "the list [1, 2, 4]",   # this can never be matched

                [1, [2, _], _], lambda a, b: "[1, [2, %s], %s]" % (a, b),
            )

        assert parser(3) == "the integer 3"
        assert parser(5) == "any integer"
        assert parser("ciao") == "the string ciao"
        assert parser("x") == "any string"
        assert parser({'a': 1}) == "any dictionary"
        assert parser([1]) == "the list [1]"
        assert parser([1, 2, 3]) == "the list [1, 2, 3]"
        assert parser([1, 2, 4]) == "the list [1, 2, _]"
        assert parser([1, 3, 3]) == "the list [1, _, 3]"
        assert parser(("hello", "world")) == "hello world"
        assert parser([1, [2, 3],    4]) == "[1, [2, 3], 4]"

    def test_lisp(self):
        # A Lisp interpreter in 5 lines
        def lisp(exp):
            return match(exp,
                int,                lambda x: x,
                callable,           lambda x: x,
                (callable, REST),   lambda f, rest: f(*map(lisp, rest)),
                tuple,              lambda t: list(map(lisp, t)),
            )

        plus = lambda a, b: a + b
        minus = lambda a, b: a - b
        self.assertEqual(lisp((plus, 1, 2)), 3)
        self.assertEqual(lisp((plus, 1, (minus, 4, 2))), 3)
        self.assertEqual(lisp((reduce, plus, (1, 2, 3))), 6)

    def test_myzip(self):
        def myzip(a, b):
            return match((a, b),
                ([], []),                   [],
                ([_, TAIL], [_, TAIL]),     lambda ha, ta, hb, tb: [(ha, hb)]+myzip(ta, tb)
            )

        self.assertEqual(myzip([1,2,3], [4, 5, 6]), [(1, 4), (2, 5), (3, 6)])
        self.assertEqual(myzip(range(5), range(5)), list(zip(range(5), range(5))))


    # def test_animals(self):
    #     pets = [
    #         { 'type': 'dog', 'pet-details': { 'name': 'carl',   'cuteness': 4   } },
    #         { 'type': 'dog', 'pet-details': { 'name': 'john',   'cuteness': 3   } },
    #         { 'type': 'cat', 'pet-details': { 'name': 'fuffy',  'cuty':     4.6 } },
    #         { 'type': 'cat', 'cat-details': { 'name': 'bonney', 'cuty':     7   } },
    #     ]
    #
    #     def avg_cuteness_pythonic():
    #         cutenesses = []
    #         for pet in pets:
    #             if 'pog-details' in pet:
    #                 if 'cuteness' in pet['pog-detail']:
    #                     cutenesses.append(pet['pog-detail']['cuteness'])
    #                 elif 'cuty' in pet['pet-details']:
    #                     cutenesses.append(pet[''])
    #             elif 'cat-detail' in pet:
    #                 if 'cuty' in pet['cat-details']:
    #                     cutenesses.append(pet[''])
    #         return sum(cutenesses) / len(cutenesses)
    #
    #     def avg_cuteness_pampy():
    #         cutenesses = []
    #         for pet in pets:
    #             match(pet,
    #                 { "pet-details": { "cuteness": _ }},  lambda x: cutenesses.append(x),
    #                 { "cat-details": { "cuty":     _ }},  lambda x: cutenesses.append(x)
    #             )
    #         return sum(cutenesses) / len(cutenesses)

