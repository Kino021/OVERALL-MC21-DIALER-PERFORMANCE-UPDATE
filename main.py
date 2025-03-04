import streamlit as st
import pandas as pd

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide", 
    page_title="Productivity Dashboard", 
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
    </style>
""", unsafe_allow_html=True)

# ------------------- HEADER -------------------
st.markdown('<div class="header">📊 PRODUCTIVITY DASHBOARD</div>', unsafe_allow_html=True)

# ------------------- DATA LOADING FUNCTION -------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
    return df

# ------------------- FUNCTION FOR HOURLY SUMMARY -------------------
def generate_time_summary(df):
    time_ranges = [
        ("06:00:00", "07:00:00"), ("07:01:00", "08:00:00"), ("08:01:00", "09:00:00"),
        ("09:01:00", "10:00:00"), ("10:01:00", "11:00:00"), ("11:01:00", "12:00:00"),
        ("12:01:00", "13:00:00"), ("13:01:00", "14:00:00"), ("14:01:00", "15:00:00"),
        ("15:01:00", "16:00:00"), ("16:01:00", "17:00:00"), ("17:01:00", "18:00:00"),
        ("18:01:00", "19:00:00"), ("19:01:00", "20:00:00"), ("20:01:00", "21:00:00")
    ]
    
    time_labels = [
        "06:00-07:00 AM", "07:01-08:00 AM", "08:01-09:00 AM", "09:01-10:00 AM",
        "10:01-11:00 AM", "11:01-12:00 PM", "12:01-01:00 PM", "01:01-02:00 PM",
        "02:01-03:00 PM", "03:01-04:00 PM", "04:01-05:00 PM", "05:01-06:00 PM",
        "06:01-07:00 PM", "07:01-08:00 PM", "08:01-09:00 PM"
    ]
    
    time_summary_by_date = {}

    for date, daily_group in df.groupby(df['Date'].dt.date):
        time_summary = pd.DataFrame(columns=['Time Range', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'])

        for i, (start, end) in enumerate(time_ranges):
            time_mask = (daily_group['Time'] >= pd.to_datetime(start, format='%H:%M:%S').time()) & \
                        (daily_group['Time'] <= pd.to_datetime(end, format='%H:%M:%S').time())

            df_filtered = daily_group[time_mask]

            total_connected = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = df_filtered[df_filtered['Status'].str.contains('PTP', na=False) & (df_filtered['PTP Amount'] > 0)]['Account No.'].count()
            total_rpc = df_filtered[df_filtered['Status'].str.contains('RPC', na=False)]['Account No.'].count()
            ptp_amount = df_filtered[df_filtered['PTP Amount'] > 0]['PTP Amount'].sum()
            balance_amount = df_filtered[(df_filtered['Balance'] > 0) & (df_filtered['PTP Amount'] > 0)]['Balance'].sum()

            time_summary = pd.concat([time_summary, pd.DataFrame([{
                'Time Range': time_labels[i],
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
                'Balance Amount': balance_amount
            }])], ignore_index=True)

        # Add totals row
        totals = pd.DataFrame([{
            'Time Range': 'Total',
            'Total Connected': time_summary['Total Connected'].sum(),
            'Total PTP': time_summary['Total PTP'].sum(),
            'Total RPC': time_summary['Total RPC'].sum(),
            'PTP Amount': time_summary['PTP Amount'].sum(),
            'Balance Amount': time_summary['Balance Amount'].sum()
        }])

        time_summary = pd.concat([time_summary, totals], ignore_index=True)

        # Store per date
        time_summary_by_date[date] = time_summary

    return time_summary_by_date

# ------------------- FILE UPLOAD AND DISPLAY -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Display the title for Time-Based Productivity
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY TIME (Separated per Date)</div>', unsafe_allow_html=True)

    # Generate and display time summary per date
    time_summary_by_date = generate_time_summary(df)
    
    # Display time summary for each date separately
    for date, summary in time_summary_by_date.items():
        st.markdown(f'**Date: {date}**')
        st.write(summary)
