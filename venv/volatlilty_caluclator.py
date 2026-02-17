import math
import statistics
import sqlite3


class Volatlity:
    def __init__(self, db_path, ticker):
        """
        db_path: path to SQLite database
        ticker: stock symbol to retrieve prices for
        """
        self.db_path = db_path
        self.ticker = ticker
        self.closing_prices = self._load_closing_prices_from_db()
        self.log_returns = self._calculate_log_returns()

    def _load_closing_prices_from_db(self):
        """
        Loads closing prices from database ordered by date (oldest → newest).
        Supports either:
        1) stock_prices(ticker, close_price, date)
        2) PORTFOLIO + STOCK_PLOTTING schema used in this project
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='stock_prices';"
        )
        has_stock_prices = cursor.fetchone() is not None

        if has_stock_prices:
            cursor.execute(
                """
                SELECT close_price
                FROM stock_prices
                WHERE ticker = ?
                ORDER BY date ASC
                """,
                (self.ticker,),
            )
            prices = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute(
                """
                SELECT s.Close
                FROM STOCK_PLOTTING s
                JOIN PORTFOLIO p ON p.portfolioID = s.portfolioID
                WHERE p.ticker = ?
                ORDER BY s.DateID ASC
                """,
                (self.ticker,),
            )
            prices = [row[0] for row in cursor.fetchall()]

        conn.close()
        if not prices:
            raise ValueError(
                f"No closing prices found for ticker '{self.ticker}' in database '{self.db_path}'."
            )
        return prices

    def _calculate_log_returns(self):
        """
        Compute logarithmic returns from closing prices.
        r_t = ln(P_t / P_(t-1))
        """
        returns = []
        for i in range(1, len(self.closing_prices)):
            if self.closing_prices[i - 1] <= 0 or self.closing_prices[i] <= 0:
                continue
            r = math.log(self.closing_prices[i] / self.closing_prices[i - 1])
            returns.append(r)
        return returns

    def rolling_volatility(self, window=30):
        """
        Calculate rolling historical volatility using a moving window.
        Standard deviation of log returns is calculated inside the window.
        Then annualised.
        """
        volatilities = []

        if len(self.log_returns) < window:
            return []

        for i in range(window, len(self.log_returns) + 1):
            window_slice = self.log_returns[i - window:i]

            if len(window_slice) < 2:
                continue

            std_dev = statistics.stdev(window_slice)

            # Annualise volatility
            annualised_vol = std_dev * math.sqrt(252)
            volatilities.append(annualised_vol)

        return volatilities

    def latest_volatility(self, window=30):
        """
        Convenience method to return the most recent rolling volatility value.
        """
        vols = self.rolling_volatility(window)
        return vols[-1] if vols else None


if __name__ == "__main__":
    # Example usage
    DATABASE_PATH = "marketanalysis_2.db"   # change to your actual database file
    TICKER = "AAPL"               # change to stock you want

    vol = Volatlity(DATABASE_PATH, TICKER)

    print("Loaded prices:", len(vol.closing_prices))
    print("Latest annualised volatility:", vol.latest_volatility())
    print("All rolling volatilities:", vol.rolling_volatility())
