import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import defaultdict

st.set_page_config(layout="wide")
st.title("MAYA AI: All-in-One Master Engine (Sabhi Shifts Ek Sath)")
st.write("Ab bar-bar shift badalne ki zaroorat nahi. Ek click mein sabhi shifton ka prediction aur Parikshan dekhein. Sath hi 3 tarah ki 11-din ki history check karein.")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

def get_andar_bahar(val):
    if pd.isna(val): return None, None
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

    st.markdown("### 📅 Tareekh Chunein")
    max_date = df['DATE'].max().to_pydatetime()
    min_date = df['DATE'].min().to_pydatetime()
    
    selected_date = st.date_input("Jis din ko INPUT (Kal) manna hai:", 
                                  value=max_date - timedelta(days=1), min_value=min_date, max_value=max_date)

    sel_date_pd = pd.to_datetime(selected_date)
    
    if sel_date_pd not in df['DATE'].values:
        st.error("Sheet mein is Input date ka data nahi hai.")
    else:
        idx_kal = df[df['DATE'] == sel_date_pd].index[0]
        idx_parikshan = idx_kal + 1 if (idx_kal + 1) < len(df) else None
        
        if idx_kal < 5:
            st.error("Engine ko check karne ke liye aur purani history chahiye (kam se kam 5 din).")
        else:
            with st.spinner("MAYA AI sabhi shifton ka data ek sath scan kar rahi hai..."):
                
                # --- CORE PREDICTION FUNCTION (NO GLOBALS, WORKS FOR ANY SHIFT & DATE) ---
                def get_vip_jodis_for_shift(history_df, shift_col, target_idx):
                    if target_idx < 2 or target_idx > len(history_df): return []
                    
                    transition_a = defaultdict(lambda: defaultdict(int))
                    transition_b = defaultdict(lambda: defaultdict(int))
                    
                    # Target index se pehle ki history scan karo
                    for i in range(2, target_idx):
                        p_a, p_b = get_andar_bahar(history_df.iloc[i-2][shift_col])
                        k_a, k_b = get_andar_bahar(history_df.iloc[i-1][shift_col])
                        aaj_a,
                        
