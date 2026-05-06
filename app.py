import pandas as pd
import streamlit as st
from datetime import timedelta

st.set_page_config(layout="wide")
st.title("MAYA AI: Auto-Adaptive Master Engine (100% Tukka Free)")
st.write("Yeh engine koi pehle se set rule nahi manta. Yeh maujooda history aur trend ko match karke apne naye rules khud banata hai.")

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
        selected_date = st.date_input("📅 Jis din ka data INPUT manna hai (Kal):", 
                                      value=max_date - timedelta(days=1), min_value=min_date, max_value=max_date)
    with col_shift:
        target_shift = st.selectbox("🎯 Aaj kis Shift ka prediction aur Parikshan dekhna hai?", cols)

    sel_date_pd = pd.to_datetime(selected_date)
    parikshan_date_pd = sel_date_pd + pd.Timedelta(days=1)

    day_data = df[df['DATE'] == sel_date_pd]
    parikshan_data = df[df['DATE'] == parikshan_date_pd]
    
    inputs = {}
    actual_parikshan_results = {}
    
    if not day_data.empty:
        for c in cols:
            val = str(day_data.iloc[0][c]) if c in day_data.columns else ""
            inputs[c] = "" if val in ['nan', 'XX'] else val
            
    if not parikshan_data.empty:
        for c in cols:
            val = str(parikshan_data.iloc[0][c]) if c in parikshan_data.columns else ""
            actual_parikshan_results[c] = "" if val in ['nan', 'XX'] else val

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**📥 Input Data ({sel_date_pd.strftime('%d-%m-%Y')}):** \n" + " | ".join([f"{c}: {inputs.get(c, '-')}" for c in cols]))
    with c2:
        st.warning(f"**🎯 Parikshan Data ({parikshan_date_pd.strftime('%d-%m-%Y')}):** \n" + " | ".join([f"{c}: {actual_parikshan_results.get(c, '-')}" for c in cols]))
    st.markdown("---")

    if day_data.empty:
        st.error("Sheet mein is Input date ka data nahi hai.")
    else:
        with st.spinner("MAYA AI apna Dynamic Rule bana rahi hai..."):
            andar_scores = {str(i): 0 for i in range(10)}
            bahar_scores = {str(i): 0 for i in range(10)}
            
            # --- IDENTIFY 11-DAY TREND DATES (To solve the "Kyun Fail Hota Hai" problem) ---
            seq_dates = df[(df['DATE'] <= sel_date_pd)].tail(11)['DATE'].tolist()
            war_dates = df[(df['DATE'] <= sel_date_pd) & (df['DATE'].dt.weekday == sel_date_pd.weekday())].tail(11)['DATE'].tolist()
            tarikh_dates = df[(df['DATE'] <= sel_date_pd) & (df['DATE'].dt.day == sel_date_pd.day)].tail(11)['DATE'].tolist()

            total_matches = 0

            # --- DYNAMIC RULE ENGINE ---
            for i in range(len(df) - 1):
                hist_date = df.iloc[i]['DATE']
                if hist_date >= sel_date_pd: continue
                
                day_has_match = False
                for c in cols:
                    if not inputs.get(c): continue
                    inp_a, inp_b = get_andar_bahar(inputs[c])
                    hist_a, hist_b = get_andar_bahar(df.iloc[i][c])
                    
                    if (inp_a and hist_a == inp_a) or (inp_b and hist_b == inp_b):
                        day_has_match = True

                if day_has_match:
                    tom_a, tom_b = get_andar_bahar(df.iloc[i+1][target_shift])
                    if tom_a and tom_b:
                        # Base Point (Overall History)
                        weight = 1
                        
                        # Dynamic Trend Multiplier (Agar yeh match pichle 11 din ya same war/date me hua hai)
                        if hist_date in seq_dates: weight += 5
                        if hist_date in war_dates: weight += 5
                        if hist_date in tarikh_dates: weight += 5
                        
                        andar_scores[tom_a] += weight
                        bahar_scores[tom_b] += weight
                        total_matches += 1
                        
            # Get Top Predicted Digits
            res_a = sorted(andar_scores.items(), key=lambda x: x[1], reverse=True)
            res_b = sorted(bahar_scores.items(), key=lambda x: x[1], reverse=True)
            
            top_3_a = [x[0] for x in res_a[:3]]
            top_3_b = [x[0] for x in res_b[:3]]
            
            actual_str = actual_parikshan_results.get(target_shift, "")
            act_a, act_b = get_andar_bahar(actual_str)
            
            if actual_str:
                st.error(f"🎯 **ACTUAL PARIKSHAN RESULT ({target_shift}):** {actual_str}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.success("🔥 **DYNAMIC RULE ANDAR (Top Scored)**")
                for val, score in res_a[:3]:
                    is_hit = "✅ **PASS**" if val == act_a else "❌ Lal"
                    st.write(f"**[{val}]** - (Score: {score}) {is_hit}")
            with col2:
                st.success("🔥 **DYNAMIC RULE BAHAR (Top Scored)**")
                for val, score in res_b[:3]:
                    is_hit = "✅ **PASS**" if val == act_b else "❌ Lal"
                    st.write(f"**[{val}]** - (Score: {score}) {is_hit}")

        # --- RED & GREEN STYLING LOGIC FOR 11-DAY HISTORY ---
        st.markdown("---")
        st.subheader(f"📚 3-Way History & Pattern Cross-Check")
        st.write("🟢 **Hara (Green):** Wo ank jo hamari Top 3 Prediction me the aur sach me aaye.")
        st.write("🔴 **Lal (Red):** Wo ank jo hamari Prediction me nahi the.")

        def color_cells(val):
            if pd.isna(val) or val == 'XX' or val == '':
                return ''
            v_str = str(val).replace('.0', '').strip()
            if len(v_str) == 1: v_str = '0' + v_str
            if len(v_str) >= 2:
                a, b = v_str[0], v_str[1]
                # Agar us din ka Andar ya Bahar hamari Top prediction me hai to Hara (Green), varna Lal (Red)
                if a in top_3_a or b in top_3_b:
                    return 'background-color: #c3e6cb; color: #155724; font-weight: bold;' # Green
                else:
                    return 'background-color: #f5c6cb; color: #721c24;' # Red
            return ''

        df_seq = df[df['DATE'] <= parikshan_date_pd].tail(11).copy()
        df_war = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.weekday == parikshan_date_pd.weekday())].tail(11).copy()
        df_tarikh = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.day == parikshan_date_pd.day)].tail(11).copy()

        for d in [df_seq, df_war, df_tarikh]:
            d['DATE'] = d['DATE'].dt.strftime('%d-%m-%Y')

        tab1, tab2, tab3 = st.tabs(["1️⃣ Lagaatar (Seq) 11 Din", "2️⃣ War (Day) 11 Din", "3️⃣ Tareekh (Date) 11 Din"])
        
        with tab1: 
            st.dataframe(df_seq.style.applymap(color_cells, subset=cols), use_container_width=True)
        with tab2: 
            st.dataframe(df_war.style.applymap(color_cells, subset=cols), use_container_width=True)
        with tab3: 
            st.dataframe(df_tarikh.style.applymap(color_cells, subset=cols), use_container_width=True)

else:
    st.info("Kripya engine chalane ke liye 0DSP0 sheet upload karein.")
    
