import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import defaultdict, Counter

st.set_page_config(layout="wide")
st.title("MAYA AI: Rashi-Chain & 7-Day Eliminator Engine")
st.write("Yeh engine 'Parso -> Kal' ki Rashi Chain check karta hai, aur pichle 5-7 din ke 'Kachra' (Altu-Faltu) ankon ko list se hamesha ke liye kaat deta hai.")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

def get_andar_bahar(val):
    if pd.isna(val): return None, None
    val = str(val).replace('.0', '').strip()
    if val in ['nan', 'XX', '']: return None, None
    if len(val) == 1 and val.isdigit(): val = '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
    return None, None

def get_rashi(d):
    return str((int(d) + 5) % 10)

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
        
        if idx_kal < 15:
            st.warning("Engine ko calculate karne ke liye thodi aur history chahiye.")
        else:
            with st.spinner("MAYA AI Rashi-Chain aur 7-Day Elimination kar rahi hai..."):
                
                # --- CORE 1: BASE MACRO/MICRO (Base Trend) ---
                def get_base_36(target_idx, shift_col):
                    scores_a = {str(i): 0 for i in range(10)}
                    scores_b = {str(i): 0 for i in range(10)}
                    
                    m1_a, m1_b = get_andar_bahar(df.iloc[target_idx-1][shift_col])
                    m2_a, m2_b = get_andar_bahar(df.iloc[target_idx-2][shift_col])
                    
                    if not m1_a: return []

                    for i in range(2, target_idx):
                        h_t_a, h_t_b = get_andar_bahar(df.iloc[i][shift_col])
                        h_m1_a, h_m1_b = get_andar_bahar(df.iloc[i-1][shift_col])
                        h_m2_a, h_m2_b = get_andar_bahar(df.iloc[i-2][shift_col])
                        
                        if h_t_a and h_t_b:
                            if h_m1_a == m1_a: scores_a[h_t_a] += 2
                            if h_m2_a == m2_a: scores_a[h_t_a] += 1
                            if h_m1_b == m1_b: scores_b[h_t_b] += 2
                            if h_m2_b == m2_b: scores_b[h_t_b] += 1

                    top_a = [x[0] for x in sorted(scores_a.items(), key=lambda x: x[1], reverse=True)[:6]]
                    top_b = [x[0] for x in sorted(scores_b.items(), key=lambda x: x[1], reverse=True)[:6]]
                    return [f"{a}{b}" for a in top_a for b in top_b]

                # --- CORE 2: RASHI CHAIN PREDICTOR (Parso -> Kal -> Aaj) ---
                def get_rashi_chain_jodis(target_idx, shift_col):
                    p_a, p_b = get_andar_bahar(df.iloc[target_idx-2][shift_col])
                    k_a, k_b = get_andar_bahar(df.iloc[target_idx-1][shift_col])
                    
                    if not (p_a and p_b and k_a and k_b): return [], False
                    
                    rp_a, rp_b = get_rashi(p_a), get_rashi(p_b)
                    
                    # Kya Parso ki Rashi Kal mein aayi hai?
                    rashi_chain_triggered = (rp_a in [k_a, k_b]) or (rp_b in [k_a, k_b])
                    
                    chain_jodis = []
                    if rashi_chain_triggered:
                        # Scan History: Jab bhi yeh specific chain banti hai, tab history mein kya khulta hai?
                        hist_next_jodis = []
                        for i in range(2, target_idx):
                            hp_a, hp_b = get_andar_bahar(df.iloc[i-2][shift_col])
                            hk_a, hk_b = get_andar_bahar(df.iloc[i-1][shift_col])
                            
                            if hp_a and hk_a:
                                hrp_a, hrp_b = get_rashi(hp_a), get_rashi(hp_b)
                                if (hrp_a in [hk_a, hk_b]) or (hrp_b in [hk_a, hk_b]):
                                    # Chain matched in history! See what came next
                                    act_val = str(df.iloc[i][shift_col]).replace('.0', '').strip()
                                    if len(act_val) == 1: act_val = '0' + act_val
                                    if len(act_val) == 2: hist_next_jodis.append(act_val)
                                    
                        if hist_next_jodis:
                            # Take top 5 most historically accurate outcomes for this specific Rashi Chain
                            top_outcomes = [item[0] for item in Counter(hist_next_jodis).most_common(5)]
                            chain_jodis.extend(top_outcomes)
                            
                    return chain_jodis, rashi_chain_triggered

                # --- CORE 3: THE ELIMINATOR (Kachra Hatao) ---
                def apply_grand_filter(base_jodis, rashi_jodis, target_idx, shift_col):
                    # 1. 7-DAY ELIMINATION RULE (Altu Faltu ank hatao)
                    days_to_check = 7 if shift_col == 'DS' else 5
                    garbage_jodis = set()
                    
                    for i in range(max(0, target_idx - days_to_check), target_idx):
                        val = str(df.iloc[i][shift_col]).replace('.0', '').strip()
                        if len(val) == 1: val = '0' + val
                        if len(val) == 2: garbage_jodis.add(val)
                    
                    # Base Jodis me se Garbage hatao
                    filtered_base = [j for j in base_jodis if j not in garbage_jodis]
                    
                    # 2. SMART PALTI ELIMINATION
                    hist_counts = defaultdict(int)
                    for i in range(target_idx):
                        val = str(df.iloc[i][shift_col]).replace('.0', '').strip()
                        if len(val) == 1: val = '0' + val
                        if len(val) == 2: hist_counts[val] += 1
                    
                    final_list = []
                    seen_combos = set()
                    
                    for j in filtered_base:
                        palti = f"{j[1]}{j[0]}"
                        combo = "".join(sorted([j[0], j[1]]))
                        
                        if palti in filtered_base and palti != j:
                            if combo not in seen_combos:
                                seen_combos.add(combo)
                                # Jo Palti history me zyada aati hai sirf use rakho
                                if hist_counts[j] > hist_counts[palti]: final_list.append(j)
                                elif hist_counts[palti] > hist_counts[j]: final_list.append(palti)
                                else: final_list.extend([j, palti])
                        else:
                            if j not in final_list: final_list.append(j)

                    # 3. ADD RASHI CHAIN JODIS (Yeh sabse pakke hain, isliye inko eliminate nahi karna)
                    for rj in rashi_jodis:
                        if rj not in final_list:
                            final_list.append(rj)
                            
                    return final_list, list(garbage_jodis)

                # --- UI DISPLAY (ALL SHIFTS AT ONCE) ---
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
                        
                        target_idx = idx_parikshan if idx_parikshan is not None else idx_kal + 1
                        
                        # Execute Logic
                        base_36 = get_base_36(target_idx, shift)
                        rashi_chain_jodis, is_rashi_triggered = get_rashi_chain_jodis(target_idx, shift)
                        final_vip, garbage_removed = apply_grand_filter(base_36, rashi_chain_jodis, target_idx, shift)
                        
                        st.write(f"**📥 Input (Kal):** {kal_val if kal_val not in ['nan', 'XX', ''] else '-'}")
                        st.write(f"**🎯 Parikshan:** {parikshan_val if parikshan_val not in ['nan', 'XX', ''] else 'Pending'}")
                        
                        # Info Tags
                        tags_html = ""
                        if is_rashi_triggered:
                            tags_html += f"<span style='background-color:#ffc107; color:black; padding:3px 6px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:5px;'>🔗 Rashi Chain Active</span>"
                        tags_html += f"<span style='background-color:#dc3545; color:white; padding:3px 6px; border-radius:4px; font-size:12px; font-weight:bold;'>🗑️ {len(garbage_removed)} Kachra Hata</span>"
                        st.markdown(f"<div style='margin-bottom:10px;'>{tags_html}</div>", unsafe_allow_html=True)
                        
                        if final_vip:
                            if parikshan_val in final_vip:
                                st.markdown(f"<div style='color:white; background-color:#28a745; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>✅ PASS! ({parikshan_val})</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>❌ Miss</div>", unsafe_allow_html=True)
                                
                            st.write(f"**💎 High-Accuracy VIPs ({len(final_vip)} Jodis):**")
                            j_chunks = [final_vip[x:x+5] for x in range(0, len(final_vip), 5)]
                            for chunk in j_chunks:
                                st.code(" | ".join(chunk))
                        else:
                            st.warning("⚠️ Data incomplete hai.")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                # --- 11-DAY HISTORY HTML TABLES ---
                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Strict Filter Tracker (Jo Paas Hua, Sirf Wahan Hara Dabba)")
                
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
                                
                            h_base = get_base_36(row_idx, c)
                            h_rashi, _ = get_rashi_chain_jodis(row_idx, c)
                            h_final, _ = apply_grand_filter(h_base, h_rashi, row_idx, c)
                            
                            if actual_val in h_final:
                                html_table += f'<td style="border:2px solid #1e7e34; padding:10px; background-color:#d4edda; color:#155724; font-weight:bold; font-size: 18px;">{actual_val} ✅</td>'
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
                    
