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
    df = df[~df['Status'].str.contains('BP|ABORT', na=False)]
    
    # Exclude rows where REMARK contains certain keywords or phrases
    excluded_remarks = [
        "NEW", 
        "New files imported", 
        "Updates when case reassign to another collector", 
        "NDF IN ICS", 
        "FOR PULL OUT (END OF HANDLING PERIOD)", 
        "END OF HANDLING PERIOD",
        "1_Cured as of"  # Added new exclusion
    ]
    df = df[~df['Remark'].str.contains('|'.join(excluded_remarks), case=False, na=False)]

    # Check if data is empty after filtering
    if df.empty:
        st.warning("No valid data available after filtering.")
    else:
        # Calculate Combined Summary Table with Negative Call Drop
        def calculate_combined_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #', 'NEGATIVE CALL DROP #'
            ]) 

            # Filter for the remark types: Follow Up, Outgoing, and Predictive
            df = df[df['Remark Type'].isin(['Follow Up', 'Outgoing', 'Predictive'])]

            for date, group in df.groupby(df['Date'].dt.date):
                accounts = group[group['Remark'] != 'Broken Promise']['Account No.'].nunique()
                total_dialed = group[group['Remark'] != 'Broken Promise']['Account No.'].count()

                connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
                connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
                connected_acc = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
                ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

                # Drop Call Count: Calculate drop calls for both predictive and manual directly
                predictive_drop_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark By'] == 'SYSTEM')].shape[0]
                manual_drop_count = group[(group['Call Status'] == 'DROPPED') & 
                                           (group['Remark Type'] == 'Outgoing') & 
                                           (~group['Remark By'].str.upper().isin(['SYSTEM']))].shape[0]
                drop_call_count = predictive_drop_count + manual_drop_count

                call_drop_ratio = (drop_call_count / connected * 100) if connected != 0 else None

                # Negative Call Drop: Count for STATUS 'NEGATIVE CALLOUTS - DROP CALL'
                negative_call_drop_count = group[(group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) &
                                                  group['Remark Type'].isin(['Follow Up', 'Outgoing', 'Predictive'])].shape[0]

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
                    'CALL DROP #': drop_call_count,
                    'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                    'NEGATIVE CALL DROP #': negative_call_drop_count,
                }])], ignore_index=True)

            return summary_table

        # Display Combined Summary Table
        st.write("## Overall Combined Summary Table")
        combined_summary_table = calculate_combined_summary(df)
        st.write(combined_summary_table, container_width=True)

        def calculate_summary(df, remark_type, remark_by=None):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #', 'NEGATIVE CALL DROP #'
            ])

            for date, group in df.groupby(df['Date'].dt.date):
                accounts = group[(group['Remark Type'] == remark_type) | 
                                 ((group['Remark'] != 'Broken Promise') & 
                                  (group['Remark Type'] == 'Follow Up') & 
                                  (group['Remark By'] == remark_by))]['Account No.'].nunique()
                total_dialed = group[(group['Remark Type'] == remark_type) | 
                                     ((group['Remark'] != 'Broken Promise') & 
                                      (group['Remark Type'] == 'Follow Up') & 
                                      (group['Remark By'] == remark_by))]['Account No.'].count()

                connected = group[(group['Call Status'] == 'CONNECTED') & 
                                  (group['Remark Type'] == remark_type)]['Account No.'].count()
                connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
                connected_acc = group[(group['Call Status'] == 'CONNECTED') & 
                                      (group['Remark Type'] == remark_type)]['Account No.'].nunique()

                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & 
                                (group['PTP Amount'] != 0) & 
                                (group['Remark Type'] == remark_type)]['Account No.'].nunique()
                ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

                # Drop call count logic for the tables
                if remark_type == 'Predictive' and remark_by == 'SYSTEM':
                    drop_call_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark By'] == 'SYSTEM')]['Account No.'].count()
                elif remark_type == 'Outgoing' and remark_by is None:  # For manual, check only non-system agents
                    drop_call_count = group[(group['Call Status'] == 'DROPPED') & 
                                             (group['Remark Type'] == 'Outgoing') & 
                                             (~group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()

                call_drop_ratio = (drop_call_count / connected * 100) if connected != 0 else None

                # Negative Call Drop: Count for STATUS 'NEGATIVE CALLOUTS - DROP CALL'
                negative_call_drop_count = group[(group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) &
                                                  group['Remark Type'].isin([remark_type])].shape[0]

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
                    'CALL DROP #': drop_call_count,
                    'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                    'NEGATIVE CALL DROP #': negative_call_drop_count,
                }])], ignore_index=True)

            return summary_table

        # Create columns for side-by-side display
        col1, col2 = st.columns(2)

        # Display Overall Predictive Summary Table (Modified)
        with col1:
            st.write("## Overall Predictive Summary Table")
            overall_predictive_table = calculate_summary(df, 'Predictive', 'SYSTEM')
            st.write(overall_predictive_table)

        # Display Overall Manual Summary Table
        with col2:
            st.write("## Overall Manual Summary Table")
            overall_manual_table = calculate_summary(df, 'Outgoing')
            st.write(overall_manual_table)

        # Summary Table by Cycle Predictive (Modified)
        st.write("## Summary Table by Cycle Predictive")
        for cycle, cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {cycle}")
            cycle_group_filtered = cycle_group[cycle_group['Remark Type'].isin(['Follow Up', 'Predictive'])]
            summary_table = calculate_summary(cycle_group_filtered, 'Predictive', 'SYSTEM')
            st.write(summary_table)

        # Summary Table by Cycle Manual
        st.write("## Summary Table by Cycle Manual")
        for manual_cycle, manual_cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {manual_cycle}")
            summary_table = calculate_summary(manual_cycle_group, 'Outgoing')
            st.write(summary_table)
