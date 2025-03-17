import pandas as pd
import streamlit as st

# Set up the page configuration
st.set_page_config(layout="wide", page_title="AGENTS BEHAVIOR", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode styling
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

# Title of the app
st.title('Daily Remark Summary')

# Data loading function with file upload support
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

# File uploader for Excel file
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
        "1_Cured as of"
    ]

    # Create a mask to exclude remarks that contain any of the excluded phrases
    df = df[~df['Remark'].str.contains('|'.join(excluded_remarks), case=False, na=False)]

    # Exclude rows where 'Debtor' contains "DEFAULT_LEAD_"
    df = df[~df['Debtor'].str.contains('DEFAULT_LEAD_', na=False)]

    # Create the columns layout
    col1, col2 = st.columns(2)

    with col1:
        st.write("## Summary Table by Collector per Day")

        # Add date filter
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

        filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

        # Initialize an empty DataFrame for the summary table by collector
        collector_summary = pd.DataFrame(columns=[ 
            'Day', 'Collector', 'Campaign', 'Total Manual Calls', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount', 'Talk Time (HH:MM:SS)', 'Dropped Calls Count'
        ])

        # Group by 'Date' and 'Remark By' (Collector)
        for (date, collector), collector_group in filtered_df[~filtered_df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([filtered_df['Date'].dt.date, 'Remark By']):
            campaign = collector_group['Client'].iloc[0] if 'Client' in collector_group.columns else 'N/A'

            total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            balance_amount = collector_group[(collector_group['Status'].str.contains('PTP', na=False)) & (collector_group['PTP Amount'] != 0)]['Balance'].sum()
            
            ptp_amount = round(ptp_amount, 2)
            balance_amount = round(balance_amount, 2)

            total_talk_time = collector_group['Talk Time Duration'].sum() / 60
            rounded_talk_time = round(total_talk_time * 60)
            talk_time_str = str(pd.to_timedelta(rounded_talk_time, unit='s'))
            formatted_talk_time = talk_time_str.split()[2]

            # **Filter only OUTGOING calls for Total Manual Calls**
            total_manual_calls = collector_group[collector_group['Remark Type'].str.contains('OUTGOING', case=False, na=False)].shape[0]

            collector_summary = pd.concat([collector_summary, pd.DataFrame([{
                'Day': date,
                'Collector': collector,
                'Campaign': campaign,
                'Total Manual Calls': total_manual_calls,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
                'Balance Amount': balance_amount,
                'Talk Time (HH:MM:SS)': formatted_talk_time,
                'Dropped Calls Count': 0,  # Placeholder for dropped call count
            }])], ignore_index=True)

        # Now, let's add the dropped call count based on specific conditions (system dropped and follow-up/predictive remarks)
        dropped_calls_mask = (df['Status'].str.contains('dropped', case=False, na=False)) & \
                             (df['Remark Type'].str.contains('follow up|predictive', case=False, na=False))

        # Get the count of dropped calls for each group based on date and collector
        dropped_calls_summary = df[dropped_calls_mask].groupby([df['Date'].dt.date, 'Remark By']).size().reset_index(name='Dropped Calls Count')

        # Merge this summary with the existing collector summary
        collector_summary_final = pd.merge(collector_summary, dropped_calls_summary, how='left', on=['Day', 'Collector'])

        # Optional: Fill NaN values in the "Dropped Calls Count" column with 0
        collector_summary_final['Dropped Calls Count'] = collector_summary_final['Dropped Calls Count'].fillna(0).astype(int)

        # Formatting the columns to add comma style for amounts
        collector_summary_final['PTP Amount'] = collector_summary_final['PTP Amount'].apply(lambda x: f"{x:,.2f}")
        collector_summary_final['Balance Amount'] = collector_summary_final['Balance Amount'].apply(lambda x: f"{x:,.2f}")

        # Remove the index column from the Excel export (for display)
        collector_summary_final = collector_summary_final.reset_index(drop=True)

        # Display the final summary table without index
        st.write(collector_summary_final)

        # Add download button for the table in Excel format (without index)
        @st.cache_data
        def to_excel(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Summary")
            processed_data = output.getvalue()
            return processed_data

        excel_data = to_excel(collector_summary_final)

        # Download button for Excel file with dropped calls count
        st.download_button(
            label="Download Updated Excel File with Dropped Calls",
            data=excel_data,
            file_name="collector_summary_with_dropped_calls.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
