import pandas as pd
import streamlit as st
from datetime import timedelta

st.set_page_config(layout="wide")
st.title("MAYA AI: 3D Cross-Elimination & Selection Engine")
st.write("Yeh engine Seedha (Straight), Upar-Neeche (Vertical), aur Teda (Cross) teeno tarah se rules check karta hai. Jo rule history mein fail hain unhe hatata hai, jo paas hain unhe apply karke VIP Jodi banata hai.")

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

    col_date, col_shift = st.columns(2)
    max_date = df['DATE'].max().to_pydatetime()
    min_date = df['DATE'].min().to_pydatetime()
    
    with col_date:
        selected_date = st.date_input("📅 Jis din ko INPUT (Kal) manna hai:", 
                                      value=max_date - timedelta(days=1), min_value=min_date, max_value=max_date)
    with col_shift:
        target_shift = st.selectbox("🎯 Aaj kis Shift ka Ank nikalna hai?", cols)

    sel_date_pd = pd.to_datetime(selected_date)
    
    if sel_date_pd not in df['DATE'].values:
        st.error("Sheet mein is Input date ka data nahi hai.")
    else:
        idx_kal = df[df['DATE'] == sel_date_pd].index[0]
        idx_parikshan = idx_kal + 1 if idx_kal + 1 < len(df) else None
        
