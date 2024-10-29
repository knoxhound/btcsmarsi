import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import csv

def fetch_bitcoin_data():
    """Fetch Bitcoin historical data from Yahoo Finance"""
    btc = yf.Ticker("BTC-USD")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=300)
    df = btc.history(start=start_date, end=end_date)
    return df

def calculate_indicators(df):
    """Calculate technical indicators: 50-day SMA, 200-day SMA, and RSI"""
    # Calculate SMAs
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    
    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

def generate_signals(df, rsi_threshold_upper=70, rsi_threshold_lower=30):
    """Generate trading signals based on SMA crossover and RSI"""
    df['Signal'] = 0
    df['Position_Type'] = 'None'  # Track if we're in a long or short position
    current_position = 'None'
    
    for i in range(1, len(df)):
        # First check for SMA crossover signals
        if df['SMA50'].iloc[i] > df['SMA200'].iloc[i] and df['SMA50'].iloc[i-1] <= df['SMA200'].iloc[i-1]:
            df.iloc[i, df.columns.get_loc('Signal')] = 1  # Golden Cross
            current_position = 'Long'
        elif df['SMA50'].iloc[i] < df['SMA200'].iloc[i] and df['SMA50'].iloc[i-1] >= df['SMA200'].iloc[i-1]:
            df.iloc[i, df.columns.get_loc('Signal')] = -1  # Death Cross
            current_position = 'Short'
            
        # Then check for RSI exit conditions
        if current_position == 'Long' and df['RSI'].iloc[i] > rsi_threshold_upper:
            df.iloc[i, df.columns.get_loc('Signal')] = -1  # Exit long position
            current_position = 'None'
        elif current_position == 'Short' and df['RSI'].iloc[i] < rsi_threshold_lower:
            df.iloc[i, df.columns.get_loc('Signal')] = 1  # Exit short position
            current_position = 'None'
            
        df.iloc[i, df.columns.get_loc('Position_Type')] = current_position
    
    return df

def calculate_indicators(df):
    """Calculate technical indicators: 50-day SMA, 200-day SMA, and RSI"""
    # Calculate SMAs
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    
    # Calculate RSI with more detailed implementation
    delta = df['Close'].diff()
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    loss = abs(loss)
    
    # First average of gains and losses
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    
    # Calculate subsequent averages using the RSI formula
    for i in range(14, len(df)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * 13 + gain.iloc[i]) / 14
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * 13 + loss.iloc[i]) / 14
    
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df