import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import defaultdict

st.set_page_config(layout="wide")
st.title("MAYA AI: Smart Decider Engine (Add vs Delete)")
st.write("Ab engine blindly delete nahi karega. Yeh pehle trend check karega ki aaj pichle ankon ko DELETE karna hai ya wapas ADD karna hai.")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

# Aapke Fixed Rules
FIXED_PATTERN = {
    '0': ['3', '8', '9', '5'],
    '1': ['4', '9', '3', '6'],
    '2': ['7', '5', '0'], 
    '3': ['0', '9', '5', '8'],
    '4': ['1', '9', '6'],
    '5': ['0', '3', '8'],
    '6': ['1', '4', '9'],
    '7': ['2', '0', '5'],
    '8': ['0', '3', '5'],
    '9': ['0', '4', '1']
}

def get_val_str(val):
    if pd.isna(val): return ""
    val = str(val).replace('.0', '').strip()
    if val in ['nan', 'XX', '']: return ""
    if len(val) == 1 and val.isdigit(): return '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[:2]
    return ""

def get_andar_bahar(val_str):
    if len(val_str) == 2: return val_str[0], val_str[1]
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
        
        if idx_kal < 30:
            st.warning("Trend Decider ko calculate karne ke liye kam se kam 30 din ki history chahiye.")
        else:
            with st.spinner("MAYA AI trend check kar rahi hai ki ankon ko DELETE karna hai ya ADD..."):
                
                def apply_smart_decider(target_idx, shift_col):
                    # --- STEP 1: TREND ANALYZER (Faisla Lena) ---
                    # Check past 30 days to see if this shift repeats its last 7 days numbers
                    repeats_count = 0
                    total_checks = 0
                    
                    start_trend = max(7, target_idx - 30)
                    for i in range(start_trend, target_idx):
                        act_val = get_val_str(df.iloc[i][shift_col])
                        if not act_val: continue
                        
                        # Get past 7 days values
                        past_7_vals = []
                        for k in range(i-7, i):
                            v = get_val_str(df.iloc[k][shift_col])
                            if v: past_7_vals.append(v)
                            
                        if act_val in past_7_vals:
                            repeats_count += 1
                        total_checks += 1
                        
                    repeat_rate = (repeats_count / max(1, total_checks)) * 100
                    # Agar 30 din me se 20% se zyada baar purane ank repeat hote hain, to ADD trend hai
                    is_repeat_trend = repeat_rate >= 20.0 

                    # --- STEP 2: BUILD BASE JODIS ---
                    val_kal = get_val_str(df.iloc[target_idx-1][shift_col])
                    val_parso = get_val_str(df.iloc[target_idx-2][shift_col])
                    k_a, k_b = get_andar_bahar(val_kal)
                    p_a, p_b = get_andar_bahar(val_parso)
                    
                    if not k_a: return [], "No Data", 0, 0
                    
                    pool_a = set([k_a])
                    pool_b = set([k_b])
                    
                    # Apply Fixed Logic
                    if k_a in FIXED_PATTERN: pool_a.update(FIXED_PATTERN[k_a])
                    if k_b in FIXED_PATTERN: pool_b.update(FIXED_PATTERN[k_b])
                        
                    # Apply Rashi Chain logic
                    if p_a and p_b:
                        p_a_rashi, p_b_rashi = get_rashi(p_a), get_rashi(p_b)
                        if k_a == p_a_rashi or k_b == p_a_rashi or k_a == p_b_rashi or k_b == p_b_rashi:
                            pool_a.update([p_a, k_a])
                            pool_b.update([p_b, k_b])

                    base_jodis = [f"{a}{b}" for a in pool_a for b in pool_b]
                    
                    # --- STEP 3: THE DECIDER (ADD or DELETE) ---
                    days_lookback = 7 if shift_col == 'DS' else 5
                    recent_jodis = set()
                    
                    for i in range(max(0, target_idx - days_lookback), target_idx):
                        v = get_val_str(df.iloc[i][shift_col])
                        if v: recent_jodis.add(v)

                    final_jodis = []
                    action_taken = ""
                    added_count = 0
                    deleted_count = 0

                    if is_repeat_trend:
                        # TREND KEHTA HAI KI PURANE ANK AA SAKTE HAIN (ADD LOGIC)
                        action_taken = "ADD (Repeat Phase)"
                        final_jodis = list(set(base_jodis + list(recent_jodis)))
                        added_count = len(recent_jodis)
                    else:
                        # TREND KEHTA HAI KI PURANE ANK DEAD HAIN (DELETE LOGIC)
                        action_taken = "DELETE (Dead Phase)"
                        for j in base_jodis:
                            if j in recent_jodis:
                                deleted_count += 1
                            else:
                                final_jodis.append(j)
                        final_jodis = list(set(final_jodis))

                    return final_jodis, action_taken, added_count, deleted_count

                parikshan_date_str = df.iloc[idx_parikshan]['DATE'].strftime('%d-%m-%Y') if idx_parikshan is not None else "Data Pending"
                
                st.markdown("---")
                st.markdown(f"<h2 style='text-align:center; color:#0056b3;'>🎯 Parikshan Ka Din (Aaj): {parikshan_date_str}</h2>", unsafe_allow_html=True)
                
                grid_cols = st.columns(3)
                
                for i, shift in enumerate(cols):
                    with grid_cols[i % 3]:
                        st.markdown(f"<div style='background-color:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #ccc; margin-bottom:20px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
                        st.markdown(f"<h4 style='text-align:center; color:#e0245e;'>🎰 {shift}</h4>", unsafe_allow_html=True)
                        
                        kal_val = get_val_str(df.iloc[idx_kal][shift])
                        parikshan_val = get_val_str(df.iloc[idx_parikshan][shift]) if idx_parikshan is not None else ""
                        
                        target_idx = idx_parikshan if idx_parikshan is not None else idx_kal + 1
                        
                        final_vips, trend_action, add_c, del_c = apply_smart_decider(target_idx, shift)
                        
                        st.write(f"**📥 Input (Kal):** {kal_val if kal_val else '-'}")
                        st.write(f"**🎯 Parikshan:** {parikshan_val if parikshan_val else 'Pending'}")
                        
                        # --- DYNAMIC DECIDER UI ---
                        if trend_action == "ADD (Repeat Phase)":
                            st.markdown(f"<div style='background-color:#cce5ff; color:#004085; padding:5px; border-radius:5px; font-size:13px; margin-bottom:10px; font-weight:bold;'>🔄 Trend: REPEAT<br>➕ {add_c} Pichle Ank Jode Gaye</div>", unsafe_allow_html=True)
                        elif trend_action == "DELETE (Dead Phase)":
                            st.markdown(f"<div style='background-color:#f8d7da; color:#721c24; padding:5px; border-radius:5px; font-size:13px; margin-bottom:10px; font-weight:bold;'>🚫 Trend: DEAD<br>🗑️ {del_c} Pichle Ank Delete Kiye</div>", unsafe_allow_html=True)
                        
                        if final_vips:
                            if parikshan_val in final_vips:
                                st.markdown(f"<div style='color:white; background-color:#28a745; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>✅ Pass! ({parikshan_val})</div>", unsafe_allow_html=True)
                            elif parikshan_val:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>❌ Miss</div>", unsafe_allow_html=True)
                                
                            st.write(f"**💎 Final Jodis ({len(final_vips)}):**")
                            j_chunks = [final_vips[x:x+5] for x in range(0, len(final_vips), 5)]
                            for chunk in j_chunks:
                                st.code(" | ".join(chunk))
                        else:
                            st.warning("⚠️ Data incomplete hai.")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Tracker (Trend Decider ke Aadhar Par)")
                
                def generate_html_table(history_slice):
                    html_table = '<table style="width:100%; text-align:center; border-collapse: collapse; font-size: 16px;">'
                    html_table += '<tr><th style="border:1px solid #ccc; padding:10px; background-color:#343a40; color:white;">Date</th>'
                    for c in cols: html_table += f'<th style="border:1px solid #ccc; padding:10px; background-color:#343a40; color:white;">{c}</th>'
                    html_table += '</tr>'
                    
                    for row_idx, row in history_slice.iterrows():
                        html_table += '<tr>'
                        html_table += f'<td style="border:1px solid #ccc; padding:10px; font-weight:bold; background-color:#f8f9fa;">{row["DATE"].strftime("%d-%m-%Y")}</td>'
                        
                        for c in cols:
                            actual_val = get_val_str(row[c])
                            if not actual_val:
                                html_table += f'<td style="border:1px solid #ccc; padding:10px; color:#aaa;">-</td>'
                                continue
                                
                            h_final, action, _, _ = apply_smart_decider(row_idx, c)
                            
                            # Chota indicator dikhane ke liye ki add kiya tha ya delete
                            marker = "🔄" if action == "ADD (Repeat Phase)" else "🗑️"
                            
                            if actual_val in h_final:
                                html_table += f'<td style="border:2px solid #1e7e34; padding:10px; background-color:#d4edda; color:#155724; font-weight:bold; font-size: 18px;">{actual_val} ✅ {marker}</td>'
                            else:
                                html_table += f'<td style="border:1px solid #ccc; padding:10px; color:#333;">{actual_val} <span style="font-size:12px;">{marker}</span></td>'
                                
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
    
