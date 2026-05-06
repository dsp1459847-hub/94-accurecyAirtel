import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import defaultdict

st.set_page_config(layout="wide")
st.title("MAYA AI: All-in-One Master Engine (Sabhi Shifts Ek Sath)")
st.write("Sirf tareekh chunein. Saari shifton ki 16 VIP Jodi aur 11 din ki History ek sath aayegi. Jo paas hoga, sirf wo Hara (Green) dikhega.")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

def get_andar_bahar(val):
    if pd.isna(val): return None, None
    val = str(val).replace('.0', '').strip()
    if val in ['nan', 'XX', '']: return None, None
    if len(val) == 1 and val.isdigit(): val = '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
    return None, None

if uploaded_file is not None:
    # --- 1. DATA LOADING ---
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    df = df.dropna(subset=['DATE'])
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('DATE').reset_index(drop=True)
    cols = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

    # --- 2. AUTOMATIC VALID DATE SELECTION ---
    valid_df = df.dropna(subset=cols, how='all')
    max_valid_date = valid_df['DATE'].max().date() if not valid_df.empty else df['DATE'].max().date()

    st.markdown("### 📅 Tareekh Chunein (Kal Ki Date Jispar Calculation Hogi)")
    
    # SHIFT SELECTOR HATA DIYA GAYA HAI
    selected_date = st.date_input("INPUT (Kal) ki Tareekh:", 
                                  value=max_valid_date, 
                                  min_value=df['DATE'].min().date(), 
                                  max_value=df['DATE'].max().date())

    sel_date_pd = pd.to_datetime(selected_date)
    date_match = df[df['DATE'] == sel_date_pd]
    
    if date_match.empty:
        st.error("Sheet mein is date ka data nahi hai.")
    else:
        idx_kal = date_match.index[0]
        # Parikshan (Aaj) ka index
        idx_parikshan = idx_kal + 1 if (idx_kal + 1) < len(df) else None
        
        if idx_kal < 2:
            st.warning("Engine ko calculate karne ke liye kam se kam 3 din ka purana data chahiye.")
        else:
            with st.spinner("MAYA AI ek sath saari shifton ka Plus/Minus nikal rahi hai..."):
                
                # --- CORE PREDICTION FUNCTION FOR 16 JODIS ---
                def get_16_vip_jodis(history_df, shift_col, target_idx):
                    if target_idx < 2 or target_idx > len(history_df): return []
                    
                    transition_a = defaultdict(lambda: defaultdict(int))
                    transition_b = defaultdict(lambda: defaultdict(int))
                    general_a = defaultdict(int)
                    general_b = defaultdict(int)
                    
                    # Limit scan before target day to avoid cheating
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
                    
                    if not (parso_in_a and kal_in_a and parso_in_b and kal_in_b): return []
                        
                    gap_in_a = (int(kal_in_a) - int(parso_in_a)) % 10
                    gap_in_b = (int(kal_in_b) - int(parso_in_b)) % 10
                    
                    sort_a = sorted(transition_a[gap_in_a].items(), key=lambda x: x[1], reverse=True)
                    sort_b = sorted(transition_b[gap_in_b].items(), key=lambda x: x[1], reverse=True)
                    
                    top_gaps_a = [x[0] for x in sort_a[:4]]
                    top_gaps_b = [x[0] for x in sort_b[:4]]
                    
                    # Fallback if specific gap history not found
                    if not top_gaps_a: top_gaps_a = [x[0] for x in sorted(general_a.items(), key=lambda x: x[1], reverse=True)[:4]]
                    if not top_gaps_b: top_gaps_b = [x[0] for x in sorted(general_b.items(), key=lambda x: x[1], reverse=True)[:4]]
                    if not top_gaps_a: top_gaps_a = [0,1,2,3]
                    if not top_gaps_b: top_gaps_b = [0,1,2,3]
                    
                    jodis = []
                    for ga in top_gaps_a:
                        for gb in top_gaps_b:
                            jodis.append(f"{(int(kal_in_a) + ga) % 10}{(int(kal_in_b) + gb) % 10}")
                            
                    return list(dict.fromkeys(jodis))

                # --- 3. UI DISPLAY (ALL SHIFTS AT ONCE) ---
                parikshan_date_str = df.iloc[idx_parikshan]['DATE'].strftime('%d-%m-%Y') if idx_parikshan is not None else "Data Pending"
                
                st.markdown("---")
                st.markdown(f"<h2 style='text-align:center; color:#0056b3;'>🎯 Parikshan Ka Din (Aaj): {parikshan_date_str}</h2>", unsafe_allow_html=True)
                
                # Grid for 6 shifts (3 columns x 2 rows)
                grid_cols = st.columns(3)
                
                for i, shift in enumerate(cols):
                    with grid_cols[i % 3]:
                        st.markdown(f"<div style='background-color:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #ccc; margin-bottom:20px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
                        st.markdown(f"<h4 style='text-align:center; color:#e0245e;'>🎰 {shift}</h4>", unsafe_allow_html=True)
                        
                        kal_val = str(df.iloc[idx_kal][shift]).replace('.0', '').strip()
                        parikshan_val = str(df.iloc[idx_parikshan][shift]).replace('.0', '').strip() if idx_parikshan is not None else ""
                        if len(parikshan_val) == 1 and parikshan_val.isdigit(): parikshan_val = '0' + parikshan_val
                        
                        st.write(f"**📥 Input (Kal):** {kal_val if kal_val not in ['nan', 'XX', ''] else '-'}")
                        st.write(f"**🎯 Parikshan:** {parikshan_val if parikshan_val not in ['nan', 'XX', ''] else 'Pending'}")
                        
                        target_idx = idx_parikshan if idx_parikshan is not None else idx_kal + 1
                        vip_jodis = get_16_vip_jodis(df, shift, target_idx)
                        
                        if vip_jodis:
                            if parikshan_val in vip_jodis:
                                st.markdown(f"<div style='color:white; background-color:#28a745; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px; font-size:18px;'>✅ {parikshan_val} (PASS)</div>", unsafe_allow_html=True)
                            elif parikshan_val:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px; font-size:18px;'>❌ Miss</div>", unsafe_allow_html=True)
                                
                            st.write(f"**💎 VIP 16 Jodis:**")
                            # Format jodis into 4 neat lines
                            j_chunks = [vip_jodis[x:x+4] for x in range(0, len(vip_jodis), 4)]
                            for chunk in j_chunks:
                                st.code(" | ".join(chunk))
                        else:
                            st.warning("⚠️ Data incomplete hai.")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                # --- 4. 11-DAY HISTORY HTML TABLES (GREEN BOXES FOR ALL SHIFTS) ---
                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka All-Shift Tracker (Jo Paas Hua, Sirf Us Par Hara Dabba)")
                
                def generate_html_table(history_slice):
                    html_table = '<table style="width:100%; text-align:center; border-collapse: collapse; font-size: 16px;">'
                    html_table += '<tr><th style="border:1px solid #ccc; padding:10px; background-color:#343a40; color:white;">Date</th>'
                    for c in cols: html_table += f'<th style="border:1px solid #ccc; padding:10px; background-color:#343a40; color:white;">{c}</th>'
                    html_table += '</tr>'
                    
                    for row_idx, row in history_slice.iterrows():
                        html_table += '<tr>'
                        html_table += f'<td style="border:1px solid #ccc; padding:10px; font-weight:bold; background-color:#f8f9fa;">{row["DATE"].strftime("%d-%m-%Y")}</td>'
                        
                        for c in cols:
                            actual_val = str(row[c]).replace('.0', '').strip()
                            if len(actual_val) == 1 and actual_val.isdigit(): actual_val = '0' + actual_val
                            
                            if actual_val in ['nan', 'XX', '']:
                                html_table += f'<td style="border:1px solid #ccc; padding:10px; color:#aaa;">-</td>'
                                continue
                                
                            # Calculate prediction for this specific day and this specific shift
                            hist_jodis = get_16_vip_jodis(df, c, row_idx)
                            
                            if actual_val in hist_jodis:
                                # GREEN BOX FOR PASS (Yahan Parikshan me paas hua tha)
                                html_table += f'<td style="border:2px solid #1e7e34; padding:10px; background-color:#d4edda; color:#155724; font-weight:bold; font-size: 18px;">{actual_val} ✅</td>'
                            else:
                                # NORMAL FOR FAIL (Koi rang nahi)
                                html_table += f'<td style="border:1px solid #ccc; padding:10px; color:#333;">{actual_val}</td>'
                                
                        html_table += '</tr>'
                    html_table += '</table>'
                    return html_table

                parikshan_date_pd = sel_date_pd + pd.Timedelta(days=1)
                
                # Filter 11 Days for each category
                df_seq = df[df['DATE'] <= parikshan_date_pd].tail(11).copy()
                df_war = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.weekday == parikshan_date_pd.weekday())].tail(11).copy()
                df_tarikh = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.day == parikshan_date_pd.day)].tail(11).copy()

                tab1, tab2, tab3 = st.tabs(["1️⃣ Lagaatar (Seq) 11 Din", "2️⃣ War (Day) 11 Din", "3️⃣ Tareekh (Date) 11 Din"])
                
                with tab1:
                    st.markdown(generate_html_table(df_seq), unsafe_allow_html=True)
                with tab2:
                    st.markdown(generate_html_table(df_war), unsafe_allow_html=True)
                with tab3:
                    st.markdown(generate_html_table(df_tarikh), unsafe_allow_html=True)

else:
    st.info("Kripya engine chalane ke liye 0DSP0 sheet upload karein.")
                    
