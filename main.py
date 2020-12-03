from src.business.html_formatter import HtmlFormatter
from src.business.parser import parse
from src.business.processor import TransactionProcessor

processor = TransactionProcessor()
formatter = HtmlFormatter()

transactions = parse('transactions.tsv')
processed = processor.process(transactions)
html = formatter.render(processed)

with open('tax_return.html', 'w') as fp:
    fp.write(html)
