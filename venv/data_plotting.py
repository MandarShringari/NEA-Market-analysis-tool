import sqlite3
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import yfinance as yf
from matplotlib.patches import Rectangle


class StockDataPlotter:
    def __init__(self, db_path="marketanalysis_2.db"):
        self.db_path = db_path
        self.df = pd.DataFrame()
        self.last_status = "Ready"

    def load_from_sqlite(self):
        try:
            con = sqlite3.connect(self.db_path)
            self.df = pd.read_sql_query(
                """
                SELECT DateID, Open, High, Low, Close
                FROM STOCK_PLOTTING
                ORDER BY DateID
                """,
                con,
            )
            con.close()
        except Exception as exc:
            self.df = pd.DataFrame()
            self.last_status = f"SQLite load failed: {exc}"
            return

        if self.df.empty:
            self.last_status = "No rows found in STOCK_PLOTTING."
            return

        self.df["DateID"] = pd.to_datetime(self.df["DateID"], errors="coerce")
        self.df = self.df.dropna(subset=["DateID", "High"]).sort_values("DateID")
        self.last_status = f"Loaded {len(self.df)} rows from SQLite."

    def fetch_from_yfinance(self, ticker):
        try:
            downloaded = yf.Ticker(ticker).history(period="10y", interval="1d")
            if downloaded.empty:
                self.last_status = f"No Yahoo data for ticker: {ticker}"
                return

            downloaded = downloaded.reset_index()
            self.df = downloaded[["Date", "Open", "High", "Low", "Close"]].rename(columns={"Date": "DateID"})
            self.df["DateID"] = pd.to_datetime(self.df["DateID"], errors="coerce")
            self.df = self.df.dropna(subset=["DateID", "High"]).sort_values("DateID")
            self.last_status = f"Loaded {len(self.df)} rows from Yahoo for {ticker}."
        except Exception as exc:
            self.last_status = f"Yahoo load failed: {exc}"

    def get_filtered_data(self, range_label="ALL"):
        if self.df.empty:
            return self.df

        end_date = self.df["DateID"].max()
        label = range_label.upper()

        if label == "1M":
            start_date = end_date - timedelta(days=30)
        elif label == "6M":
            start_date = end_date - timedelta(days=182)
        elif label == "YTD":
            start_date = datetime(end_date.year, 1, 1)
        elif label == "1Y":
            start_date = end_date - timedelta(days=365)
        else:
            return self.df

        return self.df[self.df["DateID"] >= start_date]

    def build_figure(self, range_label="ALL", ticker_label=None):
        fig, ax = plt.subplots(figsize=(9, 5), dpi=100)

        if self.df.empty:
            ax.set_title("No data available")
            return fig

        plot_df = self.get_filtered_data(range_label)
        if plot_df.empty:
            ax.set_title("No data available for selected range")
            return fig

        date_nums = mdates.date2num(plot_df["DateID"].dt.to_pydatetime())
        if len(date_nums) > 1:
            candle_width = min(0.8, (date_nums[1] - date_nums[0]) * 0.7)
        else:
            candle_width = 0.6

        for x, open_p, high_p, low_p, close_p in zip(
            date_nums,
            plot_df["Open"],
            plot_df["High"],
            plot_df["Low"],
            plot_df["Close"],
        ):
            up_candle = close_p >= open_p
            color = "green" if up_candle else "red"

            ax.vlines(x, low_p, high_p, color=color, linewidth=1)
            body_bottom = min(open_p, close_p)
            body_height = abs(close_p - open_p)
            if body_height == 0:
                body_height = 0.001

            rect = Rectangle(
                (x - candle_width / 2, body_bottom),
                candle_width,
                body_height,
                facecolor=color,
                edgecolor=color,
                alpha=0.75,
            )
            ax.add_patch(rect)

        title_ticker = f"{ticker_label} " if ticker_label else ""
        ax.set_title(f"{title_ticker}Candlestick Chart ({range_label.upper()})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig

    def show_plot(self, range_label="ALL", ticker="AAPL"):
        self.load_from_sqlite()
        if self.df.empty:
            self.fetch_from_yfinance(ticker)

        fig = self.build_figure(range_label=range_label, ticker_label=ticker)
        fig.show()
        plt.show()


if __name__ == "__main__":
    plotter = StockDataPlotter()
    plotter.show_plot(range_label="ALL", ticker="AAPL")
