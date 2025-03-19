import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def display_etf_detail(etf_row, etf_data=None):
    """
    Display detailed information about a specific ETF or CEF
    
    Args:
        etf_row (pd.Series): Row of ETF data from portfolio DataFrame
        etf_data (dict, optional): Additional ETF data from API
    """
    # Create columns for basic information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ETF Basics")
        st.metric("Name", etf_row['Name'])
        st.metric("Ticker", etf_row['Ticker'])
        
        # Payout frequency if available
        if 'Payout Frequency' in etf_row:
            st.metric("Payout Frequency", etf_row['Payout Frequency'])
    
    with col2:
        st.markdown("### Current Investment Details")
        st.metric("Investment", f"${etf_row['Investment']:,.2f}")
        st.metric("Shares", f"{etf_row['Shares']:,.2f}")
        st.metric("Current Price", f"${etf_row['Current Price']:,.2f}")
    
    # Dividend and Income Information
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### Distribution Information")
        st.metric("Current Yield", f"{etf_row['Current Yield']:.2f}%")
        st.metric("Annual Income", f"${etf_row['Annual Income']:,.2f}")
        
        # Monthly income if calculated
        if 'Monthly Income' in etf_row:
            st.metric("Monthly Income (Est.)", f"${etf_row['Monthly Income']:,.2f}")
        
        # Expense ratio if available
        if 'Expense Ratio' in etf_row:
            st.metric("Expense Ratio", f"{etf_row['Expense Ratio']:.2f}%")
    
    with col4:
        # Display notes if available
        if 'Notes' in etf_row and etf_row['Notes']:
            st.markdown("### Additional Notes")
            st.write(etf_row['Notes'])
        elif 'Description' in etf_row and etf_row['Description']:
            st.markdown("### Fund Description")
            st.write(etf_row['Description'])
        else:
            st.markdown("### Fund Type Information")
            st.write("No additional information available for this ETF.")
    
    # Additional market data if available
    if etf_data:
        st.markdown("### Current Market Data")
        
        # Display additional ETF data columns
        market_columns = ['price', 'dividend', 'yield', 'expense_ratio', 'aum', 'nav']
        market_labels = {
            'price': 'Current Price',
            'dividend': 'Annual Distribution',
            'yield': 'Distribution Yield',
            'expense_ratio': 'Expense Ratio',
            'aum': 'Assets Under Management',
            'nav': 'Net Asset Value'
        }
        
        # Create columns for market data
        col_count = len([key for key in market_columns if key in etf_data])
        if col_count > 0:
            columns = st.columns(min(col_count, 3))
            
            for i, key in enumerate([key for key in market_columns if key in etf_data]):
                with columns[i % 3]:
                    # Format the value appropriately
                    if key in ['price', 'dividend', 'nav', 'aum']:
                        value = f"${etf_data[key]:,.2f}" if key != 'aum' else f"${etf_data[key]:,.0f}M"
                    elif key in ['yield', 'expense_ratio']:
                        value = f"{etf_data[key]:.2f}%"
                    else:
                        value = str(etf_data[key])
                    
                    st.metric(market_labels.get(key, key.replace('_', ' ').title()), value)
        else:
            st.info("No additional market data available for this ETF.")
    
    # ETF Holdings information
    st.markdown("### Top Holdings")
    try:
        # Try to get holdings data if available
        if etf_data and 'holdings' in etf_data and etf_data['holdings']:
            holdings = etf_data['holdings']
            
            # Display top holdings in a table
            holdings_df = pd.DataFrame(holdings)
            st.dataframe(holdings_df, use_container_width=True)
            
            # Create pie chart of top holdings
            fig = px.pie(
                holdings_df,
                values='weight',
                names='name',
                title='Top Holdings Allocation',
                hole=0.4,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Create sample data if not available
            st.info("Detailed holdings data not available. Showing sample visualization instead.")
            
            # Create sample holdings data
            sample_holdings = [
                {"name": "Example Holding 1", "weight": 15.2},
                {"name": "Example Holding 2", "weight": 12.8},
                {"name": "Example Holding 3", "weight": 9.5},
                {"name": "Example Holding 4", "weight": 7.2},
                {"name": "Example Holding 5", "weight": 6.8},
                {"name": "Other Holdings", "weight": 48.5}
            ]
            
            # Display sample holdings chart
            sample_df = pd.DataFrame(sample_holdings)
            fig = px.pie(
                sample_df,
                values='weight',
                names='name',
                title='Sample Holdings Allocation (Not Actual Data)',
                hole=0.4,
            )
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.warning(f"Could not display holdings data: {e}")
        
    # ETF Performance section if data available
    if etf_data and 'performance' in etf_data and etf_data['performance']:
        st.markdown("### Historical Performance")
        
        performance = etf_data['performance']
        
        # Create performance chart
        try:
            perf_df = pd.DataFrame(performance)
            fig = px.line(
                perf_df,
                x='date',
                y='value',
                title='Historical Price Performance',
                labels={'date': 'Date', 'value': 'Price ($)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not display performance chart: {e}")