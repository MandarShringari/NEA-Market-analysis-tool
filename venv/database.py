import sqlite3
class DatabaseManager:
    def __init__(self):
        super().__init__()

        self.connect_db = sqlite3.connect('marketanalysis_2.db')
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
            portfolioID INTEGER PRIMARY KEY AUTOINCREMENT,
            userID INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            stockName TEXT,
            currentPrice REAL,
            volatility REAL,
            timestamp TIMESTAMP,
            FOREIGN KEY (userID) REFERENCES USER(userID)
        );
        """)

        self.cursor_obj.execute("""
        CREATE TABLE IF NOT EXISTS STOCK_PLOTTING(
            DateID DATE NOT NULL,
            portfolioID INTEGER NOT NULL,
            Open REAL NOT NULL,
            Close REAL NOT NULL,
            High REAL NOT NULL,
            Low REAL NOT NULL,
            Volume REAL NOT NULL,
            PRIMARY KEY (DateID, portfolioID),
            FOREIGN KEY (portfolioID) REFERENCES PORTFOLIO(portfolioID)
        );
        """)

        self.cursor_obj.execute("""
        CREATE TABLE IF NOT EXISTS STOCK_LIST(
            stockListID INTEGER PRIMARY KEY AUTOINCREMENT,
            tickername TEXT NOT NULL,
            companyname TEXT NOT NULL
        );
        """)

        # Clear all data from tables (reset database content)
        # Order matters because of foreign keys
        self.cursor_obj.execute("DELETE FROM STOCK_PLOTTING;")
        self.cursor_obj.execute("DELETE FROM PORTFOLIO;")
        self.cursor_obj.execute("DELETE FROM USER;")
        self.cursor_obj.execute("DELETE FROM STOCK_LIST;")

        # Re-seed STOCK_LIST with commonly used tickers (stocks, indices, commodities, crypto)
        self.cursor_obj.executemany(
            "INSERT OR IGNORE INTO STOCK_LIST (tickername, companyname) VALUES (?, ?);",
            [
                # Major US stocks
                ("AAPL", "Apple Inc"),
                ("MSFT", "Microsoft Corporation"),
                ("GOOGL", "Alphabet Inc"),
                ("AMZN", "Amazon.com Inc"),
                ("META", "Meta Platforms Inc"),
                ("NVDA", "NVIDIA Corporation"),
                ("TSLA", "Tesla Inc"),
                ("BRK-B", "Berkshire Hathaway"),
                ("JPM", "JPMorgan Chase"),
                ("V", "Visa Inc"),

                # UK / EU stocks
                ("BP", "BP plc"),
                ("HSBA", "HSBC Holdings"),
                ("SHEL", "Shell plc"),
                ("ULVR", "Unilever"),
                ("AZN", "AstraZeneca"),
                ("RIO", "Rio Tinto"),
                ("BHP", "BHP Group"),
                ("NESN.SW", "Nestlé"),

                # Indices
                ("^GSPC", "S&P 500"),
                ("^DJI", "Dow Jones Industrial Average"),
                ("^IXIC", "NASDAQ Composite"),
                ("^FTSE", "FTSE 100"),
                ("^N225", "Nikkei 225"),

                # Commodities
                ("GC=F", "Gold Futures"),
                ("SI=F", "Silver Futures"),
                ("CL=F", "Crude Oil"),
                ("NG=F", "Natural Gas"),

                # Forex
                ("GBPUSD=X", "GBP/USD"),
                ("EURUSD=X", "EUR/USD"),
                ("USDJPY=X", "USD/JPY"),

                # Crypto
                ("BTC-USD", "Bitcoin"),
                ("ETH-USD", "Ethereum"),
                ("BNB-USD", "Binance Coin"),
                ("SOL-USD", "Solana"),
                ("XRP-USD", "Ripple"),
                ("ADA-USD", "Cardano")
            ]
        )

        self.connect_db.commit()
 
DatabaseManager()