import streamlit as st
import pandas as pd

# Set up the page configuration
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

# Cache the data to improve performance
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    # Filter out the agents that are to be excluded
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS'
                                   , 'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER'
                                   , 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA','JATERRADO'])]

    return df

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    # Load and filter the data
    df = load_data(uploaded_file)

    # Check columns to verify 'STATUS' exists
    st.write("Columns in DataFrame:", df.columns)

    # Check if 'STATUS' column exists before proceeding
    if 'STATUS' in df.columns and 'Remark By' in df.columns:
        # Filter rows where 'STATUS' contains "PTP" but not "PTP FF" or "PTP FOLLOW UP"
        filtered_df = df[df['STATUS'].str.contains('PTP', na=False)]
        filtered_df = filtered_df[~filtered_df['STATUS'].str.contains('PTP FF|PTP FOLLOW UP', na=False)]

        # Exclude rows where 'REMARKS BY' is 'SYSTEM'
        filtered_df = filtered_df[~filtered_df['Remark By'].str.contains('SYSTEM', na=False)]

        # Count the total PTP entries
        total_ptp_count = filtered_df.shape[0]
        
        # Display the count
        st.write(f"Total PTP Count: {total_ptp_count}")

        # Display the filtered dataframe (optional)
        st.write(filtered_df)
    else:
        st.error("The 'STATUS' or 'Remark By' column does not exist in the uploaded file.")
