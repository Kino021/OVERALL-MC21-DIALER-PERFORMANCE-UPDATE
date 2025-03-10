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
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS'
                                   , 'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER'
                                   , 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA','JATERRADO'])]
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.write(df)
    
    def calculate_combined_summary(df):
        summary_table = pd.DataFrame(columns=[
            'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 
            'SYSTEM DROPPED #', 'CALL DROP RATIO #', 'SYSTEM DROP #'
        ])
        
        for date, group in df.groupby(df['Date'].dt.date):
            accounts = group[group['Remark'] != 'Broken Promise']['Account No.'].nunique()
            total_dialed = group[group['Remark'] != 'Broken Promise']['Account No.'].count()

            connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            connected_acc = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

            ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

            call_drop_count = group[group['Call Status'] == 'DROPPED']['Account No.'].count()
            system_dropped_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark By'] == 'SYSTEM')]['Account No.'].count()
            call_drop_ratio = (call_drop_count / connected * 100) if connected != 0 else None
            
            # Adding the SYSTEM DROP count based on 'STATUS' column containing 'SYSTEM DROP'
            system_drop_count = group[group['Status'].str.contains('SYSTEM DROP', na=False)]['Account No.'].count()

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
                'CALL DROP #': call_drop_count,
                'SYSTEM DROPPED #': system_dropped_count,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                'SYSTEM DROP #': system_drop_count,  # Added SYSTEM DROP count here
            }])], ignore_index=True)
        
        return summary_table

    st.write("## Overall Combined Summary Table")
    combined_summary_table = calculate_combined_summary(df)
    st.write(combined_summary_table, container_width=True)

    def calculate_summary(df, remark_type, remark_by=None):
        summary_table = pd.DataFrame(columns=[
            'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 
            'SYSTEM DROPPED #', 'CALL DROP RATIO #', 'SYSTEM DROP #'
        ])
        
        for date, group in df.groupby(df['Date'].dt.date):
            accounts = group[(group['Remark Type'] == remark_type) | ((group['Remark'] != 'Broken Promise') & (group['Remark Type'] == 'Follow Up') & (group['Remark By'] == remark_by))]['Account No.'].nunique()
            total_dialed = group[(group['Remark Type'] == remark_type) | ((group['Remark'] != 'Broken Promise') & (group['Remark Type'] == 'Follow Up') & (group['Remark By'] == remark_by))]['Account No.'].count()

            connected = group[(group['Call Status'] == 'CONNECTED') & (group['Remark Type'] == remark_type)]['Account No.'].count()
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            connected_acc = group[(group['Call Status'] == 'CONNECTED') & (group['Remark Type'] == remark_type)]['Account No.'].nunique()

            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

            ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0) & (group['Remark Type'] == remark_type)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

            call_drop_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark Type'] == remark_type)]['Account No.'].count()
            system_dropped_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark By'] == 'SYSTEM') & (group['Remark Type'] == remark_type)]['Account No.'].count()
            call_drop_ratio = (call_drop_count / connected * 100) if connected != 0 else None

            # Adding the SYSTEM DROP count based on 'STATUS' column containing 'SYSTEM DROP'
            system_drop_count = group[group['Status'].str.contains('SYSTEM DROP', na=False)]['Account No.'].count()

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
                'CALL DROP #': call_drop_count,
                'SYSTEM DROPPED #': system_dropped_count,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
                'SYSTEM DROP #': system_drop_count,  # Added SYSTEM DROP count here
            }])], ignore_index=True)
        
        return summary_table

    # Continue with the rest of your implementation as before...
