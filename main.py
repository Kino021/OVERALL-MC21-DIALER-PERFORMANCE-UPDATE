import streamlit as st
import pandas as pd
import plotly.express as px

# Load Data
def load_data():
    # Replace with actual data source
    df = pd.read_csv("data.csv")
    return df

# Productivity Summary Table
def productivity_summary(df):
    st.subheader("Productivity Summary Table")
    st.dataframe(df)

# Productivity Summary per Cycle
def productivity_per_cycle(df):
    st.subheader("Productivity Summary per Cycle")
    cycle_summary = df.groupby("Date").sum()
    st.dataframe(cycle_summary)

# Productivity Summary per Collector
def productivity_per_collector(df):
    st.subheader("Productivity Summary per Collector")
    collector_summary = df.groupby("Collector").sum()
    st.dataframe(collector_summary)

# Hourly PTP Summary
def hourly_ptp_summary(df):
    st.subheader("Hourly PTP Summary")
    fig = px.line(df, x="Hour", y="PTP", title="Hourly PTP Summary")
    st.plotly_chart(fig)

# Main Function
def main():
    st.title("PRODUCTIVITY PER AGENT")
    df = load_data()
    productivity_summary(df)
    productivity_per_cycle(df)
    productivity_per_collector(df)
    hourly_ptp_summary(df)

if __name__ == "__main__":
    main()
