import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import Counter

st.set_page_config(layout="wide")
st.title("MAYA AI: 3-Way Anchor & Rashi Rule Engine")
st.write("Yeh engine aapke bataye fixed rules (Rashi aur Pattern) ko Pichle Din, Pichle War, aur Pichli Tareekh par lagakar probability nikalta hai.")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

# ==========================================
# AAPKE BATAYE GAYE RULES AUR RASHI LOGIC
# ==========================================
def expand_digit(d):
    res = {d} # Khud ka ank
    
    # 1. Rashi Logic (+5)
    rashi = str((int(d) + 5) % 10)
    res.add(rashi)
    
    # 2. User Specific Pattern Logic
    if d == '0': res.update(['3', '8', '9'])
    if d == '1': res.update(['4', '9', '3', '6'])
    if d == '3': res.update(['0', '8'])
    if d == '8': res.update(['0', '3'])
    if d == '9': res.update(['0', '4'])
    
    return list(res)

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

    # Automatic Valid Date
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
        
        if idx_kal < 15:
            st.warning("Engine ko calculate karne ke liye thodi aur purani history chahiye.")
        else:
            with st.spinner("MAYA AI 3-Way Anchor, Rashi, aur Probability calculate kar rahi hai..."):
                
                # --- CORE ENGINE LOGIC ---
                def get_vip_jodis_for_date(t_date, shift_col):
                    past_df = df[df['DATE'] < t_date]
                    if len(past_df) < 1: return []
                    
                    # 1. Teen Anchors Uthana
                    kal_row = past_df.iloc[-1]
                    
                    war_df = past_df[past_df['DATE'].dt.weekday == t_date.weekday()]
                    war_row = war_df.iloc[-1] if not war_df.empty else None
                    
                    tarikh_df = past_df[past_df['DATE'].dt.day == t_date.day]
                    tarikh_row = tarikh_df.iloc[-1] if not tarikh_df.empty else None
                    
                    a_anchors, b_anchors = [], []
                    for r in [kal_row, war_row, tarikh_row]:
                        if r is not None:
                            val = str(r[shift_col]).replace('.0', '').strip()
                            if len(val) == 1 and val.isdigit(): val = '0' + val
                            if len(val) >= 2 and val[:2].isdigit():
                                a_anchors.append(val[0])
                                b_anchors.append(val[1])
                                
                    if not a_anchors or not b_anchors: return []
                    
                    # 2. Rule aur Rashi Apply Karna
                    pool_A, pool_B = [], []
                    for a in a_anchors: pool_A.extend(expand_digit(a))
                    for b in b_anchors: pool_B.extend(expand_digit(b))
                    
                    # 3. Probability Check (Kaunsa ank kitni baar bana)
                    count_A = Counter(pool_A)
                    count_B = Counter(pool_B)
                    
                    # 4. History Match (Past me inme se kaunsa sach me sabse jyada khula)
                    hist_actual_A = Counter()
                    hist_actual_B = Counter()
                    for i in range(len(past_df)):
                        val = str(past_df.iloc[i][shift_col]).replace('.0', '').strip()
                        if len(val) == 1 and val.isdigit(): val = '0' + val
                        if len(val) >= 2 and val[:2].isdigit():
                            hist_actual_A[val[0]] += 1
                            hist_actual_B[val[1]] += 1
                            
                    # Final Score = Pattern Probability * Historical Frequency
                    final_scores_A = {d: count_A.get(d, 0) * hist_actual_A.get(d, 1) for d in set(pool_A)}
                    final_scores_B = {d: count_B.get(d, 0) * hist_actual_B.get(d, 1) for d in set(pool_B)}
                    
                    # Top 4 Andar, Top 4 Bahar
                    top_a = sorted(final_scores_A, key=final_scores_A.get, reverse=True)[:4]
                    top_b = sorted(final_scores_B, key=final_scores_B.get, reverse=True)[:4]
                    
                    return [f"{a}{b}" for a in top_a for b in top_b]

                # --- UI DISPLAY FOR ALL 6 SHIFTS ---
                parikshan_date_str = parikshan_date.strftime('%d-%m-%Y')
                
                st.markdown("---")
                st.markdown(f"<h2 style='text-align:center; color:#0056b3;'>🎯 Parikshan Ka Din (Aaj): {parikshan_date_str}</h2>", unsafe_allow_html=True)
                
                grid_cols = st.columns(3)
                for i, shift in enumerate(cols):
                    with grid_cols[i % 3]:
                        st.markdown(f"<div style='background-color:#f1f3f5; padding:15px; border-radius:10px; border:1px solid #ccc; margin-bottom:20px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
                        st.markdown(f"<h4 style='text-align:center; color:#e0245e;'>🎰 {shift}</h4>", unsafe_allow_html=True)
                        
                        kal_val = str(df.iloc[idx_kal][shift]).replace('.0', '').strip()
                        parikshan_val = str(df.iloc[idx_parikshan][shift]).replace('.0', '').strip() if idx_parikshan is not None else ""
                        if len(parikshan_val) == 1 and parikshan_val.isdigit(): parikshan_val = '0' + parikshan_val
                        
                        st.write(f"**📥 Input (Kal):** {kal_val if kal_val not in ['nan', 'XX', ''] else '-'}")
                        st.write(f"**🎯 Parikshan:** {parikshan_val if parikshan_val not in ['nan', 'XX', ''] else 'Pending'}")
                        
                        vip_jodis = get_vip_jodis_for_date(parikshan_date, shift)
                        
                        if vip_jodis:
                            if parikshan_val in vip_jodis:
                                st.markdown(f"<div style='color:white; background-color:#28a745; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px; font-size:18px;'>✅ {parikshan_val} (PASS)</div>", unsafe_allow_html=True)
                            elif parikshan_val:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px; font-size:18px;'>❌ Miss</div>", unsafe_allow_html=True)
                                
                            st.write(f"**💎 VIP 16 Jodis:**")
                            j_chunks = [vip_jodis[x:x+4] for x in range(0, len(vip_jodis), 4)]
                            for chunk in j_chunks:
                                st.code(" | ".join(chunk))
                        else:
                            st.warning("⚠️ Data incomplete hai.")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                # --- 11-DAY HISTORY HTML TABLES (GREEN BOXES ONLY) ---
                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Tracker (Jo Paas Hua, Sirf Us Par Hara Dabba)")
                
                def generate_html_table(history_slice):
                    html_table = '<table style="width:100%; text-align:center; border-collapse: collapse; font-size: 16px;">'
                    html_table += '<tr><th style="border:1px solid #ccc; padding:10px; background-color:#343a40; color:white;">Date</th>'
                    for c in cols: html_table += f'<th style="border:1px solid #ccc; padding:10px; background-color:#343a40; color:white;">{c}</th>'
                    html_table += '</tr>'
                    
                    for row_idx, row in history_slice.iterrows():
                        html_table += '<tr>'
                        row_dt = pd.to_datetime(row["DATE"])
                        html_table += f'<td style="border:1px solid #ccc; padding:10px; font-weight:bold; background-color:#f8f9fa;">{row_dt.strftime("%d-%m-%Y")}</td>'
                        
                        for c in cols:
                            actual_val = str(row[c]).replace('.0', '').strip()
                            if len(actual_val) == 1 and actual_val.isdigit(): actual_val = '0' + actual_val
                            
                            if actual_val in ['nan', 'XX', '']:
                                html_table += f'<td style="border:1px solid #ccc; padding:10px; color:#aaa;">-</td>'
                                continue
                                
                            # Pure logic run for each past day
                            hist_jodis = get_vip_jodis_for_date(row_dt, c)
                            
                            if actual_val in hist_jodis:
                                # GREEN BOX FOR PASS
                                html_table += f'<td style="border:2px solid #1e7e34; padding:10px; background-color:#d4edda; color:#155724; font-weight:bold; font-size: 18px;">{actual_val} ✅</td>'
                            else:
                                # NORMAL FOR FAIL
                                html_table += f'<td style="border:1px solid #ccc; padding:10px; color:#333;">{actual_val}</td>'
                                
                        html_table += '</tr>'
                    html_table += '</table>'
                    return html_table
                
                # Filter 11 Days for each category ending on Parikshan date
                df_seq = df[df['DATE'] <= parikshan_date].tail(11).copy()
                df_war = df[(df['DATE'] <= parikshan_date) & (df['DATE'].dt.weekday == parikshan_date.weekday())].tail(11).copy()
                df_tarikh = df[(df['DATE'] <= parikshan_date) & (df['DATE'].dt.day == parikshan_date.day)].tail(11).copy()

                tab1, tab2, tab3 = st.tabs(["1️⃣ Lagaatar (Seq) 11 Din", "2️⃣ War (Day) 11 Din", "3️⃣ Tareekh (Date) 11 Din"])
                
                with tab1:
                    st.markdown(generate_html_table(df_seq), unsafe_allow_html=True)
                with tab2:
                    st.markdown(generate_html_table(df_war), unsafe_allow_html=True)
                with tab3:
                    st.markdown(generate_html_table(df_tarikh), unsafe_allow_html=True)

else:
    st.info("Kripya engine chalane ke liye 0DSP0 sheet upload karein.")
                
