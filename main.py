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
    """Loads the uploaded data file into a pandas DataFrame."""
    if file is not None:
        file_extension = file.name.split('.')[-1]
        if file_extension == "csv":
            return pd.read_csv(file)
        elif file_extension == "xlsx":
            return pd.read_excel(file)
    return None

# ------------------- FUNCTION TO GENERATE COLLECTOR SUMMARY -------------------
def generate_collector_summary(df):
    """Creates a summary of productivity by collector."""
    return df.groupby(['Date', 'Remark By']).agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: (x.str.contains('PTP', na=False)).sum()),
        Total_RPC=('Status', lambda x: (x.str.contains('RPC', na=False)).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

# ------------------- FUNCTION TO GENERATE CYCLE SUMMARY -------------------
def generate_cycle_summary(df):
    """Creates a summary of productivity by cycle."""
    return df.groupby(['Date', 'Service No.']).agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: (x.str.contains('PTP', na=False)).sum()),
        Total_RPC=('Status', lambda x: (x.str.contains('RPC', na=False)).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

# ------------------- MAIN APP LOGIC -------------------
if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        # Display Hourly Summary
        st.markdown('<h2 style="text-align:center;">📊 Hourly PTP Summary</h2>', unsafe_allow_html=True)
        # Assuming generate_time_summary is another function, you need to implement it
        time_summary_by_date = generate_time_summary(df)
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
