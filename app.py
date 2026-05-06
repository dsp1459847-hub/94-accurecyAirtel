import pandas as pd
import streamlit as st
from datetime import timedelta
from collections import Counter

st.set_page_config(layout="wide")
st.title("MAYA AI: Magnet & Trigger Engine (100% Rule Based)")
st.write("Yeh engine 'Tukka' nahi marta. Yeh check karta hai ki kal Joda, Counting, ya Ulta-Pulta aaya tha kya? Aur us 'Trigger' ke hisaab se history se number khinchta hai.")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

# ==========================================
# ADVANCED MAGNET RULES (Devender Ji's Logic)
# ==========================================
def is_joda(val):
    return len(val) == 2 and val[0] == val[1]

def is_forward_counting(val):
    if len(val) != 2: return False
    return int(val[1]) - int(val[0]) == 1

def is_backward_counting(val):
    if len(val) != 2: return False
    return int(val[0]) - int(val[1]) == 1

def get_magnet_digits(d):
    # Aapke bataye gaye fix khinchne wale ank aur (-1) drop logic
    magnets = set()
    if d == '1': magnets.update(['4', '9'])
    if d == '3': magnets.update(['0', '5', '8', '9'])
    if d == '9': magnets.update(['0', '8']) # 9 aata hai to 0 aata hai, ya 1 kam karke 8
    if d == '8': magnets.update(['0', '7']) # 8 aata hai to 0 aata hai, ya 1 kam karke 7
    if d == '4': magnets.update(['1', '9'])
    return list(magnets)

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
        
        if idx_kal < 15:
            st.warning("Trigger scan karne ke liye thodi aur history chahiye.")
        else:
            with st.spinner("MAYA AI Joda, Counting aur Magnet Triggers check kar rahi hai..."):
                
                # --- CORE ENGINE: TRIGGER BASED SCANNER ---
                def get_trigger_based_jodis(target_idx, shift_col):
                    val_kal = str(df.iloc[target_idx-1][shift_col]).replace('.0', '').strip()
                    if len(val_kal) == 1: val_kal = '0' + val_kal
                    
                    if len(val_kal) != 2 or not val_kal.isdigit(): 
                        return [], "No Active Trigger"
                        
                    k_a, k_b = val_kal[0], val_kal[1]
                    
                    # 1. IDENTIFY ACTIVE TRIGGERS FOR TODAY
                    active_triggers = []
                    if is_joda(val_kal): active_triggers.append("Joda")
                    if is_forward_counting(val_kal): active_triggers.append("Sidhi Counting")
                    if is_backward_counting(val_kal): active_triggers.append("Ulta Counting")
                    
                    # 2. HISTORICAL SCAN BASED ON TRIGGERS
                    # Agar koi trigger active hai, to history me dekho jab bhi ye trigger aaya tha, agle din kya aaya?
                    hist_outcomes = []
                    
                    for i in range(2, target_idx):
                        hist_val_kal = str(df.iloc[i-1][shift_col]).replace('.0', '').strip()
                        if len(hist_val_kal) == 1: hist_val_kal = '0' + hist_val_kal
                        if len(hist_val_kal) != 2 or not hist_val_kal.isdigit(): continue
                            
                        trigger_match = False
                        if "Joda" in active_triggers and is_joda(hist_val_kal): trigger_match = True
                        elif "Sidhi Counting" in active_triggers and is_forward_counting(hist_val_kal): trigger_match = True
                        elif "Ulta Counting" in active_triggers and is_backward_counting(hist_val_kal): trigger_match = True
                        # Fallback: Agar koi special trigger nahi hai, to general A aur B ka match dekho
                        elif not active_triggers and (hist_val_kal[0] == k_a or hist_val_kal[1] == k_b):
                            trigger_match = True
                            
                        if trigger_match:
                            act_next_day = str(df.iloc[i][shift_col]).replace('.0', '').strip()
                            if len(act_next_day) == 1: act_next_day = '0' + act_next_day
                            if len(act_next_day) == 2 and act_next_day.isdigit():
                                hist_outcomes.append(act_next_day)

                    # 3. SELECT TOP OUTCOMES FROM HISTORY
                    base_vip_jodis = []
                    if hist_outcomes:
                        # Grab the top 15 most frequent exact Jodis that came after this specific trigger
                        top_hist = [item[0] for item in Counter(hist_outcomes).most_common(15)]
                        base_vip_jodis.extend(top_hist)

                    # 4. APPLY MAGNET RULES (-1 Drop & Fixed Rashi Additions)
                    magnet_a_pool = set([k_a])
                    magnet_b_pool = set([k_b])
                    
                    magnet_a_pool.update(get_magnet_digits(k_a))
                    magnet_b_pool.update(get_magnet_digits(k_b))
                    
                    magnet_jodis = [f"{a}{b}" for a in magnet_a_pool for b in magnet_b_pool]
                    
                    # Combine historical truth with Magnet rules
                    final_pool = list(set(base_vip_jodis + magnet_jodis))
                    
                    # 5. REMOVE KACHRA (Dead Numbers of Last 5 Days)
                    garbage = set()
                    for i in range(max(0, target_idx - 5), target_idx):
                        v = str(df.iloc[i][shift_col]).replace('.0', '').strip()
                        if len(v) == 1: v = '0' + v
                        if len(v) == 2: garbage.add(v)
                            
                    final_filtered = [j for j in final_pool if j not in garbage]
                    
                    status_msg = " + ".join(active_triggers) if active_triggers else "Normal Digit Magnet"
                    return final_filtered[:25], status_msg # Return max 25 solid Jodis

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
                        
                        final_vips, trigger_status = get_trigger_based_jodis(target_idx, shift)
                        
                        st.write(f"**📥 Input (Kal):** {kal_val if kal_val not in ['nan', 'XX', ''] else '-'}")
                        st.write(f"**🎯 Parikshan:** {parikshan_val if parikshan_val not in ['nan', 'XX', ''] else 'Pending'}")
                        
                        # Trigger Notification
                        if "Normal" not in trigger_status and trigger_status != "No Active Trigger":
                            st.markdown(f"<div style='font-size:12px; color:#856404; background-color:#fff3cd; padding:5px; border-radius:5px; margin-bottom:10px;'>🧲 Program Active: <b>{trigger_status}</b></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='font-size:12px; color:#155724; background-color:#d4edda; padding:5px; border-radius:5px; margin-bottom:10px;'>🧲 Program Active: Normal Magnet</div>", unsafe_allow_html=True)
                            
                        if final_vips:
                            if parikshan_val in final_vips:
                                st.markdown(f"<div style='color:white; background-color:#28a745; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>✅ PASS! ({parikshan_val})</div>", unsafe_allow_html=True)
                            elif parikshan_val:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>❌ Miss</div>", unsafe_allow_html=True)
                                
                            st.write(f"**💎 High-Impact Jodis ({len(final_vips)}):**")
                            j_chunks = [final_vips[x:x+5] for x in range(0, len(final_vips), 5)]
                            for chunk in j_chunks:
                                st.code(" | ".join(chunk))
                        else:
                            st.warning("⚠️ Data incomplete hai.")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Tracker (Magnet & Trigger Results)")
                
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
                                
                            h_final, _ = get_trigger_based_jodis(row_idx, c)
                            
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
                
