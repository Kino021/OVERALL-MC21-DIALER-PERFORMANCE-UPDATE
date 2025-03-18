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
        # New Dialer Report Balance Summary Table
        def calculate_balance_summary(df):
            balance_summary = pd.DataFrame(columns=[ 
                'Balance Range', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
                'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 
                'SYSTEM DROP', 'CALL DROP RATIO #'
            ]) 

            # Define the balance ranges
            balance_ranges = [
                (6000.00, 49000.00),  # 6,000 to 49,000
                (50000.00, 99000.00),  # 50,000 to 99,000
                (100000.00, float('inf'))  # 100,000 and above
            ]

            # Process the data for each balance range
            for lower, upper in balance_ranges:
                df_filtered = df[(df['Balance'] >= lower) & (df['Balance'] <= upper)]

                # Calculate metrics for each balance range
                accounts = df_filtered['Account No.'].nunique()
                total_dialed = df_filtered['Account No.'].count()
                connected = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()
                penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None
                connected_acc = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].count()
                connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None
                ptp_acc = df_filtered[(df_filtered['Status'].str.contains('PTP', na=False)) & (df_filtered['PTP Amount'] != 0)]['Account No.'].nunique()
                ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
                system_drop = df_filtered[(df_filtered['Status'].str.contains('DROPPED', na=False)) & (df_filtered['Remark By'] == 'SYSTEM')]['Account No.'].count()
                call_drop_count = df_filtered[(df_filtered['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                              (~df_filtered['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()
                call_drop_ratio = (system_drop / connected_acc * 100) if connected_acc != 0 else None

                balance_range_str = f"{lower:,.2f} to {upper:,.2f}" if upper != float('inf') else f"{lower:,.2f} and above"

                balance_summary = pd.concat([balance_summary, pd.DataFrame([{
                    'Balance Range': balance_range_str,
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

            return balance_summary

        # Display Dialer Report Balance Summary Table
        st.write("## Dialer Report Balance Summary Table")
        balance_summary_table = calculate_balance_summary(df)
        st.write(balance_summary_table)

        # Overall Combined Summary Table (existing)
        st.write("## Overall Combined Summary Table")
        combined_summary_table = calculate_combined_summary(df)
        st.write(combined_summary_table)

        # (Continue with the existing summary tables...)
