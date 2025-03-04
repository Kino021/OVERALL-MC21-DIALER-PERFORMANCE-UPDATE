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

# ------------------- FILE UPLOAD -------------------
uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])

df = None
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    st.success("File uploaded successfully!")
    st.write(df.head())  # Display first few rows for verification

# ------------------- DATA PROCESSING FOR TIME SUMMARY -------------------
def generate_time_summary(df):
    time_summary = pd.DataFrame(columns=[
        'Date', 'Time Range', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
    ])
    
    # Exclude rows where Status is 'PTP FF UP'
    df = df[df['Status'] != 'PTP FF UP']
    
    # Define time intervals
    time_intervals = [
        (21600, 25200), (25201, 28800), (28801, 32400), (32401, 36000), 
        (36001, 39600), (39601, 43200), (43201, 46800), (46801, 50400), 
        (50401, 54000), (54001, 57600), (57601, 61200), (61201, 64800), 
        (64801, 68400), (68401, 72000), (72001, 75600)
    ]
    
    time_labels = [
        "06:00-07:00 AM", "07:01-08:00 AM", "08:01-09:00 AM", "09:01-10:00 AM",
        "10:01-11:00 AM", "11:01-12:00 PM", "12:01-01:00 PM", "01:01-02:00 PM",
        "02:01-03:00 PM", "03:01-04:00 PM", "04:01-05:00 PM", "05:01-06:00 PM",
        "06:01-07:00 PM", "07:01-08:00 PM", "08:01-09:00 PM"
    ]
    
    # Ensure 'Time' column is in datetime format
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time
    df['Time_Seconds'] = df['Time'].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second)
    df['Time Range'] = pd.cut(df['Time_Seconds'], bins=[t[0] for t in time_intervals] + [75600], labels=time_labels)
    
    # Group by Date and Time Range
    time_summary_by_date = {}
    
    for (date, time_range), time_group in df[~df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Time Range']):
        total_connected = time_group[time_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['Account No.'].nunique()
        total_rpc = time_group[time_group['Status'].str.contains('RPC', na=False)]['Account No.'].count()
        ptp_amount = time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        balance_amount = time_group[
            (time_group['Status'].str.contains('PTP', na=False)) & 
            (time_group['PTP Amount'] != 0) & 
            (time_group['Balance'] != 0)
        ]['Balance'].sum()
        
        summary_row = pd.DataFrame([{
            'Date': date,
            'Time Range': time_range,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])
        
        if date in time_summary_by_date:
            time_summary_by_date[date] = pd.concat([time_summary_by_date[date], summary_row], ignore_index=True)
        else:
            time_summary_by_date[date] = summary_row
    
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

# ------------------- DISPLAY TIME SUMMARY -------------------
if df is not None:
    time_summary_by_date = generate_time_summary(df)
    
    for date, summary in time_summary_by_date.items():
        st.markdown(f'<div class="category-title">Hourly PTP Summary for {date}</div>', unsafe_allow_html=True)
        st.dataframe(summary)
