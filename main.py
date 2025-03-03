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

    return collector_summary

# ------------------- FILE UPLOAD AND DISPLAY -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    collector_summary = generate_collector_summary(df)
    
    # Sort the collector summary by 'PTP Amount' in descending order, but exclude the totals row
    collector_summary_sorted = collector_summary[:-1].sort_values(by='PTP Amount', ascending=False)
    
    # Append the totals row back to the sorted DataFrame
    collector_summary_sorted = pd.concat([collector_summary_sorted, collector_summary.iloc[[-1]]], ignore_index=True)
    
    st.write(collector_summary_sorted)

  # ------------------- PRODUCTIVITY PER CYCLE -------------------
    st.markdown("### Productivity per Cycle")

    # Filter Data for each condition
    total_connected = df[df['Call Status'] == 'CONNECTED'].groupby('Service No.').size()
    total_ptp = df[df['Status'].str.contains('PTP', case=False, na=False)].groupby('Service No.')['PTP Amount'].sum()
    total_rpc = df[df['Status'].str.contains('RPC', case=False, na=False)].groupby('Service No.').size()
    total_balance = df[df['Status'].str.contains('PTP', case=False, na=False) & df['Balance'].notna()] \
        .groupby('Service No.')['Balance'].sum()

    # Merge all the data
    cycle_productivity = pd.DataFrame({
        'Total Connected': total_connected,
        'Total PTP': total_ptp,
        'Total RPC': total_rpc,
        'Total Balance (PTP)': total_balance
    }).fillna(0)

    # Display the aggregated data
    st.dataframe(cycle_productivity)

Key Adjustments:
Data Filtering:

Total Connected: df[df['Call Status'] == 'CONNECTED'] filters the rows where the call status is "CONNECTED" and then groups by Service No. to count occurrences (using .size()).
Total PTP: Filters rows where the Status contains "PTP" and sums the PTP Amount grouped by Service No., using .sum().
Total RPC: Similar to Total PTP but counting the rows with "RPC" in Status.
Total Balance: Filters for rows where Status contains "PTP" and the Balance is not null, then sums the Balance values grouped by Service No..
Merged Results: After calculating the totals for each category, the results are combined into a single DataFrame with columns for "Total Connected," "Total PTP," "Total RPC," and "Total Balance (PTP)."

Next Steps:
Upload your Excel file: You can upload an Excel file that contains the relevant columns like Service No., Call Status, Status, PTP Amount, and Balance for the calculations.
Review the Results: The table will display the total connected, PTP amount, RPC count, and balance per cycle (Service No.).
