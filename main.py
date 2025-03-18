import streamlit as st
import pandas as pd

# Streamlit Page Configuration
st.set_page_config(layout="wide", page_title="Daily Remark Summary", page_icon="📊", initial_sidebar_state="expanded")

# Dark Mode Styling
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
        # Helper Function to Calculate Overall Summary
        def calculate_overall_summary(df):
            total_accounts = df['Account No.'].nunique()
            total_dialed = df['Account No.'].count()
            connected = df[df['Call Status'] == 'CONNECTED']['Account No.'].nunique()
            penetration_rate = (total_dialed / total_accounts * 100) if total_accounts != 0 else None
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            ptp_acc = df[df['Status'].str.contains('PTP', na=False)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
            system_drop = df[(df['Status'].str.contains('DROPPED', na=False)) & (df['Remark By'] == 'SYSTEM')]['Account No.'].count()
            call_drop_count = df[(df['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                 (~df['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()
            call_drop_ratio = (system_drop / connected * 100) if connected != 0 else None

            ptp_amount = df[df['PTP Amount'] > 0]['PTP Amount'].sum()
            balance = df[df['PTP Amount'] > 0]['Balance'].sum()

            overall_summary = {
                'ACCOUNTS': total_accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                'PTP ACC': ptp_acc,
                'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                'CALL DROP #': call_drop_count,
                'SYSTEM DROP': system_drop,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                'PTP AMOUNT': ptp_amount,
                'BALANCE': balance
            }
            return overall_summary

        # Overall Summary
        st.write("## Overall Summary")
        overall_summary = calculate_overall_summary(df)
        st.write(pd.DataFrame([overall_summary]))

        # Helper Function to Calculate Predictive Overall Summary
        def calculate_predictive_overall_summary(df):
            df_filtered = df[df['Remark Type'].isin(['Predictive', 'Follow Up'])]

            total_accounts = df_filtered['Account No.'].nunique()
            total_dialed = df_filtered['Account No.'].count()
            connected = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()
            penetration_rate = (total_dialed / total_accounts * 100) if total_accounts != 0 else None
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            ptp_acc = df_filtered[df_filtered['Status'].str.contains('PTP', na=False)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
            system_drop = df_filtered[(df_filtered['Status'].str.contains('DROPPED', na=False)) & 
                                      (df_filtered['Remark By'] == 'SYSTEM')]['Account No.'].count()
            call_drop_count = df_filtered[(df_filtered['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                          (~df_filtered['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()
            call_drop_ratio = (system_drop / connected * 100) if connected != 0 else None

            ptp_amount = df_filtered[df_filtered['PTP Amount'] > 0]['PTP Amount'].sum()
            balance = df_filtered[df_filtered['PTP Amount'] > 0]['Balance'].sum()

            predictive_overall_summary = {
                'ACCOUNTS': total_accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                'PTP ACC': ptp_acc,
                'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                'CALL DROP #': call_drop_count,
                'SYSTEM DROP': system_drop,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                'PTP AMOUNT': ptp_amount,
                'BALANCE': balance
            }
            return predictive_overall_summary

        # Predictive Overall Summary
        st.write("## Predictive Overall Summary")
        predictive_overall_summary = calculate_predictive_overall_summary(df)
        st.write(pd.DataFrame([predictive_overall_summary]))

        # Helper Function to Calculate Manual Overall Summary
        def calculate_manual_overall_summary(df):
            df_filtered = df[df['Remark Type'] == 'Outgoing']

            total_accounts = df_filtered['Account No.'].nunique()
            total_dialed = df_filtered['Account No.'].count()
            connected = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()
            penetration_rate = (total_dialed / total_accounts * 100) if total_accounts != 0 else None
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            ptp_acc = df_filtered[df_filtered['Status'].str.contains('PTP', na=False)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
            system_drop = df_filtered[(df_filtered['Status'].str.contains('DROPPED', na=False)) & 
                                      (df_filtered['Remark By'] == 'SYSTEM')]['Account No.'].count()
            call_drop_count = df_filtered[(df_filtered['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                          (~df_filtered['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()
            call_drop_ratio = (system_drop / connected * 100) if connected != 0 else None

            ptp_amount = df_filtered[df_filtered['PTP Amount'] > 0]['PTP Amount'].sum()
            balance = df_filtered[df_filtered['PTP Amount'] > 0]['Balance'].sum()

            manual_overall_summary = {
                'ACCOUNTS': total_accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                'PTP ACC': ptp_acc,
                'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                'CALL DROP #': call_drop_count,
                'SYSTEM DROP': system_drop,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                'PTP AMOUNT': ptp_amount,
                'BALANCE': balance
            }
            return manual_overall_summary

        # Manual Overall Summary
        st.write("## Manual Overall Summary")
        manual_overall_summary = calculate_manual_overall_summary(df)
        st.write(pd.DataFrame([manual_overall_summary]))

        # Helper Function for Predictive Per Cycle Summary
        def calculate_per_cycle_summary(df, remark_type):
            summary_table = pd.DataFrame(columns=[ 
                'Cycle', 'Date', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 
                'SYSTEM DROP', 'CALL DROP RATIO #', 'PTP AMOUNT', 'BALANCE'
            ]) 
            df_filtered = df[df['Remark Type'] == remark_type]

            for cycle, group in df_filtered.groupby('Service No.'):

                for date, date_group in group.groupby(group['Date'].dt.date):  
                    accounts = date_group['Account No.'].nunique()
                    total_dialed = date_group['Account No.'].count()
                    connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()
                    penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None
                    connected_acc = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                    connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None
                    ptp_acc = date_group[(date_group['Status'].str.contains('PTP', na=False)) & (date_group['PTP Amount'] != 0)]['Account No.'].nunique()
                    ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
                    system_drop = date_group[(date_group['Status'].str.contains('DROPPED', na=False)) & (date_group['Remark By'] == 'SYSTEM')]['Account No.'].count()
                    call_drop_count = date_group[(date_group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                                 (~date_group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()
                    call_drop_ratio = (system_drop / connected_acc * 100) if connected_acc != 0 else None

                    ptp_amount = date_group[date_group['PTP Amount'] > 0]['PTP Amount'].sum()
                    balance = date_group[date_group['PTP Amount'] > 0]['Balance'].sum()

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
                        'CALL DROP #': call_drop_count,
                        'SYSTEM DROP': system_drop,
                        'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                        'PTP AMOUNT': ptp_amount,
                        'BALANCE': balance
                    }])], ignore_index=True)

            return summary_table

        # Predictive Per Cycle Summary
        st.write("## Predictive Per Cycle Summary")
        predictive_per_cycle_summary = calculate_per_cycle_summary(df, 'Predictive')
        st.write(predictive_per_cycle_summary)

        # Manual Per Cycle Summary
        st.write("## Manual Per Cycle Summary")
        manual_per_cycle_summary = calculate_per_cycle_summary(df, 'Outgoing')
        st.write(manual_per_cycle_summary)
