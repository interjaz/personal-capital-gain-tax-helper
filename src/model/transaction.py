from datetime import datetime
from decimal import Decimal
from typing import List

from config import DATE_FORMAT


class Asset(object):

    def __init__(self, symbol, type):
        self.symbol = symbol
        self.type = type

    def __eq__(self, other):
        return self.symbol == other.symbol and self.type == other.type

    def __hash__(self):
        return hash((self.symbol, self.type))

    def __repr__(self) -> str:
        return f"Asset(symbol={self.symbol},type={self.type})"


class Transaction(object):

    def __init__(self, date: datetime, type: str, asset: Asset,
                 volume: Decimal, taxable_price: Decimal, original_price: Decimal):
        self.date = date
        self.type = type
        self.asset = asset
        self.volume = volume
        self.taxable_price = taxable_price
        self.original_price = original_price

    def is_sell(self) -> bool:
        return self.type == "SELL"

    def is_buy(self) -> bool:
        return self.type == "BUY"

    def copy(self):
        return Transaction(
            self.date,
            self.type,
            self.asset,
            self.volume,
            self.taxable_price,
            self.original_price
        )

    @staticmethod
    def parse(row: List[str]) -> 'Transaction':
        def decimal(str_value):
            return Decimal(str_value.replace(",", ""))

        type = row[1]
        asset = Asset(row[2], row[3])

        if type != 'SELL' and type != 'BUY':
            raise ValueError(f"Transaction type can only by of SELL or BUY, got: {type}")

        return Transaction(datetime.strptime(row[0], DATE_FORMAT), type, asset,
                           decimal(row[4]), decimal(row[5]), decimal(row[6]))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash((self.date, self.type, self.asset, self.volume, self.taxable_price, self.original_price))

    def __repr__(self) -> str:
        return f"Transaction(" \
               f"date={self.date.strftime(DATE_FORMAT)}," \
               f"type={self.type}," \
               f"asset={self.asset}," \
               f"volume={self.volume}," \
               f"taxable_price={self.taxable_price}," \
               f"original_price={self.original_price}" \
               f")"
