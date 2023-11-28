import os
import logging

from flask import Flask, session, request, render_template, redirect 
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from dotenv import load_dotenv


from helpers import lookup, usd, login_required, apology, get_portfolio
from cs50 import SQL

# from .db import create_tables

load_dotenv()
debug = os.getenv('DEBUG')

pip_version = os.popen('pip -V').read()
print('----------------------pip version: ', pip_version)

app = Flask(__name__)

app.jinja_env.filters['usd'] = usd

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# log with gunicorn
if app.config.get('LOG_WITH_UNICORN'):
    gunicorn_error_loger  = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_loger.handlers)
    app.logger.setLevel(logging.DEBUG)
else:
    # use standard logging configuration
    ...

# print(dict(app.config))

if debug:
    app.config['DEBUG'] = True



# if app.config['DEBUG'] == True:
#     url = 'sqlite:///project.db'
#     db = SQL(url)
# else:
#     url = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://', 1)
#     db = SQL(url)

url = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://', 1)
db = SQL(url)

users = db.execute('SELECT * FROM users')
print(users, '-----------------------------------------------------------------||')

@app.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    if request.method == 'GET':
        return render_template('landing_page.html')
    elif request.method == 'POST':
        return render_template('layout.html', page='home')
    
            


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    order = request.args.get('order')
    if not order:
        order = 'transaction_id'
    asc = ' ASC'
    if order in ['transaction_date', 'profit', 'transaction_id']:
        if order == 'transaction_id':
            order = order + asc
        else:
            order = order + ' DESC'
        transactions = db.execute(f'''SELECT * FROM transactions WHERE user_id = ?
                        ORDER BY {order}'''
                        , session['user_id'])
    if order == 'profit':
        sales = filter(lambda k: k[order] != None, transactions)
        purchases = filter(lambda k: k[order] == None, transactions)
        sales = list(sales)
        purchases = list(purchases)
        sales = sorted(sales, key=lambda k: k['profit'], reverse=True)
        transactions = sales + purchases

        # history = sorted(history, key=lambda k: k[order], reverse=False)
    total_profit = db.execute('''SELECT SUM(profit) AS total 
                                   FROM transactions WHERE user_id = ? AND transaction_type="sell" ''', session['user_id'])
    total_profit = total_profit[0]['total']
    if total_profit is None:
        total_profit = 0
    return render_template('history.html' ,history=transactions, page='history', total_profit=total_profit)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'GET':
        return render_template('register.html', page='register')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        if not username or not password or not confirmation:
            return apology('Must enter both username and password')
        if password != confirmation:
            return apology('password mismatch')
        # check if username already taken
        connection = sqlite3.connect('project.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        rows = cursor.fetchall()
        if len(rows) != 0:
            return apology('Username already Taken')

        hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, hash) VALUES (?, ?)', (username, hash))
        connection.commit()
        connection.close()
        
        return redirect('/login')
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        connection = sqlite3.connect('project.db')
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        # Query database for username
        username = request.form.get('username')
        cursor.execute("SELECT * FROM users WHERE username = ?", (username, ))
        rows = cursor.fetchall()
        connection.close()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        print(session['user_id'], '----------------------------session user id ------------------------------', end="\n\n")

        # Redirect user to home page
        return redirect("/portfolio")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # handle demo request
        user = request.args.get('user')
        if user == 'demo':
            rows = db.execute('SELECT * from users WHERE username = ?', user)

            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], '0'):
                return 'No valid username or password'
            else:
                # login demo user
                session['user_id'] = rows[0]['id']
                return redirect('/portfolio')


            

        # else return the login page.    
        return render_template("login.html", page='login')


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route('/portfolio')
@login_required
def portfolio_view():
    portfolio, total, gains = get_portfolio(session['user_id'])
    order = request.args.get('order')
    if order:
        portfolio = sorted(portfolio, key=lambda k: k[order], reverse=True)
    return render_template('portfolio.html', portfolio=portfolio, page='portfolio', total=total, gains=gains)




@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """ add transaction"""
    if request.method == 'GET':
        return render_template('add_transaction.html', page='add')
    elif request.method == 'POST':
        symbol = request.form.get('symbol')
        shares = request.form.get('quantity')
        transaction_type = request.form.get('transaction_type')
        comments = request.form.get('comments')
        price = request.form.get('price')
        # the price gets automatically converted to an integer when you givc it to the database as input even though
        # it is a string at the beginning.

        date = request.form.get('date')
        # input validation
        if not symbol or  not shares:
            return apology('Enter both symbol and shares')
        elif shares.isdigit() == False:
            return apology('not integer')
        else:
            # convert shares to int
            shares = int(shares)
            price = float(price)
            total = shares * price
            stock = lookup(symbol)
            if not stock:
                return apology('symbol not found')
            symbol = stock['symbol']
            # remove the following later. only for testing ===============
            if not price:
                price = stock['price']

            # if shares are not 1 or more 
            if shares < 1:
                return apology('shares must be an integer greater than zero')
            
            else:
                if transaction_type == 'buy':
                    connection = sqlite3.connect('project.db')
                    cursor = connection.cursor()
                    # insert purchase in transactions table and put its id in a variable
                    transaction_id = db.execute('''INSERT INTO transactions 
                                                (user_id, symbol, shares, price, transaction_type, transaction_date, total, comments) 
                                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                                session['user_id'], symbol, shares, price, transaction_type, date, total, comments
                                                )

                    # put the transaction_id also in the purchase queue table. It will allow us to identify those transactions that have been dequeued.
                    cursor.execute('INSERT INTO purchase_queue (user_id, transaction_id, symbol, quantity_left, price, total) VALUES (?, ?, ?, ?, ?, ?)', (session['user_id'], transaction_id, symbol, shares, price, total))
                    connection.commit()
                    connection.close()
                elif  transaction_type == 'sell':
                    # calculate using FIFO the gains from this transaction
                    # use a queue to store the purchase/buy transactions and you get their cost basis and subtract it from the total of the sale
                    # each object stored in the queue could be a row resulting from an sql select statement or just a dictionary containing
                    # the numbers of shares and the total price of the transaction, which we would obtain at first from a select statement
                    # this queue should be stored in its own table so that it is persistant in memory.
                    rows = db.execute(
                            '''
                                SELECT transaction_id, purchase_id, symbol, price, quantity_left, proportional, total FROM purchase_queue 
                                WHERE user_id = ?
                                AND symbol = ?
                            '''
                                , session['user_id'], symbol
                        )

                    profit = 0
                    # copy shares variable because ww will modify it later.
                    shares_sold = shares
                    # retrieve item from queue, the for loop ensures we can keep retrieving items from the queue when we need to sell
                    # more shares than we bought in the corresponding transaction
                    for i in range(len(rows)):     
                         item = rows[i]
                         old_price = item['price']
                         shares = item['quantity_left'] - shares
                         if shares == 0:
                            profit += (price - old_price) * item['quantity_left'] 
                            db.execute('DELETE FROM purchase_queue WHERE purchase_id = ?', item['purchase_id'])
                            # mark the transaction as dequeued from transactions table
                            db.execute('UPDATE transactions SET dequeued = 1 WHERE transaction_id = ?', item['transaction_id'])
                            break
                         elif shares > 0:
                            #update
                            profit += (price - old_price) * (item['quantity_left'] - shares) 
                            db.execute('''UPDATE purchase_queue SET quantity_left = ?, proportional = 1
                                    WHERE purchase_id = ?''',shares, item['purchase_id'])
                            break
                         else:
                            #delete
                            db.execute('DELETE FROM purchase_queue WHERE purchase_id = ?', item['purchase_id'])
                            # everytime we delete mark the transaction as dequeued in the transactions table
                            db.execute('UPDATE transactions SET dequeued = 1 WHERE transaction_id = ?', item['transaction_id'])
                            # flip the sign of the shares
                            shares = -shares
                            profit += (price - old_price) * (item['quantity_left'])

                    db.execute('INSERT INTO transactions (user_id, symbol, shares, price, transaction_type, transaction_date, profit, total, comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', session['user_id'], symbol, shares_sold, price, transaction_type, date, profit, total, comments)
                    
                return redirect('/history')
            

@app.route('/history/<transaction_id>')
@login_required
def transaction_detail(transaction_id):
    detail = db.execute('SELECT * FROM transactions WHERE transaction_id = ?', transaction_id)
    return render_template('history_detail.html', detail=detail[0])
    
