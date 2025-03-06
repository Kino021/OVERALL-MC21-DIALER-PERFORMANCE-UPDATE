import streamlit as st
import pandas as pd

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide",
    page_title="PRODUCTIVITY PER AGENT",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ------------------- GLOBAL STYLING -------------------
st.markdown("""
    <style>
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(to right, #FFD700, #FFA500);
            color: white;
            font-size: 24px;
            border-radius: 10px;
            font-weight: bold;
        }
        .category-title {
            font-size: 20px;
            font-weight: bold;
            margin-top: 30px;
            color: #FF8C00;
        }
        .card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- HEADER -------------------
st.markdown('<div class="header">📊 PRODUCTIVITY PER AGENT</div>', unsafe_allow_html=True)

# ------------------- FILE UPLOAD -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx"])

# ------------------- FUNCTION TO LOAD DATA -------------------
def load_data(file):
    """Loads CSV or Excel file and ensures proper data formatting."""
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Convert 'Date' column to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Ensure 'Time' column is parsed correctly
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# ------------------- FUNCTION TO GENERATE COLLECTOR SUMMARY -------------------
def generate_collector_summary(df):
    """Creates a summary of productivity by collector."""
    collector_summary = df.groupby(['Date', 'Remark By']).agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: (x.str.contains('PTP', na=False)).sum()),
        Total_RPC=('Status', lambda x: (x.str.contains('RPC', na=False)).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

    # Calculate totals
    totals = collector_summary[['Total_Connected', 'Total_PTP', 'Total_RPC', 'PTP_Amount', 'Balance_Amount']].sum()
    totals['Date'] = 'Total'
    totals['Remark By'] = 'All Collectors'
    
    # Append totals to the dataframe
    collector_summary = collector_summary.append(totals, ignore_index=True)
    
    return collector_summary

# ------------------- FUNCTION TO GENERATE CYCLE SUMMARY -------------------
def generate_cycle_summary(df):
    """Creates a summary of productivity by cycle."""
    cycle_summary = df.groupby(['Date', 'Service No.']).agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: (x.str.contains('PTP', na=False)).sum()),
        Total_RPC=('Status', lambda x: (x.str.contains('RPC', na=False)).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

    # Calculate totals
    totals = cycle_summary[['Total_Connected', 'Total_PTP', 'Total_RPC', 'PTP_Amount', 'Balance_Amount']].sum()
    totals['Date'] = 'Total'
    totals['Service No.'] = 'All Cycles'
    
    # Append totals to the dataframe
    cycle_summary = cycle_summary.append(totals, ignore_index=True)
    
    return cycle_summary

# ------------------- MAIN APP LOGIC -------------------
if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        # Display Hourly Summary (assuming a function `generate_time_summary` is defined elsewhere in the code)
        st.markdown('<h2 style="text-align:center;">📊 Hourly PTP Summary</h2>', unsafe_allow_html=True)
        time_summary_by_date = generate_time_summary(df)  # This function should be defined somewhere in your code.
        for date, summary in time_summary_by_date.items():
            st.markdown(f"### {date}")
            st.dataframe(pd.DataFrame(summary))

        # Display Collector Summary
        st.markdown('<div class="category-title">📋 PRODUCTIVITY BY COLLECTOR</div>', unsafe_allow_html=True)
        collector_summary = generate_collector_summary(df)
        st.dataframe(collector_summary)

        # Display Cycle Summary
        st.markdown('<div class="category-title">📋 PRODUCTIVITY BY CYCLE</div>', unsafe_allow_html=True)
        cycle_summary = generate_cycle_summary(df)
        st.dataframe(cycle_summary)
