import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
from pandas import ExcelWriter

st.set_page_config(layout="wide", page_title="Daily Remark Summary", page_icon="📊", initial_sidebar_state="expanded")

st.title('Daily Remark Summary')

@st.cache_data
def load_data(uploaded_file):
    st.write("Test")
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.upper()
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df = df[df['DATE'].dt.weekday != 6]  # Exclude Sundays
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

def to_excel(df_dict):
    output = BytesIO()
    with ExcelWriter(output, engine='xlsxwriter', date_format='yyyy-mm-dd') as writer:
        workbook = writer.book
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFFF00',
        })
        center_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        header_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': 'red',
            'font_color': 'white',
            'bold': True
        })
        comma_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0'
        })
        percent_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '0.00%'
        })
        date_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': 'yyyy-mm-dd'
        })
        time_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': 'hh:mm:ss'
        })
        
        for sheet_name, df in df_dict.items():
            # Convert percentage strings back to floats for Excel
            df_for_excel = df.copy()
            df_for_excel['CALL DROP RATIO #'] = df_for_excel['CALL DROP RATIO #'].str.rstrip('%').astype(float)
            
            df_for_excel.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
            worksheet = writer.sheets[sheet_name]
            
            worksheet.merge_range('A1:' + chr(65 + len(df.columns) - 1) + '1', sheet_name, title_format)
            
            for col_num, col_name in enumerate(df_for_excel.columns):
                worksheet.write(1, col_num, col_name, header_format)
            
            for row_num in range(2, len(df_for_excel) + 2):
                for col_num, col_name in enumerate(df_for_excel.columns):
                    value = df_for_excel.iloc[row_num - 2, col_num]
                    if col_name == 'DATE':
                        if isinstance(value, (pd.Timestamp, datetime.date)):
                            worksheet.write_datetime(row_num, col_num, value, date_format)
                        else:
                            worksheet.write(row_num, col_num, value, date_format)
                    elif col_name in ['TOTAL PTP AMOUNT', 'TOTAL BALANCE']:
                        worksheet.write(row_num, col_num, value, comma_format)
                    elif col_name in ['PENETRATION RATE (%)', 'CONNECTED RATE (%)', 'PTP RATE', 'CALL DROP RATIO #']:
                        worksheet.write(row_num, col_num, value / 100, percent_format)
                    elif col_name in ['TOTAL TALK TIME', 'TALK TIME AVE']:
                        worksheet.write(row_num, col_num, value, time_format)
                    else:
                        worksheet.write(row_num, col_num, value, center_format)
            
            for col_num, col_name in enumerate(df_for_excel.columns):
                max_len = max(
                    df_for_excel[col_name].astype(str).str.len().max(),
                    len(col_name)
                ) + 2
                worksheet.set_column(col_num, col_num, max_len)

    return output.getvalue()

if uploaded_file is not None:
    df = load_data(uploaded_file)
    df = df[~df['DEBTOR'].str.contains("DEFAULT_LEAD_", case=False, na=False)]
    df = df[~df['STATUS'].str.contains('ABORT', na=False)]
    
    excluded_remarks = [
        "Broken Promise", "New files imported", "Updates when case reassign to another collector", 
        "NDF IN ICS", "FOR PULL OUT (END OF HANDLING PERIOD)", "END OF HANDLING PERIOD", "New Assignment -",
    ]
    df = df[~df['REMARK'].str.contains('|'.join(excluded_remarks), case=False, na=False)]
    df = df[~df['CALL STATUS'].str.contains('OTHERS', case=False, na=False)]
    
    df['SERVICE NO.'] = df['SERVICE NO.'].astype(str)
    df['CYCLE'] = df['SERVICE NO.'].str.extract(r'(\d+)')
    df['CYCLE'] = df['CYCLE'].fillna('Unknown')
    df['CYCLE'] = df['CYCLE'].astype(str)

    def format_seconds_to_hms(seconds):
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def calculate_summary(df, remark_types, manual_correction=False):
        summary_columns = [
            'DATE', 'CLIENT', 'COLLECTORS', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'TOTAL TALK TIME', 'TALK TIME AVE', 'PTP ACC', 'PTP RATE', 
            'TOTAL PTP AMOUNT', 'TOTAL BALANCE', 'CALL DROP #', 'SYSTEM DROP', 'CALL DROP RATIO #'
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
            # Format as percentage string with 2 decimal places
            call_drop_ratio_formatted = f"{call_drop_ratio:.2f}%"

            collectors = group[group['CALL DURATION'].notna()]['REMARK BY'].nunique()
            total_talk_seconds = group['TALK TIME DURATION'].sum()
            total_talk_time = format_seconds_to_hms(total_talk_seconds)
            talk_time_ave = format_seconds_to_hms(total_talk_seconds / collectors) if collectors != 0 else "00:00:00"

            summary_data = {
                'DATE': date,
                'CLIENT': client,
                'COLLECTORS': collectors,
                'ACCOUNTS': accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': round(penetration_rate),
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': round(connected_rate),
                'CONNECTED ACC': connected_acc,
                'TOTAL TALK TIME': total_talk_time,
                'TALK TIME AVE': talk_time_ave,
                'PTP ACC': ptp_acc,
                'PTP RATE': round(ptp_rate),
                'TOTAL PTP AMOUNT': total_ptp_amount,
                'TOTAL BALANCE': total_balance,
                'CALL DROP #': call_drop_count,
                'SYSTEM DROP': system_drop,
                'CALL DROP RATIO #': call_drop_ratio_formatted,
            }
            
            summary_table = pd.concat([summary_table, pd.DataFrame([summary_data])], ignore_index=True)
        
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
