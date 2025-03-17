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

    # Exclude rows where STATUS contains only 'ABORT' (BP and NEW are retained)
    df = df[~df['Status'].str.contains('ABORT', na=False)]

    # Define excluded remarks correctly with commas
    excluded_remarks = [
        "Broken Promise",  
        "New files imported",  
        "Updates when case reassign to another collector",  
        "NDF IN ICS",  
        "FOR PULL OUT (END OF HANDLING PERIOD)",  
        "END OF HANDLING PERIOD",  
        "1_Cured as of"  # Added new exclusion
    ]

    # Create a mask to exclude remarks that contain any of the excluded phrases
    df = df[~df['Remark'].str.contains('|'.join(excluded_remarks), case=False, na=False)]
    
    # Exclude remarks only if they do not contain the inclusion phrase
    df = df[~mask_exclude | mask_include]


    # Check if data is empty after filtering
    if df.empty:
        st.warning("No valid data available after filtering.")
    else:
        # Calculate Combined Summary Table with Negative Call Drop
        def calculate_combined_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'SYSTEM CALL DROP #', 'NEGATIVE CALL DROP #', 'CALL DROP RATIO #'
            ]) 

            # Filter for the remark types: Follow Up, Outgoing, and Predictive
            df = df[df['Remark Type'].isin(['Follow Up', 'Outgoing', 'Predictive'])]

            for date, group in df.groupby(df['Date'].dt.date):
                # Accounts: Count unique Account No. with the given Remark Types
                accounts = group[group['Remark Type'].isin(['Follow Up', 'Outgoing', 'Predictive'])]['Account No.'].nunique()
                total_dialed = group[group['Remark Type'].isin(['Follow Up', 'Outgoing', 'Predictive'])]['Account No.'].count()

                # Connected: Count unique Account No. where Call Status is 'CONNECTED'
                connected = group[(group['Call Status'] == 'CONNECTED') & 
                                  group['Remark Type'].isin(['Follow Up', 'Outgoing', 'Predictive'])]['Account No.'].count()
                connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
                connected_acc = group[(group['Call Status'] == 'CONNECTED') & 
                                      group['Remark Type'].isin(['Follow Up', 'Outgoing', 'Predictive'])]['Account No.'].nunique()

                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                # PTP ACC: Count unique Account No. where PTP Amount is not zero and Remark Type is valid
                ptp_acc = group[(group['PTP Amount'] > 0) & 
                                group['Remark Type'].isin(['Follow Up', 'Outgoing', 'Predictive'])]['Account No.'].nunique()
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
                    'SYSTEM CALL DROP #': drop_call_count,  # Changed to UPPERCASE
                    'NEGATIVE CALL DROP #': negative_call_drop_count,  # Moved after 'SYSTEM CALL DROP #'
                    'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                }])], ignore_index=True)

            return summary_table

        # Display Combined Summary Table
        st.write("## Overall Combined Summary Table")
        combined_summary_table = calculate_combined_summary(df)
        st.write(combined_summary_table, container_width=True)

        # Additional logic for individual summaries by remark type (Follow Up, Outgoing, Predictive)
        def calculate_summary(df, remark_types):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'SYSTEM CALL DROP #', 'NEGATIVE CALL DROP #', 'CALL DROP RATIO #'
            ])

            for date, group in df.groupby(df['Date'].dt.date):
                # Filter for multiple remark types (Follow Up and Predictive)
                accounts = group[group['Remark Type'].isin(remark_types)]['Account No.'].nunique()
                total_dialed = group[group['Remark Type'].isin(remark_types)]['Account No.'].count()

                connected = group[(group['Call Status'] == 'CONNECTED') & 
                                  group['Remark Type'].isin(remark_types)]['Account No.'].count()
                connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
                connected_acc = group[(group['Call Status'] == 'CONNECTED') & 
                                      group['Remark Type'].isin(remark_types)]['Account No.'].nunique()

                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                ptp_acc = group[(group['PTP Amount'] > 0) & 
                                group['Remark Type'].isin(remark_types)]['Account No.'].nunique()
                ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

                predictive_drop_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark By'] == 'SYSTEM')].shape[0]
                manual_drop_count = group[(group['Call Status'] == 'DROPPED') & 
                                           (group['Remark Type'] == 'Outgoing') & 
                                           (~group['Remark By'].str.upper().isin(['SYSTEM']))].shape[0]
                drop_call_count = predictive_drop_count + manual_drop_count

                call_drop_ratio = (drop_call_count / connected * 100) if connected != 0 else None

                # Negative Call Drop: Count for STATUS 'NEGATIVE CALLOUTS - DROP CALL'
                negative_call_drop_count = group[(group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                                  group['Remark Type'].isin(remark_types)].shape[0]

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
                    'SYSTEM CALL DROP #': drop_call_count, 
                    'NEGATIVE CALL DROP #': negative_call_drop_count, 
                    'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                }])], ignore_index=True)

            return summary_table

        # Create columns for side-by-side display
        col1, col2 = st.columns(2)

        # Display Overall Predictive + Follow Up Summary Table
        with col1:
            st.write("## Overall Predictive + Follow Up Summary Table")  
            overall_predictive_table = calculate_summary(df, ['Follow Up', 'Predictive'])
            st.write(overall_predictive_table)

        # Display Overall Manual Summary Table (excluding SYSTEM CALL DROP #)
        with col2:
            st.write("## Overall Manual Summary Table")
            overall_manual_table = calculate_summary(df, ['Outgoing'])
            # Remove SYSTEM CALL DROP # column
            overall_manual_table = overall_manual_table.drop(columns=['SYSTEM CALL DROP #'], errors='ignore')
            st.write(overall_manual_table)
