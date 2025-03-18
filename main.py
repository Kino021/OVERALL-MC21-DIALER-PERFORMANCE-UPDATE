import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Daily Remark Summary", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode
st.markdown(
    """
    <style>
    .reportview-container {
        background: #2E2E2E;
        color: white;
    }
    .sidebar .sidebar-content {
        background: #2E2E2E;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Daily Remark Summary')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)

    # Convert 'Date' to datetime if it isn't already
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Exclude rows where the date is a Sunday (weekday() == 6)
    df = df[df['Date'].dt.weekday != 6]  # 6 corresponds to Sunday

    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Exclude rows where 'Debtor' contains 'DEFAULT_LEAD_'
    df = df[~df['Debtor'].str.contains("DEFAULT_LEAD_", case=False, na=False)]

    # Exclude rows where STATUS contains 'BP' (Broken Promise) or 'ABORT'
    df = df[~df['Status'].str.contains('ABORT', na=False)]

    # Exclude rows where REMARK contains certain keywords or phrases
    excluded_remarks = [
        "Broken Promise",
        "New files imported", 
        "Updates when case reassign to another collector", 
        "NDF IN ICS", 
        "FOR PULL OUT (END OF HANDLING PERIOD)", 
        "END OF HANDLING PERIOD"
    ]
    df = df[~df['Remark'].str.contains('|'.join(excluded_remarks), case=False, na=False)]

    # Check if data is empty after filtering
    if df.empty:
        st.warning("No valid data available after filtering.")
    else:
        # Overall Per Cycle Predictive Summary Table
        def calculate_per_cycle_predictive_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Cycle', 'Date', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'TOTAL PTP AMOUNT', 
                'TOTAL BALANCE', 'CALL DROP #', 'SYSTEM DROP', 'CALL DROP RATIO #'
            ]) 

            # Filter for 'Predictive' and 'Follow Up' Remark Types
            df_filtered = df[df['Remark Type'].isin(['Predictive', 'Follow Up'])]

            for cycle, group in df_filtered.groupby('Service No.'):
                for date, date_group in group.groupby(group['Date'].dt.date):
                    accounts = date_group[date_group['Remark Type'].isin(['Predictive', 'Follow Up'])]['Account No.'].nunique()
                    total_dialed = date_group[date_group['Remark Type'].isin(['Predictive', 'Follow Up'])]['Account No.'].count()
                    connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()
                    penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None
                    connected_acc = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                    connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None
                    ptp_acc = date_group[(date_group['Status'].str.contains('PTP', na=False)) & 
                                         (date_group['PTP Amount'] != 0)]['Account No.'].nunique()
                    ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
                    total_ptp_amount = date_group[(date_group['Status'].str.contains('PTP', na=False)) & 
                                                  (date_group['PTP Amount'] != 0)]['PTP Amount'].sum()
                    total_balance = date_group[(date_group['PTP Amount'] != 0)]['Balance'].sum()  
                    system_drop = date_group[(date_group['Status'].str.contains('DROPPED', na=False)) & 
                                            (date_group['Remark By'] == 'SYSTEM')]['Account No.'].count()
                    call_drop_count = date_group[(date_group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                                (~date_group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()
                    call_drop_ratio = (system_drop / connected_acc * 100) if connected_acc != 0 else None

                    summary_table = pd.concat([summary_table, pd.DataFrame([{
                        'Cycle': cycle,
                        'Date': date,
                        'ACCOUNTS': accounts,
                        'TOTAL DIALED': total_dialed,
                        'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                        'CONNECTED #': connected,
                        'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                        'CONNECTED ACC': connected_acc,
                        'PTP ACC': ptp_acc,
                        'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                        'TOTAL PTP AMOUNT': total_ptp_amount,
                        'TOTAL BALANCE': total_balance,
                        'CALL DROP #': call_drop_count,
                        'SYSTEM DROP': system_drop,
                        'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                    }])], ignore_index=True)

            return summary_table

        # Display Overall Per Cycle Predictive Summary Table
        st.write("## Overall Per Cycle Predictive Summary Table")
        overall_per_cycle_predictive_table = calculate_per_cycle_predictive_summary(df)
        st.write(overall_per_cycle_predictive_table)

        # Per Service Per Cycle Predictive Summary Table
        def calculate_per_service_cycle_predictive_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Cycle', 'Date', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'TOTAL PTP AMOUNT', 
                'TOTAL BALANCE', 'CALL DROP #', 'SYSTEM DROP', 'CALL DROP RATIO #'
            ]) 

            # Filter for 'Predictive' and 'Follow Up' Remark Types
            df_filtered = df[df['Remark Type'].isin(['Predictive', 'Follow Up'])]

            for cycle, group in df_filtered.groupby('Service No.'):
                for date, date_group in group.groupby(group['Date'].dt.date):
                    accounts = date_group[date_group['Remark Type'].isin(['Predictive', 'Follow Up'])]['Account No.'].nunique()
                    total_dialed = date_group[date_group['Remark Type'].isin(['Predictive', 'Follow Up'])]['Account No.'].count()
                    connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()
                    penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None
                    connected_acc = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                    connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None
                    ptp_acc = date_group[(date_group['Status'].str.contains('PTP', na=False)) & 
                                         (date_group['PTP Amount'] != 0)]['Account No.'].nunique()
                    ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
                    total_ptp_amount = date_group[(date_group['Status'].str.contains('PTP', na=False)) & 
                                                  (date_group['PTP Amount'] != 0)]['PTP Amount'].sum()
                    total_balance = date_group[(date_group['PTP Amount'] != 0)]['Balance'].sum()  
                    system_drop = date_group[(date_group['Status'].str.contains('DROPPED', na=False)) & 
                                            (date_group['Remark By'] == 'SYSTEM')]['Account No.'].count()
                    call_drop_count = date_group[(date_group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                                (~date_group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()
                    call_drop_ratio = (system_drop / connected_acc * 100) if connected_acc != 0 else None

                    summary_table = pd.concat([summary_table, pd.DataFrame([{
                        'Cycle': cycle,
                        'Date': date,
                        'ACCOUNTS': accounts,
                        'TOTAL DIALED': total_dialed,
                        'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                        'CONNECTED #': connected,
                        'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                        'CONNECTED ACC': connected_acc,
                        'PTP ACC': ptp_acc,
                        'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                        'TOTAL PTP AMOUNT': total_ptp_amount,
                        'TOTAL BALANCE': total_balance,
                        'CALL DROP #': call_drop_count,
                        'SYSTEM DROP': system_drop,
                        'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                    }])], ignore_index=True)

            return summary_table

        # Display Per Service Per Cycle Predictive Summary Table
        st.write("## Per Service Per Cycle Predictive Summary Table")
        per_service_per_cycle_predictive_table = calculate_per_service_cycle_predictive_summary(df)
        st.write(per_service_per_cycle_predictive_table)
