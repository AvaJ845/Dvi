import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Define the function directly in this file to avoid import issues
def calculate_dividend_growth_stats(dividend_history):
    """
    Calculate dividend growth statistics from dividend history
    
    Args:
        dividend_history (pd.DataFrame): DataFrame with dividend history data
                                        Expected to have 'date' and 'dividend' columns
    
    Returns:
        dict: Dictionary containing growth statistics
    """
    # If dividend history is empty, return zeros
    if dividend_history is None or len(dividend_history) == 0:
        return {
            '1yr_growth': 0,
            '3yr_growth': 0,
            '5yr_growth': 0,
            '10yr_growth': 0,
            'cagr': 0
        }
    
    # Sort by date
    dividend_history = dividend_history.sort_values('date')
    
    # Get the most recent dividend
    latest_dividend = dividend_history['dividend'].iloc[-1]
    
    # Calculate growth rates for different periods
    growth_stats = {}
    
    # 1-year growth
    try:
        one_year_ago = dividend_history['date'].iloc[-1] - pd.DateOffset(years=1)
        one_year_dividend = dividend_history[dividend_history['date'] <= one_year_ago]['dividend'].iloc[-1]
        growth_stats['1yr_growth'] = (latest_dividend / one_year_dividend - 1) * 100
    except (IndexError, KeyError):
        growth_stats['1yr_growth'] = 0
    
    # 3-year growth
    try:
        three_years_ago = dividend_history['date'].iloc[-1] - pd.DateOffset(years=3)
        three_year_dividend = dividend_history[dividend_history['date'] <= three_years_ago]['dividend'].iloc[-1]
        growth_stats['3yr_growth'] = (latest_dividend / three_year_dividend - 1) * 100
    except (IndexError, KeyError):
        growth_stats['3yr_growth'] = 0
    
    # 5-year growth
    try:
        five_years_ago = dividend_history['date'].iloc[-1] - pd.DateOffset(years=5)
        five_year_dividend = dividend_history[dividend_history['date'] <= five_years_ago]['dividend'].iloc[-1]
        growth_stats['5yr_growth'] = (latest_dividend / five_year_dividend - 1) * 100
    except (IndexError, KeyError):
        growth_stats['5yr_growth'] = 0
    
    # 10-year growth
    try:
        ten_years_ago = dividend_history['date'].iloc[-1] - pd.DateOffset(years=10)
        ten_year_dividend = dividend_history[dividend_history['date'] <= ten_years_ago]['dividend'].iloc[-1]
        growth_stats['10yr_growth'] = (latest_dividend / ten_year_dividend - 1) * 100
    except (IndexError, KeyError):
        growth_stats['10yr_growth'] = 0
    
    # Calculate CAGR (Compound Annual Growth Rate)
    try:
        first_date = dividend_history['date'].iloc[0]
        last_date = dividend_history['date'].iloc[-1]
        years = (last_date - first_date).days / 365.25
        first_dividend = dividend_history['dividend'].iloc[0]
        
        if years > 0 and first_dividend > 0:
            growth_stats['cagr'] = ((latest_dividend / first_dividend) ** (1 / years) - 1) * 100
        else:
            growth_stats['cagr'] = 0
    except (IndexError, KeyError, ZeroDivisionError):
        growth_stats['cagr'] = 0
    
    return growth_stats

def display_stock_detail(stock_row, stock_data=None):
    """
    Display detailed information about a specific stock
    
    Args:
        stock_row (pd.Series): Row of stock data from portfolio DataFrame
        stock_data (dict, optional): Additional stock data from API
    """
    # Create columns for basic information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Stock Basics")
        st.metric("Company", stock_row['Company'])
        st.metric("Ticker", stock_row['Ticker'])
        
        # Years of dividend growth
        if 'Years of Growth' in stock_row:
            st.metric("Years of Dividend Growth", stock_row['Years of Growth'])
    
    with col2:
        st.markdown("### Current Investment Details")
        st.metric("Investment", f"${stock_row['Investment']:,.2f}")
        st.metric("Shares", f"{stock_row['Shares']:,.2f}")
        st.metric("Current Price", f"${stock_row['Current Price']:,.2f}")
    
    # Dividend and Income Information
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### Dividend Information")
        st.metric("Current Yield", f"{stock_row['Current Yield']:.2f}%")
        st.metric("Annual Income", f"${stock_row['Annual Income']:,.2f}")
        
        # Payout month if available
        if 'Payout Month' in stock_row:
            st.metric("Typical Payout Month", stock_row['Payout Month'])
    
    with col4:
        # Display notes if available
        if 'Notes' in stock_row and stock_row['Notes']:
            st.markdown("### Additional Notes")
            st.write(stock_row['Notes'])
    
    # Fetch dividend history
    try:
        from dividend_data import get_dividend_history
        
        # Get dividend history
        dividend_history = get_dividend_history(stock_row['Ticker'])
        
        # Calculate growth statistics
        growth_stats = calculate_dividend_growth_stats(dividend_history)
        
        # Dividend Growth Statistics
        st.markdown("### Dividend Growth Statistics")
        
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.metric("1-Year Growth", f"{growth_stats['1yr_growth']:.2f}%")
        
        with col6:
            st.metric("3-Year Growth", f"{growth_stats['3yr_growth']:.2f}%")
        
        with col7:
            st.metric("5-Year CAGR", f"{growth_stats['cagr']:.2f}%")
        
        # Detailed growth info
        with st.expander("Detailed Growth Breakdown"):
            st.write("Growth Rates:")
            st.write(f"1-Year Growth: {growth_stats['1yr_growth']:.2f}%")
            st.write(f"3-Year Growth: {growth_stats['3yr_growth']:.2f}%")
            st.write(f"5-Year Growth: {growth_stats['5yr_growth']:.2f}%")
            st.write(f"10-Year Growth: {growth_stats['10yr_growth']:.2f}%")
            st.write(f"Compound Annual Growth Rate (CAGR): {growth_stats['cagr']:.2f}%")
    
    except Exception as e:
        st.warning(f"Could not retrieve detailed dividend history: {e}")
    
    # Additional market data if available
    if stock_data:
        st.markdown("### Current Market Data")
        
        # Display additional stock data columns
        market_columns = ['price', 'dividend', 'yield', 'pe_ratio', 'market_cap']
        market_labels = {
            'price': 'Current Price',
            'dividend': 'Annual Dividend',
            'yield': 'Dividend Yield',
            'pe_ratio': 'P/E Ratio',
            'market_cap': 'Market Cap'
        }
        
        # Create columns for market data
        col_count = len([key for key in market_columns if key in stock_data])
        columns = st.columns(min(col_count, 3))
        
        for i, key in enumerate([key for key in market_columns if key in stock_data]):
            with columns[i % 3]:
                # Format the value appropriately
                if key in ['price', 'dividend', 'market_cap']:
                    value = f"${stock_data[key]:,.2f}"
                elif key == 'yield':
                    value = f"{stock_data[key]:.2f}%"
                elif key == 'pe_ratio':
                    value = f"{stock_data[key]:.2f}"
                else:
                    value = str(stock_data[key])
                
                st.metric(market_labels.get(key, key.replace('_', ' ').title()), value)