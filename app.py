import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import defaultdict

st.set_page_config(layout="wide")
st.title("MAYA AI: Exact Gap & Transition Engine")
st.write("Yeh engine check karta hai ki kal history mein kya 'Gap' (Plus/Minus) aaya tha, aur us Gap ke aane ke baad aaj kaunsa Gap sabse zyada aata hai.")

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
        
        if idx_kal < 5:
            st.error("Engine ko check karne ke liye aur purani history chahiye.")
        else:
            with st.spinner("MAYA AI 'Kal ka Gap -> Aaj ka Gap' scan kar rahi hai..."):
                
                # ==========================================
                # LAYER 1: CALCULATE ALL HISTORICAL GAPS
                # ==========================================
                # Histry me har din apne pichle din se kitna aage/piche tha
                # Transition Matrix: transition[yesterday_gap][today_gap] = count
                transition_a = defaultdict(lambda: defaultdict(int))
                transition_b = defaultdict(lambda: defaultdict(int))
                
                # Limit scan up to the Parikshan day to prevent lookahead
                limit_idx = idx_parikshan if idx_parikshan is not None else idx_kal + 1
                
                for i in range(2, limit_idx):
                    parso_a, parso_b = get_andar_bahar(df.iloc[i-2][target_shift])
                    kal_a, kal_b = get_andar_bahar(df.iloc[i-1][target_shift])
                    aaj_a, aaj_b = get_andar_bahar(df.iloc[i][target_shift])
                    
                    if parso_a and kal_a and aaj_a and parso_b and kal_b and aaj_b:
                        # Yesterday's Gap (Kal aaya hua difference)
                        gap_kal_a = (int(kal_a) - int(parso_a)) % 10
                        gap_kal_b = (int(kal_b) - int(parso_b)) % 10
                        
                        # Today's Gap (Aaj ka difference)
                        gap_aaj_a = (int(aaj_a) - int(kal_a)) % 10
                        gap_aaj_b = (int(aaj_b) - int(kal_b)) % 10
                        
                        # Track transition (Agar kal X gap tha, toh aaj Y gap kitni baar aaya)
                        transition_a[gap_kal_a][gap_aaj_a] += 1
                        transition_b[gap_kal_b][gap_aaj_b] += 1

                # ==========================================
                # LAYER 2: APPLY GAP LOGIC ON TODAY
                # ==========================================
                # Find exactly what the gap was yesterday (Input Day)
                parso_input_a, parso_input_b = get_andar_bahar(df.iloc[idx_kal-1][target_shift])
                kal_input_a, kal_input_b = get_andar_bahar(df.iloc[idx_kal][target_shift])
                
                gap_kal_a = (int(kal_input_a) - int(parso_input_a)) % 10 if (kal_input_a and parso_input_a) else None
                gap_kal_b = (int(kal_input_b) - int(parso_input_b)) % 10 if (kal_input_b and parso_input_b) else None
                
                top_expected_gaps_a = []
                top_expected_gaps_b = []
                
                if gap_kal_a is not None and gap_kal_b is not None:
                    # Sort the most frequent "Today Gaps" based on "Yesterday's Gap"
                    sort_gaps_a = sorted(transition_a[gap_kal_a].items(), key=lambda x: x[1], reverse=True)
                    sort_gaps_b = sorted(transition_b[gap_kal_b].items(), key=lambda x: x[1], reverse=True)
                    
                    # Top 4 most frequent gaps for today
                    top_expected_gaps_a = [x[0] for x in sort_gaps_a[:4]]
                    top_expected_gaps_b = [x[0] for x in sort_gaps_b[:4]]

                # ==========================================
                # LAYER 3: PREDICT FINAL VIP JODIS
                # ==========================================
                vip_jodis = []
                top_a_digits = []
                top_b_digits = []
                
                if kal_input_a and kal_input_b and top_expected_gaps_a and top_expected_gaps_b:
                    for ga in top_expected_gaps_a:
                        final_a = str((int(kal_input_a) + ga) % 10)
                        top_a_digits.append(final_a)
                    for gb in top_expected_gaps_b:
                        final_b = str((int(kal_input_b) + gb) % 10)
                        top_b_digits.append(final_b)
                        
                    top_a_digits = list(dict.fromkeys(top_a_digits)) # Remove duplicates
                    top_b_digits = list(dict.fromkeys(top_b_digits))
                    
                    for a in top_a_digits:
                        for b in top_b_digits:
                            vip_jodis.append(f"{a}{b}")

                # --- Parikshan Result Fetching ---
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
                    st.info(f"🔄 **History Check:** \nKal Andar ka Gap: **{'+'+str(gap_kal_a) if gap_kal_a is not None else 'N/A'}** \nKal Bahar ka Gap: **{'+'+str(gap_kal_b) if gap_kal_b is not None else 'N/A'}**")
                with c2:
                    a_info = ', '.join([f"+{g}" for g in top_expected_gaps_a])
                    b_info = ', '.join([f"+{g}" for g in top_expected_gaps_b])
                    st.warning(f"📈 **Aaj Ka Predicted Gap:** \nAndar: **{a_info}** \nBahar: **{b_info}**")
                with c3:
                    st.error(f"🎯 **Aaj/Parikshan ({parikshan_date_str}):** \n### {parikshan_actual if parikshan_actual else 'Result Aana Baki Hai'}")
                st.markdown("---")

                if vip_jodis:
                    st.write("### 💎 Target VIP Anks (Based on Gap Repetition Frequency)")
                    if parikshan_actual in vip_jodis:
                        st.success(f"🎉 **SHANDAAR PASS!** Gap Tracking Engine ne exact result pakad liya!")
                    elif parikshan_actual:
                        st.error(f"Target miss hua. Aaya: {parikshan_actual}")
                    
                    jodi_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>"
                    for j in vip_jodis:
                        if j == parikshan_actual:
                            jodi_html += f"<div style='background-color: #28a745; color: white; padding: 10px 20px; font-size: 20px; font-weight: bold; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>{j} ✅ PASS</div>"
                        else:
                            jodi_html += f"<div style='background-color: #f1f3f5; color: #333; padding: 10px 20px; font-size: 18px; font-weight: bold; border-radius: 8px; border: 1px solid #ccc;'>{j}</div>"
                    jodi_html += "</div>"
                    st.markdown(jodi_html, unsafe_allow_html=True)
                else:
                    st.error("Gap calculate karne ke liye data missing hai.")

                # ==========================================
                # 11-DAY HISTORY HTML TABLE (ONLY GREEN BOXES FOR PASS)
                # ==========================================
                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Gap Tracker (Sirf Paas = Hara Dabba)")
                
                # Pre-calculate a function to predict for any day i using the transition logic
                def predict_for_day(day_idx):
                    try:
                        p_a, p_b = get_andar_bahar(df.iloc[day_idx-2][target_shift])
                        k_a, k_b = get_andar_bahar(df.iloc[day_idx-1][target_shift])
                        
                        if not (p_a and k_a and p_b and k_b): return []
                        
                        g_k_a = (int(k_a) - int(p_a)) % 10
                        g_k_b = (int(k_b) - int(p_b)) % 10
                        
                        s_g_a = sorted(transition_a[g_k_a].items(), key=lambda x: x[1], reverse=True)[:4]
                        s_g_b = sorted(transition_b[g_k_b].items(), key=lambda x: x[1], reverse=True)[:4]
                        
                        top_ga = [x[0] for x in s_g_a]
                        top_gb = [x[0] for x in s_g_b]
                        
                        day_jodis = []
                        for ga in top_ga:
                            for gb in top_gb:
                                day_jodis.append(f"{(int(k_a) + ga) % 10}{(int(k_b) + gb) % 10}")
                        return day_jodis
                    except:
                        return []

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
                            hist_jodis = predict_for_day(i)
                            if actual_val in hist_jodis:
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
                                                                                                                                                           
