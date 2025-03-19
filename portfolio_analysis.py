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

def calculate_etf_portfolio_metrics(etf_portfolio):
    """
    Calculate portfolio metrics for ETF portfolio
    
    Args:
        etf_portfolio (pd.DataFrame): DataFrame with ETF portfolio data
    
    Returns:
        tuple: (total_investment, total_annual_income, portfolio_yield, weighted_expense_ratio)
    """
    total_investment = etf_portfolio['Investment'].sum()
    total_annual_income = etf_portfolio['Annual Income'].sum()
    
    # Calculate portfolio yield
    portfolio_yield = (total_annual_income / total_investment * 100) if total_investment > 0 else 0
    
    # Calculate weighted expense ratio
    weighted_expense_ratio = (etf_portfolio['Expense Ratio'] * etf_portfolio['Investment'] / total_investment).sum() if total_investment > 0 else 0
    
    return total_investment, total_annual_income, portfolio_yield, weighted_expense_ratio

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

def calculate_etf_monthly_income(etf_portfolio):
    """
    Calculate monthly income distribution for ETF portfolio
    
    Args:
        etf_portfolio (pd.DataFrame): DataFrame with ETF portfolio data
    
    Returns:
        dict: Monthly income values
    """
    # Create a dictionary to store monthly income
    monthly_income = {month: 0 for month in calendar.month_name[1:]}
    
    # Calculate income for each ETF
    for _, row in etf_portfolio.iterrows():
        payout_frequency = row.get('Payout Frequency', 'Quarterly')
        monthly_income_value = row['Monthly Income']
        
        if payout_frequency == 'Monthly':
            # Distribute evenly across all months
            for month in monthly_income.keys():
                monthly_income[month] += monthly_income_value / 12
        else:
            # For quarterly payers, distribute across 3 months
            payout_month = row.get('Payout Month', 'January')
            month_map = {month: i+1 for i, month in enumerate(calendar.month_name) if month}
            payout_month_idx = month_map[payout_month]
            
            # Distribute quarterly income across 3 months
            for i in range(3):
                month_idx = ((payout_month_idx - 1 + i) % 12) + 1
                month_name = calendar.month_name[month_idx]
                monthly_income[month_name] += monthly_income_value / 3
    
    return monthly_income

def calculate_income_stability_score(portfolio_data):
    """
    Calculate income stability score
    
    Args:
        portfolio_data (pd.DataFrame): DataFrame with portfolio data
    
    Returns:
        float: Income stability score (0-100)
    """
    # Factors to consider for stability score
    # 1. Yield consistency
    # 2. Payout frequency
    # 3. Expense ratio (for ETFs)
    
    # Yield stability
    yield_variation = portfolio_data['Current Yield'].std() / portfolio_data['Current Yield'].mean() * 100 if len(portfolio_data) > 1 else 0
    
    # Payout frequency bonus
    monthly_payers = portfolio_data[portfolio_data.get('Payout Frequency', 'Quarterly') == 'Monthly']
    monthly_payer_percentage = len(monthly_payers) / len(portfolio_data) * 100 if len(portfolio_data) > 0 else 0
    
    # Expense ratio penalty (for ETFs)
    if 'Expense Ratio' in portfolio_data.columns:
        expense_ratio_penalty = portfolio_data['Expense Ratio'].mean() if len(portfolio_data) > 0 else 0
    else:
        expense_ratio_penalty = 0
    
    # Calculate stability score
    # Base score starts at 100
    base_score = 100
    
    # Reduce score based on yield variation
    variation_penalty = min(yield_variation * 0.5, 20)  # Max 20 point penalty
    
    # Bonus for monthly payers
    monthly_payer_bonus = min(monthly_payer_percentage, 10)
    
    # Penalty for high expense ratios
    expense_ratio_deduction = min(expense_ratio_penalty * 5, 10)  # Max 10 point penalty
    
    # Final stability score
    stability_score = base_score - variation_penalty + monthly_payer_bonus - expense_ratio_deduction
    
    # Ensure score is between 0 and 100
    return max(0, min(stability_score, 100))