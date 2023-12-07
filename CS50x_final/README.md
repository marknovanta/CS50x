# CS50 PORTFOLIO MANAGER
#### Video Demo: https://youtu.be/RgNdxGtenO4

## Description:
This project can be considered an extension of the CS50 finance project
It's a web application that still allows to register multiple users and
to buy and sell stocks,
as extra features, it even allows to see the income from each stock as dividends
and allows to even manage multiple partecipations in the portfolio through the
shareholders page, in case the user manage funds even for friends and family.

It then stores all the data about the users, shareholders, stocks and dividends
into a database.

## Technologies used:
- Python
- Flask
- SQL
- HTML
- CSS
- JavaScript
- Jinja
- Financial Modeling Prep API

## How the web application works:
First thing the user sees is the login page. In case is not already registered,
to the top right a link to the registration page. It will be requested an username
and a password (asked to be typed twice). On the backend is checked for potential errors
like an already taken username or a mismatching password.

Once the user is registered (or logged in) is taken to the homepage, presented as an overview
of the owning stocks, their position size and market value.
Followed by the available cash and the total value of the portfolio, considering last prices of each stock.

From the homepage is even possible to buy and sell stocks from your portfolio, but in order to do
that, if you just started, is required to add shareholders and cash from the "Shareholders" page.

The "Shareholders" page shows shareholders name, percentage of ownership of the portfolio,
income from dividends (based on the ownership) and available cash to withdraw.
Followed by info about total cash and total capital provided by shareholders.
On top controls to add shareholders, deposit or withdraw cash.
Is even possible to edit existing shareholders with the "edit" button that whill show beside each shareholder once added.

The "Deposit/Withdraw" page shows the shareholders activity. Every deposit and withdraw.

The "History" page shows the portfoldio activity, every bought and sold stocks

The "Dividends" page shows all the dividends coming from the portfolio ownings, organized in a calendar, by month. With a summ of the total income per each month and the whole year.
Dividend data is provided through Financial Modeling Prep (https://site.financialmodelingprep.com/) and their API. The amount of requests per day is limited with the free plan, but they are way more than enough. All the data are stored into the database once downloaded and is not needed to make another request every time you load the page. You can make a manual download by the "Update database" button.

When you want to buy a new stock, you can do that through the "Overview" page, using the "Buy stock" button.
You will then be able to specify the ticker symbol, the amount of shares and the price (you can insert the price manually just in case you want to add stocks you already own before using the app).
You can even sell stocks from the "Overview" page, using the "Sell" button showed beside each stock.

On the top right of the page is always showed the available cash and the username. If you click on the username, you will view the setting page where you will be able to change the password.

## Database:
Tables:
- users: stores all the users and their passwords (hashs)
- stocks: stores all the stocks symbols
- owning: is used to merge users and stocks through their IDs
- transactions: stores all the portfolio movements (buy and sell)
- shareholders: stores the shareholder names and their share
- d_and_w: stores the shareholders activity (deposit and withdraw)
- dividends: stores the dividend amount each stock pays
- div_payments: stores what months each stock pays the dividend


## Key Features:
- Buy and Sell stocks
- Manual position entry for stocks owned before using the app
- Keep track of your dividend income
- Add shareholders to your portfolio
- Keep track of their share and individual income
- Keep track of portfolio value
- Keep track of portfolio activity (bought and sold stocks)
- Keep track of shareholders activity (deposits and withdraws)

## Files:
project/:
- app.py
- helpers.py
- db_init.py (to initialize the database)
- manager.db
- README.md
- static/
    - scripts.js
    - styles.css
- templates/
    - dividend.html
    - history.html
    - layout.html
    - register.html
    - shareholders.html
    - d_w.html
    - index.html
    - login.html
    - settings.html
