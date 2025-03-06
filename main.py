import pandas as pd

def filter_ptp_data(input_file, output_file):
    # Read the Excel or CSV file
    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    elif input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
    else:
        raise ValueError("The input file must be in .xlsx or .csv format.")
    
    # Filter rows based on conditions
    filtered_df = df[
        df['STATUS'].str.contains('PTP') & 
        ~df['STATUS'].str.contains('PTP FF|PTP FOLLOW UP') &
        df['REMARKS BY'].str.contains(r'\b(?!SYSTEM\b)\w+', na=False)
    ]
    
    # Count the number of filtered rows
    total_ptp_count = len(filtered_df)
    
    print(f"Total PTP count: {total_ptp_count}")
    
    # Save the filtered data to a new file (CSV or Excel)
    if output_file.endswith('.xlsx'):
        filtered_df.to_excel(output_file, index=False)
    elif output_file.endswith('.csv'):
        filtered_df.to_csv(output_file, index=False)
    else:
        raise ValueError("The output file must be in .xlsx or .csv format.")
    
    print(f"Filtered data saved to: {output_file}")

# Example Usage
input_file = 'your_input_file.xlsx'  # Replace with your input file path
output_file = 'filtered_ptp_data.xlsx'  # Replace with your desired output file path
filter_ptp_data(input_file, output_file)
