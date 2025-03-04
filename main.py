# Define time bins
time_bins = [
    "06:00-07:00 AM", "07:01-08:00 AM", "08:01-09:00 AM", "09:01-10:00 AM",
    "10:01-11:00 AM", "11:01-12:00 PM", "12:01-01:00 PM", "01:01-02:00 PM",
    "02:01-03:00 PM", "03:01-04:00 PM", "04:01-05:00 PM", "05:01-06:00 PM",
    "06:01-07:00 PM", "07:01-08:00 PM", "08:01-09:00 PM"
]

time_intervals = [
    ("06:00:00", "07:00:00"), ("07:01:00", "08:00:00"), ("08:01:00", "09:00:00"),
    ("09:01:00", "10:00:00"), ("10:01:00", "11:00:00"), ("11:01:00", "12:00:00"),
    ("12:01:00", "13:00:00"), ("13:01:00", "14:00:00"), ("14:01:00", "15:00:00"),
    ("15:01:00", "16:00:00"), ("16:01:00", "17:00:00"), ("17:01:00", "18:00:00"),
    ("18:01:00", "19:00:00"), ("19:01:00", "20:00:00"), ("20:01:00", "21:00:00")
]

# Ensure 'Time' column is in datetime format
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time

# Initialize DataFrame
time_summary = pd.DataFrame(columns=['Time Range', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'])

for i, (start, end) in enumerate(time_intervals):
    time_mask = (df['Time'] >= pd.to_datetime(start, format='%H:%M:%S').time()) & \
                (df['Time'] <= pd.to_datetime(end, format='%H:%M:%S').time())

    # Apply filters
    df_filtered = df[time_mask]

    # Total Connected: Unique 'Account No.' where 'Call Status' = CONNECTED
    total_connected = df_filtered[df_filtered['Call Status'] == 'CONNECTED']['Account No.'].nunique()
    
    # Total PTP: Unique 'Account No.' where 'Status' contains 'PTP' & 'PTP Amount' > 0
    total_ptp = df_filtered[df_filtered['Status'].str.contains('PTP', na=False) & (df_filtered['PTP Amount'] > 0)]['Account No.'].nunique()
    
    # Total RPC: Count where 'Status' contains 'RPC'
    total_rpc = df_filtered[df_filtered['Status'].str.contains('RPC', na=False)]['Account No.'].count()
    
    # PTP Amount: Sum where 'PTP Amount' > 0
    ptp_amount = df_filtered[df_filtered['PTP Amount'] > 0]['PTP Amount'].sum()
    
    # Balance Amount: Sum where 'Balance' > 0 & 'PTP Amount' > 0
    balance_amount = df_filtered[(df_filtered['Balance'] > 0) & (df_filtered['PTP Amount'] > 0)]['Balance'].sum()

    time_summary = pd.concat([time_summary, pd.DataFrame([{
        'Time Range': time_bins[i],
        'Total Connected': total_connected,
        'Total PTP': total_ptp,
        'Total RPC': total_rpc,
        'PTP Amount': ptp_amount,
        'Balance Amount': balance_amount
    }])], ignore_index=True)

# ------------------- ADD TOTAL ROW -------------------
totals = pd.DataFrame([{
    'Time Range': 'Total',
    'Total Connected': time_summary['Total Connected'].sum(),
    'Total PTP': time_summary['Total PTP'].sum(),
    'Total RPC': time_summary['Total RPC'].sum(),
    'PTP Amount': time_summary['PTP Amount'].sum(),
    'Balance Amount': time_summary['Balance Amount'].sum()
}])

time_summary = pd.concat([time_summary, totals], ignore_index=True)

# Display Time Summary Table
st.markdown('<div class="category-title">Hourly Productivity Summary</div>', unsafe_allow_html=True)
st.dataframe(time_summary)
