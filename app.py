import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import defaultdict

st.set_page_config(layout="wide")
st.title("MAYA AI: Cross-Shift Rashi Impact Engine")
st.write("Yeh engine Parso aur Kal ki shifton ko cross-match karke Rashi Impact nikalta hai. (100% Cache Cleared & Fixed)")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

def get_andar_bahar(val):
    if pd.isna(val): return None, None
    val = str(val).replace('.0', '').strip()
    if val in ['nan', 'XX', '']: return None, None
    if len(val) == 1 and val.isdigit(): val = '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
    return None, None

def get_rashi(d):
    if not d: return None
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
        
        if idx_kal < 10:
            st.warning("Engine ko Rashi logic calculate karne ke liye history chahiye.")
        else:
            with st.spinner("MAYA AI Parso aur Kal ki shifton ka Rashi Connection dhoondh rahi hai..."):
                
                def get_rashi_vip_jodis(target_idx, target_shift):
                    scores_a = {str(i): 0 for i in range(10)}
                    scores_b = {str(i): 0 for i in range(10)}
                    
                    active_rashi_links = []
                    
                    for c_parso in cols:
                        p_a, p_b = get_andar_bahar(df.iloc[target_idx-2][c_parso])
                        if not p_a: continue
                        
                        p_a_rashi = get_rashi(p_a)
                        p_b_rashi = get_rashi(p_b)
                        
                        for c_kal in cols:
                            k_a, k_b = get_andar_bahar(df.iloc[target_idx-1][c_kal])
                            if not k_a: continue
                            
                            if k_a == p_a_rashi or k_a == p_a:
                                active_rashi_links.append({'p_shift': c_parso, 'p_pos': 'A', 'k_shift': c_kal, 'k_pos': 'A', 'p_val': p_a})
                            if k_b == p_a_rashi or k_b == p_a:
                                active_rashi_links.append({'p_shift': c_parso, 'p_pos': 'A', 'k_shift': c_kal, 'k_pos': 'B', 'p_val': p_a})
                            if k_a == p_b_rashi or k_a == p_b:
                                active_rashi_links.append({'p_shift': c_parso, 'p_pos': 'B', 'k_shift': c_kal, 'k_pos': 'A', 'p_val': p_b})
                            if k_b == p_b_rashi or k_b == p_b:
                                active_rashi_links.append({'p_shift': c_parso, 'p_pos': 'B', 'k_shift': c_kal, 'k_pos': 'B', 'p_val': p_b})

                    for i in range(2, target_idx):
                        act_a, act_b = get_andar_bahar(df.iloc[i][target_shift])
                        if not act_a: continue
                        
                        match_weight = 0
                        for link in active_rashi_links:
                            # PROPER BRACKETS ARE PLACED HERE
                            hp_a, hp_b = get_andar_bahar(df.iloci-2
                            hk_a, hk_b = get_andar_bahar(df.iloci-1
                            
                            if not (hp_a and hk_a): continue
                            
                            hp_val = hp_a if link['p_pos'] == 'A' else hp_b
                            hk_val = hk_a if link['k_pos'] == 'A' else hk_b
                            
                            if hk_val == get_rashi(hp_val) or hk_val == hp_val:
                                power = 3 if (link['p_shift'] == target_shift or link['k_shift'] == target_shift) else 1
                                match_weight += power
                                
                        if match_weight > 0:
                            scores_a[act_a] += match_weight
                            scores_b[act_b] += match_weight

                    top_a = [x[0] for x in sorted(scores_a.items(), key=lambda x: x[1], reverse=True)[:6]]
                    top_b = [x[0] for x in sorted(scores_b.items(), key=lambda x: x[1], reverse=True)[:6]]
                    
                    garbage = set()
                    safe_digits = set()
                    for link in active_rashi_links:
                        safe_digits.add(link['p_val'])
                        safe_digits.add(get_rashi(link['p_val']))
                    
                    for i in range(max(0, target_idx - 5), target_idx):
                        val = str(df.iloc[i][target_shift]).replace('.0', '').strip()
                        if len(val) == 1: val = '0' + val
                        if len(val) == 2: garbage.add(val)

                    vip_jodis = []
                    for a in top_a:
                        for b in top_b:
                            jodi = f"{a}{b}"
                            if jodi not in garbage or jodi[0] in safe_digits or jodi[1] in safe_digits:
                                vip_jodis.append(jodi)
                                
                    final_jodis = []
                    seen_combos = set()
                    for j in vip_jodis:
                        palti = f"{j[1]}{j[0]}"
                        combo = "".join(sorted([j[0], j[1]]))
                        if palti in vip_jodis and palti != j:
                            if combo not in seen_combos:
                                seen_combos.add(combo)
                                if scores_a[j[0]] + scores_b[j[1]] >= scores_a[palti[0]] + scores_b[palti[1]]:
                                    final_jodis.append(j)
                                else:
                                    final_jodis.append(palti)
                        else:
                            if j not in final_jodis: final_jodis.append(j)
                            
                    return final_jodis, len(active_rashi_links)

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
                        
                        final_vip_jodis, rashi_link_count = get_rashi_vip_jodis(target_idx, shift)
                        
                        st.write(f"**📥 Input (Kal):** {kal_val if kal_val not in ['nan', 'XX', ''] else '-'}")
                        st.write(f"**🎯 Parikshan:** {parikshan_val if parikshan_val not in ['nan', 'XX', ''] else 'Pending'}")
                        
                        if rashi_link_count > 0:
                            st.markdown(f"<div style='font-size:12px; color:#856404; background-color:#fff3cd; padding:5px; border-radius:5px; margin-bottom:10px;'>🔗 {rashi_link_count} Rashi/Same Chains Active</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='font-size:12px; color:#155724; background-color:#d4edda; padding:5px; border-radius:5px; margin-bottom:10px;'>📊 Normal Trend Active</div>", unsafe_allow_html=True)
                            
                        if final_vip_jodis:
                            if parikshan_val in final_vip_jodis:
                                st.markdown(f"<div style='color:white; background-color:#28a745; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>✅ PASS! ({parikshan_val})</div>", unsafe_allow_html=True)
                            elif parikshan_val:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>❌ Miss</div>", unsafe_allow_html=True)
                                
                            st.write(f"**💎 Prediction ({len(final_vip_jodis)} Jodis):**")
                            j_chunks = [final_vip_jodis[x:x+5] for x in range(0, len(final_vip_jodis), 5)]
                            for chunk in j_chunks:
                                st.code(" | ".join(chunk))
                        else:
                            st.warning("⚠️ Data incomplete hai.")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Strict Tracker (Sirf Paas Hone Par Hara Dabba)")
                
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
                                
                            h_final, _ = get_rashi_vip_jodis(row_idx, c)
                            
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
                          
