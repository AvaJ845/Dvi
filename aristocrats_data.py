import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def load_dividend_aristocrats_data():
    """
    Load the predefined Dividend Aristocrats data
    """
    # Create dataframe with the 10 Dividend Aristocrats
    data = {
        'Company': [
            'McDonald\'s Corporation', 'Walmart Inc.', 'Chevron Corporation', 'Johnson & Johnson',
            'Procter & Gamble', 'Exxon Mobil Corporation', 'Coca-Cola Company', 'Lowe\'s Companies',
            'AT&T Inc.', 'AbbVie Inc.'
        ],
        'Ticker': [
            'MCD', 'WMT', 'CVX', 'JNJ',
            'PG', 'XOM', 'KO', 'LOW',
            'T', 'ABBV'
        ],
        'Years of Growth': [
            47, 49, 36, 62,
            68, 40, 62, 59,
            35, 50
        ],
        'Payout Month': [
            'January', 'February', 'March', 'April',
            'May', 'June', 'July', 'August',
            'September', 'October'
        ],
        'Description': [
            'World\'s largest fast-food restaurant chain with strong global presence and franchising revenue',
            'World\'s largest retailer with massive scale, e-commerce growth, and recession-resistant consumer staples',
            'Integrated energy company with strong balance sheet, diverse operations, and commitment to dividends',
            'Healthcare conglomerate with diversified revenue streams across pharmaceuticals, medical devices, and consumer health',
            'Consumer goods giant with diverse portfolio of essential household brands with pricing power',
            'Integrated oil and gas company with vertical integration, scale, and diverse global operations',
            'Beverage company with unrivaled brand power, global distribution network, and pricing flexibility',
            'Home improvement retailer with housing market exposure, professional customer relationships, and e-commerce growth',
            'Telecommunications company with steady subscription-based revenue and 5G infrastructure investments',
            'Biopharmaceutical company with strong drug portfolio, robust pipeline, and commitment to increasing shareholder returns'
        ],
        'Current Yield': [
            2.2, 1.4, 4.0, 3.2,
            2.4, 3.5, 3.0, 1.7,
            5.5, 3.7
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add notes for AT&T and AbbVie
    df.loc[df['Ticker'] == 'T', 'Notes'] = "AT&T reset its dividend in 2022 after the WarnerMedia spinoff but has a long history of dividends"
    df.loc[df['Ticker'] == 'ABBV', 'Notes'] = "Including time as part of Abbott. AbbVie pays quarterly and helps complete Oct/Nov/Dec"
    
    # Fill NaN values in Notes column
    df['Notes'] = df['Notes'].fillna("")
    
    return df