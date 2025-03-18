import os
import pandas as pd
import streamlit as st

# Function to load CSV file
def load_csv(file_path):
    try:
        # Check if file exists
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df
        else:
            st.error(f"File '{file_path}' not found. Please check the file path.")
            return None
    except Exception as e:
        # Handle other potential errors
        st.error(f"An error occurred while loading the file: {e}")
        return None

# Streamlit file uploader
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

# If a file is uploaded, process it
if uploaded_file is not None:
    # Load the CSV file uploaded by the user
    df = pd.read_csv(uploaded_file)
    st.write("File loaded successfully!")
    st.write(df)  # Display the dataframe in Streamlit

# Alternative: If you want to use a hardcoded file path instead of uploading
# Uncomment the following lines if using a local file path
# file_path = "your_data.csv"
# df = load_csv(file_path)
# if df is not None:
#     st.write(df)  # Display the dataframe if it's loaded
