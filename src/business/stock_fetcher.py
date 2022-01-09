from decimal import Decimal
from time import sleep

import requests


class StockFetcher(object):

    # Free account 5 request per minute
    THROTTLE_TPS = 5.0 / 60.0

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

    def get_us_stock_price(self, asset_code):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={asset_code}&apikey={self.api_key}&outputsize=compact"
        response = requests.get(url)
        body = response.json()

        try:
            time_series = body['Time Series (Daily)']
            latest_key = list(time_series.keys())[0]
            close = time_series[latest_key]['4. close']

            self.__throttle()
            return Decimal(close)
        except Exception as ex:
            print(body)
            raise ex

    def get_crypto_price(self, asset):
        url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={asset}&to_currency=GBP&apikey={self.api_key}"
        response = requests.get(url)
        body = response.json()

        try:
            rate_details = body['Realtime Currency Exchange Rate']
            rate = rate_details['5. Exchange Rate']

            self.__throttle()
            return Decimal(rate)
        except Exception as ex:
            print(body)
            raise ex

    def get_usd_to_gbp(self):
        url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=GBP&apikey={self.api_key}"
        response = requests.get(url)
        body = response.json()

        try:
            rate_details = response.json()['Realtime Currency Exchange Rate']
            rate = rate_details['5. Exchange Rate']

            self.__throttle()
            return Decimal(rate)
        except Exception as ex:
            print(body)
            raise ex

    def __throttle(self):
        delay_sec = 1.0 / StockFetcher.THROTTLE_TPS
        print(f"Avoiding throttling for {delay_sec} sec")
        sleep(delay_sec)
