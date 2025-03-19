import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar
import streamlit as st
from datetime import datetime, timedelta

from dividend_data import get_dividend_history


    # Format x-axis as percentage
    fig.update_xaxes(ticksuffix='%')
    
    return fig

def plot_dividend_growth(ticker):
    """
    Create a line chart showing dividend growth history
    
    Args:
        ticker (str): Stock ticker
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Get dividend history
    dividend_history = get_dividend_history(ticker)
    
    if dividend_history.empty:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No dividend history available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Convert date to datetime
    dividend_history['Date'] = pd.to_datetime(dividend_history['Date'])
    
    # Group by year
    dividend_history['Year'] = dividend_history['Date'].dt.year
    annual_dividends = dividend_history.groupby('Year')['Dividend'].sum().reset_index()
    
    # Calculate year-over-year growth
    annual_dividends['Previous'] = annual_dividends['Dividend'].shift(1)
    annual_dividends['Growth'] = (annual_dividends['Dividend'] / annual_dividends['Previous'] - 1) * 100
    
    # Create figure
    fig = go.Figure()
    
    # Add annual dividend bars
    fig.add_trace(go.Bar(
        x=annual_dividends['Year'],
        y=annual_dividends['Dividend'],
        marker_color='#4682B4',
        name='Annual Dividend'
    ))
    
    # Add growth rate line
    fig.add_trace(go.Scatter(
        x=annual_dividends['Year'],
        y=annual_dividends['Growth'],
        mode='lines+markers',
        line=dict(color='#FF4500', width=2),
        marker=dict(size=8),
        name='Growth Rate (%)',
        yaxis='y2'
    ))
    
    # Update layout with secondary y-axis
    fig.update_layout(
        title=f'{ticker} Dividend Growth History',
        xaxis_title='Year',
        yaxis_title='Annual Dividend ($)',
        yaxis2=dict(
            title='Growth Rate (%)',
            titlefont=dict(color='#FF4500'),
            tickfont=dict(color='#FF4500'),
            anchor='x',
            overlaying='y',
            side='right',
            ticksuffix='%'
        ),
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
    
    # Format primary y-axis as currency
    fig.update_yaxes(tickprefix=', secondary_y=False)
    
    return fig

def plot_investment_vs_income(dividend_kings):
    """
    Create a scatter plot comparing investment amount vs income
    
    Args:
        dividend_kings (pd.DataFrame): DataFrame with portfolio data
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Create figure
    fig = px.scatter(
        dividend_kings,
        x='Investment',
        y='Annual Income',
        size='Current Yield',
        color='Current Yield',
        hover_name='Company',
        text='Ticker',
        color_continuous_scale='Viridis',
        title='Investment vs. Income Comparison',
        size_max=30
    )
    
    # Add reference lines for average yield
    avg_yield = dividend_kings['Current Yield'].mean()
    x_range = [dividend_kings['Investment'].min(), dividend_kings['Investment'].max()]
    y_range = [x * avg_yield / 100 for x in x_range]
    
    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_range,
        mode='lines',
        line=dict(dash='dash', color='red', width=2),
        name=f'Average Yield ({avg_yield:.2f}%)'
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title='Investment Amount ($)',
        yaxis_title='Annual Income ($)',
        template='plotly_white',
        height=600
    )
    
    # Format axes as currency
    fig.update_xaxes(tickprefix=')
    fig.update_yaxes(tickprefix=')
    
    # Improve text display
    fig.update_traces(
        textposition='top center',
        textfont=dict(size=10, color='black', family='Arial')
    )
    
    return fig