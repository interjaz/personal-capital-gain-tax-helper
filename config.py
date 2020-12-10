from typing import Dict

from src.model.tax import TaxRate, TaxPeriod

DATE_FORMAT = '%Y-%m-%d'
DATE_TIME_FORMAT = '"%Y-%m-%dT%H:%M:%S%z'

TAX_RATES: Dict[str, TaxRate] = {
    '2018/2019': TaxRate(rate="0.2", allowance="11,700.00"),
    '2019/2020': TaxRate(rate="0.2", allowance="12,000.00"),
    '2020/2021': TaxRate(rate="0.2", allowance="12,300.00"),
    '2021/2022': TaxRate(rate="0.2", allowance="12,300.00")
}

TAX_PERIOD = TaxPeriod("UK", 4, 6, 4, 5)
