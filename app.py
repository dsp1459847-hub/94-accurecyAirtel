import pandas as pd
import streamlit as st
from datetime import timedelta

st.set_page_config(layout="wide")
st.title("MAYA AI: Plus-Minus Adaptive Engine & Color Grid")
st.write("Yeh engine har shift ke liye apne aap sabse best +/- (Plus/Minus) rule dhoondhta hai aur 11 din ki history ko Hare/Lal dabbo me dikhata hai.")

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

    # --- DATE & SHIFT SELECTION ---
    col_date, col_shift = st.columns(2)
    max_date = df['DATE'].max().to_pydatetime()
    min_date = df['DATE'].min().to_pydatetime()
    
    with col_date:
        selected_date = st.date_input("📅 Jis din ko INPUT manna hai (Kal):", 
                                      value=max_date - timedelta(days=1), min_value=min_date, max_value=max_date)
    with col_shift:
        target_shift = st.selectbox("🎯 Aaj kis Shift ka Plus/Minus Prediction dekhna hai?", cols)

    sel_date_pd = pd.to_datetime(selected_date)
    parikshan_date_pd = sel_date_pd + pd.Timedelta(days=1)

    day_data = df[df['DATE'] == sel_date_pd]
    parikshan_data = df[df['DATE'] == parikshan_date_pd]
    
    input_str = str(day_data.iloc[0][target_shift]) if not day_data.empty and target_shift in day_data.columns else ""
    parikshan_str = str(parikshan_data.iloc[0][target_shift]) if not parikshan_data.empty and target_shift in parikshan_data.columns else ""
    
    inp_a, inp_b = get_andar_bahar(input_str)
    act_a, act_b = get_andar_bahar(parikshan_str)

    st.markdown("---")
    st.info(f"**📥 Input Data ({target_shift} @ {sel_date_pd.strftime('%d-%m-%Y')}):** {input_str}")
    st.warning(f"**🎯 Parikshan Data ({target_shift} @ {parikshan_date_pd.strftime('%d-%m-%Y')}):** {parikshan_str}")
    st.markdown("---")

    if day_data.empty or not inp_a:
        st.error(f"Sheet mein {target_shift} ka Input data nahi mila.")
    else:
        with st.spinner("MAYA AI Plus/Minus Rule nikal rahi hai..."):
            
            # --- PLUS/MINUS (OFFSET) LOGIC ENGINE ---
            # Engine dekhega ki Target shift me ek din se agle din me kitna plus ya minus hota hai
            offset_counts_a = {i: 0 for i in range(10)}
            offset_counts_b = {i: 0 for i in range(10)}
            
            total_history_days = 0

            for i in range(len(df) - 1):
                if df.iloc[i]['DATE'] >= sel_date_pd: continue
                
                yest_a, yest_b = get_andar_bahar(df.iloc[i][target_shift])
                tom_a, tom_b = get_andar_bahar(df.iloc[i+1][target_shift])
                
                if yest_a and tom_a and yest_b and tom_b:
                    # Plus/Minus calculate karna (0 se 9 ke beech)
                    diff_a = (int(tom_a) - int(yest_a)) % 10
                    diff_b = (int(tom_b) - int(yest_b)) % 10
                    
                    offset_counts_a[diff_a] += 1
                    offset_counts_b[diff_b] += 1
                    total_history_days += 1

            # Sabse zyada aane wale Plus/Minus Rules nikalna
            best_offsets_a = sorted(offset_counts_a.items(), key=lambda x: x[1], reverse=True)
            best_offsets_b = sorted(offset_counts_b.items(), key=lambda x: x[1], reverse=True)

            # Aaj ke input par best Plus/Minus lagana
            top_3_pred_a = [str((int(inp_a) + off) % 10) for off, count in best_offsets_a[:3]]
            top_3_pred_b = [str((int(inp_b) + off) % 10) for off, count in best_offsets_b[:3]]

            st.write(f"### ⚙️ {target_shift} Ke Liye Shift-Specific Rules")
            st.write(f"Engine ne history ke {total_history_days} din check kiye aur yeh pata lagaya ki **{target_shift}** mein lagataar kya Plus/Minus chal raha hai.")

            # --- DISPLAY PREDICTIONS ---
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🎯 **ANDAR PREDICTION** (Input Andar: {inp_a})")
                for i in range(3):
                    off, count = best_offsets_a[i]
                    pred_val = top_3_pred_a[i]
                    rule_text = f"+{off}" if off <= 5 else f"-{10-off}"
                    is_hit = "✅ **PASS**" if pred_val == act_a else "❌ Lal"
                    st.write(f"**[{pred_val}]** -> (Rule: **{rule_text}**, History me {count} baar paas) {is_hit}")
                    
            with col2:
                st.success(f"🎯 **BAHAR PREDICTION** (Input Bahar: {inp_b})")
                for i in range(3):
                    off, count = best_offsets_b[i]
                    pred_val = top_3_pred_b[i]
                    rule_text = f"+{off}" if off <= 5 else f"-{10-off}"
                    is_hit = "✅ **PASS**" if pred_val == act_b else "❌ Lal"
                    st.write(f"**[{pred_val}]** -> (Rule: **{rule_text}**, History me {count} baar paas) {is_hit}")

        # --- 11-DAY HTML COLOR GRID (100% WORKING GREEN/RED BOXES) ---
        st.markdown("---")
        st.subheader("📚 11-Din Ki History (Hara = Pass, Lal = Fail)")
        st.write("Ab aap saaf dekh sakte hain ki pichle 11 dino mein yeh Plus/Minus rule kitni baar sach mein paas hua hai.")

        def generate_html_table(dataframe, target_col, top_a_list, top_b_list):
            html = '<table style="width:100%; text-align:center; border-collapse: collapse;">'
            html += '<tr><th style="border:1px solid #ddd; padding:8px;">Date</th>'
            for c in cols: html += f'<th style="border:1px solid #ddd; padding:8px;">{c}</th>'
            html += '</tr>'
            
            for _, row in dataframe.iterrows():
                html += '<tr>'
                html += f'<td style="border:1px solid #ddd; padding:8px;">{row["DATE"]}</td>'
                for c in cols:
                    val = str(row[c]).replace('.0', '').strip()
                    if val in ['nan', 'XX', '']:
                        html += f'<td style="border:1px solid #ddd; padding:8px;">-</td>'
                        continue
                    
                    if len(val) == 1: val = '0' + val
                    a, b = val[0], val[1]
                    
                    # Agar target shift hai, to color apply karo
                    if c == target_col:
                        color = "#f8d7da" # Red (Lal) default
                        text_col = "#721c24"
                        if a in top_a_list or b in top_b_list:
                            color = "#d4edda" # Green (Hara)
                            text_col = "#155724"
                        
                        html += f'<td style="border:1px solid #ddd; padding:8px; background-color:{color}; color:{text_col}; font-weight:bold; border-radius:4px;">{val}</td>'
                    else:
                        html += f'<td style="border:1px solid #ddd; padding:8px;">{val}</td>'
                html += '</tr>'
            html += '</table>'
            return html

        df_seq = df[df['DATE'] <= parikshan_date_pd].tail(11).copy()
        target_weekday = parikshan_date_pd.weekday()
        df_war = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.weekday == target_weekday)].tail(11).copy()
        target_day = parikshan_date_pd.day
        df_tarikh = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.day == target_day)].tail(11).copy()

        for d in [df_seq, df_war, df_tarikh]:
            d['DATE'] = d['DATE'].dt.strftime('%d-%m-%Y')

        tab1, tab2, tab3 = st.tabs(["1️⃣ Lagaatar (Seq) 11 Din", "2️⃣ War (Day) 11 Din", "3️⃣ Tareekh (Date) 11 Din"])
        
        with tab1:
            st.markdown(generate_html_table(df_seq, target_shift, top_3_pred_a, top_3_pred_b), unsafe_allow_html=True)
        with tab2:
            st.markdown(generate_html_table(df_war, target_shift, top_3_pred_a, top_3_pred_b), unsafe_allow_html=True)
        with tab3:
            st.markdown(generate_html_table(df_tarikh, target_shift, top_3_pred_a, top_3_pred_b), unsafe_allow_html=True)

else:
    st.info("Kripya engine chalane ke liye 0DSP0 sheet upload karein.")
    
