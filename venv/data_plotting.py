import time
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3


class Stockdata:
    def __init__(self):
        # Load historical data from SQLite
        con = sqlite3.connect('marketanalysis_2.db')
        self.df = pd.read_sql_query(
            "SELECT DateID, Open, High, Low, Close FROM STOCK_PLOTTING",
            con
        )
        con.close()

        self.fig = go.Figure(
            data=[go.Candlestick(
                x=self.df['DateID'],
                open=self.df['Open'],
                high=self.df['High'],
                low=self.df['Low'],
                close=self.df['Close'],
                name="Historical price"
            )]
        )

        self.live_trace = go.Scatter(
            x=[self.df['DateID'].iloc[-1]],
            y=[self.df['Close'].iloc[-1]],
            mode="markers",
            marker=dict(size=10),
            name="Live price"
        )

        self.fig.add_trace(self.live_trace)

        self.fig.update_layout(
            title="BTC Live Price (FigureWidget – Real Time)",
            xaxis_title="Date",
            yaxis_title="Price ($)"
        )

        self.fig.show()

        # Start live updating
        self.updated_plotting()

    def updated_plotting(self):
        ticker = yf.Ticker("BTC-USD")

        while True:
            time.sleep(5)  

            data = ticker.history(period="1d", interval="1m")
            if data.empty:
                continue

            current_price = float(data["Close"].iloc[-1])

            with self.fig.batch_update():
                self.fig.layout.shapes = ()
                self.fig.add_hline(
                    y=current_price,
                    line_dash="dash",
                    annotation_text=f"Live: ${current_price:.2f}",
                    annotation_position="top right"
                )
                self.fig.data[1].y = [current_price]

    def time_series(self,a):
        pass


a = input("range: ")
Stockdata(a)


#current_value = []
