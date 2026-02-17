import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class Regression:
    def __init__ (self):
        self.conn = sqlite3.connect("marketanalysis_2.db")
        # links to the data in the database 
        self.portfolio_id = 1  
        self.query = """
        SELECT DateID, Close
        FROM STOCK_PLOTTING
        WHERE portfolioID = ?
        ORDER BY DateID ASC
        """
    def preprocessing (self):
        self.df = pd.read_sql_query(self.query, self.conn, params=(self.portfolio_id,))
        self.conn.close()
        if self.df.empty:
            raise ValueError("No stock data found for the selected portfolio.")
        self.df["DateID"] = pd.to_datetime(self.df["DateID"], errors="coerce")
        self.df = self.df.dropna(subset=["DateID"]).reset_index(drop=True)
        self.df['Prev_Close'] = self.df['Close'].shift(1)
        self.df = self.df.dropna().reset_index(drop=True)
        if len(self.df) < 2:
            raise ValueError("Not enough rows to train the regression model.")
        
    def model_training(self):
        X = self.df[['Prev_Close']].values
        y = self.df['Close'].values
        split_index = int(len(X) * 0.8)
        if split_index == 0 or split_index >= len(X):
            raise ValueError("Not enough data to create train/test split.")
        X_train, X_test = X[:split_index], X[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]

        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        print("Model Evaluation")
        print(f"Mean Squared Error: {mse:.4f}")
        print(f"R^2 Score: {r2:.4f}")

    def closingprice_predict(self):
        self.future_days = 7
        self.future_predictions = []
        last_close = self.df['Close'].iloc[-1]
        for _ in range(self.future_days):
            next_price = self.model.predict(np.array([[last_close]]))[0]
            self.future_predictions.append(next_price)
            last_close = next_price  # recursive prediction

    def plotting_prediction(self):
        plt.figure()

        # plot historical data using DateID
        plt.plot(self.df['DateID'], self.df['Close'], label="Historical Closing Price")

        # Generate future dates from the final observed date.
        last_date = self.df['DateID'].iloc[-1]
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=self.future_days,
            freq="D"
        )

        plt.plot(
            future_dates,
            self.future_predictions,
            linestyle='dashed',
            label="Predicted Closing Price (7 Days)"
        )

        plt.xlabel("Date")
        plt.ylabel("Closing Price")
        plt.title("Stock Closing Price Prediction (7 Days Ahead)")
        plt.legend()
        plt.grid(True)
        plt.show()

        print("\nNext 7 Days Predicted Closing Prices:")
        for i, price in enumerate(self.future_predictions, start=1):
            print(f"Day {i}: {price:.2f}")


if __name__ == "__main__":
    model = Regression()
    model.preprocessing()
    model.model_training()
    model.closingprice_predict()
    model.plotting_prediction()
