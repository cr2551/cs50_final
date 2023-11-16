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
    total_portfolio_value = 0
    total_gains = 0
    # calculate weighted average cost
    for stock in portfolio:
        # find the the number of stocks you have bought over time and their price that have not been dequeued
        purchases = db.execute('''
                        SELECT price, quantity_left
                            FROM purchase_queue
                        WHERE user_id = ?
                        AND symbol = ?
                        ''', user_id, stock['symbol'])

        # find the total price you have paid
        total = 0
        for purchase in purchases:
            total += purchase['price'] * purchase['quantity_left']

        quantity  = stock['quantity']
        # calculate wac: sum(Quantity*Price) / sum(Quantity)
        # I am only calculating the wac for the purchases that have not been dequeued.
        wac  = total/quantity
        # add it to our portfolio dictionary
        stock['wac'] = wac
        # then i will use the wac to calculate the avg return 
        curr_quote = lookup(stock['symbol'])
        if not curr_quote:
            return apology('could not retrieve quote')
        # total return per share
        total_return = (curr_quote['price'] - wac)
        # total unrealized gains, what would be the profit if the stock was sold right now 
        gains = total_return * quantity
        total_gains += gains
        stock['gains'] = gains
        # avg return represented in percentage, remember we are not using the stock we sold.
        return_percentage  = (total_return / wac) * 100
        return_percentage = round(return_percentage, 2)
        stock['return_percentage'] = return_percentage
        # also add the current price to our portolio dictionary
        stock['current_price'] = curr_quote['price']
        # and add the total market value
        total_value = curr_quote['price'] * quantity
        stock['total_value'] = total_value
        # add it towards the Total market value of the whole portfolio
        total_portfolio_value += total_value

    # now that you have the total add the percentage of the prtfolio that each stock occupies
    for stock in portfolio:
        diversification = stock['total_value']/total_portfolio_value * 100
        stock['portfolio_diversity'] = round(diversification, 2)

    return [portfolio, total_portfolio_value, total_gains]
    
