import csv
import datetime
import pytz
import requests
import subprocess
import urllib
from urllib.request import urlopen
import uuid
import json

from flask import redirect, render_template, session
from functools import wraps


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

        #getting company name
        """ url = f"https://financialmodelingprep.com/api/v3/search-ticker?query={symbol}&limit=1&apikey=4d50bc0e7686040383b75d29c418d390"
        response = urlopen(url)
        data = json.loads(response.read())
        comp = data[0]["name"] """

        return {
            #"company": comp,
            "name": symbol,
            "price": price,
            "symbol": symbol
        }
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# add support for multiple currencies?

def get_user_id():
    return session["user_id"]

def get_username(db):
    return db.execute("SELECT username FROM users WHERE id = ?;", get_user_id())[0]["username"]

def get_cash(db):
    return float(db.execute("SELECT cash FROM users WHERE id = ?", get_user_id())[0]["cash"])

def get_shareholders(db):
    return db.execute("SELECT * FROM shareholders WHERE user_id = ? ORDER BY share DESC;", get_user_id())

def get_capital(db):
    capital = 0
    data = db.execute("SELECT share FROM shareholders WHERE user_id = ?;", get_user_id())
    for s in data:
        capital += s["share"]
    return capital

def get_sh_acivity(db):
    return db.execute("""SELECT * FROM d_and_w
                        JOIN shareholders ON shareholders.id = d_and_w.shareholder_id
                        WHERE user_id = ? ORDER BY date DESC;""", get_user_id())


def get_div_info(stock, db):

    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{stock}?apikey=4d50bc0e7686040383b75d29c418d390"
    response = urlopen(url)
    data = json.loads(response.read())
    current_year = int(datetime.date.today().year)
    info = {"symbol": data["symbol"]}
    payment_months = list()
    for i in data["historical"]:
        date = datetime.datetime.strptime(i["paymentDate"], '%Y-%m-%d').date()
        if date.year < (current_year - 1):
            break
        else:
            if date.month in payment_months:
                continue
            else:
                payment_months.append(date.month)
    info["payment_months"] = sorted(payment_months)
    info["amount"] = data["historical"][0]["dividend"]

    #store info in DB
    #store amount
    #check if data already in db
    check = db.execute("SELECT dividend FROM dividends WHERE ticker_id = (SELECT id FROM stocks WHERE stock = ?);", info["symbol"])

    if len(check) == 0:
        db.execute("""INSERT INTO dividends (ticker_id, dividend)
                VALUES ((SELECT id FROM stocks WHERE stock = ?), ?);""",
                info["symbol"], info["amount"])

        #store payment months
        for p in info["payment_months"]:
            db.execute("""INSERT INTO div_payments (symbol_id, payment_date)
                    VALUES ((SELECT id FROM stocks WHERE stock = ?), ?);""",
                    info["symbol"], p)
    else:
        db.execute("""UPDATE dividends
                   SET dividend = ?
                   WHERE ticker_id = (SELECT id FROM stocks WHERE stock = ?);""",
                   info["amount"], info["symbol"])

        #update even the months when dividend is paid?

    return


def get_div_data(db):
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
            info = list()

            for stock in stocks:
                if int(stock["size"]) == 0:
                    continue

                #get info about dividends
                div_info = dict()
                div_info["symbol"] = stock["stock"]
                payment_months_temp = db.execute("SELECT payment_date FROM div_payments WHERE symbol_id = (SELECT id FROM stocks WHERE stock = ?);", stock["stock"])
                payment_months = list()
                for i in payment_months_temp:
                    payment_months.append(i["payment_date"])
                div_info["payment_months"] = payment_months
                try:
                    div_amount = db.execute("SELECT dividend FROM dividends WHERE ticker_id = (SELECT id FROM stocks WHERE stock = ?);", stock["stock"])[0]["dividend"]
                except:
                    return redirect("/upd_div_db")
                div_info["amount"] = div_amount * stock["size"]
                yearly_income = div_info["amount"] * len(payment_months)
                div_info["yearly_income"] = yearly_income

                info.append(div_info)
        except:
            return

        return info

def get_monthly_income(info):
    monthly_income = {
            "GEN": 0, "FEB": 0, "MAR": 0, "APR": 0, "MAY": 0, "JUN": 0,
            "JUL": 0, "AUG": 0, "SEP": 0, "OCT": 0, "NOV": 0, "DEC": 0,
        }

    #get monthly income
    for i in range(len(info)):
        if 1 in info[i]["payment_months"]:
            monthly_income["GEN"] += info[i]["amount"]
        if 2 in info[i]["payment_months"]:
            monthly_income["FEB"] += info[i]["amount"]
        if 3 in info[i]["payment_months"]:
            monthly_income["MAR"] += info[i]["amount"]
        if 4 in info[i]["payment_months"]:
            monthly_income["APR"] += info[i]["amount"]
        if 5 in info[i]["payment_months"]:
            monthly_income["MAY"] += info[i]["amount"]
        if 6 in info[i]["payment_months"]:
            monthly_income["JUN"] += info[i]["amount"]
        if 7 in info[i]["payment_months"]:
            monthly_income["JUL"] += info[i]["amount"]
        if 8 in info[i]["payment_months"]:
            monthly_income["AUG"] += info[i]["amount"]
        if 9 in info[i]["payment_months"]:
            monthly_income["SEP"] += info[i]["amount"]
        if 10 in info[i]["payment_months"]:
            monthly_income["OCT"] += info[i]["amount"]
        if 11 in info[i]["payment_months"]:
            monthly_income["NOV"] += info[i]["amount"]
        if 12 in info[i]["payment_months"]:
            monthly_income["DEC"] += info[i]["amount"]

    return monthly_income

def get_yearly_income(monthly_income):
    yearly_income = (monthly_income["GEN"] + monthly_income["FEB"] + monthly_income["MAR"] + monthly_income["APR"] + monthly_income["MAY"] + monthly_income["JUN"] +
                    monthly_income["JUL"] + monthly_income["AUG"] + monthly_income["SEP"] + monthly_income["OCT"] + monthly_income["NOV"] + monthly_income["DEC"])
    return yearly_income

def average(list):
    return sum(list) / len(list)


def get_av_cash(db, sh):
    sh_IDs = list()
    for i in range(len(sh)):
        sh_IDs.append(sh[i]["id"])

    av_cash = [0]
    capital = get_capital(db)
    cash = get_cash(db)

    for i in sh_IDs:
        share = float(db.execute("SELECT share FROM shareholders WHERE user_id = ? AND id = ?;", get_user_id(), i)[0]["share"])
        try:
            share_perc = share / capital
        except:
            share_perc = 0
        available_cash = cash * share_perc
        av_cash.append(available_cash)

    return av_cash
