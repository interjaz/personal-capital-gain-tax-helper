from datetime import datetime
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from typing import List


class Quantization(object):

    def __init__(self, precision: Decimal, rounding: str):
        self.precision = precision
        self.rounding = rounding


# https://www.gov.uk/hmrc-internal-manuals/self-assessment-manual/sam121370
# Precision should be in full pounds not pennies
# Income: ROUND_DOWN
# Tax: ROUND_UP
PRECISION = Decimal('1.')
INCOME_QUANTIZATION = Quantization(PRECISION, ROUND_DOWN)
TAX_QUANTIZATION = Quantization(PRECISION, ROUND_UP)


class TaxRate(object):

    def __init__(self, rate, allowance):
        self.rate = Decimal(rate)
        self.allowance = Decimal(allowance.replace(",", ""))

    def calculate_tax_to_pay(self, total_capital_gain):
        taxable_capital_gain = total_capital_gain - self.allowance
        if taxable_capital_gain <= 0:
            return 0

        return (taxable_capital_gain * self.rate).quantize(TAX_QUANTIZATION.precision,
                                                           rounding=TAX_QUANTIZATION.rounding)

    def __repr__(self):
        return f"TaxRate(rate={self.rate}, allowance={self.allowance}"


class TaxPeriod(object):

    def __init__(self, country, month_start_at, day_start_at, month_end_at, day_end_at):
        self.country = country
        self.month_start_at = month_start_at
        self.day_start_at = day_start_at
        self.month_end_at = month_end_at
        self.day_end_at = day_end_at

    def tax_year(self, date):
        if date.month > self.month_start_at or (date.month == self.month_start_at and date.day > self.day_start_at):
            tax_year = f"{date.year + 1}/{date.year + 2}"
        else:
            tax_year = f"{date.year}/{date.year + 1}"

        return tax_year

    def __repr__(self):
        return f"TaxPeriod(country={self.country}," \
               f"mm-dd/mm-dd={self.month_start_at}/{self.day_start_at}-{self.month_end_at}/{self.day_end_at}," \
               f")"


class TaxableRecord(object):

    def __init__(self, date, tax_year: str, type: str, amount: Decimal):
        if type != 'GAIN' and type != 'LOSS':
            raise ValueError('Type can only be GAIN or LOSS')

        self.date = date
        self.tax_year = tax_year
        self.type = type
        self.amount = amount

    @staticmethod
    def as_taxable_income(tax_year: str, taxable_records: List['TaxableRecord']) -> 'TaxableRecord':
        total = sum([x.amount if x.type == 'GAIN' else - x.amount for x in taxable_records])
        amount = total.quantize(INCOME_QUANTIZATION.precision, rounding=INCOME_QUANTIZATION.rounding)
        return TaxableRecord(None, tax_year, 'GAIN' if amount >= 0 else 'LOSS', abs(amount))

    def is_gain(self):
        return self.type == 'GAIN'

    def __eq__(self, other):
        return self.date == other.date and self.tax_year == other.tax_year and \
               self.type == other.type and self.amount == other.amount

    def __hash__(self):
        return hash((self.date, self.tax_year, self.type, self.amount))

    def __repr__(self) -> str:
        return f"TaxRecord(date={self.date},tax_year={self.tax_year},type={self.type},amount={self.amount})"
