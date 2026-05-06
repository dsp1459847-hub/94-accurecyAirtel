import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")
st.title("MAYA AI: 3-Way History & Rule Master Engine")

# 1. File Upload
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

    # 2. Date Selection
    st.subheader("📅 Tareekh Chunein (Parikshan Ka Din)")
    max_date = df['DATE'].max().to_pydatetime()
    min_date = df['DATE'].min().to_pydatetime()
    
    selected_date = st.date_input("Jis din ka data uthana aur check karna hai:", 
                                  value=max_date, min_value=min_date, max_value=max_date)
    
    sel_date_pd = pd.to_datetime(selected_date)

    # ---------------------------------------------------------
    # 3. 3-WAY HISTORY LOGIC (11 Din Ki List)
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("📚 3-Way History Data (10 Pichle Din + 1 Aaj = Total 11 Din)")
    
    # A. Lagaatar History (Last 11 Days ending on selected date)
    df_seq = df[df['DATE'] <= sel_date_pd].tail(11).copy()
    
    # B. War (Day of Week) History
    target_weekday = sel_date_pd.weekday()
    df_war = df[(df['DATE'] <= sel_date_pd) & (df['DATE'].dt.weekday == target_weekday)].tail(11).copy()
    
    # C. Tareekh (Date) History
    target_day = sel_date_pd.day
    df_tarikh = df[(df['DATE'] <= sel_date_pd) & (df['DATE'].dt.day == target_day)].tail(11).copy()

    # Formating dates for display
    for d in [df_seq, df_war, df_tarikh]:
        d['DATE'] = d['DATE'].dt.strftime('%d-%m-%Y')

    # Streamlit Tabs banaye hain taaki screen saaf rahe
    tab1, tab2, tab3 = st.tabs(["1️⃣ Lagaatar (Seq) 11 Din", "2️⃣ War (Day) 11 Din", "3️⃣ Tareekh (Date) 11 Din"])
    
    with tab1:
        st.write("Aaj aur pichle 10 lagataar dino ki history:")
        st.dataframe(df_seq[['DATE'] + cols].reset_index(drop=True), use_container_width=True)
        
    with tab2:
        war_name = sel_date_pd.strftime('%A')
        st.write(f"Aaj aur pichle 10 **{war_name}** ki history:")
        st.dataframe(df_war[['DATE'] + cols].reset_index(drop=True), use_container_width=True)
        
    with tab3:
        st.write(f"Aaj aur pichle 10 mahino ki **{target_day} tareekh** ki history:")
        st.dataframe(df_tarikh[['DATE'] + cols].reset_index(drop=True), use_container_width=True)

    # ---------------------------------------------------------
    # 4. AUTO-FILL INPUTS & RULE ENGINE
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("📊 Engine Input (Automatic Filled)")
    
    day_data = df[df['DATE'] == sel_date_pd]
    inputs = {}
    
    if not day_data.empty:
        grid = st.columns(3)
        for idx, c in enumerate(cols):
            val = str(day_data.iloc[0][c]) if c in day_data.columns else ""
            if val == 'nan' or val == 'XX': val = ""
            inputs[c] = grid[idx % 3].text_input(f"{c} Result:", value=val, key=f"inp_{c}")
    else:
        st.error("Is tareekh ka data sheet mein nahi mila.")

    target_shift = st.selectbox("Aaj kis Shift ka VIP prediction dekhna hai?", cols)

    if st.button("Run Rule-Applied Backtest"):
        andar_counts = {str(i): 0 for i in range(10)}
        bahar_counts = {str(i): 0 for i in range(10)}
        total_matches = 0
        
        # Rule Engine Target
        rule_expected_targets = set()
        for c in cols:
            if inputs[c]:
                a, b = get_andar_bahar(inputs[c])
                if a or b:
                    pool = [a, b]
                    if '0' in pool: rule_expected_targets.update(['5', '9', '8', '3'])
                    if '1' in pool: rule_expected_targets.add('3')
                    if '8' in pool: rule_expected_targets.add('0')
                    if '9' in pool: rule_expected_targets.add('0')
                    if '3' in pool: rule_expected_targets.add('0')
        
        for i in range(len(df) - 1):
            match_score = 0
            for c in cols:
                if inputs[c]:
                    inp_a, inp_b = get_andar_bahar(inputs[c])
                    hist_a, hist_b = get_andar_bahar(df.iloc[i][c])
                    if inp_a and inp_b and hist_a and hist_b:
                        if hist_a == inp_a or hist_b == inp_b:
                            match_score += 1
            
            if match_score > 0:
                tom_target_a, tom_target_b = get_andar_bahar(df.iloc[i+1][target_shift])
                if tom_target_a and tom_target_b:
                    weight_a = 10 if tom_target_a in rule_expected_targets else 1
                    weight_b = 10 if tom_target_b in rule_expected_targets else 1
                    
                    andar_counts[tom_target_a] += weight_a
                    bahar_counts[tom_target_b] += weight_b
                    total_matches += 1
                    
        res_a = sorted(andar_counts.items(), key=lambda x: x[1], reverse=True)
        res_b = sorted(bahar_counts.items(), key=lambda x: x[1], reverse=True)
        
        st.write(f"---")
        st.info(f"History mein {total_matches} dino ki matching hui aur rules automatically apply kiye gaye.")
        
        if rule_expected_targets:
            st.write(f"🎯 **Rules ne in ankon ko automatic target kiya:** {', '.join(rule_expected_targets)}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"🔥 **Rule-Applied Top Andar:**")
            st.write(f"1. [{res_a[0][0]}] (Score: {res_a[0][1]})")
            st.write(f"2. [{res_a[1][0]}] (Score: {res_a[1][1]})")
            st.write(f"3. [{res_a[2][0]}] (Score: {res_a[2][1]})")
        
        with col2:
            st.success(f"🔥 **Rule-Applied Top Bahar:**")
            st.write(f"1. [{res_b[0][0]}] (Score: {res_b[0][1]})")
            st.write(f"2. [{res_b[1][0]}] (Score: {res_b[1][1]})")
            st.write(f"3. [{res_b[2][0]}] (Score: {res_b[2][1]})")

else:
    st.info("Kripya 0DSP0 sheet upload karein.")
                    
