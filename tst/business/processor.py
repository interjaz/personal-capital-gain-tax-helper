import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from src.business.processor import TransactionProcessor
from src.model.transaction import Asset, Transaction


class TestProcessor(unittest.TestCase):

    def setUp(self):
        self.date_mar_1 = datetime(2020, 1, 1)
        self.date_mar_2 = datetime(2020, 1, 2)
        self.date_mar_15 = datetime(2020, 3, 15)
        self.date_apr_1 = datetime(2020, 4, 1)
        self.date_apr_30 = datetime(2020, 4, 30)
        self.date_jul_1 = datetime(2020, 7, 1)

        asset = Asset('group', 'a', 'b')
        volume_buy_mar_1 = Decimal(100)
        volume_buy_mar_2 = Decimal(20)
        volume_buy_mar_15 = Decimal(30)
        volume_buy_apr_1 = Decimal(4000)
        volume_buy_apr_30 = Decimal(50)
        volume_buy_jul_1 = Decimal(60)
        volume_sell_mar_1 = Decimal(70)
        volume_sell_mar_2 = Decimal(800)
        volume_sell_mar_15 = Decimal(9000)
        volume_sell_apr_1 = Decimal(1000)
        volume_sell_apr_30 = Decimal(1100)
        volume_sell_jul_1 = Decimal(1200)
        price_buy_mar_1 = Decimal(1000)
        price_buy_mar_2 = Decimal(2000)
        price_buy_mar_15 = Decimal(3000)
        price_buy_apr_1 = Decimal(4000)
        price_buy_apr_30 = Decimal(5000)
        price_buy_jul_1 = Decimal(6000)
        price_sell_mar_1 = Decimal(7000)
        price_sell_mar_2 = Decimal(8000)
        price_sell_mar_15 = Decimal(9000)
        price_sell_apr_1 = Decimal(10000)
        price_sell_apr_30 = Decimal(11000)
        price_sell_jul_1 = Decimal(11000)
        aux_price = Decimal(777)

        self.buy_mar_1 = Transaction(self.date_mar_1, 'BUY', asset, volume_buy_mar_1, price_buy_mar_1, aux_price)
        self.buy_mar_2 = Transaction(self.date_mar_2, 'BUY', asset, volume_buy_mar_2, price_buy_mar_2, aux_price)
        self.buy_mar_15 = Transaction(self.date_mar_15, 'BUY', asset, volume_buy_mar_15, price_buy_mar_15, aux_price)
        self.buy_apr_1 = Transaction(self.date_apr_1, 'BUY', asset, volume_buy_apr_1, price_buy_apr_1, aux_price)
        self.buy_apr_30 = Transaction(self.date_apr_30, 'BUY', asset, volume_buy_apr_30, price_buy_apr_30, aux_price)
        self.buy_jul_1 = Transaction(self.date_jul_1, 'BUY', asset, volume_buy_jul_1, price_buy_jul_1, aux_price)

        sell_time_delta = timedelta(hours=1)
        self.sell_mar_1 = Transaction(self.date_mar_1 + sell_time_delta, 'SELL', asset, volume_sell_mar_1,
                                      price_sell_mar_1, aux_price)
        self.sell_mar_2 = Transaction(self.date_mar_2 + sell_time_delta, 'SELL', asset, volume_sell_mar_2,
                                      price_sell_mar_2, aux_price)
        self.sell_mar_15 = Transaction(self.date_mar_15 + sell_time_delta, 'SELL', asset, volume_sell_mar_15,
                                       price_sell_mar_15,
                                       aux_price)
        self.sell_apr_1 = Transaction(self.date_apr_1 + sell_time_delta, 'SELL', asset, volume_sell_apr_1,
                                      price_sell_apr_1, aux_price)
        self.sell_apr_30 = Transaction(self.date_apr_30 + sell_time_delta, 'SELL', asset, volume_sell_apr_30,
                                       price_sell_apr_30,
                                       aux_price)
        self.sell_jul_1 = Transaction(self.date_jul_1 + sell_time_delta, 'SELL', asset, volume_sell_jul_1,
                                      price_sell_jul_1, aux_price)

        self.processor = TransactionProcessor()
        self.process_same_day = self.processor._TransactionProcessor__process_same_day
        self.process_30_days = self.processor._TransactionProcessor__process_30_days

    def test___process_same_day_when_empty(self):
        self.assertEqual(self.process_same_day([]), [])

    def test___process_same_day_when_no_overlap(self):
        buy1 = self.buy_mar_1
        buy2 = self.buy_mar_2
        sell1 = self.sell_mar_1
        sell2 = self.sell_mar_2

        self.assertEqual(
            [buy1, sell2],
            self.process_same_day(
                [buy1, sell2]
            )
        )

        self.assertEqual(
            [sell1, buy2],
            self.process_same_day(
                [sell1, buy2]
            )
        )

    def test___process_same_day_when_no_merge(self):
        buy1 = self.buy_mar_1
        buy2 = self.buy_mar_2
        sell1 = self.sell_mar_1
        sell2 = self.sell_mar_2

        self.assertEqual(
            [buy1, buy2],
            self.process_same_day(
                [buy1, buy2]
            )
        )

        self.assertEqual(
            [sell1, sell2],
            self.process_same_day(
                [sell1, sell2]
            )
        )

    def test___process_same_day_when_partial_overlap(self):
        buy1 = self.buy_mar_1
        buy2 = self.buy_mar_2
        sell1 = self.sell_mar_1
        sell2 = self.sell_mar_2

        buy1_sell1_diff = Transaction(buy1.date, 'BUY', buy1.asset, buy1.volume - sell1.volume, buy1.taxable_price,
                                      buy1.original_price)
        buy2_sell2_diff = Transaction(sell2.date, 'SELL', buy2.asset, sell2.volume - buy2.volume, sell2.taxable_price,
                                      sell2.original_price)

        self.assertEqual(
            [buy1, buy2_sell2_diff],
            self.process_same_day(
                [buy1, sell2, buy2]
            )
        )

        self.assertEqual(
            [buy1_sell1_diff, buy2],
            self.process_same_day(
                [buy1, sell1, buy2]
            )
        )

    def test___process_same_day_when_full_overlap(self):
        buy1 = self.buy_mar_1
        buy2 = self.buy_mar_2
        sell1 = self.sell_mar_1
        sell2 = self.sell_mar_2

        buy1_sell1_diff = Transaction(buy1.date, 'BUY', buy1.asset, buy1.volume - sell1.volume, buy1.taxable_price,
                                      buy1.original_price)
        buy2_sell2_diff = Transaction(sell2.date, 'SELL', buy2.asset, sell2.volume - buy2.volume, sell2.taxable_price,
                                      sell2.original_price)

        self.assertEqual(
            [buy1_sell1_diff, buy2_sell2_diff],
            self.process_same_day(
                [buy1, sell2, buy2, sell1]
            )
        )

        self.assertEqual(
            [buy1_sell1_diff, buy2_sell2_diff],
            self.process_same_day(
                [sell2, sell1, buy1, buy2]
            )
        )

    def test___process_30_days_when_empty(self):
        self.assertEqual(self.process_30_days([]), [])

    def test___process_30_days_when_no_overlap(self):
        self.assertEqual(
            [self.buy_mar_1, self.sell_jul_1],
            self.process_30_days(
                [self.buy_mar_1, self.sell_jul_1]
            )
        )

        self.assertEqual(
            [self.buy_mar_1, self.sell_jul_1],
            self.process_30_days(
                [self.sell_jul_1, self.buy_mar_1]
            )
        )

    def test___process_30_days_when_no_merge(self):
        self.assertEqual(
            [self.buy_mar_1, self.buy_mar_2],
            self.process_30_days(
                [self.buy_mar_1, self.buy_mar_2]
            )
        )

        self.assertEqual(
            [self.sell_mar_1, self.sell_mar_2],
            self.process_30_days(
                [self.sell_mar_1, self.sell_mar_2]
            )
        )

    def test___process_30_days_when_partial_overlap(self):
        buy_apr_1_sell_apr_30_diff = Transaction(self.buy_apr_1.date, 'BUY', self.buy_apr_1.asset,
                                                 self.buy_apr_1.volume - self.sell_apr_30.volume,
                                                 self.buy_apr_1.taxable_price, self.buy_apr_1.original_price)
        self.assertEqual(
            [buy_apr_1_sell_apr_30_diff, self.sell_jul_1],
            self.process_30_days(
                [self.buy_apr_1, self.sell_apr_30, self.sell_jul_1]
            )
        )

        sell_mar_15_buy_apr_1_diff = Transaction(self.sell_mar_15.date, 'SELL', self.sell_mar_15.asset,
                                                 self.sell_mar_15.volume - self.buy_apr_1.volume,
                                                 self.sell_mar_15.taxable_price, self.sell_mar_15.original_price)
        self.assertEqual(
            [sell_mar_15_buy_apr_1_diff, self.buy_jul_1],
            self.process_30_days(
                [self.buy_apr_1, self.sell_mar_15, self.buy_jul_1]
            )
        )

    def test___process_30_days_when_full_overlap(self):
        buy_mar_15_sell_apr_1_buy_apr_30 = Transaction(self.sell_apr_1.date, 'SELL', self.sell_mar_15.asset,
                                                       self.sell_apr_1.volume - self.buy_mar_15.volume - self.buy_apr_30.volume,
                                                       self.sell_apr_1.taxable_price, self.sell_mar_15.original_price)
        self.assertEqual(
            [buy_mar_15_sell_apr_1_buy_apr_30],
            self.process_30_days(
                [self.buy_mar_15, self.sell_apr_1, self.buy_apr_30]
            )
        )
