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
    
    df = df[df['Status'] != 'PTP FF UP']
    
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
    
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time
    df['Time_Seconds'] = df['Time'].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second)
    df['Time Range'] = pd.cut(df['Time_Seconds'], bins=[t[0] for t in time_intervals] + [75600], labels=time_labels)
    
    return df.groupby(['Date', 'Time Range']).agg(
        Total_Connected=('Account No.', 'count'),
        Total_PTP=('PTP Amount', lambda x: (x != 0).sum()),
        Total_RPC=('Status', lambda x: x.str.contains('RPC', na=False).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

# ------------------- DATA PROCESSING FOR CYCLE SUMMARY -------------------
def generate_cycle_summary(df):
    df = df[df['Status'] != 'PTP FF UP']
    
    return df.groupby(['Date', 'Service No.']).agg(
        Total_Connected=('Account No.', 'count'),
        Total_PTP=('PTP Amount', lambda x: (x != 0).sum()),
        Total_RPC=('Status', lambda x: x.str.contains('RPC', na=False).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

# ------------------- DISPLAY TIME SUMMARY -------------------
if df is not None:
    time_summary = generate_time_summary(df)
    cycle_summary = generate_cycle_summary(df)
    
    st.markdown('<div class="category-title">Hourly PTP Summary</div>', unsafe_allow_html=True)
    st.dataframe(time_summary)
    
    st.markdown('<div class="category-title">Cycle Summary</div>', unsafe_allow_html=True)
    st.dataframe(cycle_summary)
