import tkinter as tk
from tkinter import *
import sqlite3
from datetime import datetime

class MarketAnalysisApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Market analysis tool")
        self.geometry('650x650')

        self.start_page = StartPage(self)
        self.start_page.pack(fill="both", expand=True)
        
    def show_login_page(self):
        self.start_page.pack_forget()
        self.Login_page = Loginpage(self)
        self.Login_page.pack(fill="both", expand=True)


class StartPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.welcome = tk.Label(self, text="Hello, Welcome", font=("Arial", 30))
        self.sign_button = tk.Button(self, text="Sign up", width=20, height=2, font=("Arial", 20))
        self.login_button = tk.Button(self, text="Login", width=20, height=2, font=("Arial", 20), command=self.goto_loginpage)
        
        self.welcome.pack(padx=50, pady=50)
        self.sign_button.pack(padx=25, pady=25)
        self.login_button.pack(padx=25, pady=25)
       
    def goto_loginpage(self):
        self.master.show_login_page()


class Loginpage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.user_username = tk.StringVar()
        self.user_password = tk.StringVar()

        self.username_label = tk.Label(self, text="Username", font=("Arial", 20))
        self.input_username = tk.Entry(self, textvariable=self.user_username, font=("Arial", 20))

        self.password_label = tk.Label(self, text="Password", font=("Arial", 20))
        self.input_password = tk.Entry(self, textvariable=self.user_password, font=("Arial", 20), show="*")

        self.login_button = tk.Button(self, text="Login", font=("Arial", 20), command=self.validate_login)

        self.username_label.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.input_username.grid(column=0, row=1, padx=10, pady=10, sticky="w")
        self.password_label.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.input_password.grid(column=0, row=3, padx=10, pady=10, sticky="w")
        self.login_button.grid(column=0, row=4, padx=10, pady=20)

    def validate_login(self):
        username = self.user_username.get()
        password = self.user_password.get()
        if username and password:
            print(f"Login successful for user: {username}")
        else:
            print("Please enter both username and password.")



class DatabaseManager:
    def __init__(self):
        super().__init__()
        self.connect_db = sqlite3.connect('Marketanalysis.db')
        self.cursor_obj = self.connect_db.cursor()

        self.cursor_obj.execute("PRAGMA foreign_keys = ON;")

        self.cursor_obj.execute(""" 
        CREATE TABLE IF NOT EXISTS USER(
            userID INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            salt INTEGER NOT NULL,
            hashedPassword TEXT NOT NULL
        );
        """)
        self.cursor_obj.execute(""" 
        CREATE TABLE IF NOT EXISTS PORTFOLIO(
            stockID INTEGER PRIMARY KEY AUTOINCREMENT,
            userID INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            stockName TEXT,
            price FLOAT,
            field TEXT,
            volatility FLOAT,
            timestamp TIMESTAMP,
            FOREIGN KEY (userID) REFERENCES USER(userID)
        );
        """)

        self.cursor_obj.execute(""" 
        CREATE TABLE IF NOT EXISTS STOCK_HISTORY(
            historyID INTEGER PRIMARY KEY AUTOINCREMENT,
            stockID INTEGER NOT NULL,
            closingprice FLOAT NOT NULL,
            date TEXT,
            predictedprice FLOAT
        );
        """)






market_analysis = MarketAnalysisApp()
market_analysis.mainloop()

