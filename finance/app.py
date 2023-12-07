import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    usr = session["user_id"]

    try:
        cash = float(db.execute("SELECT cash FROM users WHERE id = ?;", usr)[0]["cash"])
    except:
        cash = 0

    stocks = db.execute(
        "SELECT * FROM owning JOIN stocks ON stocks.id = owning.stock_id WHERE user_id = ?;",
        usr,
    )
    portfolio_value = cash
    stocks_final = list()
    if len(stocks) != 0 and stocks != None:
        try:
            for stock in stocks:
                if int(stock["size"]) == 0:
                    continue
                price = lookup(stock["stock"])["price"]
                value = int(stock["size"]) * price
                stocks_final.append(
                    {
                        "stock": stock["stock"],
                        "size": stock["size"],
                        "price": usd(price),
                        "value": usd(value),
                    }
                )
                portfolio_value += value
            username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
                "username"
            ]
            return render_template(
                "index.html",
                cash=usd(cash),
                stocks=stocks_final,
                portfolio_value=usd(portfolio_value),
                username=username,
            )
        except TypeError:
            pass

    portfolio_value = cash
    username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
        "username"
    ]
    return render_template(
        "index.html",
        cash=usd(cash),
        portfolio_value=usd(portfolio_value),
        username=username,
    )


@app.route("/cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        try:
            more = float(request.form.get("add_cash"))
        except ValueError:
            return apology("amount not valid", 400)

        if not more:
            return apology("enter an amount", 400)
        if more < 1:
            return apology("enter an amount bigger than ZERO", 400)

        usr = session["user_id"]
        cash = float(db.execute("SELECT cash FROM users WHERE id = ?;", usr)[0]["cash"])
        cash += more

        db.execute("UPDATE users SET cash = ? WHERE id = ?;", cash, usr)

        return redirect("/")

    else:
        usr = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
            "username"
        ]
        return render_template("add_cash.html", username=username)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # getting user input
        ticker = request.form.get("symbol")

        # checking for errors
        try:
            size = int(request.form.get("shares"))
        except ValueError:
            return apology("size not valid", 400)

        if not ticker:
            return apology("enter a ticker symbol", 400)
        if not size:
            return apology("enter a size", 400)
        if size < 1:
            return apology("enter a valid size", 400)
        stock = lookup(ticker)
        if stock == None:
            return apology("stock not found", 400)

        # getting stock price
        price = float(stock["price"])
        usr = session["user_id"]

        # getting available cash
        cash = float(db.execute("SELECT cash FROM users WHERE id = ?;", usr)[0]["cash"])

        tot_cost = price * size
        if tot_cost > cash:
            return apology("not enough cash", 400)

        cash -= tot_cost

        # update cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?;", cash, usr)

        # check if already owning the stock
        row = db.execute(
            "SELECT * FROM users JOIN owning ON users.id = owning.user_id JOIN stocks ON stocks.id = owning.stock_id WHERE stock = ? AND user_id = ?;",
            stock["name"],
            usr,
        )
        if len(row) > 0:
            # get current size
            current_size = int(row[0]["size"])

            # update size
            new_size = size + current_size
            db.execute(
                "UPDATE owning SET size = ? WHERE user_id = ? AND stock_id = (SELECT id FROM stocks WHERE stock = ?);",
                new_size,
                usr,
                stock["name"],
            )

        else:
            db.execute("INSERT INTO stocks (stock) VALUES (?);", stock["name"])
            db.execute(
                "INSERT INTO owning (user_id, stock_id, size) VALUES (?, (SELECT id FROM stocks WHERE stock = ?), ?);",
                usr,
                stock["name"],
                size,
            )

        # register transaction
        act = "BUY"
        db.execute(
            "INSERT INTO transactions (user_id, stock_id, action, size, cost) VALUES (?, (SELECT id FROM stocks WHERE stock = ?), ?, ?, ?);",
            usr,
            stock["name"],
            act,
            size,
            tot_cost,
        )

        price = usd(price)
        tot_cost = usd(tot_cost)
        cash = usd(cash)
        stock = stock["name"]
        result = f"You bought {size} {stock} at {price} per share, for a total of {tot_cost}. You have {cash} left."
        username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
            "username"
        ]
        return render_template("buy.html", result=result, username=username)

    else:
        usr = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
            "username"
        ]
        return render_template("buy.html", username=username)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    usr = session["user_id"]
    temp = db.execute(
        "SELECT * FROM stocks JOIN transactions ON stocks.id = transactions.stock_id WHERE user_id = ?;",
        usr,
    )
    history = list()
    for e in temp:
        history.append(
            {
                "stock": e["stock"],
                "action": e["action"],
                "size": e["size"],
                "cost": usd(e["cost"]),
            }
        )

    username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
        "username"
    ]
    return render_template("history.html", history=history, username=username)


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

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        ticker = request.form.get("symbol")
        stock = lookup(ticker)
        if stock == None:
            return apology("stock not found", 400)
        usr = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
            "username"
        ]
        return render_template(
            "quote.html", companyName=stock["name"], price=usd(stock["price"])
        )
    else:
        usr = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
            "username"
        ]
        return render_template("quote.html", username=username)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        usr = request.form.get("username")
        psw = request.form.get("password")
        psw_check = request.form.get("confirmation")

        # check if data provided are valid
        if not usr:
            return apology("no username provided", 400)
        if not psw:
            return apology("no password provided", 400)
        if not psw_check:
            return apology("type password twice", 400)
        if not psw == psw_check:
            return apology("two passwords don't match", 400)
        if "'" in usr or ";" in usr:
            return apology("char not allowed in the username", 400)

        # check if username is already taken
        usr_check = db.execute("SELECT * FROM users WHERE username = ?;", usr)
        if len(usr_check) != 0:
            return apology("username already taken", 400)

        # store data into db
        h_psw = generate_password_hash(psw)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", usr, h_psw)

        rows = db.execute("SELECT id FROM users WHERE username = ?;", usr)
        # rows = db.execute("SELECT * FROM users WHERE username = ?", usr)

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # getting user input
        ticker = request.form.get("symbol")

        # checking for errors
        try:
            size = int(request.form.get("shares"))
        except ValueError:
            return apology("size not valid", 400)

        if not ticker:
            return apology("enter a ticker symbol", 400)
        if not size:
            return apology("enter a size", 400)
        if size < 1:
            return apology("enter a valid size", 400)
        stock = lookup(ticker)
        if stock == None:
            return apology("stock not found", 400)

        # getting stock price
        price = float(stock["price"])
        usr = session["user_id"]

        # getting available cash
        cash = float(db.execute("SELECT cash FROM users WHERE id = ?;", usr)[0]["cash"])

        # check the available shares to sell
        try:
            row = db.execute(
                "SELECT * FROM users JOIN owning ON users.id = owning.user_id JOIN stocks ON stocks.id = owning.stock_id WHERE stock = ? AND user_id = ?;",
                stock["name"],
                usr,
            )
        except KeyError:
            return apology("failed checking available shares", 400)

        if len(row) < 0 or not row:
            return apology("you don't have that amount of shares", 400)

        current_size = row[0]["size"]
        if size > current_size:
            return apology("you don't have that amount of shares", 400)

        # execute transaction
        gain = price * size
        current_size -= size
        cash += gain

        # update cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?;", cash, usr)

        # updating size
        try:
            db.execute(
                "UPDATE owning SET size = ? WHERE user_id = ? AND stock_id = (SELECT id FROM stocks WHERE stock = ?);",
                current_size,
                usr,
                stock["name"],
            )
        except KeyError:
            return apology("failed updating shares", 400)

        # register transaction
        act = "SELL"
        try:
            db.execute(
                "INSERT INTO transactions (user_id, stock_id, action, size, cost) VALUES (?, (SELECT id FROM stocks WHERE stock = ?), ?, ?, ?);",
                usr,
                stock["name"],
                act,
                size,
                gain,
            )
        except KeyError:
            return apology("failed registration of the transaction", 400)

        stocks = db.execute(
            "SELECT * FROM owning JOIN stocks ON stocks.id = owning.stock_id WHERE user_id = ?;",
            usr,
        )
        stocks_final = list()
        if len(stocks) != 0:
            for stock in stocks:
                if int(stock["size"]) == 0:
                    continue
                stocks_final.append({"symbol": stock["stock"]})

        stock = stock["stock"]
        price = usd(price)
        gain = usd(gain)
        cash = usd(cash)
        result = f"You sold {size} {stock} at {price} per share, for a total of {gain}. You have {cash} left."
        username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
            "username"
        ]
        return render_template(
            "sell.html", stocks=stocks_final, username=username, result=result
        )

    else:
        usr = session["user_id"]
        stocks = db.execute(
            "SELECT * FROM owning JOIN stocks ON stocks.id = owning.stock_id WHERE user_id = ?;",
            usr,
        )
        stocks_final = list()
        if len(stocks) != 0:
            for stock in stocks:
                if int(stock["size"]) == 0:
                    continue
                stocks_final.append({"symbol": stock["stock"]})
        username = db.execute("SELECT username FROM users WHERE id = ?;", usr)[0][
            "username"
        ]
        return render_template("sell.html", stocks=stocks_final, username=username)
