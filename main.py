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
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx", "csv"])

# ------------------- DATA LOADING FUNCTION -------------------
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    excluded_users = ['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                      'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                      'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO', 
                      'LMLABRADOR', 'EASORIANO']
    df = df[~df['Remark By'].isin(excluded_users)]
    return df

# ------------------- FUNCTION TO GENERATE COLLECTOR SUMMARY -------------------
def generate_collector_summary(df):
    summary = df.groupby(['Date', 'Remark By']).agg(
        Total_Connected=('Account No.', lambda x: (df['Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: ((df['Status'].str.contains('PTP', na=False)) & (df['PTP Amount'] != 0)).sum()),
        Total_RPC=('Account No.', lambda x: df['Status'].str.contains('RPC', na=False).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()
    summary.rename(columns={'Remark By': 'Collector'}, inplace=True)
    return summary

# ------------------- FUNCTION TO GENERATE CYCLE SUMMARY -------------------
def generate_cycle_summary(df):
    summary = df.groupby(['Date', 'Service No.']).agg(
        Total_Connected=('Account No.', lambda x: (df['Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: ((df['Status'].str.contains('PTP', na=False)) & (df['PTP Amount'] != 0)).sum()),
        Total_RPC=('Account No.', lambda x: df['Status'].str.contains('RPC', na=False).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()
    summary.rename(columns={'Service No.': 'Cycle'}, inplace=True)
    return summary

# ------------------- MAIN APP LOGIC -------------------
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Display Collector Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY COLLECTOR</div>', unsafe_allow_html=True)
    collector_summary = generate_collector_summary(df)
    st.dataframe(collector_summary)
    
    # Display Cycle Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY CYCLE</div>', unsafe_allow_html=True)
    cycle_summary = generate_cycle_summary(df)
    st.dataframe(cycle_summary)
