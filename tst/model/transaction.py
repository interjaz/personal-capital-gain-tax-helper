import unittest

from src.model.transaction import Asset


class TestAsset(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(Asset('a', 'b', 'c'), Asset('a', 'b', 'c'))
        self.assertNotEqual(Asset('a', 'b', 'c'), Asset('b', 'a', 'c'))
        self.assertNotEqual(Asset('a', 'b', 'c'), Asset('b', 'b', 'c'))
        self.assertNotEqual(Asset('a', 'b', 'c'), Asset('a', 'a', 'c'))

    def test_hash(self):
        self.assertEqual(Asset('a', 'b', 'c').__hash__(), Asset('a', 'b', 'c').__hash__())
        self.assertNotEqual(Asset('a', 'b', 'c').__hash__(), Asset('b', 'a', 'c').__hash__())
        self.assertNotEqual(Asset('a', 'b', 'c').__hash__(), Asset('b', 'b', 'c').__hash__())
        self.assertNotEqual(Asset('a', 'b', 'c').__hash__(), Asset('a', 'a', 'c').__hash__())
