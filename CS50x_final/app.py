import os

from cs50 import SQL
from datetime import date
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import (
    login_required,
    lookup,
    usd,
    get_user_id,
    get_username,
    get_cash,
    get_shareholders,
    get_capital,
    get_sh_acivity,
    get_div_info,
    get_div_data,
    get_monthly_income,
    get_yearly_income,
    average,
    get_av_cash
)

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///manager.db")


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

    usr = get_user_id()

    try:
        cash = get_cash(db)
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
                #comp = lookup(stock["stock"])["company"]
                value = int(stock["size"]) * price
                s_id = stock["id"]
                stocks_final.append(
                    {
                        #"company": comp,
                        "id": stock["id"],
                        "stock": stock["stock"],
                        "size": stock["size"],
                        "price": price,
                        "value": value,
                    }
                )
                portfolio_value += value

            capital = get_capital(db)
            perc_change = (portfolio_value - capital) / capital

            return render_template("index.html", cash=get_cash(db), stocks=stocks_final, portfolio_value=portfolio_value, username=get_username(db), perc_change=perc_change)
        except TypeError:
            pass

    portfolio_value = cash
    perc_change = 0

    return render_template("index.html", cash=get_cash(db), portfolio_value=portfolio_value, username=get_username(db), perc_change=perc_change)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Provide an username")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Provide a password")
            return redirect("/login")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password")
            return redirect("/login")

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        usr = request.form.get("username")
        psw = request.form.get("password")
        psw_check = request.form.get("confirmation")

        # check if data provided are valid
        if not usr:
            flash("No username provided")
            return redirect("/register")
        if not psw:
            flash("No password provided")
            return redirect("/register")
        if not psw_check:
            flash("Type password twice")
            return redirect("/register")
        if not psw == psw_check:
            flash("Two passwords don't match")
            return redirect("/register")
        if "'" in usr or ";" in usr:
            flash("Char not allowed in username")
            return redirect("/register")

        # check if username is already taken
        usr_check = db.execute("SELECT * FROM users WHERE username = ?;", usr)
        if len(usr_check) != 0:
            flash("Username already taken")
            return redirect("/register")

        # store data into db
        h_psw = generate_password_hash(psw)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", usr, h_psw)

        rows = db.execute("SELECT id FROM users WHERE username = ?;", usr)

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")



@app.route("/cash", methods=["POST"])
@login_required
def add_cash():
    try:
        more = float(request.form.get("added_cash"))
    except ValueError:
        flash("Amount not valid")
        return redirect("/shareholders")

    if not more:
        flash("Insert an amount")
        return redirect("/shareholders")
    if more < 0.01:
        flash("Insert a positive amount")
        return redirect("/shareholders")

    #check if a valid shareholder
    shareholder = request.form.get("shareholder")
    shareholders = get_shareholders(db)
    s_check = list()
    for i in shareholders:
        s_check.append(i["name"])
    if shareholder not in s_check:
        flash("Invalid shareholder")
        return redirect("/shareholders")


    cash = get_cash(db)
    cash += more

    #update cash available
    db.execute("UPDATE users SET cash = ? WHERE id = ?;", cash, get_user_id())

    #update current shareholder share
    share = float(db.execute("SELECT share FROM shareholders WHERE user_id = ? AND name = ?;", get_user_id(), shareholder)[0]["share"])
    share += more

    #update share for the shareholder in db
    db.execute("UPDATE shareholders SET share = ? WHERE user_id = ? AND name = ?;", share, get_user_id(), shareholder)

    #register deposit / withdraw
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action = "DEPOSIT"
    db.execute("INSERT INTO d_and_w (date, shareholder_id, action, amount) VALUES (?, (SELECT id FROM shareholders WHERE name = ? AND user_id = ?), ?, ?);", today, shareholder, get_user_id(), action, more)

    flash("Cash added correctly")
    return redirect("/shareholders")



@app.route("/subCash", methods=["POST"])
@login_required
def sub_cash():
    try:
        more = float(request.form.get("added_cash"))
    except ValueError:
        flash("Amount not valid")
        return redirect("/shareholders")

    if not more:
        flash("Insert an amount")
        return redirect("/shareholders")
    if more < 0.01:
        flash("Insert a positive amount")
        return redirect("/shareholders")

    #check if a valid shareholder
    shareholder = request.form.get("shareholder")
    shareholders = get_shareholders(db)
    s_check = list()
    for i in shareholders:
        s_check.append(i["name"])
    if shareholder not in s_check:
        flash("Invalid shareholder")
        return redirect("/shareholders")

    cash = get_cash(db)

    if more > cash:
        flash("Trying to withdraw too much cash")
        return redirect("/shareholders")

    capital = get_capital(db)
    share = float(db.execute("SELECT share FROM shareholders WHERE user_id = ? AND name = ?;", get_user_id(), shareholder)[0]["share"])
    share_perc = share / capital
    available_cash = cash * share_perc

    if more > available_cash:
        flash("Not enough cash available")
        return redirect("/shareholders")

    cash -= more

    #update cash available
    db.execute("UPDATE users SET cash = ? WHERE id = ?;", cash, get_user_id())

    #update current shareholder share

    share -= more

    #update share for the shareholder in db
    db.execute("UPDATE shareholders SET share = ? WHERE user_id = ? AND name = ?;", share, get_user_id(), shareholder)

    #register deposit / withdraw
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action = "WITHDRAW"
    db.execute("INSERT INTO d_and_w (date, shareholder_id, action, amount) VALUES (?, (SELECT id FROM shareholders WHERE name = ? AND user_id = ?), ?, ?);", today, shareholder, get_user_id(), action, more)

    if share == 0:
        #delete shareholder
        db.execute("DELETE FROM shareholders WHERE user_id = ? AND name = ?;", get_user_id(), shareholder)

    flash("Cash removed correctly")
    return redirect("/shareholders")




@app.route("/shareholders", methods=["GET", "POST"])
@login_required
def shareholders():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Insert a name")
            return redirect("/shareholders")
        sh_check = db.execute("SELECT * FROM shareholders WHERE user_id = ? AND name = ?;", get_user_id(), name)
        if len(sh_check) != 0:
            flash("Name already taken")
            return redirect("/shareholders")

        #add shareholder to db
        db.execute("INSERT INTO shareholders (user_id, name) VALUES (?, ?);", get_user_id(), name)
        flash("Shareholder added correctly")
        return redirect("/shareholders")

    else:
        try:
            info = get_div_data(db)
            monthly_income = get_monthly_income(info)
            yearly_income = get_yearly_income(monthly_income)
            sh = get_shareholders(db)
            av_cash = get_av_cash(db, sh)

            return render_template("shareholders.html", username=get_username(db), cash=get_cash(db), shareholders=get_shareholders(db), capital=get_capital(db), yearly_income=yearly_income, av_cash=av_cash)
        except:
            pass

        info = []
        monthly_income = {
                "GEN": 0, "FEB": 0, "MAR": 0, "APR": 0, "MAY": 0, "JUN": 0,
                "JUL": 0, "AUG": 0, "SEP": 0, "OCT": 0, "NOV": 0, "DEC": 0,
            }
        yearly_income = 0
        sh = get_shareholders(db)
        av_cash = get_av_cash(db, sh)
        return render_template("shareholders.html", username=get_username(db), cash=get_cash(db), shareholders=get_shareholders(db), capital=get_capital(db), yearly_income=yearly_income, av_cash=av_cash)



@app.route("/edit_shareholders", methods=["POST"])
@login_required
def edit_shareholder():
    new_name = request.form.get("name")
    if not new_name:
        flash("Insert a name")
        return redirect("/shareholders")
    sh_check = db.execute("SELECT * FROM shareholders WHERE user_id = ? AND name = ?;", get_user_id(), new_name)
    if len(sh_check) != 0:
        flash("Name already taken")
        return redirect("/shareholders")

    shareholder_id = request.form.get("id")

    #update shareholder name in db
    db.execute("UPDATE shareholders SET name = ? WHERE id = ?;", new_name, shareholder_id)

    return redirect("/shareholders")


@app.route("/d_w")
@login_required
def d_w():
    return render_template("d_w.html", username=get_username(db), cash=get_cash(db), activity=get_sh_acivity(db))



@app.route("/buy", methods=["POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # getting user input
    ticker = request.form.get("symbol")

    # checking for errors
    try:
        size = int(request.form.get("shares"))
    except ValueError:
        flash("Size not valid")
        return redirect("/")

    price = request.form.get("price")
    if not price:
        flash("Price is empty")
        return redirect("/")

    try:
        price = float(request.form.get("price"))
    except ValueError:
        flash("Price not valid")
        return redirect("/")

    if not ticker:
        flash("Enter a ticker symbol")
        return redirect("/")
    if not size:
        flash("Enter a size")
        return redirect("/")
    if size < 1:
        flash("Enter a valid size")
        return redirect("/")
    stock = lookup(ticker)
    if stock == None:
        flash("Stock not found")
        return redirect("/")

    # getting stock price
    #price = float(stock["price"])
    usr = get_user_id()

    # getting available cash
    cash = get_cash(db)

    tot_cost = price * size
    if tot_cost > cash:
        flash("Not enough cash available")
        return redirect("/")

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
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    act = "BUY"
    db.execute(
        "INSERT INTO transactions (date, user_id, stock_id, action, size, cost_per_share, cost) VALUES (?, ?, (SELECT id FROM stocks WHERE stock = ?), ?, ?, ?, ?);",
        today,
        usr,
        stock["name"],
        act,
        size,
        price,
        tot_cost
    )


    return redirect("/")





@app.route("/sell", methods=["POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # getting user input
    ticker = request.form.get("symbol")

    # checking for errors
    try:
        size = int(request.form.get("shares"))
    except ValueError:
        flash("Size not valid")
        return redirect("/")

    price = request.form.get("price")
    if not price:
        flash("Price is empty")
        return redirect("/")

    try:
        price = float(request.form.get("price"))
    except ValueError:
        flash("Price not valid")
        return redirect("/")

    if not ticker:
        flash("Enter a ticker symbol")
        return redirect("/")
    if not size:
        flash("Enter a size")
        return redirect("/")
    if size < 1:
        flash("Enter a valid size")
        return redirect("/")
    stock = lookup(ticker)
    if stock == None:
        flash("Stock not found")
        return redirect("/")

    # getting stock price
    #price = float(stock["price"])
    usr = get_user_id()

    # getting available cash
    cash = get_cash(db)

    # check the available shares to sell
    try:
        row = db.execute("SELECT * FROM users JOIN owning ON users.id = owning.user_id JOIN stocks ON stocks.id = owning.stock_id WHERE stock = ? AND user_id = ?;", stock["name"], usr)
    except KeyError:
        flash("Failure in checking available shares")
        return redirect("/")

    if len(row) < 0 or not row:
        flash("You don't have that amount of shares")
        return redirect("/")

    current_size = row[0]["size"]
    if size > current_size:
        flash("You don't have that amount of shares")
        return redirect("/")

    # execute transaction
    gain = price * size
    current_size -= size
    cash += gain

    # update cash
    db.execute("UPDATE users SET cash = ? WHERE id = ?;", cash, usr)

    # updating size
    try:
        db.execute("UPDATE owning SET size = ? WHERE user_id = ? AND stock_id = (SELECT id FROM stocks WHERE stock = ?);", current_size, usr, stock["name"])
    except KeyError:
        flash("Failed updating the shares")
        return redirect("/")

    # register transaction
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    act = "SELL"
    try:
        db.execute(
            "INSERT INTO transactions (date, user_id, stock_id, action, size, cost_per_share, cost) VALUES (?, ?, (SELECT id FROM stocks WHERE stock = ?), ?, ?, ?, ?);",
            today,
            usr,
            stock["name"],
            act,
            size,
            price,
            gain,
        )
    except KeyError:
        flash("Failed registration of the transaction")
        return redirect("/")

    return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(now)
    history = db.execute("SELECT * FROM stocks JOIN transactions ON stocks.id = transactions.stock_id WHERE user_id = ? ORDER BY date DESC;", get_user_id())

    return render_template("history.html", history=history, username=get_username(db), cash=get_cash(db))


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "GET":
        return render_template("settings.html", username=get_username(db), cash=get_cash(db))
    else:
        old_psw = request.form.get("old_password")
        new_psw = request.form.get("new_password")
        psw_check = request.form.get("password_check")

        if not old_psw:
            flash("Type old password")
            return redirect("/settings")
        if not new_psw:
            flash("Type new password")
            return redirect("/settings")
        if not psw_check:
            flash("Type new password twice")
            return redirect("/settings")
        if not new_psw == psw_check:
            flash("Second typed password not matching")
            return redirect("/settings")

        #get row from db
        rows = db.execute("SELECT * FROM users WHERE id = ? AND username = ?;", get_user_id(), get_username(db))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], old_psw):
            flash("Old password is invalid")
            return redirect("/settings")

        h_psw = generate_password_hash(new_psw)

        #update password in db
        db.execute("UPDATE users SET hash = ? WHERE id = ? AND username = ?;", h_psw, get_user_id(), get_username(db))
        flash("Password changed correctly")
        return redirect("/settings")


@app.route("/dividends")
@login_required
def dividends():

    try:
        info = get_div_data(db)
        monthly_income = get_monthly_income(info)
        yearly_income = get_yearly_income(monthly_income)
        avg_income = average(list(monthly_income.values()))

        return render_template("dividends.html", cash=get_cash(db), username=get_username(db), info=info, monthly_income=monthly_income, yearly_income=yearly_income, avg_income=avg_income)
    except:
        pass

    info = []
    monthly_income = {
            "GEN": 0, "FEB": 0, "MAR": 0, "APR": 0, "MAY": 0, "JUN": 0,
            "JUL": 0, "AUG": 0, "SEP": 0, "OCT": 0, "NOV": 0, "DEC": 0,
        }
    yearly_income = 0
    avg_income = 0

    return render_template("dividends.html", cash=get_cash(db), username=get_username(db), info=info, monthly_income=monthly_income, yearly_income=yearly_income, avg_income=avg_income)



@app.route("/upd_div_db", methods=["GET", "POST"])
@login_required
def update_div_db():

    usr = get_user_id()

    stocks = db.execute("SELECT stock_id, size, stock FROM owning JOIN stocks ON stocks.id = owning.stock_id WHERE user_id = ?;", usr)
    if len(stocks) > 0:
        alert = True
        for s in stocks:
            try:
                get_div_info(s["stock"], db)
            except:
                if alert is True:
                    flash("Error querying info")
                    alert = False
                continue
    return redirect("/dividends")
