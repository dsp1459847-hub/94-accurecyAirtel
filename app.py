import pandas as pd
import streamlit as st
from collections import Counter

st.set_page_config(layout="wide")
st.title("MAYA AI: Historical Magnet & Pattern Scanner")
st.write("Yeh engine kal ke 'Triggers' (Joda, Counting, Anchors) pakadta hai, aur pichle 7 saal ki history chhan kar wahi ank nikalta hai jo sach mein aate hain.")

uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

# --- HELPER FUNCTIONS ---
def get_val_str(val):
    if pd.isna(val): return ""
    val = str(val).replace('.0', '').strip()
    if val in ['nan', 'XX', '']: return ""
    if len(val) == 1 and val.isdigit(): return '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[:2]
    return ""

def get_active_triggers(val):
    triggers = []
    if not val or len(val) != 2: return triggers
    
    # Trigger 1: Joda
    if val[0] == val[1]: triggers.append("Joda")
    
    # Trigger 2 & 3: Counting
    try:
        diff = int(val[1]) - int(val[0])
        if diff == 1: triggers.append("Sidhi Counting")
        if diff == -1: triggers.append("Ulti Counting")
    except:
        pass
        
    # Trigger 4: Anchor Digits (0 se 9 tak)
    triggers.append(f"Anchor_{val[0]}")
    if val[0] != val[1]: # Taki double anchor na ho jaye
        triggers.append(f"Anchor_{val[1]}")
    
    return triggers

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
            st.warning("Data kam hai. Kam se kam 10 din ki history chahiye.")
        else:
            with st.spinner("MAYA AI pichle 7 saal ka data chhan rahi hai..."):
                
                # --- CORE ENGINE: HISTORICAL MAGNET SCANNER ---
                def run_magnet_scanner(target_idx, shift):
                    val_kal = get_val_str(df.iloc[target_idx-1][shift])
                    if not val_kal or len(val_kal) != 2: return [], []
                    
                    active_triggers = get_active_triggers(val_kal)
                    if not active_triggers: return [], []
                    
                    outcomes = []
                    
                    # 7-Saal ki history scan karo
                    for i in range(2, target_idx):
                        h_kal = get_val_str(df.iloc[i-1][shift])
                        if not h_kal or len(h_kal) != 2: continue
                        
                        h_trigs = get_active_triggers(h_kal)
                        common_trigs = set(active_triggers).intersection(set(h_trigs))
                        
                        # Agar history ke us din wahi pattern bana tha jo aaj bana hai
                        if common_trigs:
                            h_act = get_val_str(df.iloc[i][shift])
                            if h_act and len(h_act) == 2:
                                # Weightage: Jitne zyada pattern match honge, utni power
                                weight = len(common_trigs)
                                
                                # Joda aur Counting wale match ko double power
                                for ct in common_trigs:
                                    if ct in ["Joda", "Sidhi Counting", "Ulti Counting"]:
                                        weight += 2
                                        
                                outcomes.extend([h_act] * weight)
                                
                    # Sabse zyada baar aane wale Top 25 Ank uthao
                    top_vips = [x[0] for x in Counter(outcomes).most_common(25)]
                    
                    # Active triggers ka naam saaf karne ke liye
                    clean_triggers = [t.replace("Anchor_", "Ank ") for t in active_triggers]
                    
                    return top_vips, clean_triggers

                # --- UI DISPLAY ---
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
                        
                        final_vips, active_trigs = run_magnet_scanner(target_idx, shift)
                        
                        st.write(f"**📥 Input (Kal):** {kal_val if kal_val else '-'}")
                        st.write(f"**🎯 Parikshan:** {parikshan_val if parikshan_val else 'Pending'}")
                        
                        if active_trigs:
                            trig_str = " + ".join(active_trigs)
                            st.markdown(f"<div style='font-size:12px; color:#856404; background-color:#fff3cd; padding:5px; border-radius:5px; margin-bottom:10px;'>⚡ <b>Active Pattern:</b> {trig_str}</div>", unsafe_allow_html=True)
                            
                        if final_vips:
                            if parikshan_val in final_vips:
                                st.markdown(f"<div style='color:white; background-color:#28a745; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>✅ PASS! ({parikshan_val})</div>", unsafe_allow_html=True)
                            elif parikshan_val:
                                st.markdown(f"<div style='color:white; background-color:#dc3545; padding:8px; border-radius:5px; font-weight:bold; text-align:center; margin-bottom:10px;'>❌ Miss</div>", unsafe_allow_html=True)
                                
                            st.write(f"**💎 Prediction ({len(final_vips)} Jodis):**")
                            j_chunks = [final_vips[x:x+5] for x in range(0, len(final_vips), 5)]
                            for chunk in j_chunks:
                                st.code(" | ".join(chunk))
                        else:
                            st.warning("⚠️ Data incomplete hai.")
                            
                        st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Tracker (Historical Magnet Scanner)")
                
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
                                
                            h_final, _ = run_magnet_scanner(row_idx, c)
                            
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
    
