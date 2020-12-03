import csv

from src.model.transaction import Transaction


def parse(filename):
    transactions = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=" ", quotechar='"')
        is_header = True
        for row in reader:
            if is_header:
                is_header = False
                continue

            if len(row) == 0:
                continue

            transaction = Transaction.parse([x for x in row if x != ''])
            transactions.append(transaction)

    return transactions