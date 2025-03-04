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
st.markdown('<div class="header">📊 PRODUCTIVITY DASHBOARD</div>', unsafe_allow_html=True)


def generate_time_summary(df):
    time_summary = pd.DataFrame(columns=[
        'Date', 'Time Range', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
    ])
    
    # Exclude rows where Status is 'PTP FF UP'
    df = df[df['Status'] != 'PTP FF UP']
    
    # Define time intervals
    time_bins = [
        "06:00-07:00 AM", "07:01-08:00 AM", "08:01-09:00 AM", "09:01-10:00 AM",
        "10:01-11:00 AM", "11:01-12:00 PM", "12:01-01:00 PM", "01:01-02:00 PM",
        "02:01-03:00 PM", "03:01-04:00 PM", "04:01-05:00 PM", "05:01-06:00 PM",
        "06:01-07:00 PM", "07:01-08:00 PM", "08:01-09:00 PM"
    ]
    
    time_intervals = [
        ("06:00:00", "07:00:00"), ("07:01:00", "08:00:00"), ("08:01:00", "09:00:00"),
        ("09:01:00", "10:00:00"), ("10:01:00", "11:00:00"), ("11:01:00", "12:00:00"),
        ("12:01:00", "13:00:00"), ("13:01:00", "14:00:00"), ("14:01:00", "15:00:00"),
        ("15:01:00", "16:00:00"), ("16:01:00", "17:00:00"), ("17:01:00", "18:00:00"),
        ("18:01:00", "19:00:00"), ("19:01:00", "20:00:00"), ("20:01:00", "21:00:00")
    ]
    
    # Ensure 'Time' column is in datetime format
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
    
    time_summary_by_date = {}
    
    for (date, time_range), time_group in df[~df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([
        df['Date'].dt.date,
        pd.cut(pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour * 60 + pd.to_datetime(df['Time'], format='%H:%M:%S').dt.minute,
               bins=[0] + [int(t.split(':')[0]) * 60 + int(t.split(':')[1].split('-')[0]) for t in time_intervals],
               labels=time_bins)
    ]):
        total_connected = time_group[time_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['Account No.'].nunique()
        total_rpc = time_group[time_group['Status'].str.contains('RPC', na=False)]['Account No.'].count()
        ptp_amount = time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        balance_amount = time_group[
            (time_group['Status'].str.contains('PTP', na=False)) & 
            (time_group['PTP Amount'] != 0) & 
            (time_group['Balance'] != 0)
        ]['Balance'].sum()

        time_summary_entry = pd.DataFrame([{
            'Date': date,
            'Time Range': time_range,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])
        
        if date in time_summary_by_date:
            time_summary_by_date[date] = pd.concat([time_summary_by_date[date], time_summary_entry], ignore_index=True)
        else:
            time_summary_by_date[date] = time_summary_entry

    # Add totals row for each date
    for date, summary in time_summary_by_date.items():
        totals = {
            'Date': 'Total',
            'Time Range': '',
            'Total Connected': summary['Total Connected'].sum(),
            'Total PTP': summary['Total PTP'].sum(),
            'Total RPC': summary['Total RPC'].sum(),
            'PTP Amount': summary['PTP Amount'].sum(),
            'Balance Amount': summary['Balance Amount'].sum()
        }
        time_summary_by_date[date] = pd.concat([summary, pd.DataFrame([totals])], ignore_index=True)

    return time_summary_by_date
