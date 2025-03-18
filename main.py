import os
import pandas as pd
import streamlit as st

# Function to load data from a CSV or Excel file
def load_file(file):
    try:
        # Check if the uploaded file is a CSV or Excel file
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")
            return None
        return df
    except Exception as e:
        st.error(f"An error occurred while loading the file: {e}")
        return None

# Function to calculate combined summary
def calculate_combined_summary(df):
    try:
        # Example calculation for combined summary
        combined_summary = df.groupby(['Balance Category', 'Cycle Date']).agg(
            Total_Amount=('Amount', 'sum'),
            Average_Amount=('Amount', 'mean')
        ).reset_index()
        return combined_summary
    except Exception as e:
        st.error(f"An error occurred while calculating the combined summary: {e}")
        return None

# Function to calculate overall predictive summary
def calculate_overall_predictive(df):
    try:
        # Example calculation for overall predictive
        overall_predictive = df.groupby(['Balance Category']).agg(
            Total_Amount=('Amount', 'sum'),
            Average_Amount=('Amount', 'mean')
        ).reset_index()
        return overall_predictive
    except Exception as e:
        st.error(f"An error occurred while calculating the overall predictive summary: {e}")
        return None

# Function to calculate overall manual summary
def calculate_overall_manual(df):
    try:
        # Example calculation for overall manual summary
        overall_manual = df.groupby(['Balance Category']).agg(
            Manual_Amount=('Manual Amount', 'sum')
        ).reset_index()
        return overall_manual
    except Exception as e:
        st.error(f"An error occurred while calculating the overall manual summary: {e}")
        return None

# Function to calculate per cycle summary
def calculate_per_cycle(df):
    try:
        # Example calculation for per cycle summary
        per_cycle = df.groupby(['Cycle Date']).agg(
            Total_Amount=('Amount', 'sum'),
            Average_Amount=('Amount', 'mean')
        ).reset_index()
        return per_cycle
    except Exception as e:
        st.error(f"An error occurred while calculating the per cycle summary: {e}")
        return None

# Function to calculate per balance category summary
def calculate_per_balance_category(df):
    try:
        # Example calculation for per balance category summary
        per_balance_category = df.groupby(['Balance Category']).agg(
            Total_Amount=('Amount', 'sum'),
            Average_Amount=('Amount', 'mean')
        ).reset_index()
        return per_balance_category
    except Exception as e:
        st.error(f"An error occurred while calculating the per balance category summary: {e}")
        return None

# Streamlit file uploader
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])

# If a file is uploaded, process it
if uploaded_file is not None:
    try:
        # Read the uploaded file into a DataFrame
        df = load_file(uploaded_file)
        if df is not None:
            st.write("File loaded successfully!")
            st.write(df)  # Display the dataframe in Streamlit
            
            # Calculate combined summary
            combined_summary = calculate_combined_summary(df)
            if combined_summary is not None:
                st.write("Combined Summary")
                st.write(combined_summary)
            
            # Calculate overall predictive summary
            overall_predictive = calculate_overall_predictive(df)
            if overall_predictive is not None:
                st.write("Overall Predictive Summary")
                st.write(overall_predictive)
            
            # Calculate overall manual summary
            overall_manual = calculate_overall_manual(df)
            if overall_manual is not None:
                st.write("Overall Manual Summary")
                st.write(overall_manual)
            
            # Calculate per cycle summary
            per_cycle = calculate_per_cycle(df)
            if per_cycle is not None:
                st.write("Per Cycle Summary")
                st.write(per_cycle)
            
            # Calculate per balance category summary
            per_balance_category = calculate_per_balance_category(df)
            if per_balance_category is not None:
                st.write("Per Balance Category Summary")
                st.write(per_balance_category)
    
    except Exception as e:
        st.error(f"An error occurred while processing the uploaded file: {e}")
