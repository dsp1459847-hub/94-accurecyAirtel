import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import defaultdict, Counter

st.set_page_config(layout="wide")
st.title("MAYA AI: Double Palti Killer & +1/-1 Proximity Engine")
st.write("Yeh engine bekar Palti aur Rashi ankon ko JAD SE kaat deta hai, aur history ke error (+1/-1) ko pehchan kar naye solid ank add karta hai.")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

def get_andar_bahar(val):
    if pd.isna(val): return None, None
    val = str(val).replace('.0', '').strip()
    if val in ['nan', 'XX', '']: return None, None
    if len(val) == 1 and val.isdigit(): val = '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
    return None, None

def is_rashi(jodi):
    return abs(int(jodi[0]) - int(jodi[1])) == 5

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
        parikshan_date = sel_date_pd + pd.Timedelta(days=1)
        
        if idx_kal < 30:
            st.warning("Engine ko +1/-1 Proximity calculate karne ke liye kam se kam 30 din ka data chahiye.")
        else:
            with st.spinner("MAYA AI Palti/Rashi kaat rahi hai aur +1/-1 history scan kar rahi hai..."):
                
                # --- CORE 1: BASE 36 JODIS ---
                def get_base_36_jodis(target_idx, shift_col):
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

                # --- CORE 2: ELIMINATOR & PROXIMITY (+1/-1) ADDER ---
                def apply_grandmaster_logic(jodi_list, target_idx, shift_col):
                    # History Frequencies
                    hist_counts = defaultdict(int)
                    for i in range(target_idx):
                        val = str(df.iloc[i][shift_col]).replace('.0', '').strip()
                        if len(val) == 1 and val.isdigit(): val = '0' + val
                        if len(val) == 2 and val.isdigit(): hist_counts[val] += 1
                            
                    avg_count = sum(hist_counts.values()) / max(1, len(hist_counts))
                    
                    to_remove = set()
                    
                    # 1. DOUBLE PALTI KILLER
                    # Agar 14 aur 41 dono list me hain, aur dono ka combine history score weak hai, to dono uda do
                    for j in jodi_list:
                        palti = f"{j[1]}{j[0]}"
                        if palti in jodi_list and palti != j:
                            combo_score = hist_counts[j] + hist_counts[palti]
                            # Threshold: Agar combined score average ke 1.5 guna se bhi kam hai, to dono bekar hain
                            if combo_score < (avg_count * 1.5):
                                to_remove.add(j)
                                to_remove.add(palti)

                    # 2. RASHI KILLER
                    for j in jodi_list:
                        if is_rashi(j):
                            if hist_counts[j] < (avg_count * 0.9): # Weak Rashi pair
                                to_remove.add(j)

                    # Filtered list
                    filtered_jodis = [j for j in jodi_list if j not in to_remove]

                    # 3. PROXIMITY (+1 / -1) ERROR TRACKER
                    # Check past 30 days to see engine's most common error gap for this shift
                    err_a_history = []
                    err_b_history = []
                    
                    for i in range(max(2, target_idx - 30), target_idx):
                        past_36 = get_base_36_jodis(i, shift_col)
                        act_a, act_b = get_andar_bahar(df.iloc[i][shift_col])
                        
                        if past_36 and act_a and act_b:
                            # Compare actual against the engine's #1 predicted combination (top score)
                            # Assuming past_36[0] is the top prediction logically
                            top_pred = past_36[0] 
                            pred_a, pred_b = top_pred[0], top_pred[1]
                            
                            err_a = (int(act_a) - int(pred_a)) % 10
                            err_b = (int(act_b) - int(pred_b)) % 10
                            err_a_history.append(err_a)
                            err_b_history.append(err_b)
                            
                    most_common_err_a = Counter(err_a_history).most_common(1)[0][0] if err_a_history else 0
                    most_common_err_b = Counter(err_b_history).most_common(1)[0][0] if err_b_history else 0
                    
                    # 4. ADD PROXIMITY JODIS
                    # Agar error +1, -1, ya +2 hai (yani kareeb se miss ho raha hai)
                    proximity_added = []
                    if most_common_err_a != 0 or most_common_err_b != 0:
                        # Top 2 best base jodis uthao aur usme error gap apply karke naye ank banao
                        for top_j in jodi_list[:2]:
                            new_a = str((int(top_j[0]) + most_common_err_a) % 10)
                            new_b = str((int(top_j[1]) + most_common_err_b) % 10)
                            new_jodi = f"{new_a}{new_b}"
                            
                            if new_jodi not in filtered_jodis:
                                proximity_added.append(new_jodi)
                                
                    final_list = list(set(filtered_jodis + proximity_added))
                    return final_list, len(to_remove), proximity_added

                # --- UI DISPLAY ---
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
                        base_36 = get_base_36_jodis(target_idx, shift)
                        final_jodis, removed_count, added_prox = apply_grandmaster_logic(base_36, target_idx, shift)
                        
                        st.write(f"**📥 Input (Kal):** {kal_val if kal_val not in ['nan', 'XX', ''] else '-'}")
                        st.write(f"**🎯 Parikshan:** {parikshan_val if parikshan_val not in ['nan', 'XX', ''] else 'Pending'}")
                        
                        st.markdown(f"<div style='font-size:14px; color:#856404; background-color:#fff3cd; padding:5px; border-radius:5px; margin-bottom:10px;'>🗑️ Palti/Rashi Hatai: <b>{removed_count}</b><br>➕ +1/-1 se Jodi Jogi: <b>{len(added_prox)}</b></div>", unsafe_allow_html=True)
                        
                        if final_jodis:
                            if parikshan_val in final_jodis:
                                st.markdown(f"<div style='color:white; background-color:#28a745; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>✅ PASS! ({parikshan_val})</div>", unsafe_allow_html=True)
                            elif parikshan_val:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>❌ Miss</div>", unsafe_allow_html=True)
                                
                            st.write(f"**💎 Final VIP Anks ({len(final_jodis)} Jodis):**")
                            j_chunks = [final_jodis[x:x+5] for x in range(0, len(final_jodis), 5)]
                            for chunk in j_chunks:
                                st.code(" | ".join(chunk))
                        else:
                            st.warning("⚠️ Data incomplete hai.")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                # --- 11-DAY HISTORY HTML TABLES ---
                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Double Filter Tracker (Jo Paas Hua, Sirf Wahan Hara Dabba)")
                
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
                                
                            h_base_36 = get_base_36_jodis(row_idx, c)
                            h_final, _, _ = apply_grandmaster_logic(h_base_36, row_idx, c)
                            
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
                            
