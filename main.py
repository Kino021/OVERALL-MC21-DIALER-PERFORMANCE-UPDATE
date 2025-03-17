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
        # Per Cycle Predictive Summary Table (Sum by Date for each Cycle)
        def calculate_per_cycle_predictive_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Cycle', 'Date', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'NEGATIVE CALL DROP #', 
                'SYSTEM DROP', 'CALL DROP RATIO #'
            ]) 

            df_filtered = df[df['Remark Type'].isin(['Predictive', 'Follow Up'])]

            for cycle, group in df_filtered.groupby('Service No.'):
                # Aggregate by Date (Remove Time)
                aggregated_data = group.groupby('Date').agg(
                    ACCOUNTS=('Account No.', 'nunique'),
                    TOTAL_DIALED=('Account No.', 'count'),
                    CONNECTED=('Call Status', lambda x: (x == 'CONNECTED').sum()),
                    CONNECTED_ACC=('Call Status', lambda x: (x == 'CONNECTED').count()),
                    PTP_ACC=('Status', lambda x: x.str.contains('PTP').sum()),
                    NEGATIVE_CALL_DROP=('Remark By', lambda x: x.str.contains('NEGATIVE CALLOUTS - DROP CALL').sum()),
                    SYSTEM_DROP=('Remark By', lambda x: x.str.contains('SYSTEM').sum())
                ).reset_index()

                # Format Date to display only the date part
                aggregated_data['Date'] = aggregated_data['Date'].dt.date

                # Calculate derived columns
                for idx, row in aggregated_data.iterrows():
                    penetration_rate = (row['TOTAL_DIALED'] / row['ACCOUNTS'] * 100) if row['ACCOUNTS'] != 0 else None
                    connected_rate = (row['CONNECTED_ACC'] / row['TOTAL_DIALED'] * 100) if row['TOTAL_DIALED'] != 0 else None
                    ptp_rate = (row['PTP_ACC'] / row['CONNECTED'] * 100) if row['CONNECTED'] != 0 else None
                    call_drop_ratio = (row['SYSTEM_DROP'] / row['CONNECTED_ACC'] * 100) if row['CONNECTED_ACC'] != 0 else None

                    summary_table = pd.concat([summary_table, pd.DataFrame([{
                        'Cycle': cycle,
                        'Date': row['Date'],
                        'ACCOUNTS': row['ACCOUNTS'],
                        'TOTAL DIALED': row['TOTAL_DIALED'],
                        'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                        'CONNECTED #': row['CONNECTED'],
                        'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                        'CONNECTED ACC': row['CONNECTED_ACC'],
                        'PTP ACC': row['PTP_ACC'],
                        'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                        'NEGATIVE CALL DROP #': row['NEGATIVE_CALL_DROP'],
                        'SYSTEM DROP': row['SYSTEM_DROP'],
                        'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                    }])], ignore_index=True)

            return summary_table

        # Display Per Cycle Predictive Summary Table
        st.write("## Per Cycle Predictive Summary Table")
        per_cycle_predictive_table = calculate_per_cycle_predictive_summary(df)
        st.write(per_cycle_predictive_table)

        # Per Cycle Manual Summary Table (Sum by Date for each Cycle)
        def calculate_per_cycle_manual_summary(df):
            summary_table = pd.DataFrame(columns=[ 
                'Cycle', 'Date', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'NEGATIVE CALL DROP #', 
                'CALL DROP RATIO #'
            ]) 

            df_filtered = df[df['Remark Type'] == 'Outgoing']

            for cycle, group in df_filtered.groupby('Service No.'):
                # Aggregate by Date (Remove Time)
                aggregated_data = group.groupby('Date').agg(
                    ACCOUNTS=('Account No.', 'nunique'),
                    TOTAL_DIALED=('Account No.', 'count'),
                    CONNECTED=('Call Status', lambda x: (x == 'CONNECTED').sum()),
                    CONNECTED_ACC=('Call Status', lambda x: (x == 'CONNECTED').count()),
                    PTP_ACC=('Status', lambda x: x.str.contains('PTP').sum()),
                    NEGATIVE_CALL_DROP=('Remark By', lambda x: x.str.contains('NEGATIVE CALLOUTS - DROP CALL').sum())
                ).reset_index()

                # Format Date to display only the date part
                aggregated_data['Date'] = aggregated_data['Date'].dt.date

                # Calculate derived columns
                for idx, row in aggregated_data.iterrows():
                    penetration_rate = (row['TOTAL_DIALED'] / row['ACCOUNTS'] * 100) if row['ACCOUNTS'] != 0 else None
                    connected_rate = (row['CONNECTED_ACC'] / row['TOTAL_DIALED'] * 100) if row['TOTAL_DIALED'] != 0 else None
                    ptp_rate = (row['PTP_ACC'] / row['CONNECTED'] * 100) if row['CONNECTED'] != 0 else None
                    call_drop_ratio = (row['NEGATIVE_CALL_DROP'] / row['CONNECTED_ACC'] * 100) if row['CONNECTED_ACC'] != 0 else None

                    summary_table = pd.concat([summary_table, pd.DataFrame([{
                        'Cycle': cycle,
                        'Date': row['Date'],
                        'ACCOUNTS': row['ACCOUNTS'],
                        'TOTAL DIALED': row['TOTAL_DIALED'],
                        'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                        'CONNECTED #': row['CONNECTED'],
                        'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                        'CONNECTED ACC': row['CONNECTED_ACC'],
                        'PTP ACC': row['PTP_ACC'],
                        'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                        'NEGATIVE CALL DROP #': row['NEGATIVE_CALL_DROP'],
                        'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                    }])], ignore_index=True)

            return summary_table

        # Display Per Cycle Manual Summary Table
        st.write("## Per Cycle Manual Summary Table")
        per_cycle_manual_table = calculate_per_cycle_manual_summary(df)
        st.write(per_cycle_manual_table)
