import pandas as pd
import streamlit as st

st.title("Supreme Platinum Engine: Advanced Master Forecaster")

# 1. Load Data Directly from Numerical Sheet
@st.cache_data
def load_data():
    df = pd.read_csv('0DSP0.xlsx - Sheet1.csv').dropna(subset=['DATE'])
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('DATE').reset_index(drop=True)
    return df

df = load_data()
cols = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

# Rashi & Family Map
rashi_map = {'0':'5', '5':'0', '1':'6', '6':'1', '2':'7', '7':'2', '3':'8', '8':'3', '4':'9', '9':'4'}

def extract_andar_bahar(val):
    val = str(val).replace('.0', '').strip()
    if val == 'nan' or val == 'XX' or val == '': return None, None
    if len(val) == 1 and val.isdigit(): val = '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
    return None, None

st.subheader("Kal ki sabhi shifts ka Numerical Data")
inputs_a = {}
inputs_b = {}
overall_input_pool = set()

# Safe data entry fields
for c in cols:
    val = st.text_input(f"Kal {c} mein kya aaya?", key=c)
    a, b = extract_andar_bahar(val)
    inputs_a[c] = a
    inputs_b[c] = b
    if a: overall_input_pool.add(a)
    if b: overall_input_pool.add(b)

target_shift = st.selectbox("Aaj kis Shift ka VIP prediction nikalna hai?", cols)

if st.button("Run Supreme Master Analysis"):
    target_andar_score = {str(i): 0 for i in range(10)}
    target_bahar_score = {str(i): 0 for i in range(10)}
    
    # Base pattern matching across all historical data
    # Loop avoids looking ahead to prevent same-day fluctuation errors
    for i in range(len(df) - 1):
        match_score = 0
        hist_overall_pool = set()
        
        # 1. Shift-Wise Exact & Cross Match Check
        for c in cols:
            hist_a, hist_b = extract_andar_bahar(df.iloc[i][c])
            inp_a, inp_b = inputs_a[c], inputs_b[c]
            
            if hist_a: hist_overall_pool.add(hist_a)
            if hist_b: hist_overall_pool.add(hist_b)
            
            if inp_a and inp_b and hist_a and hist_b:
                # Direct placement match gives highest weight
                if inp_a == hist_a: match_score += 3
                if inp_b == hist_b: match_score += 3
                # Cross placement gives medium weight
                if inp_a == hist_b or inp_b == hist_a: match_score += 1.5

        if match_score > 0:
            # 2. Overall Combination Pool Test
            pool_match_count = len(overall_input_pool.intersection(hist_overall_pool))
            # Merge both scores
            final_weight = match_score + (pool_match_count * 2)
            
            tom_target_a, tom_target_b = extract_andar_bahar(df.iloc[i+1][target_shift])
            if tom_target_a and tom_target_b:
                target_andar_score[tom_target_a] += final_weight
                target_bahar_score[tom_target_b] += final_weight

    # 3. Special History & Rashi Bonus (Adding Manual Logic for 100%+ tuning)
    for val in overall_input_pool:
        # Rashi Logic
        if val in rashi_map:
            rashi_val = rashi_map[val]
            target_andar_score[rashi_val] += 5  
            target_bahar_score[rashi_val] += 5
            
        # Specific digit historical mapping bonus
        if val == '0':
            for special in ['8', '3', '9', '5']:
                target_andar_score[special] += 4
                target_bahar_score[special] += 4
        elif val == '1':
            target_andar_score['3'] += 4
            target_bahar_score['3'] += 4
        elif val == '3' or val == '8' or val == '9':
            target_andar_score['0'] += 4
            target_bahar_score['0'] += 4

    # 4. Sorting & Output
    sorted_andar = sorted(target_andar_score.items(), key=lambda x: x[1], reverse=True)
    sorted_bahar = sorted(target_bahar_score.items(), key=lambda x: x[1], reverse=True)
    
    st.write(f"### Aaj {target_shift} ke liye Supreme Numbers")
    
    # Categorizing based on top calculated weights
    st.success(f"🔥 **Super VIP (Maximum Probability):** Andar [{sorted_andar[0][0]}] | Bahar [{sorted_bahar[0][0]}]")
    
    st.info(f"⭐ **VIP (Strong Match):** Andar [{sorted_andar[1][0]}, {sorted_andar[2][0]}] | Bahar [{sorted_bahar[1][0]}, {sorted_bahar[2][0]}]")
    
    st.warning(f"✔️ **Normal (Cross-Verified Support):** Andar [{sorted_andar[3][0]}, {sorted_andar[4][0]}] | Bahar [{sorted_bahar[3][0]}, {sorted_bahar[4][0]}]")
    
