import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf

from dividend_data import get_dividend_history
from portfolio_analysis import calculate_dividend_growth_stats

def display_stock_detail(stock_row, stock_info=None):
    """
    Display detailed information for a stock
    
    Args:
        stock_row (pd.Series): Row from dividend kings dataframe
        stock_info (dict, optional): Additional stock info from yfinance
    """
    ticker = stock_row['Ticker']
    company = stock_row['Company']
    
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Price", f"${stock_row['Current Price']:.2f}")
        st.metric("Dividend Yield", f"{stock_row['Current Yield']:.2f}%")
    
    with col2:
        st.metric("Your Investment", f"${stock_row['Investment']:,.2f}")
        st.metric("Shares Owned", f"{stock_row['Shares']:.2f}")
    
    with col3:
        st.metric("Annual Income", f"${stock_row['Annual Income']:.2f}")
        st.metric("Years of Growth", f"{stock_row['Years of Growth']} years")
    
    # Display description and additional info
    st.subheader("Company Overview")
    
    # Company description from data or yfinance
    description = stock_row['Description']
    if stock_info and 'longBusinessSummary' in stock_info:
        description = stock_info['longBusinessSummary']
    
    st.write(description)
    
    # Display additional company info if available
    if stock_info:
        st.subheader("Company Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'sector' in stock_info and stock_info['sector'] != 'N/A':
                st.write(f"**Sector:** {stock_info['sector']}")
            
            if 'industry' in stock_info and stock_info['industry'] != 'N/A':
                st.write(f"**Industry:** {stock_info['industry']}")
            
            if 'marketCap' in stock_info and stock_info['marketCap'] > 0:
                market_cap = stock_info['marketCap']
                market_cap_str = f"${market_cap/1e9:.2f}B" if market_cap >= 1e9 else f"${market_cap/1e6:.2f}M"
                st.write(f"**Market Cap:** {market_cap_str}")
        
        with col2:
            if 'trailingPE' in stock_info and stock_info['trailingPE'] > 0:
                st.write(f"**P/E Ratio:** {stock_info['trailingPE']:.2f}")
            
            if 'payoutRatio' in stock_info and stock_info['payoutRatio'] > 0:
                payout_ratio = stock_info['payoutRatio'] * 100
                st.write(f"**Payout Ratio:** {payout_ratio:.2f}%")
            
            if 'beta' in stock_info and stock_info['beta'] > 0:
                st.write(f"**Beta:** {stock_info['beta']:.2f}")
    
    # Fetch price history
    st.subheader("Price History (5 Years)")
    
    try:
        price_data = yf.download(ticker, period="5y")
        
        if not price_data.empty:
            # Create price chart
            fig = go.Figure()
            
            # Add price line
            fig.add_trace(go.Scatter(
                x=price_data.index,
                y=price_data['Close'],
                mode='lines',
                name='Price',
                line=dict(color='#4682B4', width=2)
            ))
            
            # Update layout
            fig.update_layout(
                title=f'{ticker} Price History',
                xaxis_title='Date',
                yaxis_title='Price ($)',
                template='plotly_white',
                height=400
            )
            
            # Format y-axis as currency
            fig.update_yaxes(tickprefix='$')
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No price history available for {ticker}")
    except Exception as e:
        st.error(f"Error fetching price history: {e}")
        
        # Generate sample data
        dates = pd.date_range(end=datetime.now(), periods=1258, freq='D')  # ~5 years of trading days
        
        # Generate random price with upward trend
        base_price = stock_row['Current Price'] * 0.7
        noise = np.random.normal(0, 0.01, len(dates))
        trend = np.linspace(0, 0.3, len(dates))
        prices = base_price * (1 + trend + noise.cumsum())
        
        # Create sample dataframe
        sample_data = pd.DataFrame({
            'Date': dates,
            'Price': prices
        })
        
        # Create sample chart
        fig = px.line(
            sample_data,
            x='Date',
            y='Price',
            title=f'{ticker} Price History (Sample Data)'
        )
        
        fig.update_layout(height=400)
        fig.update_yaxes(tickprefix='$')
        
        st.plotly_chart(fig, use_container_width=True)
        st.info("Note: Sample data shown for demonstration")
    
    # Fetch dividend history
    st.subheader("Dividend History and Growth")
    
    dividend_history = get_dividend_history(ticker)
    
    if not dividend_history.empty:
        # Show recent dividends
        st.write("Recent Dividends:")
        recent_dividends = dividend_history.sort_values('Date', ascending=False).head(5)
        recent_dividends['Date'] = pd.to_datetime(recent_dividends['Date']).dt.strftime('%Y-%m-%d')
        recent_dividends['Dividend'] = recent_dividends['Dividend'].apply(lambda x: f"${x:.4f}")
        st.dataframe(recent_dividends, use_container_width=True)
        
        # Calculate growth stats
        growth_stats = calculate_dividend_growth_stats(dividend_history)
        
        # Display growth metrics
        growth_col1, growth_col2, growth_col3, growth_col4 = st.columns(4)
        
        with growth_col1:
            st.metric("1-Year Growth", f"{growth_stats['1yr_growth']:.2f}%")
        
        with growth_col2:
            st.metric("3-Year Growth", f"{growth_stats['3yr_growth']:.2f}%")
        
        with growth_col3:
            st.metric("5-Year Growth", f"{growth_stats['5yr_growth']:.2f}%")
        
        with growth_col4:
            st.metric("10-Year Growth", f"{growth_stats['10yr_growth']:.2f}%")
        
        st.metric("Dividend CAGR", f"{growth_stats['cagr']:.2f}%")
        
        # Dividend history chart
        dividend_history['Date'] = pd.to_datetime(dividend_history['Date'])
        
        fig = px.line(
            dividend_history,
            x='Date',
            y='Dividend',
            title=f'{ticker} Dividend History',
            markers=True
        )
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Dividend ($)',
            template='plotly_white',
            height=400
        )
        
        fig.update_yaxes(tickprefix='$')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No dividend history available for {ticker}")
    
    # Your investment performance
    st.subheader("Your Investment Performance")
    
    # Calculate years to recoup investment at current rate
    annual_income = stock_row['Annual Income']
    investment = stock_row['Investment']
    years_to_recoup = investment / annual_income if annual_income > 0 else float('inf')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Quarterly Dividend Income", f"${annual_income/4:.2f}")
        st.metric("Years to Recoup Investment", f"{years_to_recoup:.1f} years")
    
    with col2:
        # Calculate estimated 10-year income
        current_yield = stock_row['Current Yield'] / 100
        
        # Use average growth rate from history or default to 5%
        if 'cagr' in growth_stats and growth_stats['cagr'] > 0:
            growth_rate = growth_stats['cagr'] / 100
        else:
            growth_rate = 0.05
        
        # Calculate total 10-year income
        total_10yr_income = 0
        annual_yield = current_yield
        
        for year in range(1, 11):
            year_income = investment * annual_yield
            total_10yr_income += year_income
            annual_yield *= (1 + growth_rate)
        
        st.metric("Estimated 10-Year Total Income", f"${total_10yr_income:.2f}")
        st.metric("Percentage of Investment Returned", f"{(total_10yr_income/investment*100):.2f}%")
    
    # Income projection chart
    st.subheader("10-Year Income Projection")
    
    # Calculate yearly income projections
    years = list(range(1, 11))
    annual_yield = current_yield
    yearly_income = []
    cumulative_income = []
    running_total = 0
    
    for year in range(1, 11):
        year_income = investment * annual_yield
        yearly_income.append(year_income)
        running_total += year_income
        cumulative_income.append(running_total)
        annual_yield *= (1 + growth_rate)
    
    # Create projection dataframe
    projection_data = pd.DataFrame({
        'Year': years,
        'Annual Income': yearly_income,
        'Cumulative Income': cumulative_income
    })
    
    # Create projection chart
    fig = go.Figure()
    
    # Add annual income bars
    fig.add_trace(go.Bar(
        x=projection_data['Year'],
        y=projection_data['Annual Income'],
        name='Annual Income',
        marker_color='#4682B4'
    ))
    
    # Add cumulative income line
    fig.add_trace(go.Scatter(
        x=projection_data['Year'],
        y=projection_data['Cumulative Income'],
        mode='lines+markers',
        name='Cumulative Income',
        line=dict(color='#FF4500', width=2),
        marker=dict(size=8)
    ))
    
    # Add investment reference line
    fig.add_trace(go.Scatter(
        x=[1, 10],
        y=[investment, investment],
        mode='lines',
        name='Initial Investment',
        line=dict(color='green', width=2, dash='dash')
    ))
    
    # Update layout
    fig.update_layout(
        title='10-Year Dividend Income Projection',
        xaxis_title='Year',
        yaxis_title='Income ($)',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickprefix='$')
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"Projection assumes an annual dividend growth rate of {growth_rate*100:.2f}% based on historical performance.")