import uuid
from datetime import datetime
from decimal import Decimal


# Section 104 hold pool
# Immutable object
from typing import Tuple, List

from config import TAX_PERIOD
from src.model.tax import TaxableRecord
from src.model.transaction import Transaction, Asset


class HoldPool(object):

    def __init__(self, date: datetime, asset: Asset, volume: Decimal, cost: Decimal):
        self.pool_id = uuid.uuid4()
        self.pool_index = 0
        self.date = date
        self.asset = asset
        self.volume = volume
        self.cost = cost

    def deposit(self, transaction: Transaction) -> 'HoldPool':
        if transaction.date < self.date:
            raise ValueError("Deposit is only allowed for transaction that happened after or at the pool date")

        if transaction.asset != self.asset:
            raise ValueError("Deposit is only allowed for the same asset")

        if transaction.type != 'BUY':
            raise ValueError("Only BUY transactions can be deposited")

        new_volume = self.volume + transaction.volume
        new_cost = self.cost + transaction.volume * transaction.taxable_price

        new_pool = HoldPool(
            transaction.date,
            transaction.asset,
            new_volume,
            new_cost
        )

        new_pool.pool_id = self.pool_id
        new_pool.pool_index = self.pool_index + 1

        return new_pool

    def dispose(self, transaction: Transaction) -> Tuple['HoldPool', TaxableRecord]:
        if transaction.date < self.date:
            raise ValueError("Disposal is only allowed for transaction that happened after or at the pool date")

        if transaction.asset != self.asset:
            raise ValueError("Disposal is only allowed for the same asset")

        if transaction.type != 'SELL':
            raise ValueError("Only SELL transactions can be disposed")

        hold_cost_per_unit = self.cost / self.volume
        new_volume = self.volume - transaction.volume
        new_cost = hold_cost_per_unit * new_volume

        new_pool = HoldPool(
            transaction.date,
            transaction.asset,
            new_volume,
            new_cost
        )
        new_pool.pool_id = self.pool_id
        new_pool.pool_index = self.pool_index + 1

        transaction_cost_per_unit = transaction.taxable_price
        amount = (transaction_cost_per_unit - hold_cost_per_unit) * transaction.volume
        new_record = TaxableRecord(
            transaction.date,
            TAX_PERIOD.tax_year(transaction.date),
            "GAIN" if amount > 0 else "LOSS",
            abs(amount)
        )

        return new_pool, new_record

    def estimate(self, new_cost) -> TaxableRecord:
        pool, estimated_record = self.dispose(
            Transaction(datetime.utcnow().astimezone(), 'SELL', self.asset, self.volume, new_cost, None)
        )

        return estimated_record

    def __eq__(self, other):
        return self.date == other.date and self.asset == other.asset and \
            self.volume == other.volume and self.cost == other.cost

    def __hash__(self):
        return hash((self.date, self.asset, self.volume, self.cost))

    def __repr__(self) -> str:
        return f"HoldPool(date={self.date},asset={self.asset},volume={self.volume},cost={self.cost})"


class TaxableHoldPool(object):

    def __init__(self, asset: Asset, hold_pools: List[HoldPool], taxable_records: List[TaxableRecord]):
        self.asset = asset
        self.hold_pools = hold_pools
        self.taxable_records = taxable_records

    def latest_hold_pool(self):
        return self.hold_pools[-1]
