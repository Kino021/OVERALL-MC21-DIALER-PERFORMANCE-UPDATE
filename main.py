import pandas as pd
import streamlit as st
import plotly.express as px

# Load data
def load_data():
    file = st.file_uploader("Upload CSV", type=["csv"])
    if file is not None:
        df = pd.read_csv(file)
        return df
    return None

# Productivity Summary Table
def productivity_summary(df):
    st.subheader("Productivity Summary Table")
    st.dataframe(df.describe())

# Productivity Summary per Cycle (Grouped by Date)
def productivity_per_cycle(df):
    st.subheader("Productivity Summary per Cycle")
    df['Date'] = pd.to_datetime(df['Date'])
    cycle_summary = df.groupby('Date').sum()
    st.line_chart(cycle_summary)

# Productivity Summary per Collector
def productivity_per_collector(df):
    st.subheader("Productivity Summary per Collector")
    collector_summary = df.groupby('Collector').sum()
    st.bar_chart(collector_summary)

# Hourly PTP Summary
def hourly_ptp_summary(df):
    st.subheader("Hourly PTP Summary")
    df['Hour'] = pd.to_datetime(df['Time']).dt.hour
    hourly_summary = df.groupby('Hour').sum()
    fig = px.line(hourly_summary, x=hourly_summary.index, y='PTP', title='Hourly PTP Summary')
    st.plotly_chart(fig)

# Collector Summary
def collector_summary(df):
    st.subheader("Collector Summary")
    top_collectors = df.groupby('Collector').sum().sort_values(by='PTP', ascending=False)
    st.dataframe(top_collectors)

# Cycle Summary
def cycle_summary(df):
    st.subheader("Cycle Summary")
    cycle_summary = df.groupby('Cycle').sum()
    st.bar_chart(cycle_summary)

# Main Streamlit App
def main():
    st.title("PRODUCTIVITY PER AGENT")
    df = load_data()
    if df is not None:
        productivity_summary(df)
        productivity_per_cycle(df)
        productivity_per_collector(df)
        hourly_ptp_summary(df)
        collector_summary(df)
        cycle_summary(df)

if __name__ == "__main__":
    main()
