import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Daily Remark Summary", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode
st.markdown(
    """
    <style>
    .reportview-container {
        background: #2E2E2E;
        color: white;
    }
    .sidebar .sidebar-content {
        background: #2E2E2E;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Daily Remark Summary')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df[~df['Remark By'].isin([
        'FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ',
        'GPRAMOS', 'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA',
        'RRCARLIT', 'MEBEJER', 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO',
        'JMBORROMEO', 'EUGALERA', 'JATERRADO'
    ])] 
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.write(df)

    # Exclude rows where STATUS contains 'BP' (Broken Promise)
    df = df[~df['Status'].str.contains('BP', na=False)]

    # PER CYCLE OB BALANCE PENETRATION
    st.write("## PER CYCLE OB BALANCE PENETRATION")
    
    balance_categories = {
        '6,000.00 - 49,999.00': (6000, 49999),
        '50,000.00 - 99,999.00': (50000, 99999),
        '100,000.00 and up': (100000, float('inf'))
    }
    
    for cycle, cycle_group in df.groupby('Service No.'):
        st.write(f"### Cycle: {cycle}")
        
        balance_summary = pd.DataFrame(columns=['Balance Category', 'Accounts', 'Total Dialed', 'Penetration Rate (%)'])
        
        for category, (low, high) in balance_categories.items():
            balance_group = cycle_group[(cycle_group['OB Balance'] >= low) & (cycle_group['OB Balance'] <= high)]
            
            accounts = balance_group['Account No.'].nunique()
            total_dialed = balance_group.shape[0]
            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None
            
            balance_summary = pd.concat([balance_summary, pd.DataFrame([{
                'Balance Category': category,
                'Accounts': accounts,
                'Total Dialed': total_dialed,
                'Penetration Rate (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
            }])], ignore_index=True)
        
        st.write(balance_summary)

    # Summary Table by Cycle Predictive
    st.write("## Summary Table by Cycle Predictive")
    for cycle, cycle_group in df.groupby('Service No.'):
        st.write(f"Cycle: {cycle}")
        summary_table = calculate_summary(cycle_group, 'Predictive', 'SYSTEM')
        st.write(summary_table)

    # Summary Table by Cycle Manual
    st.write("## Summary Table by Cycle Manual")
    for manual_cycle, manual_cycle_group in df.groupby('Service No.'):
        st.write(f"Cycle: {manual_cycle}")
        summary_table = calculate_summary(manual_cycle_group, 'Outgoing')
        st.write(summary_table)
