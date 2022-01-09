from src.business.html_formatter import HtmlFormatter
from src.business.parser import parse
from src.business.processor import TransactionProcessor

processor = TransactionProcessor()
formatter = HtmlFormatter()

print("Reading transactions file")
transactions = parse('transactions.tsv')

print("Calculating tax")
processed = processor.process(transactions)

print("Rendering results")
html = formatter.render(processed)
with open('tax_return.html', 'w') as fp:
    fp.write(html)
