import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from etf_data import get_etf_distribution_history

def display_etf_detail(etf_row, etf_data=None):
    """
    Display detailed information about a specific ETF
    
    Args:
        etf_row (pd.Series): Row of ETF data from portfolio DataFrame
        etf_data (dict, optional): Additional ETF data from API
    """
    # Create columns for basic information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ETF Basics")
        st.metric("ETF Name", etf_row['Name'])
        st.metric("Ticker", etf_row['Ticker'])
        
        # Category if available
        if 'Category' in etf_row:
            st.metric("Category", etf_row['Category'])
        
        # Focus if available
        if 'Focus' in etf_row:
            st.metric("Investment Focus", etf_row['Focus'])
    
    with col2:
        st.markdown("### Current Investment Details")
        st.metric("Investment", f"${etf_row['Investment']:,.2f}")
        st.metric("Shares", f"{etf_row['Shares']:,.2f}")
        st.metric("Current Price", f"${etf_row['Current Price']:,.2f}")
    
    # Income Information
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### Distribution Information")
        st.metric("Current Yield", f"{etf_row['Current Yield']:.2f}%")
        st.metric("Annual Income", f"${etf_row['Annual Income']:,.2f}")
        
        # Payout frequency if available
        if 'Payout Frequency' in etf_row:
            st.metric("Payout Frequency", etf_row['Payout Frequency'])
    
    with col4:
        st.markdown("### Fees & Expenses")
        # Expense ratio if available
        if 'Expense Ratio' in etf_row:
            expense_impact = etf_row['Investment'] * etf_row['Expense Ratio'] / 100
            st.metric("Expense Ratio", f"{etf_row['Expense Ratio']:.2f}%")
            st.metric("Annual Fee Impact", f"${expense_impact:.2f}")
    
    # ETF Description if available
    if 'Description' in etf_row and etf_row['Description']:
        st.markdown("### ETF Description")
        st.write(etf_row['Description'])
    
    # Fetch distribution history
    try:
        # Get distribution history
        distribution_history = get_etf_distribution_history(etf_row['Ticker'])
        
        # Display distribution history if available
        if not distribution_history.empty:
            st.markdown("### Distribution History")
            
            # Plot distribution history
            fig = px.line(
                distribution_history,
                x='Date',
                y='Distribution',
                title=f"{etf_row['Name']} ({etf_row['Ticker']}) Distribution History",
                markers=True
            )
            
            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Distribution ($)',
                template='plotly_white',
                height=400
            )
            
            fig.update_yaxes(tickprefix='$')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate distribution statistics
            avg_distribution = distribution_history['Distribution'].mean()
            max_distribution = distribution_history['Distribution'].max()
            min_distribution = distribution_history['Distribution'].min()
            
            # Show statistics
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            
            with stat_col1:
                st.metric("Average Distribution", f"${avg_distribution:.4f}")
            
            with stat_col2:
                st.metric("Maximum Distribution", f"${max_distribution:.4f}")
            
            with stat_col3:
                st.metric("Minimum Distribution", f"${min_distribution:.4f}")
    
    except Exception as e:
        st.warning(f"Could not retrieve detailed distribution history: {e}")
    
    # Additional market data if available
    if etf_data:
        st.markdown("### Current Market Data")
        
        # Display additional ETF data columns
        market_columns = ['price', 'dividend', 'yield', 'expense_ratio', 'aum', 'beta', 'ytd_return', 'three_year_return']
        market_labels = {
            'price': 'Current Price',
            'dividend': 'Annual Distribution',
            'yield': 'Distribution Yield',
            'expense_ratio': 'Expense Ratio',
            'aum': 'Assets Under Management',
            'beta': 'Beta',
            'ytd_return': 'YTD Return',
            'three_year_return': '3-Year Return'
        }
        
        # Create multiple rows of columns for market data
        market_data_rows = [market_columns[i:i+3] for i in range(0, len(market_columns), 3)]
        
        for row_keys in market_data_rows:
            # Filter to only keys that exist in etf_data
            row_keys = [key for key in row_keys if key in etf_data]
            
            if row_keys:
                columns = st.columns(len(row_keys))
                
                for i, key in enumerate(row_keys):
                    with columns[i]:
                        # Format the value appropriately
                        if key in ['price', 'dividend', 'aum']:
                            if key == 'aum' and etf_data[key] > 1000000:
                                value = f"${etf_data[key]/1000000:,.2f}M"
                            else:
                                value = f"${etf_data[key]:,.2f}"
                        elif key in ['yield', 'expense_ratio', 'ytd_return', 'three_year_return']:
                            value = f"{etf_data[key]:.2f}%"
                        elif key == 'beta':
                            value = f"{etf_data[key]:.3f}"
                        else:
                            value = str(etf_data[key])
                        
                        st.metric(market_labels.get(key, key.replace('_', ' ').title()), value)