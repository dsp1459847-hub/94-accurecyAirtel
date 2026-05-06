import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import defaultdict

st.set_page_config(layout="wide")
st.title("MAYA AI: All-in-One Master Engine (Fixed UI)")
st.write("Ab calendar apne aap sahi tareekh chuega aur sabhi shifton ki prediction 100% screen par dikhegi.")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

def get_andar_bahar(val):
    if pd.isna(val): return None, None
    val = str(val).replace('.0', '').strip()
    if val in ['nan', 'XX', '']: return None, None
    if len(val) == 1 and val.isdigit(): val = '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
    return None, None

if uploaded_file is not None:
    # 1. Data Loading
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    df = df.dropna(subset=['DATE'])
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('DATE').reset_index(drop=True)
    cols = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

    # 2. Find the last VALID date (jisme sach me data bhara hua hai)
    valid_df = df.dropna(subset=cols, how='all')
    if not valid_df.empty:
        max_valid_date = valid_df['DATE'].max().date()
    else:
        max_valid_date = df['DATE'].max().date()

    st.markdown("### 📅 Tareekh Chunein")
    
    # Ab calendar default me valid date hi uthayega
    selected_date = st.date_input("Jis din ko INPUT (Kal) manna hai:", 
                                  value=max_valid_date, 
                                  min_value=df['DATE'].min().date(), 
                                  max_value=df['DATE'].max().date())

    sel_date_pd = pd.to_datetime(selected_date)
    
    date_match = df[df['DATE'] == sel_date_pd]
    
    if date_match.empty:
        st.error("Sheet mein is Input date ka data bilkul nahi hai.")
    else:
        idx_kal = date_match.index[0]
        idx_parikshan = idx_kal + 1 if (idx_kal + 1) < len(df) else None
        
        if idx_kal < 2:
            st.warning("Engine ko calculate karne ke liye kam se kam 3 din ka purana data chahiye.")
        else:
            with st.spinner("MAYA AI sabhi shifton ka data calculate kar rahi hai..."):
                
                # --- CORE PREDICTION FUNCTION (Fixed so it never fails silently) ---
                def get_vip_jodis_for_shift(history_df, shift_col, target_idx):
                    if target_idx < 2 or target_idx >= len(history_df) + 1: return []
                    
                    transition_a = defaultdict(lambda: defaultdict(int))
                    transition_b = defaultdict(lambda: defaultdict(int))
                    
                    general_a = defaultdict(int)
                    general_b = defaultdict(int)
                    
                    for i in range(2, target_idx):
                        p_a, p_b = get_andar_bahar(history_df.iloc[i-2][shift_col])
                        k_a, k_b = get_andar_bahar(history_df.iloc[i-1][shift_col])
                        aaj_a, aaj_b = get_andar_bahar(history_df.iloc[i][shift_col])
                        
                        if p_a and k_a and aaj_a and p_b and k_b and aaj_b:
                            gap_kal_a = (int(k_a) - int(p_a)) % 10
                            gap_aaj_a = (int(aaj_a) - int(k_a)) % 10
                            transition_a[gap_kal_a][gap_aaj_a] += 1
                            general_a[gap_aaj_a] += 1
                            
                            gap_kal_b = (int(k_b) - int(p_b)) % 10
                            gap_aaj_b = (int(aaj_b) - int(k_b)) % 10
                            transition_b[gap_kal_b][gap_aaj_b] += 1
                            general_b[gap_aaj_b] += 1

                    parso_in_a, parso_in_b = get_andar_bahar(history_df.iloc[target_idx-2][shift_col])
                    kal_in_a, kal_in_b = get_andar_bahar(history_df.iloc[target_idx-1][shift_col])
                    
                    # Agar 'Kal' ya 'Parso' ka data khali hai, to direct return taaki UI error na de
                    if not (parso_in_a and kal_in_a and parso_in_b and kal_in_b):
                        return []
                        
                    gap_in_a = (int(kal_in_a) - int(parso_in_a)) % 10
                    gap_in_b = (int(kal_in_b) - int(parso_in_b)) % 10
                    
                    sort_a = sorted(transition_a[gap_in_a].items(), key=lambda x: x[1], reverse=True)
                    sort_b = sorted(transition_b[gap_in_b].items(), key=lambda x: x[1], reverse=True)
                    
                    top_gaps_a = [x[0] for x in sort_a[:4]]
                    top_gaps_b = [x[0] for x in sort_b[:4]]
                    
                    # Fallback agar us specific gap ki history nahi mili
                    if not top_gaps_a: top_gaps_a = [x[0] for x in sorted(general_a.items(), key=lambda x: x[1], reverse=True)[:4]]
                    if not top_gaps_b: top_gaps_b = [x[0] for x in sorted(general_b.items(), key=lambda x: x[1], reverse=True)[:4]]
                    
                    # Hard fallback for extreme cases
                    if not top_gaps_a: top_gaps_a = [0,1,2,3]
                    if not top_gaps_b: top_gaps_b = [0,1,2,3]
                    
                    jodis = []
                    for ga in top_gaps_a:
                        for gb in top_gaps_b:
                            jodis.append(f"{(int(kal_in_a) + ga) % 10}{(int(kal_in_b) + gb) % 10}")
                            
                    return list(dict.fromkeys(jodis))

                # --- UI DISPLAY FOR ALL 6 SHIFTS ---
                parikshan_date_str = df.iloc[idx_parikshan]['DATE'].strftime('%d-%m-%Y') if idx_parikshan is not None else "Data Pending"
                
                st.markdown("---")
                st.write(f"### 🎯 Parikshan Ka Din (Aaj): {parikshan_date_str}")
                
                grid_cols = st.columns(3)
                
                for i, shift in enumerate(cols):
                    with grid_cols[i % 3]:
                        st.markdown(f"<div style='background-color:#f1f3f5; padding:15px; border-radius:10px; border:1px solid #ccc; margin-bottom:20px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
                        st.markdown(f"<h4 style='text-align:center; color:#0056b3;'>🎰 {shift}</h4>", unsafe_allow_html=True)
                        
                        kal_val = str(df.iloc[idx_kal][shift]).replace('.0', '').strip()
                        parikshan_val = str(df.iloc[idx_parikshan][shift]).replace('.0', '').strip() if idx_parikshan is not None else ""
                        if len(parikshan_val) == 1 and parikshan_val.isdigit(): parikshan_val = '0' + parikshan_val
                        
                        st.write(f"**📥 Input (Kal):** {kal_val if kal_val not in ['nan', 'XX', ''] else '-'}")
                        st.write(f"**🎯 Parikshan (Aaj):** {parikshan_val if parikshan_val not in ['nan', 'XX', ''] else '-'}")
                        
                        target_idx = idx_parikshan if idx_parikshan is not None else idx_kal + 1
                        vip_jodis = get_vip_jodis_for_shift(df, shift, target_idx)
                        
                        if vip_jodis:
                            if parikshan_val in vip_jodis:
                                st.markdown(f"<div style='color:white; background-color:#28a745; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px; font-size:18px;'>✅ PASS HUA! ({parikshan_val})</div>", unsafe_allow_html=True)
                            elif parikshan_val:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px; font-size:18px;'>❌ Miss Hua</div>", unsafe_allow_html=True)
                                
                            jodis_str = ", ".join(vip_jodis)
                    
