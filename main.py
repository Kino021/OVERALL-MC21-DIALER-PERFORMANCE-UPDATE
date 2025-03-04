# Function to categorize time into specific time ranges
def get_time_range(hour, minute):
    time_ranges = [
        (6, 0, "06:00AM-07:00AM"), (7, 1, "07:01AM-08:00AM"), (8, 1, "08:01AM-09:00AM"),
        (9, 1, "09:01AM-10:00AM"), (10, 1, "10:01AM-11:00AM"), (11, 1, "11:01AM-12:00PM"),
        (12, 1, "12:01PM-01:00PM"), (13, 1, "01:01PM-02:00PM"), (14, 1, "02:01PM-03:00PM"),
        (15, 1, "03:01PM-04:00PM"), (16, 1, "04:01PM-05:00PM"), (17, 1, "05:01PM-06:00PM"),
        (18, 1, "06:01PM-07:00PM"), (19, 1, "07:01PM-08:00PM"), (20, 1, "08:01PM-09:00PM"),
    ]

    for start_hour, start_minute, label in time_ranges:
        if hour == start_hour and minute >= start_minute:
            return label
    return "Outside Range"

# Ensure 'Time' column is in datetime format
df['Time'] = pd.to_datetime(df['Time'], errors='coerce')  # Convert & handle errors

# Drop rows where 'Time' couldn't be converted
df = df.dropna(subset=['Time'])

# Apply the time range function
df['Time Range'] = df['Time'].apply(lambda x: get_time_range(x.hour, x.minute))

# Now you can use 'Time Range' in groupby or other calculations
