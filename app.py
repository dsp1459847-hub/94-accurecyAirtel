import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")
st.title("MAYA AI: Explicit Rule-Based Master Engine")
st.write("Yeh engine aapke diye gaye 0-9 Rules aur Pichli History ko aapas mein cross-verify karke 100% factual combinations banata hai.")

# ---------------------------------------------------------
# 1. AAPKA RULE BOOK (Hardcoded Facts, No Guessing)
# ---------------------------------------------------------
USER_RULES = {
    '0': ['8', '6', '7', '9', '3'],
    '1': ['8', '4', '5', '7', '0'],
    '2': ['9', '6', '5', '1', '4'],
    '3': ['9', '6', '7', '2', '0'],
    '4': ['3', '0', '1', '9', '8'],
    '5': ['2', '1', '9', '3', '6'],
    '6': ['0', '2', '9', '4', '5'],
    '7': ['1', '0', '5', '7', '4'],
    '8': ['4', '1', '3', '0', '7'],
    '9': ['9', '3', '8', '5', '7']
}

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

    st.subheader("📅 Tareekh Chunein")
    max_date = df['DATE'].max().to_pydatetime()
    min_date = df['DATE'].min().to_pydatetime()
    
    selected_date = st.date_input("Jis din ka data check karna hai:", 
                                  value=max_date, min_value=min_date, max_value=max_date)
    sel_date_pd = pd.to_datetime(selected_date)

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

    if st.button("Run Exact Rule + History Combination"):
        andar_counts = {str(i): 0 for i in range(10)}
        bahar_counts = {str(i): 0 for i in range(10)}
        
        input_digits_pool = set()
        
        # 1. Aaj ke aaye hue ankon ka pool nikalna
        for c in cols:
            if inputs[c]:
                a, b = get_andar_bahar(inputs[c])
                if a: input_digits_pool.add(a)
                if b: input_digits_pool.add(b)
                
        # 2. RULE ENGINE: Aaj ke ankon ke hisab se kal kya aana chahiye (Aapka Rule)
        rule_expected_targets = set()
        for d in input_digits_pool:
            if d in USER_RULES:
                rule_expected_targets.update(USER_RULES[d])

        total_history_events_matched = 0

        # 3. HISTORY SCAN: Pichli history mein jab yeh ank aaye, toh sach mein kya khula?
        for i in range(len(df) - 1):
            day_has_match = False
            
            for c in cols:
                if not inputs[c]: continue
                inp_a, inp_b = get_andar_bahar(inputs[c])
                hist_a, hist_b = get_andar_bahar(df.iloc[i][c])
                
                # Agar input ka exact Andar ya Bahar kisi shift se match hota hai
                if (inp_a and hist_a == inp_a) or (inp_b and hist_b == inp_b):
                    day_has_match = True

            if day_has_match:
                tom_a, tom_b = get_andar_bahar(df.iloc[i+1][target_shift])
                if tom_a and tom_b:
                    andar_counts[tom_a] += 1
                    bahar_counts[tom_b] += 1
                    total_history_events_matched += 1
                    
        # History Counts ko sort karna
        res_a = sorted(andar_counts.items(), key=lambda x: x[1], reverse=True)
        res_b = sorted(bahar_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 4. CROSS-CHECK COMBINATION: History aur Rule ko mila kar filter karna
        super_vip_andar = [x for x in res_a if x[0] in rule_expected_targets and x[1] > 0]
        normal_andar = [x for x in res_a if x[0] not in rule_expected_targets and x[1] > 0]
        
        super_vip_bahar = [x for x in res_b if x[0] in rule_expected_targets and x[1] > 0]
        normal_bahar = [x for x in res_b if x[0] not in rule_expected_targets and x[1] > 0]
        
        st.write(f"---")
        st.info(f"💡 **RULE VERIFICATION:** Aapke Input ({', '.join(input_digits_pool)}) ke hisaab se kal yeh ank aane chahiye: **{', '.join(rule_expected_targets)}**")
        st.info(f"📊 **HISTORY VERIFICATION:** Pichli history mein in ankon ne **{total_history_events_matched}** baar target shift par asar dala hai.")
        
        st.markdown("### 🔥 Final Crossed Combinations (Rule + Fact)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("🎯 **SUPER VIP ANDAR** (Rule me bhi paas + History me bhi paas)")
            for val, count in super_vip_andar[:3]:
                st.write(f"**[{val}]** - (History mein {count} baar aaya)")
            
            st.warning("✔️ **Normal Andar** (Sirf History me aaya, par aapke Rule me nahi)")
            for val, count in normal_andar[:2]:
                st.write(f"[{val}] - ({count} baar)")
                
        with col2:
            st.success("🎯 **SUPER VIP BAHAR** (Rule me bhi paas + History me bhi paas)")
            for val, count in super_vip_bahar[:3]:
                st.write(f"**[{val}]** - (History mein {count} baar aaya)")
                
