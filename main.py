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
        # Overall Combined Summary Table
        def calculate_combined_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'TOTAL PTP AMOUNT', 
                'TOTAL BALANCE', 'CALL DROP #', 'SYSTEM DROP', 'CALL DROP RATIO #', 'COLLECTORS COUNT'
            ]) 

            # Define excluded remarks list
            excluded_remarks = [
                "Broken Promise", "New files imported", 
                "Updates when case reassign to another collector", 
                "NDF IN ICS", "FOR PULL OUT (END OF HANDLING PERIOD)", 
                "END OF HANDLING PERIOD"
            ]

            # Iterate over each date group
            for date, group in df.groupby(df['Date'].dt.date):
                # Filter out rows that contain any of the excluded remarks
                excluded_rows = group[group['Remark'].str.contains('|'.join(excluded_remarks), case=False, na=False)]
                
                # Remove the rows with excluded remarks from the group
                valid_group = group[~group['Remark'].isin(excluded_rows['Remark'])]

                accounts = valid_group[valid_group['Remark Type'].isin(['Predictive', 'Follow Up', 'Outgoing'])]['Account No.'].nunique()
                total_dialed = valid_group[valid_group['Remark Type'].isin(['Predictive', 'Follow Up', 'Outgoing'])]['Account No.'].count()
                connected = valid_group[valid_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()
                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None
                connected_acc = valid_group[valid_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None
                ptp_acc = valid_group[(valid_group['Status'].str.contains('PTP', na=False)) & (valid_group['PTP Amount'] != 0)]['Account No.'].nunique()
                ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
                total_ptp_amount = valid_group[(valid_group['Status'].str.contains('PTP', na=False)) & (valid_group['PTP Amount'] != 0)]['PTP Amount'].sum()
                total_balance = valid_group[(valid_group['PTP Amount'] != 0)]['Balance'].sum()  # Calculate total balance when PTP Amount exists
                system_drop = valid_group[(valid_group['Status'].str.contains('DROPPED', na=False)) & (valid_group['Remark By'] == 'SYSTEM')]['Account No.'].count()
                call_drop_count = valid_group[(valid_group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                              (~valid_group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()
                call_drop_ratio = (system_drop / connected_acc * 100) if connected_acc != 0 else None

                # Calculate the number of unique collectors excluding certain ones
                excluded_collectors = ['SYSTEM']  # You can add more names to exclude
                # Remove rows that have excluded remarks or excluded collectors
                collectors_valid_group = valid_group[~valid_group['Remark By'].isin(excluded_collectors)]
                collectors_valid_group = collectors_valid_group[~collectors_valid_group['Remark'].str.contains('|'.join(excluded_remarks), case=False, na=False)]
                collectors_count = collectors_valid_group['Remark By'].nunique()

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
                    'TOTAL PTP AMOUNT': total_ptp_amount,
                    'TOTAL BALANCE': total_balance,
                    'CALL DROP #': call_drop_count,
                    'SYSTEM DROP': system_drop,
                    'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                    'COLLECTORS COUNT': collectors_count  # Adding the collector count for each day
                }])], ignore_index=True)

            return summary_table

        # Calculate Overall Predictive Summary Table
        def calculate_predictive_summary(df):
            predictive_summary_table = pd.DataFrame(columns=[
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'CONNECTED #', 'PTP ACC', 'TOTAL PTP AMOUNT', 'COLLECTORS COUNT'
            ])
            for date, group in df.groupby(df['Date'].dt.date):
                predictive_group = group[group['Remark Type'] == 'Predictive']

                accounts = predictive_group['Account No.'].nunique()
                total_dialed = predictive_group['Account No.'].count()
                connected = predictive_group[predictive_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()
                ptp_acc = predictive_group[(predictive_group['Status'].str.contains('PTP', na=False)) & 
                                          (predictive_group['PTP Amount'] != 0)]['Account No.'].nunique()
                total_ptp_amount = predictive_group[(predictive_group['Status'].str.contains('PTP', na=False)) & 
                                                    (predictive_group['PTP Amount'] != 0)]['PTP Amount'].sum()

                # Calculate collectors count
                collectors_valid_group = predictive_group[~predictive_group['Remark By'].isin(excluded_collectors)]
                collectors_valid_group = collectors_valid_group[~collectors_valid_group['Remark'].str.contains('|'.join(excluded_remarks), case=False, na=False)]
                collectors_count = collectors_valid_group['Remark By'].nunique()

                predictive_summary_table = pd.concat([predictive_summary_table, pd.DataFrame([{
                    'Day': date,
                    'ACCOUNTS': accounts,
                    'TOTAL DIALED': total_dialed,
                    'CONNECTED #': connected,
                    'PTP ACC': ptp_acc,
                    'TOTAL PTP AMOUNT': total_ptp_amount,
                    'COLLECTORS COUNT': collectors_count
                }])], ignore_index=True)
            return predictive_summary_table

        # Calculate Overall Manual Summary Table
        def calculate_manual_summary(df):
            manual_summary_table = pd.DataFrame(columns=[
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'CONNECTED #', 'PTP ACC', 'TOTAL PTP AMOUNT', 'COLLECTORS COUNT'
            ])
            for date, group in df.groupby(df['Date'].dt.date):
                manual_group = group[group['Remark Type'] == 'Manual']

                accounts = manual_group['Account No.'].nunique()
                total_dialed = manual_group['Account No.'].count()
                connected = manual_group[manual_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()
                ptp_acc = manual_group[(manual_group['Status'].str.contains('PTP', na=False)) & 
                                       (manual_group['PTP Amount'] != 0)]['Account No.'].nunique()
                total_ptp_amount = manual_group[(manual_group['Status'].str.contains('PTP', na=False)) & 
                                                (manual_group['PTP Amount'] != 0)]['PTP Amount'].sum()

                # Calculate collectors count
                collectors_valid_group = manual_group[~manual_group['Remark By'].isin(excluded_collectors)]
                collectors_valid_group = collectors_valid_group[~collectors_valid_group['Remark'].str.contains('|'.join(excluded_remarks), case=False, na=False)]
                collectors_count = collectors_valid_group['Remark By'].nunique()

                manual_summary_table = pd.concat([manual_summary_table, pd.DataFrame([{
                    'Day': date,
                    'ACCOUNTS': accounts,
                    'TOTAL DIALED': total_dialed,
                    'CONNECTED #': connected,
                    'PTP ACC': ptp_acc,
                    'TOTAL PTP AMOUNT': total_ptp_amount,
                    'COLLECTORS COUNT': collectors_count
                }])], ignore_index=True)
            return manual_summary_table

        # Calculate Per Cycle Predictive Summary Table
        def calculate_per_cycle_predictive_summary(df):
            # Add similar logic to generate Per Cycle Predictive Summary Table
            pass

        # Calculate Per Cycle Manual Summary Table
        def calculate_per_cycle_manual_summary(df):
            # Add similar logic to generate Per Cycle Manual Summary Table
            pass

        # Generate all tables
        overall_combined_summary = calculate_combined_summary(df)
        overall_predictive_summary = calculate_predictive_summary(df)
        overall_manual_summary = calculate_manual_summary(df)

        st.subheader("Overall Combined Summary")
        st.dataframe(overall_combined_summary)

        st.subheader("Overall Predictive Summary")
        st.dataframe(overall_predictive_summary)

        st.subheader("Overall Manual Summary")
        st.dataframe(overall_manual_summary)
