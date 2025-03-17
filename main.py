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
            'Day', 'Collector', 'Campaign', 'Total Manual Calls', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount', 'Talk Time (HH:MM:SS)', 'System Call Drop'
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

            # Calculate System Call Drop count where Status contains 'DROPPED' and Remark Type is 'Follow Up' or 'Predictive'
            system_call_drop = collector_group[
                (collector_group['Status'].str.contains('DROPPED', na=False)) & 
                (collector_group['Remark Type'].isin(['Follow Up', 'Predictive']))
            ].shape[0]

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
                'System Call Drop': system_call_drop
            }])], ignore_index=True)

        collector_summary[['PTP Amount', 'Balance Amount']] = collector_summary[['PTP Amount', 'Balance Amount']].round(2)

        # Calculate total values for the summary table
        total_row = collector_summary[['Total Manual Calls', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount', 'System Call Drop']].sum()

        # Calculate the total talk time separately
        total_talk_time_seconds = collector_summary['Talk Time (HH:MM:SS)'].apply(lambda x: pd.to_timedelta(x).total_seconds()).sum()
        total_talk_time_formatted = str(pd.to_timedelta(total_talk_time_seconds, unit='s')).split()[2]

        # Add total row at the end
        total_row['Day'] = 'Total'
        total_row['Collector'] = ''
        total_row['Campaign'] = ''
        total_row['Talk Time (HH:MM:SS)'] = total_talk_time_formatted
        
        # Save the "Total" row separately for later
        total_row_df = total_row.to_frame().T

        # Remove the "Total" row from the summary before sorting
        collector_summary_without_total = collector_summary[collector_summary['Day'] != 'Total']

        # Sort by 'Total PTP' in descending order, excluding the "Total" row
        collector_summary_sorted = collector_summary_without_total.sort_values(by='Total PTP', ascending=False, na_position='last')

        # Append the "Total" row at the bottom after sorting
        collector_summary_final = pd.concat([collector_summary_sorted, total_row_df], ignore_index=True)

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

        # Download button for Excel file
        st.download_button(
            label="Download Excel File",
            data=excel_data,
            file_name="collector_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
