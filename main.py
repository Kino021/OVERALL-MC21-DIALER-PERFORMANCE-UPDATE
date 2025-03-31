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
    # [Keeping the to_excel function unchanged]
    return output.getvalue()

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Show available columns for debugging
    st.write("Available columns in your data:", list(df.columns))
    
    # Exclude remarks by SPMADRID and other filters
    df = df[df['REMARK BY'] != 'SPMADRID']
    df = df[~df['DEBTOR'].str.contains("DEFAULT_LEAD_", case=False, na=False)]
    df = df[~df['STATUS'].str.contains('ABORT', na=False)]
    df = df[~df['REMARK'].str.contains(r'1_\d{11} - PTP NEW', case=False, na=False, regex=True)]
    
    excluded_remarks = [
        "Broken Promise", "New files imported", "Updates when case reassign to another collector", 
        "NDF IN ICS", "FOR PULL OUT (END OF HANDLING PERIOD)", "END OF HANDLING PERIOD", "New Assignment -",
    ]
    df = df[~df['REMARK'].str.contains('|'.join(excluded_remarks), case=False, na=False)]
    df = df[~df['CALL STATUS'].str.contains('OTHERS', case=False, na=False)]
    
    # Let user select the column to use for cycle
    card_column_options = [col for col in df.columns if 'CARD' in col.upper() or 'NO' in col.upper()] or df.columns
    card_column = st.sidebar.selectbox(
        "Select column to use for cycle (first 2 characters)",
        options=card_column_options,
        index=0
    )
    
    try:
        df[card_column] = df[card_column].astype(str)
        df['CYCLE'] = df[card_column].str[:2]  # Get first 2 characters
        df['CYCLE'] = df['CYCLE'].fillna('Unknown')
        df['CYCLE'] = df['CYCLE'].astype(str)
    except KeyError:
        st.error(f"Selected column '{card_column}' not found. Please select a valid column from the list above.")
        st.stop()

    def format_seconds_to_hms(seconds):
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
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

    combined_summary = calculate_summary(df, ['Predictive', 'Follow Up', 'Outgoing'])
    predictive_summary = calculate_summary(df, ['Predictive', 'Follow Up'])
    manual_summary = calculate_summary(df, ['Outgoing'], manual_correction=True)
    predictive_cycle_summaries = get_cycle_summary(df, ['Predictive', 'Follow Up'])
    manual_cycle_summaries = get_cycle_summary(df, ['Outgoing'], manual_correction=True)

    st.write("## Overall Combined Summary Table")
    st.write(combined_summary)

    st.write("## Overall Predictive Summary Table")
    st.write(predictive_summary)

    st.write("## Overall Manual Summary Table")
    st.write(manual_summary)

    st.write("## Per Cycle Predictive Summary Tables")
    for cycle, table in predictive_cycle_summaries.items():
        with st.container():
            st.subheader(f"Summary for {cycle}")
            st.write(table)

    st.write("## Per Cycle Manual Summary Tables")
    for cycle, table in manual_cycle_summaries.items():
        with st.container():
            st.subheader(f"Summary for {cycle}")
            st.write(table)

    excel_data = {
        'Combined Summary': combined_summary,
        'Predictive Summary': predictive_summary,
        'Manual Summary': manual_summary,
        **{f"Predictive {k}": v for k, v in predictive_cycle_summaries.items()},
        **{f"Manual {k}": v for k, v in manual_cycle_summaries.items()}
    }

    st.download_button(
        label="Download All Summaries as Excel",
        data=to_excel(excel_data),
        file_name=f"Daily_Remark_Summary_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
