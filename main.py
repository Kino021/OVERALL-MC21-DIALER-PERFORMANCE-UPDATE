import streamlit as st
import pandas as pd

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide", 
    page_title="Productivity Per Agent", 
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
st.markdown('<div class="header">📊 PRODUCTIVITY PER AGENT</div>', unsafe_allow_html=True)

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

# ------------------- DATA PROCESSING FOR AGENT -------------------
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

    return collector_summary

# ------------------- DATA PROCESSING FOR CYCLE -------------------
def generate_cycle_summary(df):
    cycle_summary = pd.DataFrame(columns=[
        'Cycle', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
    ])
    
    # Extract cycle information from 'Service No.' (if it contains a number, it's a cycle)
    df['Cycle'] = df['Service No.'].str.extract('(\d+)', expand=False)

    # Exclude rows where Cycle is NaN (no number found in 'Service No.')
    df = df.dropna(subset=['Cycle'])

    for cycle, cycle_group in df.groupby('Cycle'):
        total_connected = cycle_group[cycle_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['Account No.'].nunique()
        
        # Count rows where Status contains 'RPC'
        total_rpc = cycle_group[cycle_group['Status'].str.contains('RPC', na=False)]['Account No.'].count()

        ptp_amount = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        
        # Include Balance Amount only for rows with PTP Amount not equal to 0
        balance_amount = cycle_group[
            (cycle_group['Status'].str.contains('PTP', na=False)) & 
            (cycle_group['PTP Amount'] != 0) & 
            (cycle_group['Balance'] != 0)
        ]['Balance'].sum()

        cycle_summary = pd.concat([cycle_summary, pd.DataFrame([{
            'Cycle': cycle,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])], ignore_index=True)

    # Add totals row at the bottom
    totals = {
        'Cycle': 'Total',
        'Total Connected': cycle_summary['Total Connected'].sum(),
        'Total PTP': cycle_summary['Total PTP'].sum(),
        'Total RPC': cycle_summary['Total RPC'].sum(),
        'PTP Amount': cycle_summary['PTP Amount'].sum(),
        'Balance Amount': cycle_summary['Balance Amount'].sum()
    }
    cycle_summary = pd.concat([cycle_summary, pd.DataFrame([totals])], ignore_index=True)

    return cycle_summary

# ------------------- FILE UPLOAD AND DISPLAY -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Generate summaries
    collector_summary = generate_collector_summary(df)
    cycle_summary = generate_cycle_summary(df)
    
    # Sort the summaries by 'PTP Amount' in descending order
    collector_summary_sorted = collector_summary[:-1].sort_values(by='PTP Amount', ascending=False)
    collector_summary_sorted = pd.concat([collector_summary_sorted, collector_summary.iloc[[-1]]], ignore_index=True)

    cycle_summary_sorted = cycle_summary[:-1].sort_values(by='PTP Amount', ascending=False)
    cycle_summary_sorted = pd.concat([cycle_summary_sorted, cycle_summary.iloc[[-1]]], ignore_index=True)

    # Display the results
    st.subheader("Productivity Per Agent")
    st.write(collector_summary_sorted)
    
    st.subheader("Productivity Per Cycle")
    st.write(cycle_summary_sorted)
