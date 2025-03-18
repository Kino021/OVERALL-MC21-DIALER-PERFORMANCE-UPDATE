import pandas as pd
import streamlit as st

# Sample data, replace this with your actual DataFrame
# df = pd.read_csv('your_data.csv')

# Example function to calculate and display per cycle manual summary
def calculate_per_cycle_manual_summary(df):
    # Filter for 'Outgoing' as the Remark Type
    df_filtered = df[df['Remark Type'] == 'Outgoing']

    # Get unique cycles (assuming 'Service No.' is the cycle identifier)
    unique_cycles = df_filtered['Service No.'].unique()

    for cycle in unique_cycles:
        # Filter data for the current cycle
        cycle_df = df_filtered[df_filtered['Service No.'] == cycle]

        # Initialize summary table for the cycle
        summary_table = pd.DataFrame(columns=[ 
            'Cycle', 'Date', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'TOTAL PTP AMOUNT', 
            'TOTAL BALANCE', 'CALL DROP #', 'SYSTEM DROP', 'CALL DROP RATIO #'
        ]) 

        # Group by date for the current cycle
        for date, date_group in cycle_df.groupby(cycle_df['Date'].dt.date):
            accounts = date_group['Account No.'].nunique()
            total_dialed = date_group['Account No.'].count()
            connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()
            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None
            connected_acc = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None
            ptp_acc = date_group[(date_group['Status'].str.contains('PTP', na=False)) & 
                                 (date_group['PTP Amount'] != 0)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
            total_ptp_amount = date_group[(date_group['Status'].str.contains('PTP', na=False)) & 
                                          (date_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            total_balance = date_group[(date_group['PTP Amount'] != 0)]['Balance'].sum()  
            system_drop = date_group[(date_group['Status'].str.contains('DROPPED', na=False)) & 
                                     (date_group['Remark By'] == 'SYSTEM')]['Account No.'].count()
            call_drop_count = date_group[(date_group['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                        (~date_group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()
            call_drop_ratio = (call_drop_count / connected_acc * 100) if connected_acc != 0 else None  # Updated Call Drop Ratio calculation

            # Add the calculated values for the current cycle and date to the summary table
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
                'TOTAL PTP AMOUNT': total_ptp_amount,
                'TOTAL BALANCE': total_balance,
                'CALL DROP #': call_drop_count,
                'SYSTEM DROP': system_drop,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
            }])], ignore_index=True)

        # Display the summary table for the current cycle
        st.write(f"## Per Cycle Manual Summary Table for Cycle {cycle}")
        st.write(summary_table)

# Sample DataFrame
data = {
    'Service No.': ['Cycle 1', 'Cycle 1', 'Cycle 2', 'Cycle 2', 'Cycle 3'],
    'Date': pd.to_datetime(['2025-03-18', '2025-03-19', '2025-03-18', '2025-03-19', '2025-03-18']),
    'Account No.': [101, 102, 103, 104, 105],
    'Call Status': ['CONNECTED', 'DROPPED', 'CONNECTED', 'NEGATIVE CALLOUTS - DROP CALL', 'CONNECTED'],
    'Remark Type': ['Outgoing', 'Outgoing', 'Outgoing', 'Outgoing', 'Outgoing'],
    'Status': ['PTP', 'NEGATIVE CALLOUTS', 'PTP', 'NEGATIVE CALLOUTS', 'PTP'],
    'PTP Amount': [100, 0, 200, 0, 150],
    'Balance': [200, 300, 400, 500, 600],
    'Remark By': ['SYSTEM', 'USER', 'SYSTEM', 'USER', 'SYSTEM']
}

# Create DataFrame
df = pd.DataFrame(data)

# Streamlit app layout
st.title("Cycle Wise Manual Summary")

# Display Per Cycle Manual Summary for each individual cycle
st.write("## Per Cycle Manual Summary Tables")
calculate_per_cycle_manual_summary(df)
