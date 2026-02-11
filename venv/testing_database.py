'''import time
import pandas as pd 
import yfinance as yf 
import plotly.graph_objects as go
import sqlite3
#basic idea of sketching would work 
class Stockdata ():
    def __init__(self):
        con = sqlite3.connect('marketanalysis_2.db')
        self.df = pd.read_sql_query("SELECT DateID,Open,High,Low,Close FROM STOCK_PLOTTING",con)
        self.fig = go.Figure(data=[go.Candlestick(x=self.df['DateID'],
                open=self.df['Open'],
                high=self.df['High'],
                low=self.df['Low'],
                close=self.df['Close'])])
        self.fig.show()
    def updated_plotting(self):
        while True:
           time.sleep(1)
           target = yf.Ticker("AAPL")
           self.current_price = target.fast_info['last_price']'''

'''import sqlite3
import yfinance as yf

class DataRetrieval:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connect_db = sqlite3.connect(db_path)
        self.cursor = self.connect_db.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def stock_search(self, ticker):
        query = """SELECT * FROM STOCK_LIST WHERE tickername LIKE ? OR companyname LIKE ?;"""
        like_value = f"%{ticker}%"
        #Parameterised queries were used to improve security and prevent malicious SQL input.
        self.cursor.execute(query, (like_value, like_value))
        results = self.cursor.fetchall()
        # Use ticker from database result instead of raw user input
        if results:
            db_ticker = results[0][1]  
            self.company = yf.Ticker(db_ticker)
            try:
                # prepares an API request and safely retrieves the ticker symbol
                self.company_name = self.company.info.get('symbol', None)
            except Exception:
                self.company_name = None
        else:
            self.company_name = None
        return results

    def ensure_portfolio_exists(self, portfolioID, ticker):
        # Check if portfolio exists
        self.cursor.execute(
            "SELECT 1 FROM PORTFOLIO WHERE portfolioID = ?;",
            (portfolioID,)
        )
        exists = self.cursor.fetchone()

        if exists:
            return

        # Ensure at least one user exists (minimal safe default)
        self.cursor.execute("SELECT userID FROM USER LIMIT 1;")
        user = self.cursor.fetchone()

        if user is None:
            self.cursor.execute(
                "INSERT INTO USER (username, salt, hashedPassword) VALUES (?, ?, ?);",
                ("default_user", 0, "placeholder")
            )
            user_id = self.cursor.lastrowid
        else:
            user_id = user[0]

        # Create the missing portfolio
        self.cursor.execute(
            """
            INSERT INTO PORTFOLIO (userID, ticker, stockName)
            VALUES (?, ?, ?);
            """,
            (user_id, ticker, ticker)
        )

        self.connect_db.commit()

    def insert_historical_data(self, portfolioID, ticker):
        # Ensure FK target exists before inserting historical data
        self.ensure_portfolio_exists(portfolioID, ticker)
        # Use yfinance Ticker object (more stable than download)
        ticker_obj = yf.Ticker(ticker)

        # Get historical price data
        hist = ticker_obj.history(period="1y", interval="1d")

        # Guard against empty results
        if hist.empty:
            raise ValueError(f"No historical data returned for ticker: {ticker}")

        insert_query = """
            INSERT OR IGNORE INTO STOCK_PLOTTING
            (DateID, portfolioID, Open, Close, High, Low, Volume)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """

        rows = []

        for date, row in hist.iterrows():
            rows.append((
                date.date(),                 # DateID
                int(portfolioID),             # portfolioID (FK + PK)
                float(row["Open"]),
                float(row["Close"]),
                float(row["High"]),
                float(row["Low"]),
                float(row["Volume"])
            ))

        try:
            self.cursor.executemany(insert_query, rows)
            self.connect_db.commit()
            print("Inserted/ignored rows attempted:", len(rows))

            self.cursor.execute(
                "SELECT COUNT(*) FROM STOCK_PLOTTING WHERE portfolioID=?;",
                (portfolioID,)
            )
            print("Rows now in DB for portfolio:", self.cursor.fetchone()[0])

        except sqlite3.IntegrityError as e:
            raise RuntimeError(f"Insert failed due to constraints: {e}")

    def close(self):
        self.connect_db.close()
        
        

db_path = "/Users/veereshshringari/Documents/Mandar Project /NEA Project/marketanalysis_2.db"

# Tables MUST already exist before this runs
q = DataRetrieval(db_path)
q.insert_historical_data(portfolioID=1, ticker="AAPL")
q.close()'''

'''import hashlib
import secrets


class PasswordHasher:
    """
    Handles password hashing, salting, and verification using SHA-256.
    """

    def __init__(self, rounds: int = 6):
        self.rounds = rounds

    def generate_salt(self) -> str:
        """
        Generates a random 16-bit salt (2 bytes) represented as hexadecimal.
        """
        return secrets.token_hex(2)

    def sha256_hash(self, data: bytes) -> bytes:
        """
        Applies SHA-256 hashing to input bytes.
        """
        return hashlib.sha256(data).digest()

    def mix_state(self, state: int, value: int) -> int:
        """
        Performs bitwise mixing to enhance the avalanche effect.
        """
        # XOR manipulation
        state ^= value

        # Bit rotation (left rotate by 7 bits)
        state = ((state << 7) | (state >> (64 - 7))) & ((1 << 64) - 1)

        # Multiplication introduces diffusion
        state = (state * 0x9E3779B97F4A7C15) & ((1 << 64) - 1)

        return state

    def hash_password(self, password: str, salt: str) -> str:
        """
        Hashes a password using SHA-256 combined with salt and multiple rounds
        of bitwise manipulation.
        """
        combined = (password + salt).encode("utf-8")
        hash_bytes = self.sha256_hash(combined)

        # Convert first 8 bytes to 64-bit state
        state = int.from_bytes(hash_bytes[:8], byteorder="big")

        for _ in range(self.rounds):
            for byte in hash_bytes:
                state = self.mix_state(state, byte)

            hash_bytes = self.sha256_hash(state.to_bytes(8, byteorder="big"))

        return f"{state:016x}"

    def create_password_record(self, password: str) -> dict:
        """
        Creates a secure password record to be stored in the database.
        """
        salt = self.generate_salt()
        hashed_password = self.hash_password(password, salt)

        return {
            "salt": salt,
            "rounds": self.rounds,
            "hash": hashed_password
        }

    def verify_password(self, input_password: str, stored_salt: str, stored_hash: str) -> bool:
        """
        Verifies an entered password against the stored hash.
        """
        return self.hash_password(input_password, stored_salt) == stored_hash
    
import sqlite3
import re
import secrets
from hashingalgorithm import PasswordHasher


DB_PATH = "marketanalysis_2.db"


class AuthTester:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.hasher = PasswordHasher(rounds=6)
        self.session_token = None

    # ---------------- VALIDATION ----------------
    def validate_signup(self, username, password, confirm):
        if not username or not password or not confirm:
            return "Please fill in all fields."

        if not re.match(r"^\w+$", username):
            return "Username can only contain letters, numbers, and underscores."

        self.cursor.execute(
            "SELECT 1 FROM USER WHERE username = ?;",
            (username,)
        )
        if self.cursor.fetchone():
            return "This username is already taken."

        if len(password) < 8:
            return "Password must be at least 8 characters long."

        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            return "Password must include letters and numbers."

        if password != confirm:
            return "Passwords do not match."

        return None

    # ---------------- SIGN UP ----------------
    def signup(self):
        print("\n=== SIGN UP ===")
        username = input("Username: ")
        password = input("Password: ")
        confirm = input("Confirm Password: ")

        error = self.validate_signup(username, password, confirm)
        if error:
            print(error)
            return

        record = self.hasher.create_password_record(password)

        self.cursor.execute(
            """
            INSERT INTO USER (username, salt, hashedPassword)
            VALUES (?, ?, ?);
            """,
            (username, record["salt"], record["hash"])
        )
        self.conn.commit()

        print("Account created successfully ✅")

    # ---------------- LOGIN ----------------
    def login(self):
        print("\n=== LOGIN ===")
        username = input("Username: ")
        password = input("Password: ")

        if not username or not password:
            print("Please fill in all fields.")
            return

        self.cursor.execute(
            """
            SELECT salt, hashedPassword
            FROM USER
            WHERE username = ?;
            """,
            (username,)
        )
        result = self.cursor.fetchone()

        if not result:
            print("Invalid username or password ❌")
            return

        salt, stored_hash = result

        if self.hasher.verify_password(password, salt, stored_hash):
            self.session_token = secrets.token_hex(16)
            print("Login successful ✅")
            print(f"Session token created: {self.session_token}")
            print("Redirecting to portfolio page...")
        else:
            print("Invalid username or password ❌")

    def close(self):
        self.conn.close()


# ---------------- RUN TESTER ----------------
if __name__ == "__main__":
    auth = AuthTester()

    while True:
        print("\n1. Sign Up")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose option: ")

        if choice == "1":
            auth.signup()
        elif choice == "2":
            auth.login()
        elif choice == "3":
            auth.close()
            print("Program closed.")
            break
        else:
            print("Invalid option.")'''

from tkinter import *
import plotly.offline as py
import plotly.graph_objs as go 

from datetime import datetime
from pandas_datareader import data as web


mGui = Tk()

mGui.geometry('651x700+51+51')
mGui.title('Plotly at Tkinter')

df = web.DataReader("AAPL", 'yahoo',
                    datetime(2007, 10, 1),
                    datetime(2016, 7, 11))

trace = go.Scatter(x=df.index,
                   y=df.High)


data = [trace]
layout = dict(
    title='Time series with range slider and selectors',
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label='1m',
                     step='month',
                     stepmode='backward'),
                dict(count=6,
                     label='6m',
                     step='month',
                     stepmode='backward'),
                dict(count=1,
                    label='YTD',
                    step='year',
                    stepmode='todate'),
                dict(count=1,
                    label='1y',
                    step='year',
                    stepmode='backward'),
                dict(step='all')
            ])
        ),
        rangeslider=dict(),
        type='date'
    )
)

fig = go.Figure(data=data, layout=layout)
fig.show()

mGui.mainloop()