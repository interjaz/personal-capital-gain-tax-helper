from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from config import DATE_FORMAT, DATE_TIME_FORMAT


class Asset(object):

    def __init__(self, group, symbol, type):
        self.group = group
        self.symbol = symbol
        self.type = type

    def __eq__(self, other):
        return self.group == other.group and self.symbol == other.symbol and self.type == other.type

    def __hash__(self):
        return hash((self.group, self.symbol, self.type))

    def __repr__(self) -> str:
        return f"Asset(group={self.group},symbol={self.symbol},type={self.type})"


class Transaction(object):

    def __init__(self, date: datetime, type: str, asset: Asset,
                 volume: Decimal, taxable_price: Decimal, original_price: Optional[Decimal]):
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
        asset = Asset(row[2], row[3], row[4])

        if type != 'SELL' and type != 'BUY':
            raise ValueError(f"Transaction type can only by of SELL or BUY, got: {type}")

        return Transaction(datetime.strptime(row[0], DATE_TIME_FORMAT), type, asset,
                           decimal(row[5]), decimal(row[6]), decimal(row[7]))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash((self.date, self.type, self.asset, self.volume, self.taxable_price, self.original_price))

    def __repr__(self) -> str:
        return f"Transaction(" \
               f"date={self.date.strftime(DATE_TIME_FORMAT)}," \
               f"type={self.type}," \
               f"asset={self.asset}," \
               f"volume={self.volume}," \
               f"taxable_price={self.taxable_price}," \
               f"original_price={self.original_price}" \
               f")"
