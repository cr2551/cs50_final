import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import sqlite3

from flask import redirect, render_template, session
from functools import wraps
from cs50 import SQL


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )
    # Query API
    try:
        response = requests.get(url, cookies={"session": str(uuid.uuid4())}, headers={"User-Agent": "python-requests", "Accept": "*/*"})
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        quotes.reverse()
        price = round(float(quotes[0]["Adj Close"]), 2)
        return {
            "name": symbol,
            "price": price,
            "symbol": symbol
        }
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def get_portfolio(user_id):
    """Infer portfolio holdings from transactions History"""
    db = SQL('sqlite:///project.db')
    portfolio = db.execute('''
                SELECT symbol,
               SUM(CASE WHEN transaction_type = 'buy' THEN shares ELSE -shares END) AS quantity
                FROM transactions
               WHERE user_id = ?
               GROUP BY symbol
                HAVING quantity > 0
               ''', user_id)

    # calculate weighted average cost
    for stock in portfolio:
        # find the the number of stocks you have bought over time and their price
        purchases = db.execute('''
                        SELECT price, shares
                            FROM transactions 
                        WHERE user_id = ?
                        AND symbol = ?
                        AND transaction_type = "buy"
                        ''', user_id, stock['symbol'])

        quantity = len(purchases)        
        # find the total price you have paid
        total = 0
        for purchase in purchases:
            total += purchase['price'] * purchase['shares']

        # calculate gain/ loss 
        total_cost_purchase = db.execute('''
                                         SELECT total FROM transactions WHERE user_id = ? AND transaction_type='buy'
                                         AND symbol = ?
                                         ''', session['user_id'], stock['symbol'])
        # calculate wac: sum(Quantity*Price) / sum(Quantity)
        wac  = total/quantity
        # add it to our portfolio dictionary
        stock['wac'] = wac

    return portfolio
    
        