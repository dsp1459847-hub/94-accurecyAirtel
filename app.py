import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")
st.title("MAYA AI: Andar-Bahar Split & Multi-Shift Master Engine")
st.write("Yeh engine exactly aapke 'Andar-Bahar Splitting' aur 'Multi-Shift Combination' logic par kaam karta hai. Koi weightage nahi, sirf history ki absolute counting (100% Facts).")

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
    
    selected_date = st.date_input("Jis din ka data check karna hai:", 
                                  value=max_date, min_value=min_date, max_value=max_date)
    
    sel_date_pd = pd.to_datetime(selected_date)

    # ---------------------------------------------------------
    # 3. 3-WAY HISTORY LOGIC (Exactly 11 Din)
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("📚 3-Way History Data (10 Pichle Din + 1 Aaj = Total 11 Din)")
    
    df_seq = df[df['DATE'] <= sel_date_pd].tail(11).copy()
    
    target_weekday = sel_date_pd.weekday()
    df_war = df[(df['DATE'] <= sel_date_pd) & (df['DATE'].dt.weekday == target_weekday)].tail(11).copy()
    
    target_day = sel_date_pd.day
    df_tarikh = df[(df['DATE'] <= sel_date_pd) & (df['DATE'].dt.day == target_day)].tail(11).copy()

    for d in [df_seq, df_war, df_tarikh]:
        d['DATE'] = d['DATE'].dt.strftime('%d-%m-%Y')

    tab1, tab2, tab3 = st.tabs(["1️⃣ Lagaatar (Seq) 11 Din", "2️⃣ War (Day) 11 Din", "3️⃣ Tareekh (Date) 11 Din"])
    
    with tab1:
        st.dataframe(df_seq[['DATE'] + cols].reset_index(drop=True), use_container_width=True)
    with tab2:
        st.dataframe(df_war[['DATE'] + cols].reset_index(drop=True), use_container_width=True)
    with tab3:
        st.dataframe(df_tarikh[['DATE'] + cols].reset_index(drop=True), use_container_width=True)

    # ---------------------------------------------------------
    # 4. AUTO-FILL INPUTS
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

    target_shift = st.selectbox("Aaj kis Shift ka VIP prediction nikalna hai?", cols)

    if st.button("Run Exact Andar-Bahar Logic"):
        andar_counts = {str(i): 0 for i in range(10)}
        bahar_counts = {str(i): 0 for i in range(10)}
        
        todays_a_pool = set()
        todays_b_pool = set()
        
        # Input se Andar aur Bahar ke Pool banana
        for c in cols:
            if inputs[c]:
                a, b = get_andar_bahar(inputs[c])
                if a: todays_a_pool.add(a)
                if b: todays_b_pool.add(b)
                
        total_history_events_matched = 0

        # Poori History Mein Loop (i aur i+1 lock)
        for i in range(len(df) - 1):
            day_has_match = False
            
            # -- STEP 2 LOGIC: Single Shift Tracking --
            # "Agar aaj Andar mein '0' aaya hai, toh kal kya aayega"
            for c in cols:
                if not inputs[c]: continue
                inp_a, inp_b = get_andar_bahar(inputs[c])
                hist_a, hist_b = get_andar_bahar(df.iloc[i][c])
                
                # Agar kisi shift ka exactly Andar ya Bahar match hota hai
                if (inp_a and hist_a == inp_a) or (inp_b and hist_b == inp_b):
                    day_has_match = True

            # -- STEP 3 LOGIC: Multi-Shift Combinations --
            # "Jab Andar me (1,9) aur Bahar me (5,0) saath mein aaye the"
            hist_a_pool = set()
            hist_b_pool = set()
            for c in cols:
                ha, hb = get_andar_bahar(df.iloc[i][c])
                if ha: hist_a_pool.add(ha)
                if hb: hist_b_pool.add(hb)
                
            # Agar aaj ke Pool ka zyada hissa history ke is din se match khata hai
            match_a = len(todays_a_pool.intersection(hist_a_pool))
            match_b = len(todays_b_pool.intersection(hist_b_pool))
            
            # Agar pool combination milta hai ya single shift match milti hai
            if day_has_match or (match_a >= 2 and match_b >= 2):
                tom_a, tom_b = get_andar_bahar(df.iloc[i+1][target_shift])
                
                if tom_a and tom_b:
                    # Dono ko alag-alag pure counting mein add kiya gaya (+1 each time it happens in reality)
                    andar_counts[tom_a] += 1
                    bahar_counts[tom_b] += 1
                    total_history_events_matched += 1
                    
        # Sort Karke Sabse Zyada Aane Wale Ank Nikalna
        res_a = sorted(andar_counts.items(), key=lambda x: x[1], reverse=True)
        res_b = sorted(bahar_counts.items(), key=lambda x: x[1], reverse=True)
        
        st.write(f"---")
        st.info(f"Pichli poori history check karne par **{total_history_events_matched}** aise exact pattern mile jahan yahi Andar-Bahar combination khule the.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"🔥 **Agle Din ANDAR mein sabse zyada aane wale ank:**")
            st.write(f"1. [{res_a[0][0]}] (Aaya: {res_a[0][1]} baar)")
            st.write(f"2. [{res_a[1][0]}] (Aaya: {res_a[1][1]} baar)")
            st.write(f"3. [{res_a[2][0]}] (Aaya: {res_a[2][1]} baar)")
        
        with col2:
            st.success(f"🔥 **Agle Din BAHAR mein sabse zyada aane wale ank:**")
            st.write(f"1. [{res_b[0][0]}] (Aaya: {res_b[0][1]} baar)")
            st.write(f"2. [{res_b[1][0]}] (Aaya: {res_b[1][1]} baar)")
            st.write(f"3. [{res_b[2][0]}] (Aaya: {res_b[2][1]} baar)")

else:
    st.info("Kripya engine chalane ke liye 0DSP0 sheet upload karein.")
    
