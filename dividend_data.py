import pandas as pd
import yfinance as yf
import streamlit as st
import calendar

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def load_dividend_kings_data():
    """
    Load the predefined Dividend Kings data
    """
    # Create dataframe with the 12 Dividend Kings
    data = {
        'Company': [
            'Procter & Gamble', 'Johnson & Johnson', 'Coca-Cola', 'Colgate-Palmolive',
            '3M Company', 'Target Corporation', 'Emerson Electric', 'Stanley Black & Decker',
            'Illinois Tool Works', 'Genuine Parts Company', 'Hormel Foods', 'Lancaster Colony'
        ],
        'Ticker': [
            'PG', 'JNJ', 'KO', 'CL',
            'MMM', 'TGT', 'EMR', 'SWK',
            'ITW', 'GPC', 'HRL', 'LANC'
        ],
        'Years of Growth': [
            68, 62, 62, 60,
            65, 56, 66, 56,
            58, 67, 57, 60
        ],
        'Payout Month': [
            'January', 'February', 'March', 'April',
            'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December'
        ],
        'Description': [
            'Consumer goods giant with stable cash flow',
            'Healthcare conglomerate with diverse revenue streams',
            'Beverage giant with global presence',
            'Consumer products leader in oral care',
            'Industrial conglomerate with diverse product portfolio',
            'Retail giant with strong consumer presence',
            'Industrial technology and engineering company',
            'Tools and storage solutions provider',
            'Diversified manufacturer of industrial products',
            'Automotive and industrial parts distributor',
            'Food products manufacturer with strong brands',
            'Specialty food manufacturer with focus on quality'
        ]
    }
    
    return pd.DataFrame(data)

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_stock_data(tickers):
    """
    Fetch current stock data using yfinance
    
    Args:
        tickers (list): List of stock tickers
    
    Returns:
        dict: Dictionary with stock data
    """
    stock_data = {}
    
    try:
        # Fetch data for all tickers at once
        yf_data = yf.download(tickers, period="1d")
        
        # Fetch additional info for each ticker
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get latest price
                price = yf_data['Close'][ticker].iloc[-1] if not yf_data.empty else 0
                
                # Get dividend data
                try:
                    annual_dividend = info.get('trailingAnnualDividendRate', 0)
                    dividend_yield = info.get('trailingAnnualDividendYield', 0) * 100
                except:
                    # Fallback to calculate from history if info not available
                    hist = stock.history(period="1y")
                    if not hist.empty and 'Dividends' in hist.columns:
                        dividends = hist[hist['Dividends'] > 0]['Dividends']
                        annual_dividend = dividends.sum() if not dividends.empty else 0
                        dividend_yield = (annual_dividend / price * 100) if price > 0 else 0
                    else:
                        annual_dividend = 0
                        dividend_yield = 0
                
                # Store the data
                stock_data[ticker] = {
                    'price': price,
                    'dividend': annual_dividend,
                    'yield': dividend_yield,
                    'name': info.get('longName', ticker),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', 0)
                }
            except Exception as e:
                st.warning(f"Error fetching detailed data for {ticker}: {e}")
                # Add placeholder data
                stock_data[ticker] = {
                    'price': yf_data['Close'][ticker].iloc[-1] if not yf_data.empty else 100,
                    'dividend': 3.0,  # Placeholder annual dividend
                    'yield': 3.0,     # Placeholder yield percentage
                    'name': ticker,
                    'sector': 'N/A',
                    'industry': 'N/A',
                    'market_cap': 0,
                    'pe_ratio': 0
                }
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        
        # Create placeholder data if API fails
        for ticker in tickers:
            stock_data[ticker] = {
                'price': 100.0,
                'dividend': 3.0,
                'yield': 3.0,
                'name': ticker,
                'sector': 'Sample Sector',
                'industry': 'Sample Industry',
                'market_cap': 1000000000,
                'pe_ratio': 15
            }
    
    return stock_data

@st.cache_data(ttl=86400)  # Cache data for 24 hours
def get_dividend_history(ticker, years=10):
    """
    Get dividend history for a specific ticker
    
    Args:
        ticker (str): Stock ticker
        years (int): Number of years to look back
    
    Returns:
        pd.DataFrame: Dividend history
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period=f"{years}y")
        
        # Extract dividends
        dividends = history[history['Dividends'] > 0][['Dividends']]
        
        if dividends.empty:
            # Return empty dataframe with proper columns
            return pd.DataFrame(columns=['Date', 'Dividend'])
        
        # Reset index to get date as column
        dividends = dividends.reset_index()
        
        # Convert to proper format
        dividends['Date'] = dividends['Date'].dt.date
        dividends = dividends.rename(columns={'Dividends': 'Dividend'})
        
        return dividends
    except Exception as e:
        st.error(f"Error fetching dividend history for {ticker}: {e}")
        
        # Generate sample data
        import numpy as np
        from datetime import datetime, timedelta
        
        # Create sample dates and growing dividends
        dates = [(datetime.now() - timedelta(days=90*i)).date() for i in range(4*years)]
        base_dividend = 0.5
        growth_rate = 1.07  # 7% annual growth
        
        dividends = []
        for i, date in enumerate(dates):
            year = i // 4
            dividend = base_dividend * (growth_rate ** year)
            dividends.append(dividend)
        
        # Create dataframe
        df = pd.DataFrame({
            'Date': dates,
            'Dividend': dividends
        })
        
        return df