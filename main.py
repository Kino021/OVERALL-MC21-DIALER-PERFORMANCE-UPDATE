import streamlit as st
import pandas as pd

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide",
    page_title="PRODUCTIVITY PER AGENT",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ------------------- GLOBAL STYLING -------------------
st.markdown("""
    <style>
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(to right, #FFD700, #FFA500);
            color: white;
            font-size: 24px;
            border-radius: 10px;
            font-weight: bold;
        }
        .category-title {
            font-size: 20px;
            font-weight: bold;
            margin-top: 30px;
            color: #FF8C00;
        }
        .card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- HEADER -------------------
st.markdown('<div class="header">📊 PRODUCTIVITY PER AGENT</div>', unsafe_allow_html=True)

# ------------------- FILE UPLOAD -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx"])

# ------------------- FUNCTION TO LOAD DATA -------------------
def load_data(file):
    """Loads CSV or Excel file and ensures proper data formatting."""
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Convert 'Date' column to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Ensure 'Time' column is parsed correctly
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# ------------------- FUNCTION TO GENERATE PRODUCTIVITY SUMMARY -------------------
def generate_productivity_summary(df, group_by):
    """Creates a productivity summary grouped by the specified column."""
    summary_list = []
    
    for (date, group), sub_df in df.groupby([df['Date'].dt.date, group_by]):
        summary_list.append({
            'Date': date,
            group_by: group,
            'Total Connected': (sub_df['Call Status'] == 'CONNECTED').sum(),
            'Total PTP': ((sub_df['Status'].str.contains('PTP', na=False)) & (sub_df['PTP Amount'] != 0)).sum(),
            'Total RPC': (sub_df['Status'].str.contains('RPC', na=False)).sum(),
            'PTP Amount': sub_df.loc[sub_df['Status'].str.contains('PTP', na=False), 'PTP Amount'].sum(),
            'Balance Amount': sub_df.loc[sub_df['Status'].str.contains('PTP', na=False), 'Balance'].sum(),
        })
    
    summary_df = pd.DataFrame(summary_list)
    
    if not summary_df.empty:
        total_row = {
            'Date': 'Total',
            group_by: 'Total',
            'Total Connected': summary_df['Total Connected'].sum(),
            'Total PTP': summary_df['Total PTP'].sum(),
            'Total RPC': summary_df['Total RPC'].sum(),
            'PTP Amount': summary_df['PTP Amount'].sum(),
            'Balance Amount': summary_df['Balance Amount'].sum()
        }
        summary_df = pd.concat([summary_df, pd.DataFrame([total_row])], ignore_index=True)
    
    return summary_df

# ------------------- MAIN APP LOGIC -------------------
if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        # Hourly PTP Summary
        st.markdown('<h2 style="text-align:center;">📊 Hourly PTP Summary</h2>', unsafe_allow_html=True)
        time_summary_df = generate_productivity_summary(df, 'Time Range')
        st.dataframe(time_summary_df)
        
        # Productivity by Collector
        st.markdown('<h2 style="text-align:center;">📊 Productivity by Collector</h2>', unsafe_allow_html=True)
        collector_summary_df = generate_productivity_summary(df, 'Collector')
        st.dataframe(collector_summary_df)
        
        # Productivity by Cycle (Separated per Date)
        st.markdown('<h2 style="text-align:center;">📊 Productivity by Cycle (Separated per Date)</h2>', unsafe_allow_html=True)
        cycle_summary_df = generate_productivity_summary(df, 'Cycle')
        st.dataframe(cycle_summary_df)
