import unittest

from src.model.transaction import Asset


class TestAsset(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(Asset('a', 'b'), Asset('a', 'b'))
        self.assertNotEqual(Asset('a', 'b'), Asset('b', 'a'))

    def test_hash(self):
        self.assertEqual(Asset('a', 'b').__hash__(), Asset('a', 'b').__hash__())
        self.assertNotEqual(Asset('a', 'b').__hash__(), Asset('b', 'a').__hash__())
