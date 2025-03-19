import pandas as pd
import numpy as np
import calendar

def calculate_portfolio_metrics(dividend_kings):
    """
    Calculate overall portfolio metrics
    
    Args:
        dividend_kings (pd.DataFrame): DataFrame with portfolio data
    
    Returns:
        tuple: (total_investment, total_annual_income, portfolio_yield)
    """
    total_investment = dividend_kings['Investment'].sum()
    total_annual_income = dividend_kings['Annual Income'].sum()
    
    # Calculate portfolio yield
    portfolio_yield = (total_annual_income / total_investment * 100) if total_investment > 0 else 0
    
    return total_investment, total_annual_income, portfolio_yield

def calculate_monthly_income(dividend_kings):
    """
    Calculate monthly income distribution
    
    Args:
        dividend_kings (pd.DataFrame): DataFrame with portfolio data
    
    Returns:
        dict: Monthly income values
    """
    month_map = {month: i+1 for i, month in enumerate(calendar.month_name) if month}
    
    # Create a dictionary to store monthly income
    monthly_income = {month: 0 for month in calendar.month_name[1:]}
    
    # Calculate income for each month based on payout month
    for _, row in dividend_kings.iterrows():
        payout_month = row['Payout Month']
        quarterly_income = row['Monthly Income']
        
        # Distribute income across quarters
        payout_month_idx = month_map[payout_month]
        
        # Add income to the payout month and subsequent quarters (3 months apart)
        for i in range(4):
            month_idx = ((payout_month_idx - 1 + i * 3) % 12) + 1
            month_name = calendar.month_name[month_idx]
            monthly_income[month_name] += quarterly_income
    
    return monthly_income

def calculate_dividend_growth_stats(dividend_history):
    """
    Calculate dividend growth statistics
    
    Args:
        dividend_history (pd.DataFrame): DataFrame with dividend history
    
    Returns:
        dict: Growth statistics
    """
    if dividend_history.empty:
        return {
            '1yr_growth': 0,
            '3yr_growth': 0,
            '5yr_growth': 0,
            '10yr_growth': 0,
            'cagr': 0
        }
    
    # Group by year
    dividend_history['Year'] = pd.to_datetime(dividend_history['Date']).dt.year
    annual_dividends = dividend_history.groupby('Year')['Dividend'].sum().reset_index()
    
    # Calculate growth rates
    years = len(annual_dividends)
    
    if years < 2:
        return {
            '1yr_growth': 0,
            '3yr_growth': 0,
            '5yr_growth': 0,
            '10yr_growth': 0,
            'cagr': 0
        }
    
    latest = annual_dividends.iloc[-1]['Dividend']
    
    # 1-year growth
    one_yr_growth = 0
    if years >= 2:
        previous = annual_dividends.iloc[-2]['Dividend']
        one_yr_growth = (latest / previous - 1) * 100 if previous > 0 else 0
    
    # 3-year growth
    three_yr_growth = 0
    if years >= 4:
        previous = annual_dividends.iloc[-4]['Dividend']
        three_yr_growth = (latest / previous - 1) * 100 if previous > 0 else 0
    
    # 5-year growth
    five_yr_growth = 0
    if years >= 6:
        previous = annual_dividends.iloc[-6]['Dividend']
        five_yr_growth = (latest / previous - 1) * 100 if previous > 0 else 0
    
    # 10-year growth
    ten_yr_growth = 0
    if years >= 11:
        previous = annual_dividends.iloc[-11]['Dividend']
        ten_yr_growth = (latest / previous - 1) * 100 if previous > 0 else 0
    
    # CAGR
    cagr = 0
    if years >= 2:
        first = annual_dividends.iloc[0]['Dividend']
        n_years = annual_dividends.iloc[-1]['Year'] - annual_dividends.iloc[0]['Year']
        if n_years > 0 and first > 0:
            cagr = ((latest / first) ** (1 / n_years) - 1) * 100
    
    return {
        '1yr_growth': one_yr_growth,
        '3yr_growth': three_yr_growth,
        '5yr_growth': five_yr_growth,
        '10yr_growth': ten_yr_growth,
        'cagr': cagr
    }