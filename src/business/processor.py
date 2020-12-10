from datetime import timedelta
from typing import List, Tuple, Dict

from src.model.hold_pool import HoldPool, TaxableHoldPool
from src.model.tax import TaxableRecord
from src.model.transaction import Transaction, Asset


class TransactionProcessor(object):

    def __merge(self, transactions: List[Transaction]) -> List[Transaction]:

        if len(transactions) <= 1:
            return transactions

        buys = [x.copy() for x in transactions if x.is_buy()]
        sells = [x.copy() for x in transactions if x.is_sell()]

        for buy in buys:
            for sell in sells:
                if sell.volume <= 0:
                    continue

                if buy.volume <= 0:
                    break

                if sell.volume <= buy.volume:
                    buy.volume -= sell.volume
                    sell.volume -= sell.volume
                else:
                    sell.volume -= buy.volume
                    buy.volume = 0

        non_zero_buys = [x for x in buys if x.volume > 0]
        non_zero_sells = [x for x in sells if x.volume > 0]
        merged = []
        merged.extend(non_zero_buys)
        merged.extend(non_zero_sells)

        return merged

    def __process_x_days(self, transactions: List[Transaction], days: int) -> List[Transaction]:

        if len(transactions) <= 0:
            return transactions

        day_delta = timedelta(days=days)

        transactions = [x.copy() for x in transactions]

        disposals = [x for x in transactions if x.is_sell()]
        for disposal in disposals:
            start_at = (disposal.date - day_delta).date()
            end_at = (disposal.date + day_delta).date()

            to_merge = set()
            to_merge.add(disposal)

            for idx in range(len(transactions)):
                transaction = transactions[idx]

                if start_at <= transaction.date.date() <= end_at:
                    to_merge.add(transaction)

            transactions = [x for x in transactions if x not in to_merge]

            merged = self.__merge(list(to_merge))
            transactions.extend(merged)

        transactions = sorted(transactions, key=lambda x: x.date)
        return transactions

    def __process_same_day(self, transactions: List[Transaction]) -> List[Transaction]:
        return self.__process_x_days(transactions, 0)

    def __process_30_days(self, transactions: List[Transaction]) -> List[Transaction]:
        return self.__process_x_days(transactions, 30)

    def __process_normal(self, transactions: List[Transaction]) \
            -> Tuple[List[HoldPool], List[TaxableRecord]]:

        hold_pools = list()
        records = list()

        if len(transactions) <= 0:
            return hold_pools, records

        first = transactions[0]
        hold_pool = HoldPool(first.date, first.asset, first.volume, first.taxable_price * first.volume)
        hold_pools.append(hold_pool)

        for idx in range(1, len(transactions)):
            transaction = transactions[idx]

            if transaction.is_sell():
                hold_pool, record = hold_pool.dispose(transaction)
                hold_pools.append(hold_pool)
                records.append(record)
            elif transaction.is_buy():
                hold_pool = hold_pool.deposit(transaction)
                hold_pools.append(hold_pool)
            else:
                raise ValueError('Unsupported transaction type')

        return hold_pools, records

    def __process_single_asset_type(self, transactions: List[Transaction]) \
            -> Tuple[List[HoldPool], List[TaxableRecord]]:

        if len(transactions) <= 0:
            return list(), list()

        transactions_ascending = sorted(transactions, key=lambda x: x.date)

        transactions_without_same_day = self.__process_same_day(transactions_ascending)
        transactions_without_30_days = self.__process_30_days(transactions_without_same_day)
        hold_pools, records = self.__process_normal(transactions_without_30_days)

        return hold_pools, records

    def process(self, transactions: List[Transaction]) -> List[TaxableHoldPool]:

        asset_to_transactions: Dict[Asset, List[Transaction]] = dict()
        for transaction in transactions:
            key = transaction.asset

            if key not in asset_to_transactions:
                asset_to_transactions[key] = [transaction]
            else:
                asset_to_transactions[key].append(transaction)

        taxable_hold_pools: List[TaxableHoldPool] = list()
        for key, value in asset_to_transactions.items():
            hold_pools, taxable_records = self.__process_single_asset_type(value)
            taxable_hold_pools.append(
                TaxableHoldPool(
                    key, hold_pools, taxable_records
                )
            )

        return taxable_hold_pools
