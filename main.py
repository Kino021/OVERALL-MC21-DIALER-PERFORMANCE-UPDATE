import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Daily Remark Summary", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode styling
st.markdown(
    """
    <style>
        .main {
            background-color: #2E2E2E;
            color: white;
        }
        .stApp {
            background: #2E2E2E;
        }
        .sidebar .sidebar-content {
            background: #2E2E2E;
            color: white;
        }
        .css-1aumxhk {
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file, keep_default_na=False)
    
    # Convert date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Exclude specific users
    excluded_users = [
        'FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
        'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
        'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO'
    ]
    df = df[~df['Remark By'].isin(excluded_users)]

    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Exclude "Broken Promise" (BP) entries
    df = df[~df['Status'].str.contains('BP', na=False)]

    st.subheader("Filtered Data Preview")
    st.dataframe(df)

    # Function to calculate summary table
    def calculate_summary(df, remark_type=None, remark_by=None):
        summary_table = []

        for date, group in df.groupby(df['Date'].dt.date):
            filtered_group = group.copy()

            if remark_type:
                filtered_group = filtered_group[filtered_group['Remark Type'] == remark_type]
            if remark_by:
                filtered_group = filtered_group[filtered_group['Remark By'] == remark_by]

            accounts = filtered_group['Account No.'].nunique()
            total_dialed = filtered_group.shape[0]

            connected = filtered_group[filtered_group['Call Status'] == 'CONNECTED'].shape[0]
            connected_acc = filtered_group[filtered_group['Call Status'] == 'CONNECTED']['Account No.'].nunique()
            penetration_rate = (total_dialed / accounts * 100) if accounts else 0
            connected_rate = (connected / total_dialed * 100) if total_dialed else 0

            ptp_acc = filtered_group[(filtered_group['Status'].str.contains('PTP', na=False)) & (filtered_group['PTP Amount'] != 0)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc else 0

            # Call Drop Count
            drop_call_count = filtered_group[(filtered_group['Call Status'] == 'DROPPED')].shape[0]
            call_drop_ratio = (drop_call_count / connected * 100) if connected else 0

            summary_table.append({
                'Day': date,
                'ACCOUNTS': accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate, 2)}%",
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate, 2)}%",
                'CONNECTED ACC': connected_acc,
                'PTP ACC': ptp_acc,
                'PTP RATE (%)': f"{round(ptp_rate, 2)}%",
                'CALL DROP #': drop_call_count,
                'CALL DROP RATIO (%)': f"{round(call_drop_ratio, 2)}%"
            })

        return pd.DataFrame(summary_table)

    st.subheader("Overall Combined Summary Table")
    combined_summary_table = calculate_summary(df)
    st.dataframe(combined_summary_table)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Predictive Call Summary")
        predictive_summary = calculate_summary(df, 'Predictive', 'SYSTEM')
        st.dataframe(predictive_summary)

    with col2:
        st.subheader("Manual Call Summary")
        manual_summary = calculate_summary(df, 'Outgoing')
        st.dataframe(manual_summary)

    # Cycle Breakdown
    st.subheader("Summary by Cycle")

    with st.expander("Predictive Calls by Cycle"):
        for cycle, cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {cycle}")
            cycle_summary = calculate_summary(cycle_group, 'Predictive', 'SYSTEM')
            st.dataframe(cycle_summary)

    with st.expander("Manual Calls by Cycle"):
        for cycle, cycle_group in df.groupby('Service No.'):
            st.write(f"Cycle: {cycle}")
            cycle_summary = calculate_summary(cycle_group, 'Outgoing')
            st.dataframe(cycle_summary)
