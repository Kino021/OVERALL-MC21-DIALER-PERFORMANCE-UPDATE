import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
from pandas import ExcelWriter

st.set_page_config(layout="wide", page_title="Daily Remark Summary", page_icon="📊", initial_sidebar_state="expanded")

st.title('Daily Remark Summary')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.upper()
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df = df[df['DATE'].dt.weekday != 6]  # Exclude Sundays
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

def to_excel(df_dict):
    # [Keeping the to_excel function unchanged as it doesn't need modification]
    # ... (previous to_excel function code remains the same)
    return output.getvalue()

if uploaded_file is not None:
    df = load_data(uploaded_file)
    # Exclude remarks by SPMADRID
    df = df[df['REMARK BY'] != 'SPMADRID']
    df = df[~df['DEBTOR'].str.contains("DEFAULT_LEAD_", case=False, na=False)]
    df = df[~df['STATUS'].str.contains('ABORT', na=False)]
    # Exclude remarks containing "1_(11-digit number) - PTP NEW"
    df = df[~df['REMARK'].str.contains(r'1_\d{11} - PTP NEW', case=False, na=False, regex=True)]
    
    excluded_remarks = [
        "Broken Promise", "New files imported", "Updates when case reassign to another collector", 
        "NDF IN ICS", "FOR PULL OUT (END OF HANDLING PERIOD)", "END OF HANDLING PERIOD", "New Assignment -",
    ]
    df = df[~df['REMARK'].str.contains('|'.join(excluded_remarks), case=False, na=False)]
    df = df[~df['CALL STATUS'].str.contains('OTHERS', case=False, na=False)]
    
    # Updated cycle extraction from Card no. column
    df['Card no.'] = df['Card no.'].astype(str)
    df['CYCLE'] = df['Card no.'].str[:2]  # Get first 2 characters
    df['CYCLE'] = df['CYCLE'].fillna('Unknown')
    df['CYCLE'] = df['CYCLE'].astype(str)

    def format_seconds_to_hms(seconds):
        # ... (keeping this function unchanged)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def calculate_summary(df, remark_types, manual_correction=False):
        # ... (keeping this function unchanged)
        return summary_table.sort_values(by=['DATE'])

    def get_cycle_summary(df, remark_types, manual_correction=False):
        result = {}
        unique_cycles = df['CYCLE'].unique()
        for cycle in unique_cycles:
            if cycle == 'Unknown':
                continue
            cycle_df = df[df['CYCLE'] == cycle]
            result[f"Cycle {cycle}"] = calculate_summary(cycle_df, remark_types, manual_correction)
        return result

    # ... (rest of the code remains unchanged)
    combined_summary = calculate_summary(df, ['Predictive', 'Follow Up', 'Outgoing'])
    predictive_summary = calculate_summary(df, ['Predictive', 'Follow Up'])
    manual_summary = calculate_summary(df, ['Outgoing'], manual_correction=True)
    predictive_cycle_summaries = get_cycle_summary(df, ['Predictive', 'Follow Up'])
    manual_cycle_summaries = get_cycle_summary(df, ['Outgoing'], manual_correction=True)

    # ... (display and download sections remain unchanged)
