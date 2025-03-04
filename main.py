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
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df

# ------------------- FILE UPLOAD -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])
if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Display the title for Collector Summary
    st.markdown('<div class="category-title">📝 PRODUCTIVITY BY COLLECTOR</div>', unsafe_allow_html=True)
    
    # ------------------- GENERATE COLLECTOR SUMMARY -------------------
    def generate_collector_summary(df):
        collector_summary = df.groupby(['Date', 'Remark By']).agg(
            Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
            Total_PTP=('Status', lambda x: ((x.str.contains('PTP', na=False)) & (df['PTP Amount'] != 0)).sum()),
            Total_RPC=('Status', lambda x: x.str.contains('RPC', na=False).sum()),
            PTP_Amount=('PTP Amount', 'sum'),
            Balance_Amount=('Balance', 'sum')
        ).reset_index()
        return collector_summary
    
    collector_summary = generate_collector_summary(df)
    st.dataframe(collector_summary, use_container_width=True)
    
    # ------------------- GENERATE CYCLE SUMMARY -------------------
    st.markdown('<div class="category-title">📝 PRODUCTIVITY BY CYCLE</div>', unsafe_allow_html=True)
    
    def generate_cycle_summary(df):
        if 'Service No.' not in df.columns:
            return pd.DataFrame()  # Return empty if column is missing
        
        cycle_summary = df.groupby(['Date', 'Service No.']).agg(
            Total_Connected=('Call Status', lambda x: (x == 'CONNECTED').sum()),
            Total_PTP=('Status', lambda x: ((x.str.contains('PTP', na=False)) & (df['PTP Amount'] != 0)).sum()),
            Total_RPC=('Status', lambda x: x.str.contains('RPC', na=False).sum()),
            PTP_Amount=('PTP Amount', 'sum'),
            Balance_Amount=('Balance', 'sum')
        ).reset_index()
        return cycle_summary
    
    cycle_summary = generate_cycle_summary(df)
    st.dataframe(cycle_summary, use_container_width=True)
