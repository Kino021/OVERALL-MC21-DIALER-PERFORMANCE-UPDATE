import pandas as pd
import streamlit as st

# Function to calculate the Overall Combined Summary
def calculate_overall_combined_summary(df):
    combined_summary = pd.DataFrame(columns=[ 
        'Total ACCOUNTS', 'Total DIALED', 'Total CONNECTED #', 'Total PTP ACC', 'Total PTP RATE', 
        'Total PTP AMOUNT', 'Total CALL DROP #', 'Total SYSTEM DROP'
    ])

    total_accounts = df['Account No.'].nunique()
    total_dialed = df['Account No.'].count()
    connected = df[df['Call Status'] == 'CONNECTED']['Account No.'].nunique()
    total_ptp_acc = df[(df['Status'].str.contains('PTP', na=False)) & (df['PTP Amount'] != 0)]['Account No.'].nunique()
    ptp_rate = (total_ptp_acc / connected * 100) if connected != 0 else None
    total_ptp_amount = df[(df['Status'].str.contains('PTP', na=False)) & (df['PTP Amount'] != 0)]['PTP Amount'].sum()
    total_call_drop = df[(df['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False))]['Account No.'].count()
    system_drop = df[(df['Status'].str.contains('DROPPED', na=False)) & (df['Remark By'] == 'SYSTEM')]['Account No.'].count()

    combined_summary = pd.concat([combined_summary, pd.DataFrame([{
        'Total ACCOUNTS': total_accounts,
        'Total DIALED': total_dialed,
        'Total CONNECTED #': connected,
        'Total PTP ACC': total_ptp_acc,
        'Total PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
        'Total PTP AMOUNT': total_ptp_amount,
        'Total CALL DROP #': total_call_drop,
        'Total SYSTEM DROP': system_drop
    }])], ignore_index=True)

    return combined_summary


# Function to calculate the Overall Predictive Summary
def calculate_overall_predictive_summary(df):
    predictive_summary = pd.DataFrame(columns=[ 
        'Total ACCOUNTS', 'Total DIALED', 'Total CONNECTED #', 'Total PTP ACC', 'Total PTP RATE', 
        'Total PTP AMOUNT', 'Total CALL DROP #', 'Total SYSTEM DROP'
    ])

    df_filtered = df[df['Remark Type'] == 'Predictive']
    total_accounts = df_filtered['Account No.'].nunique()
    total_dialed = df_filtered['Account No.'].count()
    connected = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()
    total_ptp_acc = df_filtered[(df_filtered['Status'].str.contains('PTP', na=False)) & (df_filtered['PTP Amount'] != 0)]['Account No.'].nunique()
    ptp_rate = (total_ptp_acc / connected * 100) if connected != 0 else None
    total_ptp_amount = df_filtered[(df_filtered['Status'].str.contains('PTP', na=False)) & (df_filtered['PTP Amount'] != 0)]['PTP Amount'].sum()
    total_call_drop = df_filtered[(df_filtered['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False))]['Account No.'].count()
    system_drop = df_filtered[(df_filtered['Status'].str.contains('DROPPED', na=False)) & (df_filtered['Remark By'] == 'SYSTEM')]['Account No.'].count()

    predictive_summary = pd.concat([predictive_summary, pd.DataFrame([{
        'Total ACCOUNTS': total_accounts,
        'Total DIALED': total_dialed,
        'Total CONNECTED #': connected,
        'Total PTP ACC': total_ptp_acc,
        'Total PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
        'Total PTP AMOUNT': total_ptp_amount,
        'Total CALL DROP #': total_call_drop,
        'Total SYSTEM DROP': system_drop
    }])], ignore_index=True)

    return predictive_summary


# Function to calculate the Overall Manual Summary
def calculate_overall_manual_summary(df):
    manual_summary = pd.DataFrame(columns=[ 
        'Total ACCOUNTS', 'Total DIALED', 'Total CONNECTED #', 'Total PTP ACC', 'Total PTP RATE', 
        'Total PTP AMOUNT', 'Total CALL DROP #', 'Total SYSTEM DROP'
    ])

    df_filtered = df[df['Remark Type'] == 'Manual']
    total_accounts = df_filtered['Account No.'].nunique()
    total_dialed = df_filtered['Account No.'].count()
    connected = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()
    total_ptp_acc = df_filtered[(df_filtered['Status'].str.contains('PTP', na=False)) & (df_filtered['PTP Amount'] != 0)]['Account No.'].nunique()
    ptp_rate = (total_ptp_acc / connected * 100) if connected != 0 else None
    total_ptp_amount = df_filtered[(df_filtered['Status'].str.contains('PTP', na=False)) & (df_filtered['PTP Amount'] != 0)]['PTP Amount'].sum()
    total_call_drop = df_filtered[(df_filtered['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False))]['Account No.'].count()
    system_drop = df_filtered[(df_filtered['Status'].str.contains('DROPPED', na=False)) & (df_filtered['Remark By'] == 'SYSTEM')]['Account No.'].count()

    manual_summary = pd.concat([manual_summary, pd.DataFrame([{
        'Total ACCOUNTS': total_accounts,
        'Total DIALED': total_dialed,
        'Total CONNECTED #': connected,
        'Total PTP ACC': total_ptp_acc,
        'Total PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
        'Total PTP AMOUNT': total_ptp_amount,
        'Total CALL DROP #': total_call_drop,
        'Total SYSTEM DROP': system_drop
    }])], ignore_index=True)

    return manual_summary


# Function to calculate the Per Cycle Predictive Summary
def calculate_per_cycle_predictive_summary(df):
    per_cycle_predictive_summary = pd.DataFrame(columns=[ 
        'Cycle', 'Total ACCOUNTS', 'Total DIALED', 'Total CONNECTED #', 'Total PTP ACC', 'Total PTP RATE', 
        'Total PTP AMOUNT', 'Total CALL DROP #', 'Total SYSTEM DROP'
    ])

    cycles = df['Cycle'].unique()
    for cycle in cycles:
        df_filtered = df[(df['Cycle'] == cycle) & (df['Remark Type'] == 'Predictive')]
        total_accounts = df_filtered['Account No.'].nunique()
        total_dialed = df_filtered['Account No.'].count()
        connected = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()
        total_ptp_acc = df_filtered[(df_filtered['Status'].str.contains('PTP', na=False)) & (df_filtered['PTP Amount'] != 0)]['Account No.'].nunique()
        ptp_rate = (total_ptp_acc / connected * 100) if connected != 0 else None
        total_ptp_amount = df_filtered[(df_filtered['Status'].str.contains('PTP', na=False)) & (df_filtered['PTP Amount'] != 0)]['PTP Amount'].sum()
        total_call_drop = df_filtered[(df_filtered['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False))]['Account No.'].count()
        system_drop = df_filtered[(df_filtered['Status'].str.contains('DROPPED', na=False)) & (df_filtered['Remark By'] == 'SYSTEM')]['Account No.'].count()

        per_cycle_predictive_summary = pd.concat([per_cycle_predictive_summary, pd.DataFrame([{
            'Cycle': cycle,
            'Total ACCOUNTS': total_accounts,
            'Total DIALED': total_dialed,
            'Total CONNECTED #': connected,
            'Total PTP ACC': total_ptp_acc,
            'Total PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
            'Total PTP AMOUNT': total_ptp_amount,
            'Total CALL DROP #': total_call_drop,
            'Total SYSTEM DROP': system_drop
        }])], ignore_index=True)

    return per_cycle_predictive_summary


# Function to calculate the Per Cycle Manual Summary
def calculate_per_cycle_manual_summary(df):
    per_cycle_manual_summary = pd.DataFrame(columns=[ 
        'Cycle', 'Total ACCOUNTS', 'Total DIALED', 'Total CONNECTED #', 'Total PTP ACC', 'Total PTP RATE', 
        'Total PTP AMOUNT', 'Total CALL DROP #', 'Total SYSTEM DROP'
    ])

    cycles = df['Cycle'].unique()
    for cycle in cycles:
        df_filtered = df[(df['Cycle'] == cycle) & (df['Remark Type'] == 'Manual')]
        total_accounts = df_filtered['Account No.'].nunique()
        total_dialed = df_filtered['Account No.'].count()
        connected = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()
        total_ptp_acc = df_filtered[(df_filtered['Status'].str.contains('PTP', na=False)) & (df_filtered['PTP Amount'] != 0)]['Account No.'].nunique()
        ptp_rate = (total_ptp_acc / connected * 100) if connected != 0 else None
        total_ptp_amount = df_filtered[(df_filtered['Status'].str.contains('PTP', na=False)) & (df_filtered['PTP Amount'] != 0)]['PTP Amount'].sum()
        total_call_drop = df_filtered[(df_filtered['Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False))]['Account No.'].count()
        system_drop = df_filtered[(df_filtered['Status'].str.contains('DROPPED', na=False)) & (df_filtered['Remark By'] == 'SYSTEM')]['Account No.'].count()

        per_cycle_manual_summary = pd.concat([per_cycle_manual_summary, pd.DataFrame([{
            'Cycle': cycle,
            'Total ACCOUNTS': total_accounts,
            'Total DIALED': total_dialed,
            'Total CONNECTED #': connected,
            'Total PTP ACC': total_ptp_acc,
            'Total PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
            'Total PTP AMOUNT': total_ptp_amount,
            'Total CALL DROP #': total_call_drop,
            'Total SYSTEM DROP': system_drop
        }])], ignore_index=True)

    return per_cycle_manual_summary


# Main function to display results
def main():
    # Load the data
    df = pd.read_csv('your_data.csv')  # Replace with your actual CSV file
    
    # Calculate each summary table
    overall_combined = calculate_overall_combined_summary(df)
    overall_predictive = calculate_overall_predictive_summary(df)
    overall_manual = calculate_overall_manual_summary(df)
    per_cycle_predictive = calculate_per_cycle_predictive_summary(df)
    per_cycle_manual = calculate_per_cycle_manual_summary(df)
    
    # Display in Streamlit
    st.write("### Overall Combined Summary Table")
    st.write(overall_combined)
    
    st.write("### Overall Predictive Summary Table")
    st.write(overall_predictive)
    
    st.write("### Overall Manual Summary Table")
    st.write(overall_manual)
    
    st.write("### Per Cycle Predictive Summary Table")
    st.write(per_cycle_predictive)
    
    st.write("### Per Cycle Manual Summary Table")
    st.write(per_cycle_manual)


if __name__ == "__main__":
    main()
