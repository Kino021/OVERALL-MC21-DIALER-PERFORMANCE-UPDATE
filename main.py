import streamlit as st
import pandas as pd

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide", 
    page_title="PRODUCTIVITY PER AGENT", 
    page_icon="📊", 
    initial_sidebar_state="expanded"
)

# ------------------- FILE UPLOAD -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx"])

# ------------------- DATA LOADING FUNCTION -------------------
def load_data(file):
    if file is not None:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    return None

# ------------------- HOURLY SUMMARY FUNCTION -------------------
def generate_time_summary(df):
    df = df[df['Status'] != 'PTP FF UP']  # Exclude rows where Status is 'PTP FF UP'
    
    # Define time intervals
    time_bins = [
        "06:00-07:00 AM", "07:01-08:00 AM", "08:01-09:00 AM", "09:01-10:00 AM",
        "10:01-11:00 AM", "11:01-12:00 PM", "12:01-01:00 PM", "01:01-02:00 PM",
        "02:01-03:00 PM", "03:01-04:00 PM", "04:01-05:00 PM", "05:01-06:00 PM",
        "06:01-07:00 PM", "07:01-08:00 PM", "08:01-09:00 PM"
    ]

    time_intervals = [
        ("06:00", "07:00"), ("07:01", "08:00"), ("08:01", "09:00"), ("09:01", "10:00"),
        ("10:01", "11:00"), ("11:01", "12:00"), ("12:01", "13:00"), ("13:01", "14:00"),
        ("14:01", "15:00"), ("15:01", "16:00"), ("16:01", "17:00"), ("17:01", "18:00"),
        ("18:01", "19:00"), ("19:01", "20:00"), ("20:01", "21:00")
    ]

    # Convert time to minutes
    def time_to_minutes(time_str):
        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    bins = [time_to_minutes(start) for start, _ in time_intervals] + [1260]  # Ensure bins are sorted

    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
    df = df.dropna(subset=['Time'])

    df['Time in Minutes'] = df['Time'].apply(lambda t: t.hour * 60 + t.minute)
    
    # Ensure bins are sorted properly
    bins = sorted(set(bins))  # Remove duplicates and sort to ensure they are increasing

    # Apply time ranges
    df['Time Range'] = pd.cut(df['Time in Minutes'], bins=bins, labels=time_bins, right=False)

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    summary_data = df.groupby(['Date', 'Time Range']).agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: x.str.contains('PTP', na=False).sum()),
        Total_RPC=('Status', lambda x: x.str.contains('RPC', na=False).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

    return summary_data

# ------------------- MAIN APP LOGIC -------------------
df = load_data(uploaded_file)

if df is not None:
    st.markdown("### 📋 PRODUCTIVITY BY HOUR (Separated per Date)")
    hourly_summary = generate_time_summary(df)
    st.dataframe(hourly_summary)
else:
    st.warning("Please upload a file to generate reports.")
