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

# ------------------- DATA LOADING FUNCTION -------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                                   'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                                   'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO', 
                                   'LMLABRADOR', 'EASORIANO'])]
    return df

# ------------------- DATA PROCESSING -------------------
def generate_collector_summary(df):
    collector_summary = pd.DataFrame(columns=[
        'Day', 'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
    ])
    
    # Exclude rows where Status is 'PTP FF UP'
    df = df[df['Status'] != 'PTP FF UP']

    for (date, collector), collector_group in df[~df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Remark By']):
        total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
        
        # Count rows where Status contains 'RPC'
        total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].count()

        ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        
        # Include Balance Amount only for rows with PTP Amount not equal to 0
        balance_amount = collector_group[ 
            (collector_group['Status'].str.contains('PTP', na=False)) & 
            (collector_group['PTP Amount'] != 0) & 
            (collector_group['Balance'] != 0)
        ]['Balance'].sum()

        collector_summary = pd.concat([collector_summary, pd.DataFrame([{
            'Day': date,
            'Collector': collector,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])], ignore_index=True)

    # Add totals row at the bottom
    totals = {
        'Day': 'Total',
        'Collector': '',
        'Total Connected': collector_summary['Total Connected'].sum(),
        'Total PTP': collector_summary['Total PTP'].sum(),
        'Total RPC': collector_summary['Total RPC'].sum(),
        'PTP Amount': collector_summary['PTP Amount'].sum(),
        'Balance Amount': collector_summary['Balance Amount'].sum()
    }
    collector_summary = pd.concat([collector_summary, pd.DataFrame([totals])], ignore_index=True)

    # Remove the totals row and sort by 'PTP Amount' in descending order
    collector_summary_sorted = collector_summary[collector_summary['Day'] != 'Total']
    collector_summary_sorted = collector_summary_sorted.sort_values(by='PTP Amount', ascending=False)

    return collector_summary_sorted

# ------------------- FILE UPLOAD AND DISPLAY -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    collector_summary = generate_collector_summary(df)
    
    st.write(collector_summary)
