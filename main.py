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

# ------------------- FUNCTION TO GENERATE HOURLY SUMMARY -------------------
def generate_time_summary(df):
    """Creates hourly PTP productivity summary."""
    time_summary_by_date = {}

    df = df[df['Status'] != 'PTP FF UP']  # Exclude unnecessary statuses

    # Define time bins
    time_bins = [
        "06:00-07:00 AM", "07:01-08:00 AM", "08:01-09:00 AM", "09:01-10:00 AM",
        "10:01-11:00 AM", "11:01-12:00 PM", "12:01-01:00 PM", "01:01-02:00 PM",
        "02:01-03:00 PM", "03:01-04:00 PM", "04:01-05:00 PM", "05:01-06:00 PM",
        "06:01-07:00 PM", "07:01-08:00 PM", "08:01-09:00 PM"
    ]

    time_intervals = [
        ("06:00", "07:00"), ("07:01", "08:00"), ("08:01", "09:00"),
        ("09:01", "10:00"), ("10:01", "11:00"), ("11:01", "12:00"),
        ("12:01", "13:00"), ("13:01", "14:00"), ("14:01", "15:00"),
        ("15:01", "16:00"), ("16:01", "17:00"), ("17:01", "18:00"),
        ("18:01", "19:00"), ("19:01", "20:00"), ("20:01", "21:00")
    ]

    def time_to_minutes(time_obj):
        return time_obj.hour * 60 + time_obj.minute

    bins = [time_to_minutes(pd.to_datetime(start, format='%H:%M').time()) for start, _ in time_intervals] + [1260]

    df['Time in Minutes'] = df['Time'].apply(time_to_minutes)
    df['Time Range'] = pd.cut(df['Time in Minutes'], bins=bins, labels=time_bins, right=False)

    for (date, time_range), time_group in df[~df['Remark By'].astype(str).str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Time Range']):
        time_summary_by_date.setdefault(date, []).append({
            'Time Range': time_range,
            'Total Connected': (time_group['Call Status'] == 'CONNECTED').sum(),
            'Total PTP': ((time_group['Status'].str.contains('PTP', na=False)) & (time_group['PTP Amount'] != 0)).sum(),
            'Total RPC': (time_group['Status'].str.contains('RPC', na=False)).sum(),
            'PTP Amount': time_group.loc[time_group['Status'].str.contains('PTP', na=False), 'PTP Amount'].sum(),
            'Balance Amount': time_group.loc[time_group['Status'].str.contains('PTP', na=False), 'Balance'].sum(),
        })

    return time_summary_by_date

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
