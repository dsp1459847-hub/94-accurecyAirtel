import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import defaultdict

st.set_page_config(layout="wide")
st.title("MAYA AI: Macro-Micro Probability Engine (Super VIP/VIP/Normal)")
st.write("Yeh engine Pichle 2 Din (Macro) aur Pichli 2 Shiften (Micro) cross karke sabse high probability nikalta hai aur 36 Jodis ko 3 hisson me baant-ta hai.")

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

    valid_df = df.dropna(subset=cols, how='all')
    max_valid_date = valid_df['DATE'].max().date() if not valid_df.empty else df['DATE'].max().date()

    st.markdown("### 📅 Tareekh Chunein")
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
        idx_parikshan = idx_kal + 1 if (idx_kal + 1) < len(df) else None
        
        if idx_kal < 5:
            st.warning("Engine ko calculate karne ke liye kam se kam 5 din ka purana data chahiye.")
        else:
            with st.spinner("MAYA AI Pichli Shiften aur Pichle Din cross-verify kar rahi hai..."):
                
                # Pre-calculate Global Shift Sequence for Micro Trend
                flat_shifts = []
                for i in range(len(df)):
                    for c_idx, c_name in enumerate(cols):
                        val = df.iloc[i][c_name]
                        a, b = get_andar_bahar(val)
                        flat_shifts.append({'row': i, 'col': c_idx, 'col_name': c_name, 'a': a, 'b': b})
                        
                def get_flat_idx(r, c): return r * 6 + c

                def calculate_vip_jodis(target_row_idx, target_col_name):
                    target_col_idx = cols.index(target_col_name)
                    target_flat_idx = get_flat_idx(target_row_idx, target_col_idx)
                    
                    if target_flat_idx < 12: return [], [], [] # Not enough history
                    
                    # 1. GET ACTUAL VALUES FOR MACRO & MICRO
                    # Macro: Pichla Din aur Usse Pichla Din (Same Shift)
                    macro_1_a, macro_1_b = get_andar_bahar(df.iloc[target_row_idx-1][target_col_name]) if target_row_idx-1 >=0 else (None, None)
                    macro_2_a, macro_2_b = get_andar_bahar(df.iloc[target_row_idx-2][target_col_name]) if target_row_idx-2 >=0 else (None, None)
                    
                    # Micro: Pichli Shift aur Usse Pichli Shift (Chronological)
                    prev_1 = flat_shifts[target_flat_idx - 1]
                    prev_2 = flat_shifts[target_flat_idx - 2]
                    micro_1_a, micro_1_b = prev_1['a'], prev_1['b']
                    micro_2_a, micro_2_b = prev_2['a'], prev_2['b']
                    
                    if not (macro_1_a and micro_1_a): return [], [], []

                    # 2. SCAN HISTORY TO BUILD PROBABILITY SCORES
                    scores_a = {str(i): 0 for i in range(10)}
                    scores_b = {str(i): 0 for i in range(10)}
                    
                    for i in range(2, target_row_idx):
                        hist_flat_idx = get_flat_idx(i, target_col_idx)
                        h_target_a, h_target_b = flat_shifts[hist_flat_idx]['a'], flat_shifts[hist_flat_idx]['b']
                        
                        if not (h_target_a and h_target_b): continue
                        
                        # Check History Macro
                        h_m1_a, _ = get_andar_bahar(df.iloc[i-1][target_col_name])
                        h_m2_a, _ = get_andar_bahar(df.iloc[i-2][target_col_name])
                        # Check History Micro
                        h_mi1_a = flat_shifts[hist_flat_idx - 1]['a']
                        h_mi2_a = flat_shifts[hist_flat_idx - 2]['a']
                        
                        # Add Weighted Points for Andar
                        if h_m1_a == macro_1_a: scores_a[h_target_a] += 3  # High priority (Day-1)
                        if h_m2_a == macro_2_a: scores_a[h_target_a] += 1  # Low priority (Day-2)
                        if h_mi1_a == micro_1_a: scores_a[h_target_a] += 2 # Med priority (Shift-1)
                        if h_mi2_a == micro_2_a: scores_a[h_target_a] += 1 # Low priority (Shift-2)

                        # Check History Macro (Bahar)
                        _, h_m1_b = get_andar_bahar(df.iloc[i-1][target_col_name])
                        _, h_m2_b = get_andar_bahar(df.iloc[i-2][target_col_name])
                        # Check History Micro (Bahar)
                        h_mi1_b = flat_shifts[hist_flat_idx - 1]['b']
                        h_mi2_b = flat_shifts[hist_flat_idx - 2]['b']
                        
                        # Add Weighted Points for Bahar
                        if h_m1_b == macro_1_b: scores_b[h_target_b] += 3
                        if h_m2_b == macro_2_b: scores_b[h_target_b] += 1
                        if h_mi1_b == micro_1_b: scores_b[h_target_b] += 2
                        if h_mi2_b == micro_2_b: scores_b[h_target_b] += 1

                    # 3. SELECT TOP 6 ANDAR & BAHAR
                    top_a = [x[0] for x in sorted(scores_a.items(), key=lambda x: x[1], reverse=True)[:6]]
                    top_b = [x[0] for x in sorted(scores_b.items(), key=lambda x: x[1], reverse=True)[:6]]
                    
                    # 4. TIERING (SUPER VIP, VIP, NORMAL)
                    super_vip = [] # Top 2 x Top 2 = 4 Jodis
                    vip = []       # Next crosses = 12 Jodis
                    normal = []    # Remaining = 20 Jodis
                    
                    for a_idx, a in enumerate(top_a):
                        for b_idx, b in enumerate(top_b):
                            jodi = f"{a}{b}"
                            if a_idx < 2 and b_idx < 2:
                                super_vip.append(jodi)
                            elif a_idx < 4 and b_idx < 4:
                                vip.append(jodi)
                            else:
                                normal.append(jodi)
                                
                    return super_vip, vip, normal

                # --- 3. UI DISPLAY (ALL SHIFTS AT ONCE) ---
                parikshan_date_str = df.iloc[idx_parikshan]['DATE'].strftime('%d-%m-%Y') if idx_parikshan is not None else "Data Pending"
                
                st.markdown("---")
                st.markdown(f"<h2 style='text-align:center; color:#0056b3;'>🎯 Parikshan Ka Din (Aaj): {parikshan_date_str}</h2>", unsafe_allow_html=True)
                
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
                        svip, vip, normal = calculate_vip_jodis(target_idx, shift)
                        
                        if svip:
                            all_jodis = svip + vip + normal
                            if parikshan_val in svip:
                                st.markdown(f"<div style='color:white; background-color:#1e7e34; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>🔥 SUPER VIP PASS! ({parikshan_val})</div>", unsafe_allow_html=True)
                            elif parikshan_val in vip:
                                st.markdown(f"<div style='color:black; background-color:#ffc107; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>⭐ VIP PASS! ({parikshan_val})</div>", unsafe_allow_html=True)
                            elif parikshan_val in normal:
                                st.markdown(f"<div style='color:white; background-color:#17a2b8; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>✔️ NORMAL PASS! ({parikshan_val})</div>", unsafe_allow_html=True)
                            elif parikshan_val:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>❌ Miss</div>", unsafe_allow_html=True)
                                
                            st.write(f"🔥 **Super VIP (4):** {', '.join(svip)}")
                            st.write(f"⭐ **VIP (12):** {', '.join(vip)}")
                            
                            with st.expander("Show Normal Jodis (20)"):
                                st.write(", ".join(normal))
                        else:
                            st.warning("⚠️ Data incomplete hai.")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                # --- 4. 11-DAY HISTORY HTML TABLES ---
                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Tracker (Jo Paas Hua, Sirf Us Par Rang)")
                st.write("🟢 **Super VIP Pass** | 🟡 **VIP Pass** | 🔵 **Normal Pass**")
                
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
                                
                            h_svip, h_vip, h_norm = calculate_vip_jodis(row_idx, c)
                            
                            if actual_val in h_svip:
                                html_table += f'<td style="border:2px solid #1e7e34; padding:10px; background-color:#d4edda; color:#155724; font-weight:bold; font-size: 18px;">{actual_val} 🟢</td>'
                            elif actual_val in h_vip:
                                html_table += f'<td style="border:2px solid #d39e00; padding:10px; background-color:#fff3cd; color:#856404; font-weight:bold; font-size: 18px;">{actual_val} 🟡</td>'
                            elif actual_val in h_norm:
                                html_table += f'<td style="border:2px solid #117a8b; padding:10px; background-color:#d1ecf1; color:#0c5460; font-weight:bold; font-size: 18px;">{actual_val} 🔵</td>'
                            else:
                                html_table += f'<td style="border:1px solid #ccc; padding:10px; color:#333;">{actual_val}</td>'
                                
                        html_table += '</tr>'
                    html_table += '</table>'
                    return html_table

                parikshan_date_pd = sel_date_pd + pd.Timedelta(days=1)
                
                df_seq = df[df['DATE'] <= parikshan_date_pd].tail(11).copy()
                df_war = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.weekday == parikshan_date_pd.weekday())].tail(11).copy()
                df_tarikh = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.day == parikshan_date_pd.day)].tail(11).copy()

                tab1, tab2, tab3 = st.tabs(["1️⃣ Lagaatar (Seq) 11 Din", "2️⃣ War (Day) 11 Din", "3️⃣ Tareekh (Date) 11 Din"])
                
                with tab1: st.markdown(generate_html_table(df_seq), unsafe_allow_html=True)
                with tab2: st.markdown(generate_html_table(df_war), unsafe_allow_html=True)
                with tab3: st.markdown(generate_html_table(df_tarikh), unsafe_allow_html=True)

else:
    st.info("Kripya engine chalane ke liye 0DSP0 sheet upload karein.")
    
