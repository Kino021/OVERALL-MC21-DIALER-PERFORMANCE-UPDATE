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

# ------------------- DATA PROCESSING FOR CYCLE SUMMARY -------------------
def generate_cycle_summary(df):
    cycle_summary = pd.DataFrame(columns=[
        'Date', 'Cycle', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
    ])
    
    # Exclude rows where Status is 'PTP FF UP'
    df = df[df['Status'] != 'PTP FF UP']

    # Group by Date and Cycle (formerly "Service No.")
    cycle_summary_by_date = {}

    for (date, cycle), cycle_group in df[~df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Service No.']):
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

        cycle_summary = pd.DataFrame([{
            'Date': date,
            'Cycle': cycle,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])

        # If the date already exists in the dictionary, append the cycle data
        if date in cycle_summary_by_date:
            cycle_summary_by_date[date] = pd.concat([cycle_summary_by_date[date], cycle_summary], ignore_index=True)
        else:
            cycle_summary_by_date[date] = cycle_summary

    # Add totals row for each date
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

# ------------------- FILE UPLOAD AND DISPLAY -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Display the title for Collector Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY COLLECTOR</div>', unsafe_allow_html=True)
    # Generate and display collector summary
    collector_summary = generate_collector_summary(df)
    st.write(collector_summary)
    
    # Display the title for Cycle Summary (formerly "Service No.")
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY CYCLE (Seperated per Date)</div>', unsafe_allow_html=True)
    # Generate and display cycle summary per date
    cycle_summary_by_date = generate_cycle_summary(df)
    
    # Display cycle summary for each date separately
    for date, summary in cycle_summary_by_date.items():
        st.markdown(f'**Date: {date}**')
        st.write(summary)

def calculate_combined_summary(df):
        summary_table = pd.DataFrame(columns=[
            'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #'
        ])
        
        for date, group in df.groupby(df['Date'].dt.date):
            accounts = group[group['Remark'] != 'Broken Promise']['Account No.'].nunique()
            total_dialed = group[group['Remark'] != 'Broken Promise']['Account No.'].count()

            connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            connected_acc = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

            ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

            call_drop_count = group[group['Call Status'] == 'DROPPED']['Account No.'].count()
            call_drop_ratio = (call_drop_count / connected * 100) if connected != 0 else None

            summary_table = pd.concat([summary_table, pd.DataFrame([{
                'Day': date,
                'ACCOUNTS': accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                'CONNECTED ACC': connected_acc,
                'PTP ACC': ptp_acc,
                'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                'CALL DROP #': call_drop_count,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
            }])], ignore_index=True)
        
    return summary_table

    st.write("## Overall Combined Summary Table")
    combined_summary_table = calculate_combined_summary(df)
    st.write(combined_summary_table, container_width=True)

    def calculate_summary(df, remark_type, remark_by=None):
        summary_table = pd.DataFrame(columns=[
            'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #'
        ])
        
        for date, group in df.groupby(df['Date'].dt.date):
            accounts = group[(group['Remark Type'] == remark_type) | ((group['Remark'] != 'Broken Promise') & (group['Remark Type'] == 'Follow Up') & (group['Remark By'] == remark_by))]['Account No.'].nunique()
            total_dialed = group[(group['Remark Type'] == remark_type) | ((group['Remark'] != 'Broken Promise') & (group['Remark Type'] == 'Follow Up') & (group['Remark By'] == remark_by))]['Account No.'].count()

            connected = group[(group['Call Status'] == 'CONNECTED') & (group['Remark Type'] == remark_type)]['Account No.'].count()
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            connected_acc = group[(group['Call Status'] == 'CONNECTED') & (group['Remark Type'] == remark_type)]['Account No.'].nunique()

            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

            ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0) & (group['Remark Type'] == remark_type)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

            call_drop_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark Type'] == remark_type)]['Account No.'].count()
            call_drop_ratio = (call_drop_count / connected * 100) if connected != 0 else None

            summary_table = pd.concat([summary_table, pd.DataFrame([{
                'Day': date,
                'ACCOUNTS': accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                'CONNECTED ACC': connected_acc,
                'PTP ACC': ptp_acc,
                'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                'CALL DROP #': call_drop_count,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
            }])], ignore_index=True)
        
        return summary_table

    col1, col2 = st.columns(2)

    with col1:
        st.write("## Overall Predictive Summary Table")
        overall_summary_table = calculate_summary(df, 'Predictive', 'SYSTEM')
        st.write(overall_summary_table)

    with col2:
        st.write("## Overall Manual Summary Table")
        overall_manual_table = calculate_summary(df, 'Outgoing')
        st.write(overall_manual_table)

    col3, col4 = st.columns(2)

    with col3:
        st.write("## Summary Table by Cycle Predictive")
        for cycle, cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {cycle}")
            summary_table = calculate_summary(cycle_group, 'Predictive', 'SYSTEM')
            st.write(summary_table)

    with col4:
        st.write("## Summary Table by Cycle Manual")
        for manual_cycle, manual_cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {manual_cycle}")
            summary_table = calculate_summary(manual_cycle_group, 'Outgoing')
            st.write(summary_table)
