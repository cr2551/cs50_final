from flask import Flask, session, request, render_template, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from helpers import lookup, usd, login_required, apology, get_portfolio

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

# create connection to database

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        return render_template('layout.html')
    elif request.method == 'POST':
        date = request.form.get('date')
        return render_template('layout.html', page='home')
    
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
        price = request.form.get('price')
        # the price gets automatically converted to an integer when you givc it to the database as input even though
        # it is a string at the beginning.
        print(type(price))

        date = request.form.get('date')
        # input validation
        if not symbol or  not shares:
            return apology('Enter both symbol and shares')
        elif shares.isdigit() == False:
            return apology('not integer')
        else:
            # convert shares to int
            shares = int(shares)
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
                connection = sqlite3.connect('project.db')
                cursor = connection.cursor()
                cursor.execute('INSERT INTO transactions (user_id, symbol, shares, price, transaction_type, transaction_date) VALUES (?, ?, ?, ?, ?, ?)', (session['user_id'], symbol, shares, price, transaction_type, date))
                connection.commit()
                connection.close()
                # update portfolio
                return redirect('/')
            


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    with sqlite3.connect('project.db') as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM transactions WHERE user_id = ?', (session['user_id'],))
        history = cursor.fetchall()
    # history = db.execute('SELECT * FROM transactions WHERE user_id = ?', session['user_id'])
    return render_template('history.html' ,history=history, page='history')


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
        
        return redirect('/')
    
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

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", page='login')


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@login_required
@app.route('/portfolio')
def portfolio():
    portfolio = get_portfolio(session['user_id'])
    print(portfolio)
    return apology('todo')
