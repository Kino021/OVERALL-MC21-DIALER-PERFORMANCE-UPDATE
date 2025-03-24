import streamlit as st
import pandas as pd

# Function to calculate the combined summary
def calculate_combined_summary(df):
    # Check if 'CLIENT' column exists
    if 'CLIENT' not in df.columns:
        st.error("The 'CLIENT' column is missing in the data.")
        return None
    
    summary = []
    grouped = df.groupby('CLIENT')  # Grouping by 'CLIENT' column

    for client_name, group in grouped:
        # Check if the 'CLIENT' column exists in the group
        if 'CLIENT' in group.columns:
            client = group['CLIENT'].iloc[0]  # Taking the client name from the group (assuming it's the same for the group)
        else:
            st.error(f"Column 'CLIENT' is missing for the group: {client_name}")
            continue

        # Add other summary calculations for the group if needed
        total_records = len(group)
        # You can add any other calculation here, like sum, mean, etc.

        summary.append({
            'CLIENT': client,
            'Total Records': total_records,
            # Add other relevant summary information here if needed
        })

    # Convert the summary list to a DataFrame
    combined_summary = pd.DataFrame(summary)
    return combined_summary


# Streamlit app
def main():
    st.title("Dialer Performance Update")

    # File uploader to upload CSV data
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

    if uploaded_file is not None:
        # Read the uploaded CSV file into a DataFrame
        df = pd.read_csv(uploaded_file)

        # Display the first few rows of the dataframe for the user to inspect
        st.write("Data Preview:")
        st.write(df.head())

        # Calculate the combined summary
        combined_summary_table = calculate_combined_summary(df)

        if combined_summary_table is not None:
            # Display the combined summary table
            st.write("Combined Summary:")
            st.write(combined_summary_table)

if __name__ == "__main__":
    main()
