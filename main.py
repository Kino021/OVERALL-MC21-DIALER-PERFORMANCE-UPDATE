import streamlit as st
import pandas as pd

# ------------------- FUNCTION TO GENERATE HOURLY SUMMARY -------------------
def generate_time_summary(df):
    time_summary_by_date = {}

    # Exclude rows where Status is 'PTP FF UP'
    df = df[df['Status'] != 'PTP FF UP']

    # Define time intervals
    time_bins = [
        "06:00-07:00 AM", "07:01-08:00 AM", "08:01-09:00 AM", "09:01-10:00 AM",
        "10:01-11:00 AM", "11:01-12:00 PM", "12:01-01:00 PM", "01:01-02:00 PM",
        "02:01-03:00 PM", "03:01-04:00 PM", "04:01-05:00 PM", "05:01-06:00 PM",
        "06:01-07:00 PM", "07:01-08:00 PM", "08:01-09:00 PM"
    ]

    time_intervals = [
        ("06:00", "07:00"), ("07:01", "08:00"), ("08:01", "09:00"),
        ("09:01", "10:00"), ("10:01", "11:00"), ("11:01", "12:00"),
        ("12:01", "13:00"), ("13:01", "14:00"), ("14:01", "15:00"),
        ("15:01", "16:00"), ("16:01", "17:00"), ("17:01", "18:00"),
        ("18:01", "19:00"), ("19:01", "20:00"), ("20:01", "21:00")
    ]

    # Ensure 'Time' column is in datetime format
    try:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time  # Coerce errors to avoid crashes
    except Exception as e:
        st.error(f"Error processing Time column: {e}")
        return {}

    # Drop rows where Time could not be converted
    df = df.dropna(subset=['Time'])

    # Convert 'Time' to minutes since midnight for binning
    def time_to_minutes(time_str):
        h, m = map(int, time_str.split(':'))
        return h * 60 + m

    bins = [time_to_minutes(start) for start, _ in time_intervals] + [time_to_minutes("21:00")]

    # Assign time ranges
    df['Time in Minutes'] = df['Time'].apply(lambda t: t.hour * 60 + t.minute)
    df['Time Range'] = pd.cut(df['Time in Minutes'], bins=bins, labels=time_bins, right=False)

    # Remove NaN time ranges
    df = df.dropna(subset=['Time Range'])

    for (date, time_range), time_group in df[~df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Time Range']):
        total_connected = time_group[time_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['Account No.'].nunique()
        total_rpc = time_group[time_group['Status'].str.contains('RPC', na=False)]['Account No.'].count()
        ptp_amount = time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        balance_amount = time_group[
            (time_group['Status'].str.contains('PTP', na=False)) & 
            (time_group['PTP Amount'] != 0) & 
            (time_group['Balance'] != 0)
        ]['Balance'].sum()

        time_summary_entry = pd.DataFrame([{
            'Date': date,
            'Time Range': time_range,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])
        
        if date in time_summary_by_date:
            time_summary_by_date[date] = pd.concat([time_summary_by_date[date], time_summary_entry], ignore_index=True)
        else:
            time_summary_by_date[date] = time_summary_entry

    # Add total row per date
    for date, summary in time_summary_by_date.items():
        totals = {
            'Date': 'Total',
            'Time Range': '',
            'Total Connected': summary['Total Connected'].sum(),
            'Total PTP': summary['Total PTP'].sum(),
            'Total RPC': summary['Total RPC'].sum(),
            'PTP Amount': summary['PTP Amount'].sum(),
            'Balance Amount': summary['Balance Amount'].sum()
        }
        time_summary_by_date[date] = pd.concat([summary, pd.DataFrame([totals])], ignore_index=True)

    return time_summary_by_date

# ------------------- MAIN APP LOGIC -------------------
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    
    df['Date'] = pd.to_datetime(df['Date'])
    
    time_summary_by_date = generate_time_summary(df)
    
    # Display the title
    st.markdown('<div class="category-title">📅 Hourly PTP Summary</div>', unsafe_allow_html=True)

    for date, summary in time_summary_by_date.items():
        st.markdown(f"### {date}")
        st.dataframe(summary)
