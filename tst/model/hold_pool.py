import unittest
from datetime import datetime
from decimal import Decimal

from src.model.hold_pool import HoldPool
from src.model.tax import TaxableRecord
from src.model.transaction import Asset, Transaction


class TestHoldPool(unittest.TestCase):

    def test_deposit(self):
        asset1 = Asset('a', 'b')
        asset2 = Asset('b', 'a')
        date1 = datetime(2020, 1, 2)
        date2 = datetime(2020, 1, 3)
        date3 = datetime(2020, 1, 4)
        pool1 = HoldPool(date2, asset1, Decimal("0"), Decimal("1"))

        # date
        with self.assertRaises(ValueError):
            pool1.deposit(Transaction(date1, "BUY", asset1, Decimal("2"), Decimal("3"), Decimal("4")))

        # transaction type
        with self.assertRaises(ValueError):
            pool1.deposit(Transaction(date2, "SELL", asset1, Decimal("2"), Decimal("3"), Decimal("4")))

        # different asset
        with self.assertRaises(ValueError):
            pool1.deposit(Transaction(date2, "BUY", asset2, Decimal("2"), Decimal("3"), Decimal("4")))

        pool2 = pool1.deposit(Transaction(date2, "BUY", asset1, Decimal("2"), Decimal("3"), Decimal("4")))
        pool3 = pool2.deposit(Transaction(date3, "BUY", asset1, Decimal("5"), Decimal("6"), Decimal("7")))

        self.assertEqual(pool2, HoldPool(date2, asset1, Decimal("2"), Decimal("7")))
        self.assertEqual(pool3, HoldPool(date3, asset1, Decimal("7"), Decimal("37")))

    def test_dispose(self):
        asset1 = Asset('a', 'b')
        asset2 = Asset('b', 'a')
        date1 = datetime(2020, 1, 2)
        date2 = datetime(2020, 1, 3)
        date3 = datetime(2020, 1, 4)

        # 10 shares, 2.00 each
        pool1 = HoldPool(date2, asset1, Decimal("10"), Decimal("20"))

        # date
        with self.assertRaises(ValueError):
            pool1.dispose(Transaction(date1, "SELL", asset1, Decimal("2"), Decimal("3"), Decimal("4")))

        # transaction type
        with self.assertRaises(ValueError):
            pool1.dispose(Transaction(date2, "BUY", asset1, Decimal("2"), Decimal("3"), Decimal("4")))

        # different asset
        with self.assertRaises(ValueError):
            pool1.dispose(Transaction(date2, "SELL", asset2, Decimal("2"), Decimal("3"), Decimal("4")))

        # 5 shares, 0.50 each
        pool2, record2 = pool1.dispose(Transaction(date2, "SELL", asset1, Decimal("5"), Decimal("0.5"), Decimal("4")))

        # 2 shares, 3.00 each
        pool3, record3 = pool2.dispose(Transaction(date3, "SELL", asset1, Decimal("2"), Decimal("3.0"), Decimal("7")))

        self.assertEqual(pool2, HoldPool(date2, asset1, Decimal("5"), Decimal("10")))
        self.assertEqual(pool3, HoldPool(date3, asset1, Decimal("3"), Decimal("6")))

        self.assertEqual(record2, TaxableRecord(date2, "2020/2021", "LOSS", Decimal(abs((0.50 - 2.00) * 5))))
        self.assertEqual(record3, TaxableRecord(date3, "2020/2021", "GAIN", Decimal(abs((3.00 - 2.00) * 2))))
