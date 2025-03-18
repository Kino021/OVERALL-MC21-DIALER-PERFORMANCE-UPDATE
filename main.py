import pandas as pd

# Modify this function to handle per date and per balance category
def calculate_balance_summary(df):
    # Ensure that 'Date' and 'Balance Category' are correctly formatted
    df['Date'] = pd.to_datetime(df['Date'])
    df['Balance Category'] = df['Balance Category'].astype(str)  # Ensure it's a string if it's not

    # Group by Date and Balance Category
    grouped = df.groupby(['Date', 'Balance Category']).agg(
        total_accounts=('Account No.', 'nunique'),
        total_dialed=('Account No.', 'count'),
        connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
        penetration_rate=('Account No.', lambda x: (x.count() / df['Account No.'].nunique()) * 100 if df['Account No.'].nunique() != 0 else 0),
        connected_rate=('Account No.', lambda x: (x.count() / len(x)) * 100 if len(x) != 0 else 0),
        ptp_acc=('Account No.', lambda x: (df.loc[x.index, 'Status'].str.contains('PTP', na=False) & (df.loc[x.index, 'PTP Amount'] != 0)).sum()),
        ptp_rate=('Account No.', lambda x: (df.loc[x.index, 'Status'].str.contains('PTP', na=False) & (df.loc[x.index, 'PTP Amount'] != 0)).sum() / len(x) * 100 if len(x) != 0 else 0),
        system_drop=('Account No.', lambda x: (df.loc[x.index, 'Status'].str.contains('DROPPED', na=False) & (df.loc[x.index, 'Remark By'] == 'SYSTEM')).sum()),
        call_drop_count=('Account No.', lambda x: (df.loc[x.index, 'Status'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False) & (~df.loc[x.index, 'Remark By'].str.upper().isin(['SYSTEM']))).sum())
    ).reset_index()

    # Calculate call drop ratio and add it to the grouped DataFrame
    grouped['call_drop_ratio'] = grouped['system_drop'] / grouped['connected'] * 100

    # Format the rates as percentage and round the results
    grouped['penetration_rate'] = grouped['penetration_rate'].apply(lambda x: f"{round(x, 2)}%" if pd.notnull(x) else None)
    grouped['connected_rate'] = grouped['connected_rate'].apply(lambda x: f"{round(x, 2)}%" if pd.notnull(x) else None)
    grouped['ptp_rate'] = grouped['ptp_rate'].apply(lambda x: f"{round(x, 2)}%" if pd.notnull(x) else None)
    grouped['call_drop_ratio'] = grouped['call_drop_ratio'].apply(lambda x: f"{round(x, 2)}%" if pd.notnull(x) else None)

    return grouped

# Example usage:
# Assuming 'df' is your DataFrame that contains the required columns like 'Account No.', 'Call Status', 'Status', etc.
# df = pd.read_csv("your_data.csv")  # If you're reading from a CSV file
summary_table = calculate_balance_summary(df)

# Display the summary table
import streamlit as st
st.write(summary_table)
