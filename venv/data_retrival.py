import sqlite3
import yfinance as yf

class DataRetrieval:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connect_db = sqlite3.connect(db_path)
        self.cursor = self.connect_db.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def stock_search(self, ticker):
        query = """
        SELECT * FROM STOCK_LIST
        WHERE tickername LIKE ? OR companyname LIKE ?;
        """
        like_value = f"%{ticker}%"

        # Parameterised queries were used to improve security
        self.cursor.execute(query, (like_value, like_value))
        results = self.cursor.fetchall()

        # Use ticker from database result instead of raw user input
        if results:
            db_ticker = results[0][1]
            self.company = yf.Ticker(db_ticker)
            try:
                self.company_name = self.company.info.get("symbol", None)
            except Exception:
                self.company_name = None
        else:
            self.company_name = None

        return results

    def create_or_get_user(self, username):
        self.cursor.execute(
            "SELECT userID FROM USER WHERE username = ?;",
            (username,)
        )
        user = self.cursor.fetchone()

        if user:
            return user[0]

        self.cursor.execute(
            "INSERT INTO USER (username, salt, hashedPassword) VALUES (?, ?, ?);",
            (username, 0, "placeholder")
        )
        self.connect_db.commit()
        return self.cursor.lastrowid

    def ensure_portfolio_exists(self, portfolioID, user_id, ticker):
        self.cursor.execute(
            "SELECT 1 FROM PORTFOLIO WHERE portfolioID = ?;",
            (portfolioID,)
        )
        exists = self.cursor.fetchone()

        if exists:
            return

        self.cursor.execute(
            """
            INSERT INTO PORTFOLIO (portfolioID, userID, ticker, stockName)
            VALUES (?, ?, ?, ?);
            """,
            (portfolioID, user_id, ticker, ticker)
        )

        self.connect_db.commit()

    def insert_historical_data(self, portfolioID, user_id, ticker):
        # Ensure FK target exists before inserting historical data
        self.ensure_portfolio_exists(portfolioID, user_id, ticker)
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

q = DataRetrieval(db_path)

username = input("Enter username: ")
user_id = q.create_or_get_user(username)

search_term = input("Enter ticker or company name to search: ")
results = q.stock_search(search_term)

if not results:
    print("No matching stocks found.")
    q.close()
    exit()

print("\nSearch results:")
for i, row in enumerate(results):
    print(f"{i}: Ticker={row[1]}, Company={row[2]}")

choice = int(input("Select a stock by number: "))
selected_ticker = results[choice][1]

portfolio_id = int(input("Enter portfolio ID to use: "))

q.insert_historical_data(
    portfolioID=portfolio_id,
    user_id=user_id,
    ticker=selected_ticker
)

print("Stock added and historical data stored.")
q.close()
