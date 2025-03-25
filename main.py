import streamlit as st
import pandas as pd
import datetime

st.set_page_config(layout="wide", page_title="Daily Remark Summary", page_icon="📊", initial_sidebar_state="expanded")

st.title('Daily Remark Summary')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.upper()
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df = df[df['DATE'].dt.weekday != 6]  # Exclude Sundays
    return df

# Convert DataFrame to CSV for download
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    df = df[~df['DEBTOR'].str.contains("DEFAULT_LEAD_", case=False, na=False)]
    df = df[~df['STATUS'].str.contains('ABORT', na=False)]
    
    excluded_remarks = [
        "Broken Promise", "New files imported", "Updates when case reassign to another collector", 
        "NDF IN ICS", "FOR PULL OUT (END OF HANDLING PERIOD)", "END OF HANDLING PERIOD" , "New Assignment -" ,
    ]
    df = df[~df['REMARK'].str.contains('|'.join(excluded_remarks), case=False, na=False)]
    df = df[~df['CALL STATUS'].str.contains('OTHERS', case=False, na=False)]
    
    df['SERVICE NO.'] = df['SERVICE NO.'].astype(str)
    df['CYCLE'] = df['SERVICE NO.'].str.extract(r'(\d+)')
    df['CYCLE'] = df['CYCLE'].fillna('Unknown')
    df['CYCLE'] = df['CYCLE'].astype(str)

    def format_seconds_to_hms(seconds):
        return str(datetime.timedelta(seconds=int(seconds)))

    def calculate_summary(df, remark_types, manual_correction=False, category=""):
        summary_columns = [
            'CATEGORY', 'CYCLE', 'DATE', 'CLIENT', 'COLLECTORS', 'ACCOUNTS', 'TOTAL DIALED', 
            'PENETRATION RATE (%)', 'CONNECTED #', 'CONNECTED RATE (%)', 'CONNECTED ACC', 
            'TOTAL TALK TIME', 'PTP ACC', 'PTP RATE', 'TOTAL PTP AMOUNT', 'TOTAL BALANCE', 
            'CALL DROP #', 'SYSTEM DROP', 'CALL DROP RATIO #'
        ]
        
        summary_table = pd.DataFrame(columns=summary_columns)
        
        df_filtered = df[df['REMARK TYPE'].isin(remark_types)].copy()
        df_filtered['DATE'] = df_filtered['DATE'].dt.date  

        for (date, client), group in df_filtered.groupby(['DATE', 'CLIENT']):
            accounts = group['ACCOUNT NO.'].nunique()
            total_dialed = group['ACCOUNT NO.'].count()
            connected = group[group['CALL STATUS'] == 'CONNECTED']['ACCOUNT NO.'].nunique()
            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else 0
            connected_acc = group[group['CALL STATUS'] == 'CONNECTED']['ACCOUNT NO.'].count()
            connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else 0
            ptp_acc = group[(group['STATUS'].str.contains('PTP', na=False)) & (group['PTP AMOUNT'] != 0)]['ACCOUNT NO.'].nunique()
            ptp_rate = (ptp_acc / connected * 100) if connected != 0 else 0
            total_ptp_amount = group[(group['STATUS'].str.contains('PTP', na=False)) & (group['PTP AMOUNT'] != 0)]['PTP AMOUNT'].sum()
            total_balance = group[(group['PTP AMOUNT'] != 0)]['BALANCE'].sum()
            system_drop = group[(group['STATUS'].str.contains('DROPPED', na=False)) & (group['REMARK BY'] == 'SYSTEM')]['ACCOUNT NO.'].count()
            call_drop_count = group[(group['STATUS'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                  (~group['REMARK BY'].str.upper().isin(['SYSTEM']))]['ACCOUNT NO.'].count()
            
            if manual_correction:
                call_drop_ratio = (call_drop_count / connected_acc * 100) if connected_acc != 0 else 0
            else:
                call_drop_ratio = (system_drop / connected_acc * 100) if connected_acc != 0 else 0

            collectors = group[group['CALL DURATION'].notna()]['REMARK BY'].nunique()
            total_talk_time = format_seconds_to_hms(group['TALK TIME DURATION'].sum())

            summary_data = {
                'CATEGORY': category,
                'CYCLE': 'Overall' if not category.startswith('Per Cycle') else '',
                'DATE': date,
                'CLIENT': client,
                'COLLECTORS': collectors,
                'ACCOUNTS': accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate)}%",
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate)}%",
                'CONNECTED ACC': connected_acc,
                'TOTAL TALK TIME': total_talk_time,
                'PTP ACC': ptp_acc,
                'PTP RATE': f"{round(ptp_rate)}%",
                'TOTAL PTP AMOUNT': total_ptp_amount,
                'TOTAL BALANCE': total_balance,
                'CALL DROP #': call_drop_count,
                'SYSTEM DROP': system_drop,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%",
            }
            
            summary_table = pd.concat([summary_table, pd.DataFrame([summary_data])], ignore_index=True)
        
        return summary_table.sort_values(by=['DATE'])

    def display_cycle_summary(df, remark_types, manual_correction=False, category=""):
        unique_cycles = df['CYCLE'].unique()
        all_cycle_data = pd.DataFrame()
        for cycle in unique_cycles:
            if cycle == 'Unknown':
                continue
            with st.container():
                st.subheader(f"Summary for Cycle {cycle}")
                cycle_df = df[df['CYCLE'] == cycle]
                cycle_summary = calculate_summary(cycle_df, remark_types, manual_correction, category)
                cycle_summary['CYCLE'] = cycle
                st.write(cycle_summary)
                all_cycle_data = pd.concat([all_cycle_data, cycle_summary], ignore_index=True)
        return all_cycle_data

    # Collect all data
    all_data = pd.DataFrame()

    # Overall Combined Summary
    st.write("## Overall Combined Summary Table")
    combined_summary = calculate_summary(df, ['Predictive', 'Follow Up', 'Outgoing'], category="Overall Combined")
    st.write(combined_summary)
    all_data = pd.concat([all_data, combined_summary], ignore_index=True)

    # Overall Predictive Summary
    st.write("## Overall Predictive Summary Table")
    predictive_summary = calculate_summary(df, ['Predictive', 'Follow Up'], category="Overall Predictive")
    st.write(predictive_summary)
    all_data = pd.concat([all_data, predictive_summary], ignore_index=True)

    # Overall Manual Summary
    st.write("## Overall Manual Summary Table")
    manual_summary = calculate_summary(df, ['Outgoing'], manual_correction=True, category="Overall Manual")
    st.write(manual_summary)
    all_data = pd.concat([all_data, manual_summary], ignore_index=True)

    # Per Cycle Predictive Summaries
    st.write("## Per Cycle Predictive Summary Tables")
    predictive_cycle_summary = display_cycle_summary(df, ['Predictive', 'Follow Up'], category="Per Cycle Predictive")
    all_data = pd.concat([all_data, predictive_cycle_summary], ignore_index=True)

    # Per Cycle Manual Summaries
    st.write("## Per Cycle Manual Summary Tables")
    manual_cycle_summary = display_cycle_summary(df, ['Outgoing'], manual_correction=True, category="Per Cycle Manual")
    all_data = pd.concat([all_data, manual_cycle_summary], ignore_index=True)

    # Single Download Button for All Data
    st.download_button(
        label="Download All Summary Data as CSV",
        data=convert_df_to_csv(all_data),
        file_name="all_summary_data.csv",
        mime="text/csv",
    )
