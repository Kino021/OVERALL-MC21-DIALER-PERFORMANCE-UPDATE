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
        # Overall Combined Summary Table
        def calculate_combined_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 
                'SYSTEM DROP', 'CALL DROP RATIO #'
            ]) 

            for date, group in df.groupby(df['Date'].dt.date):
                # Accounts: Count unique Account No. where Remark Type is Predictive, Follow Up, or Outgoing
                accounts = group[group['Remark Type'].isin(['Predictive', 'Follow Up', 'Outgoing'])]['Account No.'].nunique()
                
                # Total Dialed: Count Account No. where Remark Type is Predictive, Follow Up, or Outgoing (without uniqueness)
                total_dialed = group[group['Remark Type'].isin(['Predictive', 'Follow Up', 'Outgoing'])]['Account No.'].count()

                # Connected: Count unique Account No. where Call Status is CONNECTED
                connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

                # Penetration Rate: Total Dialed / Accounts * 100
                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                # Connected ACC: Count non-unique Account No. where Call Status is CONNECTED
                connected_acc = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()

                # Connected Rate: Connected ACC / Total Dialed * 100
                connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None

                # PTP ACC: Count unique Account No. where Status contains PTP and PTP Amount is not 0
                ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0)]['Account No.'].nunique()

                # PTP Rate: PTP ACC / Connected # * 100
                ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None

                # System Drop: Count rows where Status contains DROPPED and Remark By is SYSTEM
                system_drop = group[(group['Status'].str.contains('DROPPED', na=False)) & (group['Remark By'] == 'SYSTEM')]['Account No.'].count()

                # Call Drop: Count rows where Status contains NEGATIVE CALLOUTS - DROP CALL and Remark By is not SYSTEM
                call_drop_count = group[(group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                        (~group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()

                # Call Drop Ratio: System Drop / Connected ACC * 100
                call_drop_ratio = (system_drop / connected_acc * 100) if connected_acc != 0 else None

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
                    'SYSTEM DROP': system_drop,
                    'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                }])], ignore_index=True)

            return summary_table

        # Display Combined Summary Table
        st.write("## Overall Combined Summary Table")
        combined_summary_table = calculate_combined_summary(df)
        st.write(combined_summary_table, container_width=True)

        # Overall Predictive Summary Table
        def calculate_predictive_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 
                'SYSTEM DROP', 'CALL DROP RATIO #'
            ]) 

            # Filter the dataframe to include only 'Follow Up' and 'Predictive' Remark Types
            df_filtered = df[df['Remark Type'].isin(['Predictive', 'Follow Up'])]

            for date, group in df_filtered.groupby(df_filtered['Date'].dt.date):
                # Accounts: Count unique Account No. where Remark Type is Predictive or Follow Up
                accounts = group[group['Remark Type'].isin(['Predictive', 'Follow Up'])]['Account No.'].nunique()
                
                # Total Dialed: Count Account No. where Remark Type is Predictive or Follow Up (without uniqueness)
                total_dialed = group[group['Remark Type'].isin(['Predictive', 'Follow Up'])]['Account No.'].count()

                # Connected: Count unique Account No. where Call Status is CONNECTED
                connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

                # Penetration Rate: Total Dialed / Accounts * 100
                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                # Connected ACC: Count non-unique Account No. where Call Status is CONNECTED
                connected_acc = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()

                # Connected Rate: Connected ACC / Total Dialed * 100
                connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None

                # PTP ACC: Count unique Account No. where Status contains PTP and PTP Amount is not 0
                ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0)]['Account No.'].nunique()

                # PTP Rate: PTP ACC / Connected # * 100
                ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None

                # System Drop: Count rows where Status contains DROPPED and Remark By is SYSTEM
                system_drop = group[(group['Status'].str.contains('DROPPED', na=False)) & (group['Remark By'] == 'SYSTEM')]['Account No.'].count()

                # Call Drop: Count rows where Status contains NEGATIVE CALLOUTS - DROP CALL and Remark By is not SYSTEM
                call_drop_count = group[(group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                        (~group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()

                # Call Drop Ratio: System Drop / Connected ACC * 100
                call_drop_ratio = (system_drop / connected_acc * 100) if connected_acc != 0 else None

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
                    'SYSTEM DROP': system_drop,
                    'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                }])], ignore_index=True)

            return summary_table

        # Display Overall Predictive Summary Table
        st.write("## Overall Predictive Summary Table")
        overall_predictive_table = calculate_predictive_summary(df)
        st.write(overall_predictive_table)

        # Overall Manual Summary Table
        def calculate_manual_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 
                'CALL DROP RATIO #'
            ]) 

            # Filter the dataframe to include only 'Outgoing' Remark Type
            df_filtered = df[df['Remark Type'] == 'Outgoing']

            for date, group in df_filtered.groupby(df_filtered['Date'].dt.date):
                # Accounts: Count unique Account No. where Remark Type is Outgoing
                accounts = group[group['Remark Type'] == 'Outgoing']['Account No.'].nunique()
                
                # Total Dialed: Count Account No. where Remark Type is Outgoing (without uniqueness)
                total_dialed = group[group['Remark Type'] == 'Outgoing']['Account No.'].count()

                # Connected: Count unique Account No. where Call Status is CONNECTED
                connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

                # Penetration Rate: Total Dialed / Accounts * 100
                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                # Connected ACC: Count non-unique Account No. where Call Status is CONNECTED
                connected_acc = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()

                # Connected Rate: Connected ACC / Total Dialed * 100
                connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None

                # PTP ACC: Count unique Account No. where Status contains PTP and PTP Amount is not 0
                ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0)]['Account No.'].nunique()

                # PTP Rate: PTP ACC / Connected # * 100
                ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None

                # Call Drop: Count rows where Status contains NEGATIVE CALLOUTS - DROP CALL and Remark By is not SYSTEM
                call_drop_count = group[(group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                        (~group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()

                # Call Drop Ratio: Call Drop Count / Connected ACC * 100
                call_drop_ratio = (call_drop_count / connected_acc * 100) if connected_acc != 0 else None

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

        # Display Overall Manual Summary Table
        st.write("## Overall Manual Summary Table")
        overall_manual_table = calculate_manual_summary(df)
        st.write(overall_manual_table)
