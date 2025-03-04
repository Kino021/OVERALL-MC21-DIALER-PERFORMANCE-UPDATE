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
    time_summary_by_date = {}

    df = df[df['Status'] != 'PTP FF UP']  # Exclude rows where Status is 'PTP FF UP'
    
    # Define time intervals
    time_bins = [
        "06:00-07:00 AM", "07:01-08:00 AM", "08:01-09:00 AM", "09:01-10:00 AM",
        "10:01-11:00 AM", "11:01-12:00 PM", "12:01-01:00 PM", "01:01-02:00 PM",
        "02:01-03:00 PM", "03:01-04:00 PM", "04:01-05:00 PM", "05:01-06:00 PM",
        "06:01-07:00 PM", "07:01-08:00 PM", "08:01-09:00 PM"
    ]

    time_intervals = [(time.split('-')[0], time.split('-')[1]) for time in time_bins]

    # Ensure 'Time' column is properly parsed
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
    df = df.dropna(subset=['Time'])

    def time_to_minutes(time_obj):
        return time_obj.hour * 60 + time_obj.minute

    bins = [time_to_minutes(pd.to_datetime(start, format='%H:%M').time()) for start, _ in time_intervals] + [1260]
    df['Time in Minutes'] = df['Time'].apply(time_to_minutes)
    df['Time Range'] = pd.cut(df['Time in Minutes'], bins=bins, labels=time_bins, right=False)
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    for (date, time_range), time_group in df[~df['Remark By'].astype(str).str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Time Range']):
        summary_entry = pd.DataFrame([{
            'Date': date,
            'Time Range': time_range,
            'Total Connected': time_group[time_group['Call Status'] == 'CONNECTED']['Account No.'].count(),
            'Total PTP': time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['Account No.'].nunique(),
            'Total RPC': time_group[time_group['Status'].str.contains('RPC', na=False)]['Account No.'].count(),
            'PTP Amount': time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['PTP Amount'].sum(),
            'Balance Amount': time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0) & (time_group['Balance'] != 0)]['Balance'].sum(),
        }])

        if date in time_summary_by_date:
            time_summary_by_date[date] = pd.concat([time_summary_by_date[date], summary_entry], ignore_index=True)
        else:
            time_summary_by_date[date] = summary_entry

    return time_summary_by_date

# ------------------- COLLECTOR SUMMARY FUNCTION -------------------
def generate_collector_summary(df):
    df = df[df['Status'] != 'PTP FF UP']
    return df.groupby([df['Date'].dt.date, 'Remark By']).agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: x.str.contains('PTP', na=False).sum()),
        Total_RPC=('Status', lambda x: x.str.contains('RPC', na=False).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

# ------------------- CYCLE SUMMARY FUNCTION -------------------
def generate_cycle_summary(df):
    df = df[df['Status'] != 'PTP FF UP']
    return df.groupby([df['Date'].dt.date, 'Service No.']).agg(
        Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
        Total_PTP=('Status', lambda x: x.str.contains('PTP', na=False).sum()),
        Total_RPC=('Status', lambda x: x.str.contains('RPC', na=False).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

# ------------------- MAIN APP LOGIC -------------------
df = load_data(uploaded_file)

if df is not None:
    # Hourly Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY HOUR (Separated per Date)</div>', unsafe_allow_html=True)
    time_summary_by_date = generate_time_summary(df)
    for date, summary in time_summary_by_date.items():
        st.markdown(f"### {date}")
        st.dataframe(summary)

    # Collector Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY COLLECTOR</div>', unsafe_allow_html=True)
    st.dataframe(generate_collector_summary(df))

    # Cycle Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY CYCLE (Separated per Date)</div>', unsafe_allow_html=True)
    cycle_summary = generate_cycle_summary(df)
    for date in cycle_summary['Date'].unique():
        st.markdown(f"### {date}")
        st.dataframe(cycle_summary[cycle_summary['Date'] == date])

else:
    st.warning("Please upload a file to generate reports.")
