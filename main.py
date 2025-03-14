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

    # Exclude rows where STATUS contains 'BP' (Broken Promise)
    df = df[~df['Status'].str.contains('BP', na=False)]

    # Calculate Combined Summary Table
    def calculate_combined_summary(df):
        summary_table = pd.DataFrame(columns=[ 
            'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #'
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

            # Drop Call Count: Calculate drop calls for both predictive and manual directly
            predictive_drop_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark By'] == 'SYSTEM')].shape[0]
            manual_drop_count = group[(group['Call Status'] == 'DROPPED') & 
                                       (group['Remark Type'] == 'Outgoing') & 
                                       (~group['Remark By'].str.upper().isin(['SYSTEM']))].shape[0]
            drop_call_count = predictive_drop_count + manual_drop_count

            call_drop_ratio = (drop_call_count / connected * 100) if connected != 0 else None

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
                'CALL DROP #': drop_call_count,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None
            }])], ignore_index=True)

        return summary_table

    st.write("## Overall Combined Summary Table")
    combined_summary_table = calculate_combined_summary(df)
    st.write(combined_summary_table, container_width=True)

    def calculate_summary(df, remark_type, remark_by=None, balance_min=None, balance_max=None):
        summary_table = pd.DataFrame(columns=[ 
            'Day', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'CALL DROP #', 'CALL DROP RATIO #'
        ])

        for date, group in df.groupby(df['Date'].dt.date):
            accounts = group[(group['Remark Type'] == remark_type) | 
                             ((group['Remark'] != 'Broken Promise') & 
                              (group['Remark Type'] == 'Follow Up') & 
                              (group['Remark By'] == remark_by))]['Account No.'].nunique()
            total_dialed = group[(group['Remark Type'] == remark_type) | 
                                 ((group['Remark'] != 'Broken Promise') & 
                                  (group['Remark Type'] == 'Follow Up') & 
                                  (group['Remark By'] == remark_by))]['Account No.'].count()

            connected = group[(group['Call Status'] == 'CONNECTED') & 
                              (group['Remark Type'] == remark_type)]['Account No.'].count()
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            connected_acc = group[(group['Call Status'] == 'CONNECTED') & 
                                  (group['Remark Type'] == remark_type)]['Account No.'].nunique()

            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

            ptp_acc = group[(group['Status'].str.contains('PTP', na=False)) & 
                            (group['PTP Amount'] != 0) & 
                            (group['Remark Type'] == remark_type)]['Account No.'].nunique()
            ptp_rate = (ptp_acc / connected_acc * 100) if connected_acc != 0 else None

            # Drop call count logic for the tables
            if remark_type == 'Predictive' and remark_by == 'SYSTEM':
                drop_call_count = group[(group['Call Status'] == 'DROPPED') & (group['Remark By'] == 'SYSTEM')]['Account No.'].count()
            elif remark_type == 'Outgoing' and remark_by is None:  # For manual, check only non-system agents
                drop_call_count = group[(group['Call Status'] == 'DROPPED') & 
                                         (group['Remark Type'] == 'Outgoing') & 
                                         (~group['Remark By'].str.upper().isin(['SYSTEM']))]['Account No.'].count()

            call_drop_ratio = (drop_call_count / connected * 100) if connected != 0 else None

            # Filter by balance range if provided
            if balance_min is not None and balance_max is not None:
                group = group[(group['Balance'] >= balance_min) & (group['Balance'] <= balance_max)]

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
                'CALL DROP #': drop_call_count,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None
            }])], ignore_index=True)

        return summary_table

    # Penetration per OB Amount Calculation - Separate Categories for Summary Table by Cycle Predictive
    st.write("## Summary Table by Cycle Predictive - Overall Predictive")
    
    # Filtering for Predictive Category
    predictive_summary = calculate_summary(df, 'Predictive', 'SYSTEM')

    # Penetration per OB Amount Categories (6,000 - 50,000, 50,000 - 100,000, 100,000+)
    for cycle, cycle_group in df.groupby('Service No.'):

        st.write(f"### Cycle {cycle} - Predictive")

        # Display Predictive Data for this Cycle
        predictive_data = calculate_summary(cycle_group, 'Predictive', 'SYSTEM')
        st.write("#### Predictive Summary")
        st.write(predictive_data)

        st.write(f"### Cycle {cycle} - OB Amount Categories")

        # Filtering and displaying OB Amount Categories
        for min_amount, max_amount, label in [(6000, 50000, '6,000.00 - 50,000.00'),
                                             (50000, 100000, '50,000.00 - 100,000.00'),
                                             (100000, float('inf'), '100,000.00 and above')]:
            st.write(f"#### {label}")
            filtered_data = calculate_summary(cycle_group, 'Predictive', 'SYSTEM', min_amount, max_amount)
            st.write(filtered_data)
