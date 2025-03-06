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

    # Exclude specified agents
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                                   'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                                   'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO'])]
    
    # Filter rows where 'STATUS' contains 'PTP' but excludes 'PTP FF' and 'PTP FOLLOW UP'
    df = df[df['STATUS'].str.contains('PTP') & ~df['STATUS'].str.contains('PTP FF|PTP FOLLOW UP')]

    # Filter rows where 'REMARKS BY' contains an agent username and excludes 'SYSTEM'
    df = df[df['REMARKS BY'].str.contains(r'\b(?!SYSTEM\b)\w+', na=False)]

    return df

# File uploader in sidebar
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.write(df)

    # Allow user to download filtered data as CSV or Excel
    st.sidebar.markdown("### Download Filtered Data")
    
    # Option to download as CSV
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="Download as CSV",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv"
    )
    
    # Option to download as Excel
    excel = df.to_excel(index=False, engine='openpyxl')
    st.sidebar.download_button(
        label="Download as Excel",
        data=excel,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
