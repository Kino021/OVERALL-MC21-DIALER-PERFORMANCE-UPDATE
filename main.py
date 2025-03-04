import streamlit as st
import pandas as pd

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide",
    page_title="PRODUCTIVITY PER AGENT",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ------------------- HEADER -------------------
st.markdown('<div class="header">📊 PRODUCTIVITY PER AGENT</div>', unsafe_allow_html=True)

# ------------------- FILE UPLOAD -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx"])

# ------------------- FUNCTION TO LOAD DATA -------------------
def load_data(file):
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# ------------------- FUNCTION TO GENERATE HOURLY SUMMARY -------------------
def generate_time_summary(df):
    time_summary_by_date = {}
    df = df[df['Status'] != 'PTP FF UP']

    time_bins = [
        "06:00-07:00 AM", "07:01-08:00 AM", "08:01-09:00 AM", "09:01-10:00 AM",
        "10:01-11:00 AM", "11:01-12:00 PM", "12:01-01:00 PM", "01:01-02:00 PM",
        "02:01-03:00 PM", "03:01-04:00 PM", "04:01-05:00 PM", "05:01-06:00 PM",
        "06:01-07:00 PM", "07:01-08:00 PM", "08:01-09:00 PM"
    ]

    def time_to_minutes(time_obj):
        return time_obj.hour * 60 + time_obj.minute

    df['Time in Minutes'] = df['Time'].apply(time_to_minutes)
    df['Time Range'] = pd.cut(df['Time in Minutes'], bins=list(range(360, 1261, 60)), labels=time_bins, right=False)

    summary_df = df.groupby('Time Range').agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: (x.str.contains('PTP', na=False)).sum()),
        Total_RPC=('Status', lambda x: (x.str.contains('RPC', na=False)).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()
    
    summary_df.loc['Total'] = summary_df.sum(numeric_only=True)
    summary_df.at[summary_df.index[-1], 'Time Range'] = 'Total'
    
    return summary_df

# ------------------- FUNCTION TO GENERATE COLLECTOR SUMMARY -------------------
def generate_collector_summary(df):
    summary_df = df.groupby(['Date', 'Remark By']).agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: (x.str.contains('PTP', na=False)).sum()),
        Total_RPC=('Status', lambda x: (x.str.contains('RPC', na=False)).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()
    
    total_row = summary_df.sum(numeric_only=True)
    total_row['Date'] = 'Total'
    total_row['Remark By'] = 'Overall'
    summary_df = pd.concat([summary_df, pd.DataFrame([total_row])], ignore_index=True)
    
    return summary_df

# ------------------- FUNCTION TO GENERATE CYCLE SUMMARY -------------------
def generate_cycle_summary(df):
    summary_df = df.groupby(['Date', 'Service No.']).agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: (x.str.contains('PTP', na=False)).sum()),
        Total_RPC=('Status', lambda x: (x.str.contains('RPC', na=False)).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()
    
    total_row = summary_df.sum(numeric_only=True)
    total_row['Date'] = 'Total'
    total_row['Service No.'] = 'Overall'
    summary_df = pd.concat([summary_df, pd.DataFrame([total_row])], ignore_index=True)
    
    return summary_df

# ------------------- MAIN APP LOGIC -------------------
if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        st.markdown('<h2 style="text-align:center;">📊 Hourly PTP Summary</h2>', unsafe_allow_html=True)
        st.dataframe(generate_time_summary(df))
        
        st.markdown('<div class="category-title">📋l PRODUCTIVITY BY COLLECTOR</div>', unsafe_allow_html=True)
        st.dataframe(generate_collector_summary(df))
        
        st.markdown('<div class="category-title">📋l PRODUCTIVITY BY CYCLE</div>', unsafe_allow_html=True)
        st.dataframe(generate_cycle_summary(df))
