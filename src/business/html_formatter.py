from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List

import api_keys
from config import TAX_RATES
from src.business.stock_fetcher import StockFetcher
from src.model.hold_pool import TaxableHoldPool
from src.model.tax import TaxableRecord

DISPLAY_PRECISION = Decimal('.01')
DISPLAY_ROUND = ROUND_HALF_UP
DISPLAY_DATE_FORMAT = '%Y-%m-%d'

class HtmlFormatter(object):

    def __init__(self):
        self.stock_fetcher = StockFetcher(api_keys.ALPHA_VANTAGE_KEY)

    def wrap_html(self, body) -> str:
        return \
"""
<html>
    <head>
        <title>Tax summary</title>
        <style type="text/css">
            body {
                font-family: Calibri;
            }
            h2, h3 {
                margin-bottom: 2px;
            }
            th {
                text-align: left; 
            }
            th, td {
                padding-right: 10px;
            }
            .right { 
                text-align: right; 
            }
        </style>
    </head>
    <body>""" + \
"".join(["\n\t\t" + x for x in body.split("\n")]) + \
"""
    </body>
</html>
"""

    def render_footer(self):
        return f"<div style=\"margin-top: 50px\"><small><i>Page generated at: {datetime.now()}. All values in GBP.</i></small></div>"

    def render_taxable_records(self, taxable_records: List[TaxableRecord]) -> str:
        buffer = list()
        buffer.append("<h3>Tax records</h3>")

        buffer.append("<table>")
        buffer.append("<tr>")
        buffer.append("<th>Tax Year</th>")
        buffer.append("<th>Date</th>")
        buffer.append("<th>Type</th>")
        buffer.append("<th>Amount</th>")
        buffer.append("</tr>")

        for taxable_record in taxable_records:
            buffer.append("<tr>")
            buffer.append(f"<td>{taxable_record.tax_year}")
            buffer.append(f"<td>{taxable_record.date.strftime(DISPLAY_DATE_FORMAT)}")
            buffer.append(f"<td>{taxable_record.type}")
            buffer.append(f"<td class=\"right\">{taxable_record.amount.quantize(DISPLAY_PRECISION, rounding=DISPLAY_ROUND)}")
            buffer.append("</tr>")

        buffer.append("</table>")

        return "\n".join(buffer)

    def render_taxable_total(self, taxable_hold_pools: List[TaxableHoldPool]) -> str:
        buffer = list()
        buffer.append("<div>")

        taxable_years = set()
        for taxable_hold_pool in taxable_hold_pools:
            for taxable_record in taxable_hold_pool.taxable_records:
                taxable_years.add(taxable_record.tax_year)

        taxable_years = sorted(list(taxable_years))

        for taxable_year in taxable_years:
            buffer.append("<div>")
            buffer.append(f"<h2>Tax for year: {taxable_year}</h2>")

            buffer.append("<table>")
            buffer.append("<tr>")
            buffer.append("<th>Asset</th>")
            buffer.append("<th>Type</th>")
            buffer.append("<th>Amount</th>")
            buffer.append("</tr>")

            records = list()
            for taxable_hold_pool in taxable_hold_pools:

                for taxable_record in taxable_hold_pool.taxable_records:
                    if taxable_record.tax_year != taxable_year:
                        continue

                    buffer.append("<tr>")
                    buffer.append(f"<td>{taxable_hold_pool.asset.symbol}</td>")
                    buffer.append(f"<td>{taxable_record.type}")
                    buffer.append(f"<td class=\"right\">{taxable_record.amount.quantize(DISPLAY_PRECISION, rounding=DISPLAY_ROUND)}")
                    buffer.append("</tr>")
                    records.append(taxable_record)

            buffer.append("<tr><td>&nbsp;</td></tr>")

            total_capital_gain = TaxableRecord.as_taxable_income(taxable_year, records)
            buffer.append("<tr>")
            buffer.append(f"<td>Total</td>")
            buffer.append(f"<td>{total_capital_gain.type}")
            buffer.append(f"<td class=\"right\">{total_capital_gain.amount}")
            buffer.append("</tr>")
            buffer.append("<tr>")

            tax_to_pay = 0
            tax_rate = TAX_RATES[taxable_year]
            if total_capital_gain.is_gain():
                tax_to_pay = TAX_RATES[taxable_year].calculate_tax_to_pay(total_capital_gain.amount)

            buffer.append(f"<td>Tax allowance</td>")
            buffer.append(f"<td>")
            buffer.append(f"<td class=\"right\">{tax_rate.allowance}")
            buffer.append("</tr>")

            buffer.append(f"<td>Tax rate</td>")
            buffer.append(f"<td>")
            buffer.append(f"<td class=\"right\">{tax_rate.rate}")
            buffer.append("</tr>")

            buffer.append(f"<td><b>Capital gain tax to pay</b></td>")
            buffer.append(f"<td>")
            buffer.append(f"<td class=\"right\">{tax_to_pay}")
            buffer.append("</tr>")

            buffer.append("</table>")
            buffer.append("</div>")

        buffer.append("</div>")
        return "\n".join(buffer)

    def render_latest_taxable_hold_pool(self, taxable_hold_pool: TaxableHoldPool) -> str:
        buffer = list()
        hold_pool = taxable_hold_pool.latest_hold_pool()

        buffer.append("<div>")
        buffer.append("<h3>Section 104 hold</h3>")

        buffer.append("<table>")
        buffer.append("<tr>")
        buffer.append("<th>Asset</th>")
        buffer.append("<th>Market cost pre unit</th>")
        buffer.append("<th>Volume</th>")
        buffer.append("<th>Hold cost</th>")
        buffer.append("<th>Market cost</th>")
        buffer.append("<th>Gain, if disposed</th>")
        buffer.append("<th>Tax, if disposed</th>")
        buffer.append("</tr>")

        market_asset_unit_price = self.stock_fetcher.get_price(hold_pool.asset)
        market_asset_price = market_asset_unit_price * hold_pool.volume
        estimate_record = hold_pool.estimate(market_asset_unit_price)

        latest_tax_rate = TAX_RATES[max(TAX_RATES.keys())]
        estimated_tax_to_pay = latest_tax_rate.calculate_tax_to_pay(estimate_record.amount) \
            if estimate_record.is_gain() else Decimal("0.0")

        buffer.append("<tr>")
        buffer.append(f"<td>{hold_pool.asset.symbol}</td>")
        buffer.append(f"<td class=\"right\">{market_asset_unit_price.quantize(DISPLAY_PRECISION, rounding=DISPLAY_ROUND)}</td>")
        buffer.append(f"<td class=\"right\">{hold_pool.volume}</td>")
        buffer.append(f"<td class=\"right\">{hold_pool.cost.quantize(DISPLAY_PRECISION, rounding=DISPLAY_ROUND)}</td>")
        buffer.append(f"<td class=\"right\">{market_asset_price.quantize(DISPLAY_PRECISION, rounding=DISPLAY_ROUND)}</td>")
        buffer.append(f"<td class=\"right\">{estimate_record.type} {estimate_record.amount.quantize(DISPLAY_PRECISION, rounding=DISPLAY_ROUND)}</td>")
        buffer.append(f"<td class=\"right\">{estimated_tax_to_pay}</td>")
        buffer.append("</tr>")

        buffer.append("</table>")
        buffer.append("</div>")
        return "\n".join(buffer)

    def render_hold_history(self, taxable_hold_pool: TaxableHoldPool) -> str:
        buffer = list()

        buffer.append("<div>")
        buffer.append("<h3>Section 104 hold history</h3>")

        buffer.append("<table>")
        buffer.append("<tr>")
        buffer.append("<th>Asset</th>")
        buffer.append("<th>Date</th>")
        buffer.append("<th>Volume</th>")
        buffer.append("<th>Cost</th>")
        buffer.append("</tr>")

        for hold_pool in taxable_hold_pool.hold_pools:
            buffer.append("<tr>")
            buffer.append(f"<td>{hold_pool.asset.symbol}</td>")
            buffer.append(f"<td>{hold_pool.date.strftime(DISPLAY_DATE_FORMAT)}</td>")
            buffer.append(f"<td class=\"right\">{hold_pool.volume}</td>")
            buffer.append(f"<td class=\"right\">{hold_pool.cost.quantize(DISPLAY_PRECISION, rounding=DISPLAY_ROUND)}</td>")
            buffer.append("</tr>")

        buffer.append("</table>")
        buffer.append("</div>")
        return "\n".join(buffer)

    def render_taxable_hold_pool(self, taxable_hold_pool: TaxableHoldPool) -> str:
        buffer = list()

        buffer.append("<div>")
        buffer.append(f"<h2>Asset: {taxable_hold_pool.asset.symbol}</h2>")
        buffer.append(f"<small>Type: {taxable_hold_pool.asset.type}</small><br />")

        buffer.append("<div>")
        buffer.append(self.render_taxable_records(taxable_hold_pool.taxable_records))
        buffer.append(self.render_latest_taxable_hold_pool(taxable_hold_pool))
        buffer.append(self.render_hold_history(taxable_hold_pool))
        buffer.append("</div>")

        buffer.append("</div>")
        return "\n".join(buffer)

    def render(self, taxable_hold_pools: List[TaxableHoldPool]):

        hold_pools = "\n".join([self.render_taxable_hold_pool(x) for x in taxable_hold_pools])
        taxable_total = self.render_taxable_total(taxable_hold_pools)
        footer = self.render_footer()

        buffer = [taxable_total, hold_pools, footer]
        html = self.wrap_html("\n".join(buffer))

        return html