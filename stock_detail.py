import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from dividend_data import get_dividend_history
from portfolio_analysis import calculate_dividend_growth_stats

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