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

# ------------------- DATA LOADING FUNCTION -------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                                   'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                                   'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO', 
                                   'LMLABRADOR', 'EASORIANO'])]  # Exclude specific users
    return df

# ------------------- DATA PROCESSING FOR COLLECTOR SUMMARY -------------------
def generate_collector_summary(df):
    collector_summary = pd.DataFrame(columns=[
        'Date', 'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
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
            'Date': date,
            'Collector': collector,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])], ignore_index=True)

    # Add totals row at the bottom
    totals = {
        'Date': 'Total',
        'Collector': '',
        'Total Connected': collector_summary['Total Connected'].sum(),
        'Total PTP': collector_summary['Total PTP'].sum(),
        'Total RPC': collector_summary['Total RPC'].sum(),
        'PTP Amount': collector_summary['PTP Amount'].sum(),
        'Balance Amount': collector_summary['Balance Amount'].sum()
    }
    collector_summary = pd.concat([collector_summary, pd.DataFrame([totals])], ignore_index=True)

    # Remove the totals row temporarily for sorting
    collector_summary_without_total = collector_summary[collector_summary['Date'] != 'Total']

    # Sort by 'Date' and 'PTP Amount' in descending order
    collector_summary_sorted = collector_summary_without_total.sort_values(by=['Date', 'PTP Amount'], ascending=[True, False])

    # Append the totals row at the bottom again
    collector_summary_sorted = pd.concat([collector_summary_sorted, collector_summary[collector_summary['Date'] == 'Total']], ignore_index=True)

    return collector_summary_sorted

# ------------------- DATA PROCESSING FOR SERVICE SUMMARY -------------------
def generate_service_summary(df):
    service_summary = pd.DataFrame(columns=[
        'Date', 'Service No.', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
    ])
    
    # Exclude rows where Status is 'PTP FF UP'
    df = df[df['Status'] != 'PTP FF UP']

    for (date, service_no), service_group in df[~df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Service No.']):
        total_connected = service_group[service_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = service_group[service_group['Status'].str.contains('PTP', na=False) & (service_group['PTP Amount'] != 0)]['Account No.'].nunique()
        
        # Count rows where Status contains 'RPC'
        total_rpc = service_group[service_group['Status'].str.contains('RPC', na=False)]['Account No.'].count()

        ptp_amount = service_group[service_group['Status'].str.contains('PTP', na=False) & (service_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        
        # Include Balance Amount only for rows with PTP Amount not equal to 0
        balance_amount = service_group[ 
            (service_group['Status'].str.contains('PTP', na=False)) & 
            (service_group['PTP Amount'] != 0) & 
            (service_group['Balance'] != 0)
        ]['Balance'].sum()

        service_summary = pd.concat([service_summary, pd.DataFrame([{
            'Date': date,
            'Service No.': service_no,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])], ignore_index=True)

    # Add totals row at the bottom
    totals = {
        'Date': 'Total',
        'Service No.': '',
        'Total Connected': service_summary['Total Connected'].sum(),
        'Total PTP': service_summary['Total PTP'].sum(),
        'Total RPC': service_summary['Total RPC'].sum(),
        'PTP Amount': service_summary['PTP Amount'].sum(),
        'Balance Amount': service_summary['Balance Amount'].sum()
    }
    service_summary = pd.concat([service_summary, pd.DataFrame([totals])], ignore_index=True)

    # Remove the totals row temporarily for sorting
    service_summary_without_total = service_summary[service_summary['Date'] != 'Total']

    # Sort by 'Date' and 'PTP Amount' in descending order
    service_summary_sorted = service_summary_without_total.sort_values(by=['Date', 'PTP Amount'], ascending=[True, False])

    # Append the totals row at the bottom again
    service_summary_sorted = pd.concat([service_summary_sorted, service_summary[service_summary['Date'] == 'Total']], ignore_index=True)

    return service_summary_sorted

# ------------------- FILE UPLOAD AND DISPLAY -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Display the title for Collector Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY COLLECTOR</div>', unsafe_allow_html=True)
    # Generate and display collector summary
    collector_summary = generate_collector_summary(df)
    st.write(collector_summary)
    
    # Display the title for Service Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY SERVICE NO.</div>', unsafe_allow_html=True)
    # Generate and display service summary
    service_summary = generate_service_summary(df)
    st.write(service_summary)
