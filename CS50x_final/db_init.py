import sqlite3
import os

if os.path.isfile("manager.db"):
    os.remove("manager.db")

connection = sqlite3.connect("manager.db")
db = connection.cursor()

db.execute("""CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                username TEXT NOT NULL,
                hash TEXT NOT NULL,
                cash NUMERIC NOT NULL DEFAULT 0.00
            );""")

db.execute("""CREATE TABLE stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                stock TEXT NOT NULL
            );""")

db.execute("""CREATE TABLE owning (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL,
                stock_id INTEGER NOT NULL,
                size INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (stock_id) REFERENCES stocks(id)
            );""")

db.execute("""CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                date DATE NOT NULL,
                user_id INTEGER NOT NULL,
                stock_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                size INTEGER NOT NULL,
                cost_per_share FLOAT NOT NULL,
                cost FLOAT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (stock_id) REFERENCES stocks(id)
            );""")

db.execute("""CREATE TABLE shareholders (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                share FLOAT NOT NULL DEFAULT 0.00,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );""")

db.execute("""CREATE TABLE d_and_w (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                date DATE NOT NULL,
                shareholder_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                amount FLOAT NOT NULL,
                FOREIGN KEY (shareholder_id) REFERENCES shareholders(id)
            );""")

db.execute("""CREATE TABLE dividends (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                ticker_id INTEGER NOT NULL,
                dividend FLOAT NOT NULL,
                FOREIGN KEY (ticker_id) REFERENCES stocks(id)
            );""")


db.execute("""CREATE TABLE div_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                symbol_id INTEGER NOT NULL,
                payment_date INTEGER NOT NULL,
                FOREIGN KEY (symbol_id) REFERENCES stocks(id)
            );""")

