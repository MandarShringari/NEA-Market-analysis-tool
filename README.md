# NEA Market Analysis Tool

This project is a Python-based market analysis and stock prediction system developed for my A-Level Computer Science NEA.

The application retrieves historical stock data, stores it in a structured database, and uses a linear regression model to predict future closing prices. It also generates visualisations to support analysis of market trends.

---

## Overview

The system performs the following tasks:

- Retrieves and stores historical stock data
- Manages data using a relational database
- Trains a linear regression model on historical prices
- Predicts closing prices for the next 7 days
- Displays graphical representations of trends and predictions
- Updates stored data when new information becomes available

---

## Technologies Used

- Python  
- Pandas  
- NumPy  
- Matplotlib  
- Scikit-learn  
- SQLite  

---

## Project Structure
NEA Project/
│
├── data/              Data storage
├── database/          Database files
├── models/            Machine learning models
├── scripts/           Data processing and retrieval
├── main.py            Program entry point
├── README.md
└── .gitignore
---

## Installation

Clone the repository:
git clone https://github.com/MandarShringari/NEA-Market-analysis-tool.git
cd NEA-Market-analysis-tool

Install required packages:
pip install pandas numpy matplotlib scikit-learn

---

## Running the Program
The program will retrieve data, update the database, train the model, generate predictions, and display results.

---

## Machine Learning Approach

The system uses linear regression to model the relationship between time and closing price. Historical data is used to train the model, which is then applied to forecast short-term future values.

---

## Purpose

The aim of this project is to demonstrate practical application of:

- data management  
- machine learning  
- predictive modelling  
- financial data analysis  

---

## Author

Mandar Shringari  
A-Level Computer Science NEA Project