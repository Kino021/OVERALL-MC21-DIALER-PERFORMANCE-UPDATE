import streamlit as st
import pandas as pd

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide", 
    page_title="Productivity Dashboard", 
    page_icon="📊", 
    initial_sidebar_state="expanded"
)

# ------------------- LOAD DATA -------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Time'] = pd.to_datetime(df['Time']).dt.time  # Convert to time format
    return df

# ------------------- TIME RANGE FUNCTION -------------------
def get_time_range(hour, minute):
    if hour < 6:
        return "Before 6AM"
    elif hour >= 21:
        return "After 9PM"
    else:
        return f"{hour:02d}:{minute:02d}-{hour + 1:02d}:{minute:02d}"

# ------------------- GENERATE TIME-BASED SUMMARY -------------------
def generate_time_summary(df):
    time_summary = pd.DataFrame(columns=['Date', 'Time Range', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'])
    
    df = df[~df['Remark By'].str.upper().isin(['SYSTEM'])]  # Exclude system remarks
    df['Time Range'] = df['Time'].apply(lambda x: get_time_range(x.hour, x.minute))
    
    for (date, time_range, collector), group in df.groupby([df['Date'].dt.date, 'Time Range', 'Remark By']):
        total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()
        total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] > 0)]['Account No.'].nunique()
        total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].count()
        ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] > 0)]['PTP Amount'].sum()
        balance_amount = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] > 0) & (group['Balance'] != 0)]['Balance'].sum()
        
        time_summary = pd.concat([time_summary, pd.DataFrame([{
            'Date': date,
            'Time Range': time_range,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])], ignore_index=True)
    
    # Add totals row
    totals = {
        'Date': 'Total',
        'Time Range': '',
        'Total Connected': time_summary['Total Connected'].sum(),
        'Total PTP': time_summary['Total PTP'].sum(),
        'Total RPC': time_summary['Total RPC'].sum(),
        'PTP Amount': time_summary['PTP Amount'].sum(),
        'Balance Amount': time_summary['Balance Amount'].sum()
    }
    time_summary = pd.concat([time_summary, pd.DataFrame([totals])], ignore_index=True)
    return time_summary

# ------------------- FILE UPLOAD & DISPLAY -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.markdown('<div class="category-title">📉 PRODUCTIVITY BY TIME RANGE</div>', unsafe_allow_html=True)
    time_summary = generate_time_summary(df)
    st.write(time_summary)
