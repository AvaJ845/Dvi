import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar
import streamlit as st
from datetime import datetime, timedelta

from dividend_data import get_dividend_history

def plot_yield_comparison(dividend_kings, portfolio_title):
    """
    Create a bar chart comparing yields
    
    Args:
        dividend_kings (pd.DataFrame): DataFrame with portfolio data
        portfolio_title (str): Title of the portfolio
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Create yield comparison figure
    fig = px.bar(
        dividend_kings, 
        x='Company', 
        y='Current Yield',
        title=f'{portfolio_title} Yield Comparison',
        labels={'Current Yield': 'Yield (%)', 'Company': 'Company'},
        color='Current Yield',
        color_continuous_scale='Blues'
    )
    
    # Format y-axis as percentage
    fig.update_yaxes(ticksuffix='%')
    
    return fig

def plot_monthly_income(monthly_income, portfolio_title):
    """
    Create a bar chart showing monthly income distribution
    
    Args:
        monthly_income (dict): Dictionary of monthly income values
        portfolio_title (str): Title of the portfolio
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Convert monthly income to DataFrame
    monthly_data = pd.DataFrame({
        'Month': list(monthly_income.keys()),
        'Income': list(monthly_income.values())
    })
    
    # Create figure
    fig = px.bar(
        monthly_data, 
        x='Month', 
        y='Income',
        title=f'{portfolio_title} Monthly Income Distribution',
        labels={'Income': 'Monthly Income ($)', 'Month': 'Month'},
        color='Income',
        color_continuous_scale='Blues'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Monthly Income ($)',
        template='plotly_white',
        height=500
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickprefix='$')
    
    # Custom month order
    month_order = list(calendar.month_name)[1:]
    fig.update_xaxes(categoryorder='array', categoryarray=month_order)
    
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
    fig.update_yaxes(tickprefix='$', secondary_y=False)
    
    return fig

def plot_monthly_distribution(monthly_income, portfolio_title):
    """
    Create a bar chart showing monthly income distribution for ETFs
    
    Args:
        monthly_income (dict): Dictionary of monthly income values
        portfolio_title (str): Title of the portfolio
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Convert monthly income to DataFrame
    monthly_data = pd.DataFrame({
        'Month': list(monthly_income.keys()),
        'Income': list(monthly_income.values())
    })
    
    # Create figure
    fig = px.bar(
        monthly_data, 
        x='Month', 
        y='Income',
        title=f'{portfolio_title} Monthly Income Distribution',
        labels={'Income': 'Monthly Distribution ($)', 'Month': 'Month'},
        color='Income',
        color_continuous_scale='Blues'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Monthly Distribution ($)',
        template='plotly_white',
        height=500
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickprefix='$')
    
    # Custom month order
    month_order = list(calendar.month_name)[1:]
    fig.update_xaxes(categoryorder='array', categoryarray=month_order)
    
    return fig

def plot_etf_comparison(etf_portfolio, metric='yield'):
    """
    Create a comparison chart for ETFs based on selected metric
    
    Args:
        etf_portfolio (pd.DataFrame): DataFrame with ETF portfolio data
        metric (str): Metric to compare (yield, expense_ratio, or income)
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Select the appropriate column based on metric
    if metric == 'yield':
        y_column = 'Current Yield'
        y_title = 'Yield (%)'
        color_scale = 'Blues'
    elif metric == 'expense_ratio':
        y_column = 'Expense Ratio'
        y_title = 'Expense Ratio (%)'
        color_scale = 'Reds_r'  # Reversed red scale (lower is better)
    else:  # income
        y_column = 'Annual Income'
        y_title = 'Annual Income ($)'
        color_scale = 'Greens'
    
    # Create figure
    fig = px.bar(
        etf_portfolio, 
        x='Name', 
        y=y_column,
        title=f'ETF Comparison: {y_title}',
        labels={y_column: y_title, 'Name': 'ETF Name'},
        color=y_column,
        color_continuous_scale=color_scale
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='ETF Name',
        yaxis_title=y_title,
        template='plotly_white',
        height=500
    )
    
    # Format y-axis based on metric
    if metric == 'income':
        fig.update_yaxes(tickprefix='$')
    else:
        fig.update_yaxes(ticksuffix='%')
    
    return fig

def plot_etf_allocation(etf_portfolio):
    """
    Create a pie chart showing ETF allocation
    
    Args:
        etf_portfolio (pd.DataFrame): DataFrame with ETF portfolio data
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Create figure
    fig = px.pie(
        etf_portfolio,
        values='Investment',
        names='Name',
        title='ETF Investment Allocation',
        hole=0.4,
    )
    
    return fig

def plot_income_forecast(forecast_df, view_type="monthly", growth_scenario=""):
    """
    Create a plot for projected income
    
    Args:
        forecast_df (pd.DataFrame): DataFrame with forecasted income
        view_type (str): Type of view - "monthly" or "yearly"
        growth_scenario (str): Growth scenario description
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    if view_type == "monthly":
        # Line chart showing projected income by month for each year
        fig = px.line(
            forecast_df,
            x='Month',
            y='Projected Income',
            color='Year',
            title=f"Projected Monthly Income ({growth_scenario})",
            markers=True
        )
        
        # Custom month order
        month_order = list(calendar.month_name)[1:]
        fig.update_xaxes(categoryorder='array', categoryarray=month_order)
    
    else:  # Yearly Comparison
        # Calculate yearly totals
        yearly_totals = forecast_df.groupby('Year')['Projected Income'].sum().reset_index()
        yearly_totals['Projected Annual Income'] = yearly_totals['Projected Income']
        
        fig = px.bar(
            yearly_totals,
            x='Year',
            y='Projected Annual Income',
            title=f"Projected Annual Income ({growth_scenario})",
            color='Projected Annual Income',
            color_continuous_scale='Blues'
        )
    
    fig.update_layout(
        xaxis_title='Month' if view_type == "monthly" else 'Year',
        yaxis_title='Income ($)',
        template='plotly_white',
        height=500
    )
    
    fig.update_yaxes(tickprefix='$')
    
    return fig