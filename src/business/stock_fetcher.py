from decimal import Decimal
from time import sleep

import requests

ASSET_VALUE_LOOKUP_GBP = {
    'VAUG': Decimal('90.72'),
    'AMZN': Decimal('179.35'),
    'GOOGL': Decimal('157.31'),
    'MSFT': Decimal('343.19'),
    'TSLA': Decimal('326.36'),
    'NVDA': Decimal('111.33'),
    'AAPL': Decimal('194.02'),
    'SPXP': Decimal('941.55'),
    'BTC':  Decimal('77364.07'),
    'ETH':  Decimal('2696.55'),
    'LTC':  Decimal('84.68'),
}


class StockFetcher(object):

    # Free account 5 request per minute
    THROTTLE_TPS = 5.0 / 60.0

    def __init__(self, api_key):
        self.api_key = api_key

    def get_price(self, asset):
        if asset.symbol in ASSET_VALUE_LOOKUP_GBP:
            return ASSET_VALUE_LOOKUP_GBP[asset.symbol]

        return Decimal(0.0)

        if asset.symbol == 'VAUG':
            return self.get_uk_stock_price(asset.symbol)

        if asset.type == 'STOCK':
            us_price = self.get_us_stock_price(asset.symbol)
            usd_to_gbp = self.get_usd_to_gbp()
            return us_price * usd_to_gbp

        if asset.type == 'CRYPTO':
            return self.get_crypto_price(asset.symbol)

        raise ValueError(f"Supported type not supported, {asset}")

    def get_uk_stock_price(self, asset_code):
        return self.get_us_stock_price(asset_code + ".LON")

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
            print("Failed for asset: " + str(asset_code))
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
