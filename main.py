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
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                                   'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                                   'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA','JATERRADO'])] 
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.write(df)

    # Exclude rows where STATUS contains 'BP' (Broken Promise)
    df = df[~df['Status'].str.contains('BP', na=False)]

    # Ensure column names are clean
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.upper()  # Convert to uppercase for consistency
    
    # Print available columns for debugging
    st.write("### Available Columns in Uploaded File:", df.columns.tolist())

    # Function to calculate combined summary
    def calculate_combined_summary(df):
        summary_table = pd.DataFrame(columns=[ 
            'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #'
        ])

        for date, group in df.groupby(df['DATE'].dt.date):
            accounts = group['Account No.'].nunique()
            total_dialed = group['Account No.'].count()

            connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            connected_acc = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

            ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

            drop_call_count = group[group['Call Status'] == 'DROPPED'].shape[0]
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
    
    st.write("## Overall Combined Summary Table")
    combined_summary_table = calculate_combined_summary(df)
    st.write(combined_summary_table)

    # Function to calculate balance category summary
    def calculate_balance_summary(df):
        balance_ranges = [
            (6000, 49999, '6,000 - 49,999'),
            (50000, 99999, '50,000 - 99,999'),
            (100000, float('inf'), '100,000 and above')
        ]

        if 'BALANCE' not in df.columns:
            st.write("Detected column names:", df.columns.tolist())
            st.error("Error: 'BALANCE' column is missing in the uploaded file.")
            return pd.DataFrame()

        summary = pd.concat([
            calculate_combined_summary(df[(df['BALANCE'] >= min_bal) & (df['BALANCE'] <= max_bal)])
            for min_bal, max_bal, _ in balance_ranges
        ], ignore_index=True)
        
        return summary
    
    st.write("## Penetration Rate by Balance Category")
    balance_summary_table = calculate_balance_summary(df)
    st.write(balance_summary_table)
