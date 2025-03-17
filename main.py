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
        # Calculate Combined Summary Table based on 'FOLLOW UP', 'OUTGOING', and 'PREDICTIVE' Remark Types
        def calculate_combined_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #'
            ]) 

            for date, group in df.groupby(df['Date'].dt.date):
                # Filter based on Remark Types: 'FOLLOW UP', 'OUTGOING', 'PREDICTIVE'
                group_filtered = group[group['Remark Type'].isin(['FOLLOW UP', 'OUTGOING', 'PREDICTIVE'])]

                accounts = group_filtered[group_filtered['Remark'] != 'Broken Promise']['Account No.'].nunique()
                total_dialed = group_filtered[group_filtered['Remark'] != 'Broken Promise']['Account No.'].count()

                connected = group_filtered[group_filtered['Call Status'] == 'CONNECTED']['Account No.'].count()
                connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
                connected_acc = group_filtered[group_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()

                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                ptp_acc = group_filtered[(group_filtered['Status'].str.contains('PTP', na=False)) & (group_filtered['PTP Amount'] != 0)]['Account No.'].nunique()
                ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

                # Drop Call Count: Calculate drop calls for both predictive and manual directly
                predictive_drop_count = group_filtered[(group_filtered['Call Status'] == 'DROPPED') & (group_filtered['Remark By'] == 'SYSTEM')].shape[0]
                manual_drop_count = group_filtered[(group_filtered['Call Status'] == 'DROPPED') & 
                                                   (group_filtered['Remark Type'] == 'Outgoing') & 
                                                   (~group_filtered['Remark By'].str.upper().isin(['SYSTEM']))].shape[0]
                drop_call_count = predictive_drop_count + manual_drop_count

                call_drop_ratio = (drop_call_count / connected * 100) if connected != 0 else None

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
                }])], ignore_index=True)

            return summary_table

        # Display Combined Summary Table
        st.write("## Overall Combined Summary Table (Follow Up, Outgoing, Predictive Remark Types)")
        combined_summary_table = calculate_combined_summary(df)
        st.write(combined_summary_table, container_width=True)

        # Calculate Summary Table for 'PREDICTIVE' and 'FOLLOW UP'
        def calculate_summary(df, remark_type):
            summary_table = pd.DataFrame(columns=[ 
                'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #'
            ])

            for date, group in df.groupby(df['Date'].dt.date):
                group_filtered = group[group['Remark Type'] == remark_type]

                accounts = group_filtered[group_filtered['Remark'] != 'Broken Promise']['Account No.'].nunique()
                total_dialed = group_filtered[group_filtered['Remark'] != 'Broken Promise']['Account No.'].count()

                connected = group_filtered[group_filtered['Call Status'] == 'CONNECTED']['Account No.'].count()
                connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
                connected_acc = group_filtered[group_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()

                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

                ptp_acc = group_filtered[(group_filtered['Status'].str.contains('PTP', na=False)) & (group_filtered['PTP Amount'] != 0)]['Account No.'].nunique()
                ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

                # Drop call count logic for the tables
                drop_call_count = group_filtered[(group_filtered['Call Status'] == 'DROPPED')]['Account No.'].count()
                call_drop_ratio = (drop_call_count / connected * 100) if connected != 0 else None

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
                }])], ignore_index=True)

            return summary_table

        # Create columns for side-by-side display
        col1, col2 = st.columns(2)

        # Display Overall Predictive Summary Table
        with col1:
            st.write("## Overall Predictive Summary Table (Predictive, Follow Up Remark Types)")
            overall_predictive_table = calculate_summary(df, 'Predictive')
            st.write(overall_predictive_table)

        # Display Overall Manual Summary Table
        with col2:
            st.write("## Overall Manual Summary Table (Outgoing Remark Type)")
            overall_manual_table = calculate_summary(df, 'Outgoing')
            st.write(overall_manual_table)

        # Summary Table by Cycle Predictive
        st.write("## Summary Table by Cycle Predictive")
        for cycle, cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {cycle}")
            summary_table = calculate_summary(cycle_group, 'Predictive')
            st.write(summary_table)

        # Summary Table by Cycle Manual
        st.write("## Summary Table by Cycle Manual")
        for manual_cycle, manual_cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {manual_cycle}")
            summary_table = calculate_summary(manual_cycle_group, 'Outgoing')
            st.write(summary_table)
