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
        # Per Cycle Predictive Summary Table
        def calculate_per_cycle_predictive_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Cycle', 'Date', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 
                'SYSTEM DROP', 'CALL DROP RATIO #'
            ]) 

            # Filter the dataframe to include only 'Follow Up' and 'Predictive' Remark Types
            df_filtered = df[df['Remark Type'].isin(['Predictive', 'Follow Up'])]

            for cycle, group in df_filtered.groupby('Service No.'):
                for date, date_group in group.groupby(group['Date'].dt.date):  # Group by Date within each Cycle
                    # Accounts: Count unique Account No. where Remark Type is Predictive or Follow Up
                    accounts = date_group[date_group['Remark Type'].isin(['Predictive', 'Follow Up'])]['Account No.'].nunique()

                    # Total Dialed: Count Account No. where Remark Type is Predictive or Follow Up (without uniqueness)
                    total_dialed = date_group[date_group['Remark Type'].isin(['Predictive', 'Follow Up'])]['Account No.'].count()

                    # Connected: Count unique Account No. where Call Status is CONNECTED
                    connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

                    # Penetration Rate: Total Dialed / Accounts * 100
                    penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                    # Connected ACC: Count non-unique Account No. where Call Status is CONNECTED
                    connected_acc = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()

                    # Connected Rate: Connected ACC / Total Dialed * 100
                    connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None

                    # PTP ACC: Count unique Account No. where Status contains PTP and PTP Amount is not 0
                    ptp_acc = date_group[(date_group['Status'].str.contains('PTP', na=False)) & (date_group['PTP Amount'] != 0)]['Account No.'].nunique()

                    # PTP Rate: PTP ACC / Connected # * 100
                    ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None

                    # System Drop: Count rows where Status contains DROPPED and Remark By is SYSTEM
                    system_drop = date_group[(date_group['Status'].str.contains('DROPPED', na=False)) & (date_group['Remark By'] == 'SYSTEM')]['Account No.'].count()

                    # Call Drop: Count rows where Status contains NEGATIVE CALLOUTS - DROP CALL and Remark By is not SYSTEM
                    call_drop_count = date_group[(date_group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                                (~date_group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()

                    # Call Drop Ratio: System Drop / Connected ACC * 100
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
                        'CALL DROP #': call_drop_count,
                        'SYSTEM DROP': system_drop,
                        'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                    }])], ignore_index=True)

            return summary_table

        # Display Per Cycle Predictive Summary Table
        st.write("## Per Cycle Predictive Summary Table")
        per_cycle_predictive_table = calculate_per_cycle_predictive_summary(df)
        st.write(per_cycle_predictive_table)

        # Per Cycle Manual Summary Table
        def calculate_per_cycle_manual_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Cycle', 'Date', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 
                'CALL DROP RATIO #'
            ]) 

            # Filter the dataframe to include only 'Outgoing' Remark Type
            df_filtered = df[df['Remark Type'] == 'Outgoing']

            for cycle, group in df_filtered.groupby('Service No.'):
                for date, date_group in group.groupby(group['Date'].dt.date):  # Group by Date within each Cycle
                    # Accounts: Count unique Account No. where Remark Type is Outgoing
                    accounts = date_group[date_group['Remark Type'] == 'Outgoing']['Account No.'].nunique()

                    # Total Dialed: Count Account No. where Remark Type is Outgoing (without uniqueness)
                    total_dialed = date_group[date_group['Remark Type'] == 'Outgoing']['Account No.'].count()

                    # Connected: Count unique Account No. where Call Status is CONNECTED
                    connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

                    # Penetration Rate: Total Dialed / Accounts * 100
                    penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                    # Connected ACC: Count non-unique Account No. where Call Status is CONNECTED
                    connected_acc = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()

                    # Connected Rate: Connected ACC / Total Dialed * 100
                    connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None

                    # PTP ACC: Count unique Account No. where Status contains PTP and PTP Amount is not 0
                    ptp_acc = date_group[(date_group['Status'].str.contains('PTP', na=False)) & (date_group['PTP Amount'] != 0)]['Account No.'].nunique()

                    # PTP Rate: PTP ACC / Connected # * 100
                    ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None

                    # Call Drop: Count rows where Status contains NEGATIVE CALLOUTS - DROP CALL and Remark By is not SYSTEM
                    call_drop_count = date_group[(date_group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                                (~date_group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()

                    # Call Drop Ratio: Call Drop Count / Connected ACC * 100
                    call_drop_ratio = (call_drop_count / connected_acc * 100) if connected_acc != 0 else None

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
                        'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                    }])], ignore_index=True)

            return summary_table

        # Display Per Cycle Manual Summary Table
        st.write("## Per Cycle Manual Summary Table")
        per_cycle_manual_table = calculate_per_cycle_manual_summary(df)
        st.write(per_cycle_manual_table)
