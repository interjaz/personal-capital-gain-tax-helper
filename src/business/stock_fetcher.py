from decimal import Decimal

import requests


class StockFetcher(object):

    def __init__(self, api_key):
        self.api_key = api_key

    def get_price(self, asset):
        if asset.type == 'STOCK':
            us_price = self.get_us_stock_price(asset.symbol)
            usd_to_gbp = self.get_usd_to_gbp()
            return us_price * usd_to_gbp

        if asset.type == 'CRYPTO':
            return self.get_crypto_price(asset.symbol)

        raise ValueError(f"Supported type not supported, {asset}")

    def get_us_stock_price(self, asset):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={asset}&apikey={self.api_key}&outputsize=compact"
        response = requests.get(url)

        time_series = response.json()['Time Series (Daily)']
        latest_key = list(time_series.keys())[0]
        close = time_series[latest_key]['4. close']
        return Decimal(close)

    def get_crypto_price(self, asset):
        url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={asset}&to_currency=GBP&apikey={self.api_key}"
        response = requests.get(url)

        rate_details = response.json()['Realtime Currency Exchange Rate']
        rate = rate_details['5. Exchange Rate']
        return Decimal(rate)

    def get_usd_to_gbp(self):
        url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=GBP&apikey={self.api_key}"
        response = requests.get(url)

        rate_details = response.json()['Realtime Currency Exchange Rate']
        rate = rate_details['5. Exchange Rate']
        return Decimal(rate)
