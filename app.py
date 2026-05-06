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
        
        if idx_kal < 2:
            st.error("Engine ko Cross check karne ke liye aur purani history chahiye.")
        else:
            with st.spinner("MAYA AI Straight, Vertical aur Cross rules check karke kachra hata rahi hai..."):
                
                # --- STEP 1: DEFINE RELATIONS (Cross, Straight, Vertical, Same-Day) ---
                parikshan_row = df.iloc[idx_parikshan] if idx_parikshan else None
                kal_row = df.iloc[idx_kal]
                parso_row = df.iloc[idx_kal - 1]
                
                relations = [] # (Day_Offset, Source_Shift_Name, Type)
                
                for c in cols:
                    # 1. CROSS & STRAIGHT (Kal ki sabhi shift se Aaj ka Target)
                    rel_type = "Straight" if c == target_shift else "Cross"
                    relations.append((1, c, rel_type))
                    
                    # 2. VERTICAL (Parso ka Target Shift se Aaj ka Target)
                    if c == target_shift:
                        relations.append((2, c, "Vertical"))
                        
                    # 3. SAME-DAY CROSS (Aaj ki wo shifts jo Target se pehle aa chuki hain)
                    if parikshan_row is not None and c != target_shift:
                        a, _ = get_andar_bahar(parikshan_row[c])
                        if a: # Agar data maujood hai
                            relations.append((0, c, "Same-Day Cross"))

                # --- STEP 2: HISTORICAL FREQUENCY SCAN (Rule Finder) ---
                freq_tables = {}
                for rel in relations:
                    day_off, src_col, _ = rel
                    f_a = {i: 0 for i in range(10)}
                    f_b = {i: 0 for i in range(10)}
                    
                    for i in range(2, idx_parikshan if idx_parikshan else idx_kal + 1):
                        src_r = df.iloc[i - day_off]
                        tgt_r = df.iloc[i]
                        
                        s_a, s_b = get_andar_bahar(src_r[src_col])
                        t_a, t_b = get_andar_bahar(tgt_r[target_shift])
                        
                        if s_a and t_a and s_b and t_b:
                            f_a[(int(t_a) - int(s_a)) % 10] += 1
                            f_b[(int(t_b) - int(s_b)) % 10] += 1
                            
                    freq_tables[rel] = {'A': f_a, 'B': f_b}

                # Find Rules to ELIMINATE (Bottom 2) and Rules to APPLY (Top 3)
                rules_book = {}
                for rel, freqs in freq_tables.items():
                    sort_a = sorted(freqs['A'].items(), key=lambda x: x[1])
                    sort_b = sorted(freqs['B'].items(), key=lambda x: x[1])
                    
                    # Jo rule history me lagbhag zero hain (Hatao)
                    bad_a = [x[0] for x in sort_a[:2]]
                    bad_b = [x[0] for x in sort_b[:2]]
                    
                    # Jo rule history me sabse hit hain (Apply karo)
                    good_a = {x[0]: x[1] for x in sort_a[-3:]} 
                    good_b = {x[0]: x[1] for x in sort_b[-3:]}
                    
                    rules_book[rel] = {'bad_a': bad_a, 'bad_b': bad_b, 'good_a': good_a, 'good_b': good_b}

                # --- STEP 3: PREDICTION (Checking all 100 Jodis) ---
                def get_dynamic_jodis():
                    jodi_scores = []
                    for a in range(10):
                        for b in range(10):
                            jodi_str = f"{a}{b}"
                            score = 0
                            eliminated = False
                            
                            for rel in relations:
                                day_off, src_col, r_type = rel
                                
                                if day_off == 0 and parikshan_row is not None: src_val = parikshan_row[src_col]
                                elif day_off == 1: src_val = kal_row[src_col]
                                elif day_off == 2: src_val = parso_row[src_col]
                                else: src_val = None
                                
                                s_a, s_b = get_andar_bahar(src_val)
                                if s_a and s_b:
                                    req_a = (a - int(s_a)) % 10
                                    req_b = (b - int(s_b)) % 10
                                    
                                    rb = rules_book[rel]
                                    
                                    # ELIMINATION (Kachra Hatao)
                                    if req_a in rb['bad_a'] or req_b in rb['bad_b']:
                                        score -= 500 # Heavy minus mark so it never shows up
                                        eliminated = True
                                        
                                    # SELECTION (Hit Rule Apply Karo)
                                    if not eliminated:
                                        if req_a in rb['good_a']: score += rb['good_a'][req_a]
                                        if req_b in rb['good_b']: score += rb['good_b'][req_b]

                            if score > 0:
                                jodi_scores.append((jodi_str, score))
                                
                    jodi_scores.sort(key=lambda x: x[1], reverse=True)
                    return [x[0] for x in jodi_scores[:16]] # Top 16 Verified Jodis

                vip_jodis = get_dynamic_jodis()
                
                parikshan_actual = ""
                parikshan_date_str = ""
                if idx_parikshan is not None:
                    parikshan_actual = str(df.iloc[idx_parikshan][target_shift]).replace('.0', '').strip()
                    if len(parikshan_actual) == 1 and parikshan_actual.isdigit(): parikshan_actual = '0' + parikshan_actual
                    parikshan_date_str = df.iloc[idx_parikshan]['DATE'].strftime('%d-%m-%Y')

                st.markdown("---")
                st.write(f"🎯 **Aaj/Parikshan ({parikshan_date_str}):** {parikshan_actual if parikshan_actual else 'Data Pending'}")
                
                if vip_jodis:
                    st.write("### 💎 Target VIP Anks (Cross-Verified Jodis)")
                    if parikshan_actual in vip_jodis:
                        st.success(f"🎉 **SHANDAAR PASS!** Parikshan ka ank **[{parikshan_actual}]** hamare VIP Ankon mein direct paas ho gaya!")
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
                    st.error("Input data theek nahi hai, Jodis nahi ban payin.")

                # --- 11-DAY HISTORY HTML TABLE (ONLY GREEN BOXES FOR PASS) ---
                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Cross-Check (Sirf Paas Hone Par Hara Dabba)")
                
                history_table_data = []
                start_idx = max(2, idx_parikshan - 10 if idx_parikshan else idx_kal - 10)
                end_idx = idx_parikshan if idx_parikshan else idx_kal
                
                for i in range(start_idx, end_idx + 1):
                    row_date = df.iloc[i]['DATE'].strftime('%d-%m-%Y')
                    row_data = {"DATE": row_date}
                    
                    for c in cols:
                        actual_val = str(df.iloc[i][c]).replace('.0', '').strip()
                        if len(actual_val) == 1 and actual_val.isdigit(): actual_val = '0' + actual_val
                        
                        is_pass = False
                        if c == target_shift:
                            # Use historical prediction to check if it passed
                            global kal_row, parso_row, parikshan_row
                            # Temporary override for backtesting function
                            temp_parikshan = df.iloc[i]
                            kal_row = df.iloc[i-1]
                            parso_row = df.iloc[i-2]
                            parikshan_row = temp_parikshan
                            
                            hist_jodis = get_dynamic_jodis()
                            if actual_val in hist_jodis:
                                is_pass = True
                                
                        row_data[c] = {"val": actual_val, "is_pass": is_pass}
                    history_table_data.append(row_data)

                # Render HTML Table
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
                        
