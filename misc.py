import uuid
import urllib
import datetime
import pytz
import requests
import csv

def my_lookup(symbol):
    """My version of the lookup function in helpers.py"""
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone('US/Eastern'))
    start = end - datetime.timedelta(days=30)

    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    u2 = urllib.parse.quote_plus(symbol)
    try:
        response = requests.get(url, cookies={'session': str(uuid.uuid4())}, headers={'User-agent': 'python-requests', 'Accept': '*/*' })
        response.raise_for_status()

        # json_res = response.json()
        res = response.content.decode('utf-8').splitlines()
        res = list(csv.DictReader(res))
        prices = [float(x['Adj Close']) for x in res ]
        dates = [k['Date'] for k in res]
        return prices, dates
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None
    
ticker = 'AAPL'
my_lookup(ticker)