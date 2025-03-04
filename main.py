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

# ------------------- DATA PROCESSING FOR CYCLE AND TIME SUMMARY -------------------
def generate_cycle_summary(df):
    df = df[df['Status'] != 'PTP FF UP']
    cycle_summary_by_date = {}
    
    for (date, cycle), cycle_group in df[~df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Service No.']):
        total_connected = cycle_group[cycle_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['Account No.'].nunique()
        total_rpc = cycle_group[cycle_group['Status'].str.contains('RPC', na=False)]['Account No.'].count()
        ptp_amount = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        balance_amount = cycle_group[(cycle_group['Status'].str.contains('PTP', na=False)) & (cycle_group['PTP Amount'] != 0) & (cycle_group['Balance'] != 0)]['Balance'].sum()

        cycle_summary = pd.DataFrame([{
            'Date': date,
            'Cycle': cycle,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])
        
        if date in cycle_summary_by_date:
            cycle_summary_by_date[date] = pd.concat([cycle_summary_by_date[date], cycle_summary], ignore_index=True)
        else:
            cycle_summary_by_date[date] = cycle_summary
    
    for date, summary in cycle_summary_by_date.items():
        totals = {
            'Date': 'Total',
            'Cycle': '',
            'Total Connected': summary['Total Connected'].sum(),
            'Total PTP': summary['Total PTP'].sum(),
            'Total RPC': summary['Total RPC'].sum(),
            'PTP Amount': summary['PTP Amount'].sum(),
            'Balance Amount': summary['Balance Amount'].sum()
        }
        cycle_summary_by_date[date] = pd.concat([summary, pd.DataFrame([totals])], ignore_index=True)
    
    return cycle_summary_by_date

def generate_hourly_summary(df):
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
    time_intervals = [
        ("06:00:00", "07:00:00"), ("07:01:00", "08:00:00"), ("08:01:00", "09:00:00"),
        ("09:01:00", "10:00:00"), ("10:01:00", "11:00:00"), ("11:01:00", "12:00:00"),
        ("12:01:00", "13:00:00"), ("13:01:00", "14:00:00"), ("14:01:00", "15:00:00"),
        ("15:01:00", "16:00:00"), ("16:01:00", "17:00:00"), ("17:01:00", "18:00:00"),
        ("18:01:00", "19:00:00"), ("19:01:00", "20:00:00"), ("20:01:00", "21:00:00")
    ]
    time_summary = []
    
    for start, end in time_intervals:
        mask = (df['Time'] >= pd.to_datetime(start).time()) & (df['Time'] <= pd.to_datetime(end).time())
        time_group = df[mask]
        total_ptp = time_group[time_group['Status'].str.contains('PTP', na=False)]['Account No.'].nunique()
        ptp_amount = time_group[time_group['Status'].str.contains('PTP', na=False)]['PTP Amount'].sum()
        time_summary.append({
            'Time Range': f"{start} - {end}",
            'Total PTP': total_ptp,
            'PTP Amount': ptp_amount
        })
    
    return pd.DataFrame(time_summary)

# ------------------- DISPLAY SUMMARIES -------------------
if df is not None:
    cycle_summary = generate_cycle_summary(df)
    hourly_summary = generate_hourly_summary(df)
    
    st.markdown('<div class="category-title">Cycle Summary</div>', unsafe_allow_html=True)
    for date, summary in cycle_summary.items():
        st.markdown(f'<div class="category-title">Date: {date}</div>', unsafe_allow_html=True)
        st.dataframe(summary)
    
    st.markdown('<div class="category-title">Hourly PTP Summary</div>', unsafe_allow_html=True)
    st.dataframe(hourly_summary)
