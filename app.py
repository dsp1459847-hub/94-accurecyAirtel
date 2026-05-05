import pandas as pd
import streamlit as st

st.title("Supreme Platinum Engine: Advanced Master Forecaster")

# 1. File Uploader lagana taaki file cloud par na dhoondhni pade
uploaded_file = st.file_uploader("Apni Excel/CSV (0DSP0) file yahan upload karein", type=['csv', 'xlsx'])

# Rashi & Family Map
rashi_map = {'0':'5', '5':'0', '1':'6', '6':'1', '2':'7', '7':'2', '3':'8', '8':'3', '4':'9', '9':'4'}

def extract_andar_bahar(val):
    val = str(val).replace('.0', '').strip()
    if val == 'nan' or val == 'XX' or val == '': return None, None
    if len(val) == 1 and val.isdigit(): val = '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
    return None, None

# Agar user ne file upload kar di hai, tabhi aage ka code chalega
if uploaded_file is not None:
    @st.cache_data
    def load_data(file):
        # Agar excel upload ki hai ya csv, dono handle ho jayenge
        try:
            df = pd.read_csv(file)
        except:
            df = pd.read_excel(file)
            
        df = df.dropna(subset=['DATE'])
        df['DATE'] = pd.to_datetime(df['DATE'])
        df = df.sort_values('DATE').reset_index(drop=True)
        return df

    df = load_data(uploaded_file)
    cols = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

    st.subheader("Kal ki sabhi shifts ka Numerical Data")
    inputs_a = {}
    inputs_b = {}
    overall_input_pool = set()

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
        
        for i in range(len(df) - 1):
            match_score = 0
            hist_overall_pool = set()
            
            for c in cols:
                # Dhyan rahe dashboard sheets check nahi honi chahiye, sirf numerical calculations
                hist_a, hist_b = extract_andar_bahar(df.iloc[i][c])
                inp_a, inp_b = inputs_a[c], inputs_b[c]
                
                if hist_a: hist_overall_pool.add(hist_a)
                if hist_b: hist_overall_pool.add(hist_b)
                
                if inp_a and inp_b and hist_
                
