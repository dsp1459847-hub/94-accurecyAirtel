import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("MAYA AI: Explicit Rule-Based Master Engine")
st.write("Is engine mein aap Input (Kal), Prediction, aur Parikshan (Aaj) teeno ek sath aamne-saamne dekh sakte hain.")

# ---------------------------------------------------------
# 1. AAPKA RULE BOOK 
# ---------------------------------------------------------
USER_RULES = {
    '0': ['8', '6', '7', '9', '3'],
    '1': ['8', '4', '5', '7', '0'],
    '2': ['9', '6', '5', '1', '4'],
    '3': ['9', '6', '7', '2', '0'],
    '4': ['3', '0', '1', '9', '8'],
    '5': ['2', '1', '9', '3', '6'],
    '6': ['0', '2', '9', '4', '5'],
    '7': ['1', '0', '5', '7', '4'],
    '8': ['4', '1', '3', '0', '7'],
    '9': ['9', '3', '8', '5', '7']
}

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

def get_andar_bahar(val):
    val = str(val).replace('.0', '').strip()
    if val in ['nan', 'XX', '']: return None, None
    if len(val) == 1 and val.isdigit(): val = '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
    return None, None

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    df = df.dropna(subset=['DATE'])
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('DATE').reset_index(drop=True)
    cols = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

    # --- DATE SELECTION ---
    st.subheader("📅 Tareekh Chunein (Input Data Ka Din)")
    max_date = df['DATE'].max().to_pydatetime()
    min_date = df['DATE'].min().to_pydatetime()
    
    selected_date = st.date_input("Jis din ka data INPUT manna hai (Kal):", 
                                  value=max_date - timedelta(days=1), min_value=min_date, max_value=max_date)
    sel_date_pd = pd.to_datetime(selected_date)
    
    # Parikshan Date = Input Date + 1
    parikshan_date_pd = sel_date_pd + pd.Timedelta(days=1)

    # --- 3-WAY HISTORY (11 Days ending on Parikshan Day) ---
    st.markdown("---")
    st.subheader(f"📚 3-Way History Data (Parikshan Din: {parikshan_date_pd.strftime('%d-%m-%Y')} tak ki 11 din ki list)")
    
    df_seq = df[df['DATE'] <= parikshan_date_pd].tail(11).copy()
    
    target_weekday = parikshan_date_pd.weekday()
    df_war = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.weekday == target_weekday)].tail(11).copy()
    
    target_day = parikshan_date_pd.day
    df_tarikh = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.day == target_day)].tail(11).copy()

    for d in [df_seq, df_war, df_tarikh]:
        d['DATE'] = d['DATE'].dt.strftime('%d-%m-%Y')

    tab1, tab2, tab3 = st.tabs(["1️⃣ Lagaatar (Seq) 11 Din", "2️⃣ War (Day) 11 Din", "3️⃣ Tareekh (Date) 11 Din"])
    
    with tab1:
        st.dataframe(df_seq[['DATE'] + cols].reset_index(drop=True), use_container_width=True)
    with tab2:
        st.dataframe(df_war[['DATE'] + cols].reset_index(drop=True), use_container_width=True)
    with tab3:
        st.dataframe(df_tarikh[['DATE'] + cols].reset_index(drop=True), use_container_width=True)

    # --- INPUTS & PARIKSHAN ACTUALS ---
    st.markdown("---")
    col_in, col_out = st.columns(2)
    
    with col_in:
        st.subheader(f"📥 Input Ke Ank ({sel_date_pd.strftime('%d-%m-%Y')})")
        day_data = df[df['DATE'] == sel_date_pd]
        inputs = {}
        if not day_data.empty:
            for c in cols:
                val = str(day_data.iloc[0][c]) if c in day_data.columns else ""
                if val == 'nan' or val == 'XX': val = ""
                inputs[c] = st.text_input(f"{c} Input:", value=val, key=f"inp_{c}")
        else:
            st.error("Input data nahi mila.")

    with col_out:
        st.subheader(f"🎯 Parikshan Ke Ank ({parikshan_date_pd.strftime('%d-%m-%Y')})")
        parikshan_data = df[df['DATE'] == parikshan_date_pd]
        actual_parikshan_results = {}
        if not parikshan_data.empty:
            for c in cols:
                val = str(parikshan_data.iloc[0][c]) if c in parikshan_data.columns else ""
                if val == 'nan' or val == 'XX': val = ""
                actual_parikshan_results[c] = val
                st.text_input(f"{c} Actual Result:", value=val, key=f"act_{c}", disabled=True)
        else:
            st.warning("Future date ya sheet me is din ka Parikshan data abhi nahi hai.")
            
