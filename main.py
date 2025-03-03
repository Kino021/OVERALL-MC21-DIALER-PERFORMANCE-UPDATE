import streamlit as st
import pandas as pd

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide", 
    page_title="Productivity Dashboard", 
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
st.markdown('<div class="header">📊 PRODUCTIVITY DASHBOARD</div>', unsafe_allow_html=True)

# ------------------- DATA LOADING FUNCTION -------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                                   'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                                   'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO', 
                                   'LMLABRADOR', 'EASORIANO'])]  # Exclude specific users
    return df

# ------------------- LOAD DATA -------------------
uploaded_file = st.file_uploader("Upload Data", type=["xlsx", "csv"])
if uploaded_file:
    df = load_data(uploaded_file)

    # ------------------- DEBUGGING: Check Available Columns -------------------
    st.write("Columns in the DataFrame:", df.columns)

    # ------------------- CLEAN COLUMN NAMES -------------------
    # Strip leading/trailing spaces and convert to lowercase
    df.columns = df.columns.str.strip().str.lower()

    # ------------------- DEBUGGING: Show First Few Rows -------------------
    st.write("First few rows of the DataFrame:", df.head())

    # ------------------- HOURLY PRODUCTIVITY REPORT -------------------
    # Filter rows with status "PTP" but exclude "PTP FF UP"
    df_filtered = df[df['status'].str.contains('PTP', na=False) & ~df['status'].str.contains('PTP FF UP', na=False)]

    # Ensure 'time' is in a datetime format if it's not already
    df_filtered['time'] = pd.to_datetime(df_filtered['time'], errors='coerce')

    # Check if Time column is parsed correctly
    st.write(df_filtered[['time', 'status', 'ptp amount']].head())  # Preview data to ensure columns are correct

    # Add 'Time Range' based on hour
    def get_time_range(hour):
        if 6 <= hour < 7:
            return '6:00 AM - 7:00 AM'
        elif 7 <= hour < 8:
            return '7:01 AM - 8:00 AM'
        elif 8 <= hour < 9:
            return '8:01 AM - 9:00 AM'
        else:
            return f'{hour}:00 AM - {hour + 1}:00 AM'

    # Apply the time range function to 'Time' column
    df_filtered['Time Range'] = df_filtered['time'].dt.hour.apply(lambda x: get_time_range(x))

    # Check if 'Time Range' column was created correctly
    st.write(df_filtered[['time', 'Time Range', 'status', 'ptp amount']].head())  # Preview the DataFrame after adding 'Time Ra
