import pandas as pd
import streamlit as st

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
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Ensure Date is a datetime column
    
    # Exclude specific users in 'Remark By' column
    excluded_users = ['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                      'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                      'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO']
    df = df[~df['Remark By'].isin(excluded_users)]
    
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Show column names to help debug any issues with column names
    st.write("Columns in the uploaded data:", df.columns)

    # Proceed only if 'STATUS' and 'REMARKS TYPE' columns exist
    if 'STATUS' in df.columns and 'REMARKS TYPE' in df.columns and 'CALL STATUS' in df.columns and 'ACCOUNT NO.' in df.columns:
        
        def calculate_combined_summary(df):
            # Apply the exclusions first
            df_filtered = df[~df['STATUS'].str.contains("ABORT", case=False, na=False)]
            df_filtered = df_filtered[~df_filtered['REMARKS'].str.contains("Updates when case reassign to another collector", case=False, na=False)]
            
            # Get unique accounts (Account No column)
            unique_accounts = df_filtered['ACCOUNT NO.'].nunique()
            
            # Get total dialed (REMARKS TYPE contains 'OUTGOING', 'PREDICTIVE', or 'FOLLOW UP')
            total_dialed = df_filtered[df_filtered['REMARKS TYPE'].isin(['OUTGOING', 'PREDICTIVE', 'FOLLOW UP'])].shape[0]
            
            # Get connected count (CALL STATUS contains 'CONNECTED')
            connected_count = df_filtered[df_filtered['CALL STATUS'].str.contains('CONNECTED', case=False, na=False)].shape[0]
            
            # Get call drop count (STATUS contains specific drop terms)
            drop_terms = ['NEGATIVE_CALLOUTS - DROPPED_CALL', 'NEGATIVE CALLOUTS - DROP CALL', 'DROPPED']
            call_drop_count = df_filtered[df_filtered['STATUS'].str.contains('|'.join(drop_terms), case=False, na=False)].shape[0]
            
            # Create the summary table
            summary_table = pd.DataFrame([{
                'Day': df_filtered['Date'].max().strftime('%Y-%m-%d'),  # Use the latest date as the 'Day'
                'ACCOUNTS': unique_accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': (total_dialed / unique_accounts) * 100 if unique_accounts > 0 else 0,
                'CONNECTED #': connected_count,
                'CONNECTED RATE (%)': (connected_count / total_dialed) * 100 if total_dialed > 0 else 0,
                'CONNECTED ACC': connected_count,  # Same as 'CONNECTED #' here
                'PTP ACC': '',  # Placeholder as you didn't specify logic for PTP ACC
                'PTP RATE': '',  # Placeholder for PTP RATE
                'CALL DROP #': call_drop_count,
                'CALL DROP RATIO #': (call_drop_count / total_dialed) * 100 if total_dialed > 0 else 0,
            }])
            
            return summary_table

        # Calculate the summary and display it
        summary = calculate_combined_summary(df)
        st.write(summary)
    else:
        st.error("The required columns (STATUS, REMARKS TYPE, CALL STATUS, ACCOUNT NO.) are missing from the data.")
