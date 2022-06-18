import unittest
from datetime import date

from config import TAX_PERIOD

class TestTaxPeriod(unittest.TestCase):

    def test_tax_year(self):
        tax_period = TAX_PERIOD

        self.assertEqual(tax_period.tax_year(date(2021, 1, 1)), "2020/2021")
        self.assertEqual(tax_period.tax_year(date(2021, 4, 5)), "2020/2021")
        self.assertEqual(tax_period.tax_year(date(2021, 4, 6)), "2021/2022")
        self.assertEqual(tax_period.tax_year(date(2021, 12, 30)), "2021/2022")

