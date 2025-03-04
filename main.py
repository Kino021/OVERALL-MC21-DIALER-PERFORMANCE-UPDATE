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

    # ------------------- CLEAN COLUMN NAMES -------------------
    df.columns = df.columns.str.strip().str.lower()

    # ------------------- HOURLY PRODUCTIVITY REPORT -------------------
    df_filtered = df[df['status'].str.contains('PTP', na=False) & ~df['status'].str.contains('PTP FF UP', na=False)]
    df_filtered['time'] = pd.to_datetime(df_filtered['time'], errors='coerce')
    df_filtered['ptp amount'] = pd.to_numeric(df_filtered['ptp amount'], errors='coerce').fillna(0)

    # Function to categorize time ranges
    def get_time_range(hour):
        if 6 <= hour < 7:
            return '6:00 AM - 7:00 AM'
        elif 7 <= hour < 8:
            return '7:01 AM - 8:00 AM'
        elif 8 <= hour < 9:
            return '8:01 AM - 9:00 AM'
        elif 9 <= hour < 10:
            return '9:01 AM - 10:00 AM'
        elif 10 <= hour < 11:
            return '10:01 AM - 11:00 AM'
        elif 11 <= hour < 12:
            return '11:01 AM - 12:00 PM'
        elif 12 <= hour < 13:
            return '12:01 PM - 1:00 PM'
        elif 13 <= hour < 14:
            return '1:01 PM - 2:00 PM'
        elif 14 <= hour < 15:
            return '2:01 PM - 3:00 PM'
        elif 15 <= hour < 16:
            return '3:01 PM - 4:00 PM'
        elif 16 <= hour < 17:
            return '4:01 PM - 5:00 PM'
        elif 17 <= hour < 18:
            return '5:01 PM - 6:00 PM'
        elif 18 <= hour < 19:
            return '6:01 PM - 7:00 PM'
        elif 19 <= hour < 20:
            return '7:01 PM - 8:00 PM'
        elif 20 <= hour < 21:
            return '8:01 PM - 9:00 PM'
        else:
            return None  

    df_filtered['Time Range'] = df_filtered['time'].dt.hour.apply(lambda x: get_time_range(x))
    df_filtered = df_filtered[df_filtered['Time Range'].notna()]

    # Filter only rows where 'PTP AMOUNT' is greater than 0
    df_valid_ptp = df_filtered[df_filtered['ptp amount'] > 0]

    try:
        hourly_report = df_valid_ptp.groupby('Time Range').agg(
            Total_PTP_Count=('account no.', pd.Series.nunique),  # Count unique Account Numbers
            Total_PTP_Amount=('ptp amount', 'sum')
        ).reset_index()

        # ------------------- ADD TOTAL ROW -------------------
        total_ptp_count = hourly_report['Total_PTP_Count'].sum()
        total_ptp_amount = hourly_report['Total_PTP_Amount'].sum()

        total_row = pd.DataFrame({
            'Time Range': ['TOTAL'],
            'Total_PTP_Count': [total_ptp_count],
            'Total_PTP_Amount': [total_ptp_amount]
        })

        hourly_report = pd.concat([hourly_report, total_row], ignore_index=True)

        # ------------------- DISPLAY REPORT -------------------
        st.markdown('<div class="category-title">Hourly Productivity Report</div>', unsafe_allow_html=True)
        st.dataframe(hourly_report)

    except KeyError as e:
        st.error(f"Error in grouping: {e}")
        st.write("Available columns:", df_filtered.columns)
