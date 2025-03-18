import pandas as pd

# Ensure the DataFrame is loaded and has necessary columns
# Example loading of your CSV file:
df = pd.read_csv("your_data.csv")

# Check the column names in your DataFrame to make sure they're correct
print(df.columns)

# Modify this function to handle per date and per balance category
def calculate_balance_summary(df):
    # Check if necessary columns are present
    required_columns = ['Date', 'Balance Category', 'Account No.', 'Call Status', 'Status', 'PTP Amount', 'Remark By']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {', '.join(missing_columns)}")

    # Ensure that 'Date' and 'Balance Category' are correctly formatted
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Handle any invalid date format
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
# Assuming the DataFrame df is loaded correctly
try:
    summary_table = calculate_balance_summary(df)
    import streamlit as st
    st.write(summary_table)
except Exception as e:
    print(f"An error occurred: {e}")
