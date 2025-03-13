import pandas as pd
import streamlit as st

# Set up the page configuration
st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

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

    # Ensure 'Time' column is in datetime format
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time

    # Filter out specific users based on 'Remark By'
    exclude_users = ['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                     'JGCELIZ', 'SPMADRID', 'RRCARLIT', 'MEBEJER',
                     'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 'EUGALERA','JATERRADO','LMLABRADOR']
    df = df[~df['Remark By'].isin(exclude_users)]

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
            'Day', 'Collector', 'Total Calls', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount', 'Talk Time (HH:MM:SS)'
        ])

        # Group by 'Date' and 'Remark By' (Collector)
        for (date, collector), collector_group in filtered_df[~filtered_df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([filtered_df['Date'].dt.date, 'Remark By']):
            # Calculate the metrics
            total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()

            # Filter rows where PTP Amount is not zero for balance calculation
            balance_amount = collector_group[(collector_group['Status'].str.contains('PTP', na=False)) & (collector_group['PTP Amount'] != 0)]['Balance'].sum()

            # Calculate talk time in minutes
            total_talk_time = collector_group['Talk Time Duration'].sum() / 60  # Convert from seconds to minutes

            # Round the total talk time to nearest second and convert to HH:MM:SS format
            rounded_talk_time = round(total_talk_time * 60)  # Round to nearest second
            talk_time_str = str(pd.to_timedelta(rounded_talk_time, unit='s'))  # Convert to Timedelta and then to string
            formatted_talk_time = talk_time_str.split()[2]  # Extract the time part from the string (HH:MM:SS)

            # Add the total calls (filter rows based on Remark Type)
            total_calls = collector_group[
                collector_group['Remark Type'].str.contains('OUTGOING|FOLLOWUP|PREDICTIVE', case=False, na=False) &
                ~collector_group['Remark By'].isin(exclude_users)
            ].shape[0]

            # Add the row to the summary with Total Calls after Collector
            collector_summary = pd.concat([collector_summary, pd.DataFrame([{
                'Day': date,
                'Collector': collector,
                'Total Calls': total_calls,  # Move Total Calls after Collector
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
                'Balance Amount': balance_amount,
                'Talk Time (HH:MM:SS)': formatted_talk_time,  # Add formatted talk time
            }])], ignore_index=True)

        # Calculate and append totals for the collector summary
        total_calls = collector_summary['Total Calls'].sum()  # Total Calls count across all collectors

        # Calculate the total talk time for the total row
        total_talk_time_minutes = collector_summary['Talk Time (HH:MM:SS)'].apply(
            lambda x: pd.to_timedelta(x).total_seconds() / 60).sum()  # Sum the talk time in minutes

        # Round the total talk time to the nearest second before converting to HH:MM:SS
        rounded_total_talk_time_minutes = round(total_talk_time_minutes)

        # Format the total talk time as HH:MM:SS
        rounded_total_talk_time_seconds = round(rounded_total_talk_time_minutes * 60)  # Round to nearest second
        total_talk_time_str = str(pd.to_timedelta(rounded_total_talk_time_seconds, unit='s')).split()[2]

        total_row = pd.DataFrame([{
            'Day': 'Total',
            'Collector': '',
            'Total Calls': total_calls,  # Total Calls is now after Collector
            'Total Connected': collector_summary['Total Connected'].sum(),
            'Total PTP': collector_summary['Total PTP'].sum(),
            'Total RPC': collector_summary['Total RPC'].sum(),
            'PTP Amount': collector_summary['PTP Amount'].sum(),
            'Balance Amount': collector_summary['Balance Amount'].sum(),
            'Talk Time (HH:MM:SS)': total_talk_time_str,  # Add formatted total talk time
        }])

        collector_summary = pd.concat([collector_summary, total_row], ignore_index=True)

        # Round off numeric columns to 2 decimal places
        collector_summary[['PTP Amount', 'Balance Amount']] = collector_summary[['PTP Amount', 'Balance Amount']].round(2)

        # Reorder columns to ensure Total Calls is after Collector
        column_order = ['Day', 'Collector', 'Total Calls', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount', 'Talk Time (HH:MM:SS)']
        collector_summary = collector_summary[column_order]

        st.write(collector_summary)
