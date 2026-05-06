import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import Counter

st.set_page_config(layout="wide")
st.title("MAYA AI 4.0: Time-Series & Error Correction Engine")
st.write("Is engine mein Tareekh, War, Mahina ka logic aur 'Prediction Aage-Piche (Error Correction)' ka advance logic shamil hai.")

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
        idx_parikshan = idx_kal + 1 if (idx_kal + 1) < len(df) else None
        
        if idx_kal < 10:
            st.error("Engine ko check karne ke liye aur purani history chahiye.")
        else:
            with st.spinner("MAYA AI Mahina, War, Tareekh aur Plus/Minus Gap scan kar rahi hai..."):
                
                # ==========================================
                # LAYER 1: TIME-SERIES SCORING (Mahina, War, Tarikh)
                # ==========================================
                tarikh = df.iloc[idx_parikshan if idx_parikshan else idx_kal]['DATE'].day
                war = df.iloc[idx_parikshan if idx_parikshan else idx_kal]['DATE'].weekday()
                mahina = df.iloc[idx_parikshan if idx_parikshan else idx_kal]['DATE'].month
                
                time_scores_a = {str(i): 0 for i in range(10)}
                time_scores_b = {str(i): 0 for i in range(10)}
                
                limit_idx = idx_parikshan if idx_parikshan else idx_kal
                
                for i in range(limit_idx):
                    hist_date = df.iloc[i]['DATE']
                    a, b = get_andar_bahar(df.iloc[i][target_shift])
                    if a and b:
                        # Tareekh ka Rule
                        if hist_date.day == tarikh:
                            time_scores_a[a] += 2
                            time_scores_b[b] += 2
                        # War ka Rule
                        if hist_date.weekday() == war:
                            time_scores_a[a] += 2
                            time_scores_b[b] += 2
                        # Mahina ka Rule
                        if hist_date.month == mahina:
                            time_scores_a[a] += 1
                            time_scores_b[b] += 1

                # ==========================================
                # LAYER 2: BASE PREDICTION LOGIC (Kal aur Parso ka Cross)
                # ==========================================
                def get_base_prediction(idx):
                    # Ek basic cross aur vertical calculation
                    kal_r = df.iloc[idx-1] if idx-1 >= 0 else None
                    parso_r = df.iloc[idx-2] if idx-2 >= 0 else None
                    
                    scores_a = {str(i): 0 for i in range(10)}
                    scores_b = {str(i): 0 for i in range(10)}
                    
                    # Pichle 30 din ka trend check karke
                    for i in range(max(2, idx-30), idx):
                        p_a, p_b = get_andar_bahar(df.iloc[i-2][target_shift])
                        k_a, k_b = get_andar_bahar(df.iloc[i-1][target_shift])
                        t_a, t_b = get_andar_bahar(df.iloc[i][target_shift])
                        
                        if k_a and t_a and p_a:
                            req_off_a = (int(t_a) - int(k_a)) % 10
                            req_off_b = (int(t_b) - int(k_b)) % 10
                            
                            curr_k_a, curr_k_b = get_andar_bahar(kal_r[target_shift]) if kal_r is not None else (None, None)
                            
                            if curr_k_a:
                                pred_a = str((int(curr_k_a) + req_off_a) % 10)
                                pred_b = str((int(curr_k_b) + req_off_b) % 10)
                                scores_a[pred_a] += 1
                                scores_b[pred_b] += 1
                                
                    # Combining Time-Series Scores with Base Trend Scores
                    for k in range(10):
                        scores_a[str(k)] += time_scores_a[str(k)]
                        scores_b[str(k)] += time_scores_b[str(k)]
                        
                    top_a = [x[0] for x in sorted(scores_a.items(), key=lambda x: x[1], reverse=True)[:3]]
                    top_b = [x[0] for x in sorted(scores_b.items(), key=lambda x: x[1], reverse=True)[:3]]
                    return top_a, top_b

                # ==========================================
                # LAYER 3: ERROR CORRECTION (Aage-Piche Offset Tracking)
                # ==========================================
                # Check how much Base Prediction missed the Actual History in the last 60 days
                error_gaps_a = []
                error_gaps_b = []
                
                for past_idx in range(limit_idx - 60, limit_idx):
                    if past_idx < 3: continue
                    
                    pred_a_list, pred_b_list = get_base_prediction(past_idx)
                    act_a, act_b = get_andar_bahar(df.iloc[past_idx][target_shift])
                    
                    if act_a and pred_a_list and act_b and pred_b_list:
                        # Assume the top prediction was the engine's choice
                        top_pred_a = pred_a_list[0]
                        top_pred_b = pred_b_list[0]
                        
                        # Calculate Kitne ank aage/piche hua (Error Gap)
                        gap_a = (int(act_a) - int(top_pred_a)) % 10
                        gap_b = (int(act_b) - int(top_pred_b)) % 10
                        
                        error_gaps_a.append(gap_a)
                        error_gaps_b.append(gap_b)

                # Find the most frequent "Fail Hone ka Gap"
                common_gap_a = Counter(error_gaps_a).most_common(1)[0][0] if error_gaps_a else 0
                common_gap_b = Counter(error_gaps_b).most_common(1)[0][0] if error_gaps_b else 0

                # ==========================================
                # FINAL PREDICTION WITH ERROR FIX
                # ==========================================
                base_today_a, base_today_b = get_base_prediction(idx_parikshan if idx_parikshan else idx_kal + 1)
                
                # Adding the Gap to fix the history miss
                final_vip_jodis = []
                for ba in base_today_a:
                    fixed_a = str((int(ba) + common_gap_a) % 10)
                    for bb in base_today_b:
                        fixed_b = str((int(bb) + common_gap_b) % 10)
                        final_vip_jodis.append(f"{fixed_a}{fixed_b}")
                
                # Parikshan Data Check
                parikshan_actual = ""
                parikshan_date_str = "Data Pending"
                if idx_parikshan is not None:
                    parikshan_actual = str(df.iloc[idx_parikshan][target_shift]).replace('.0', '').strip()
                    if len(parikshan_actual) == 1 and parikshan_actual.isdigit(): parikshan_actual = '0' + parikshan_actual
                    parikshan_date_str = df.iloc[idx_parikshan]['DATE'].strftime('%d-%m-%Y')

                # --- UI DISPLAY ---
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.info("📅 **Time-Series Rule Applied:**")
                    st.write(f"- Tareekh: {tarikh}\n- War: {df.iloc[idx_parikshan if idx_parikshan else idx_kal]['DATE'].strftime('%A')}\n- Mahina: {mahina}")
                with c2:
                    st.warning("⚙️ **Aage-Piche (Error Fix) Tracker:**")
                    st.write(f"- Andar History Miss Gap: **{'+' + str(common_gap_a) if common_gap_a else 'No Change'}**")
                    st.write(f"- Bahar History Miss Gap: **{'+' + str(common_gap_b) if common_gap_b else 'No Change'}**")
                with c3:
                    st.error(f"🎯 **Aaj/Parikshan ({parikshan_date_str}):**")
                    st.write(f"### {parikshan_actual if parikshan_actual else 'Result Aana Baki Hai'}")
                st.markdown("---")

                if final_vip_jodis:
                    st.write("### 💎 Target VIP Anks (Error Corrected Jodis)")
                    if parikshan_actual in final_vip_jodis:
                        st.success(f"🎉 **SHANDAAR PASS!** Error correction ne result ko exactly match kara diya!")
                    elif parikshan_actual:
                        st.error(f"Target miss hua. Aaya: {parikshan_actual}")
                    
                    jodi_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>"
                    for j in list(set(final_vip_jodis)): # Remove duplicates if any
                        if j == parikshan_actual:
                            jodi_html += f"<div style='background-color: #28a745; color: white; padding: 10px 20px; font-size: 20px; font-weight: bold; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>{j} ✅ PASS</div>"
                        else:
                            jodi_html += f"<div style='background-color: #f1f3f5; color: #333; padding: 10px 20px; font-size: 18px; font-weight: bold; border-radius: 8px; border: 1px solid #ccc;'>{j}</div>"
                    jodi_html += "</div>"
                    st.markdown(jodi_html, unsafe_allow_html=True)

                # --- 11-DAY HISTORY HTML TABLE (ONLY GREEN BOXES FOR PASS) ---
                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Cross-Check (Hare Dabbe)")
                
                history_table_data = []
                start_idx = max(2, (idx_parikshan if idx_parikshan is not None else idx_kal) - 10)
                end_idx = idx_parikshan if idx_parikshan is not None else idx_kal
                
                for i in range(start_idx, end_idx + 1):
                    row_date = df.iloc[i]['DATE'].strftime('%d-%m-%Y')
                    row_data = {"DATE": row_date}
                    
                    for c in cols:
                        actual_val = str(df.iloc[i][c]).replace('.0', '').strip()
                        if len(actual_val) == 1 and actual_val.isdigit(): actual_val = '0' + actual_val
                        
                        is_pass = False
                        if c == target_shift:
                            # Verify past 11 days with the same error offset
                            past_a, past_b = get_base_prediction(i)
                            past_final_jodis = []
                            for pa in past_a:
                                for pb in past_b:
                                    past_final_jodis.append(f"{(int(pa)+common_gap_a)%10}{(int(pb)+common_gap_b)%10}")
                                    
                            if actual_val in past_final_jodis:
                                is_pass = True
                                
                        row_data[c] = {"val": actual_val, "is_pass": is_pass}
                    history_table_data.append(row_data)

                html_table = '<table style="width:100%; text-align:center; border-collapse: collapse; font-size: 16px;">'
                html_table += '<tr><th style="border:1px solid #ddd; padding:10px; background-color:#f8f9fa;">Date</th>'
                for c in cols: html_table += f'<th style="border:1px solid #ddd; padding:10px; background-color:#f8f9fa;">{c}</th>'
                html_table += '</tr>'
                
                for row in history_table_data:
                    html_table += '<tr>'
                    html_table += f'<td style="border:1px solid #ddd; padding:10px;">{row["DATE"]}</td>'
                    
                    for c in cols:
                        cell = row[c]
                        val = cell["val"] if cell["val"] not in ['nan', 'XX', ''] else '-'
                        
                        if cell["is_pass"]:
                            html_table += f'<td style="border:1px solid #ddd; padding:10px; background-color:#d4edda; color:#155724; font-weight:bold; font-size: 18px;">{val} ✅</td>'
                        else:
                            html_table += f'<td style="border:1px solid #ddd; padding:10px; color:#333;">{val}</td>'
                            
                    html_table += '</tr>'
                html_table += '</table>'
                
                st.markdown(html_table, unsafe_allow_html=True)

else:
    st.info("Kripya engine chalane ke liye 0DSP0 sheet upload karein.")
                        
