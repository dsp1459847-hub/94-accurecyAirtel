import pandas as pd
import streamlit as st
from datetime import timedelta

st.set_page_config(layout="wide")
st.title("MAYA AI: Instant Result Engine")
st.write("Ab koi input box ya button nahi. Tareekh chunein aur sidha VIP number aur Parikshan result dekhein.")

# ---------------------------------------------------------
# 1. AAPKA RULE BOOK 
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

    # --- DATE & SHIFT SELECTION ---
    col_date, col_shift = st.columns(2)
    max_date = df['DATE'].max().to_pydatetime()
    min_date = df['DATE'].min().to_pydatetime()
    
    with col_date:
        selected_date = st.date_input("📅 Jis din ka data INPUT manna hai (Kal):", 
                                      value=max_date - timedelta(days=1), min_value=min_date, max_value=max_date)
    with col_shift:
        target_shift = st.selectbox("🎯 Aaj kis Shift ka VIP prediction dekhna hai?", cols)

    sel_date_pd = pd.to_datetime(selected_date)
    parikshan_date_pd = sel_date_pd + pd.Timedelta(days=1)

    # --- AUTO-FETCH DATA (NO INPUT BOXES) ---
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

    # UI mein fetched data ko simply text (table) ki tarah dikhana, box ki tarah nahi
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**📥 Input Data ({sel_date_pd.strftime('%d-%m-%Y')}):**")
        st.write(" | ".join([f"{c}: {inputs.get(c, '-')}" for c in cols]))
    with c2:
        st.markdown(f"**🎯 Parikshan Data ({parikshan_date_pd.strftime('%d-%m-%Y')}):**")
        st.write(" | ".join([f"{c}: {actual_parikshan_results.get(c, '-')}" for c in cols]))

    st.markdown("---")

    # --- INSTANT ENGINE CALCULATION (NO BUTTON NEEDED) ---
    if day_data.empty:
        st.error("Sheet mein is Input date ka data nahi hai.")
    else:
        with st.spinner("MAYA AI History scan kar rahi hai..."):
            andar_counts = {str(i): 0 for i in range(10)}
            bahar_counts = {str(i): 0 for i in range(10)}
            
            input_digits_pool = set()
            for c in cols:
                if inputs.get(c):
                    a, b = get_andar_bahar(inputs[c])
                    if a: input_digits_pool.add(a)
                    if b: input_digits_pool.add(b)
                    
            rule_expected_targets = set()
            for d in input_digits_pool:
                if d in USER_RULES:
                    rule_expected_targets.update(USER_RULES[d])

            total_history_events_matched = 0

            for i in range(len(df) - 1):
                if df.iloc[i]['DATE'] >= sel_date_pd: continue
                
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
                        andar_counts[tom_a] += 1
                        bahar_counts[tom_b] += 1
                        total_history_events_matched += 1
                        
            res_a = sorted(andar_counts.items(), key=lambda x: x[1], reverse=True)
            res_b = sorted(bahar_counts.items(), key=lambda x: x[1], reverse=True)
            
            super_vip_andar = [x for x in res_a if x[0] in rule_expected_targets and x[1] > 0]
            normal_andar = [x for x in res_a if x[0] not in rule_expected_targets and x[1] > 0]
            
            super_vip_bahar = [x for x in res_b if x[0] in rule_expected_targets and x[1] > 0]
            normal_bahar = [x for x in res_b if x[0] not in rule_expected_targets and x[1] > 0]
            
            st.info(f"💡 **RULE CHECK:** Aapke Rule ke hisaab se kal yeh ank aane chahiye: **{', '.join(rule_expected_targets)}**")
            
            actual_str = actual_parikshan_results.get(target_shift, "")
            act_a, act_b = get_andar_bahar(actual_str)
            if actual_str:
                st.error(f"🎯 **ACTUAL PARIKSHAN RESULT ({target_shift}):** {actual_str}")
            else:
                st.warning(f"🎯 **ACTUAL PARIKSHAN RESULT ({target_shift}):** (Abhi data sheet me update nahi hua hai)")
            
            # Final Results Display
            col1, col2 = st.columns(2)
            with col1:
                st.success("🎯 **SUPER VIP ANDAR** (Rule + History)")
                for val, count in super_vip_andar[:3]:
                    is_hit = "✅ PASS" if val == act_a else ""
                    st.write(f"**[{val}]** - (History mein {count} baar) {is_hit}")
                
                st.warning("✔️ **Normal Andar**")
                for val, count in normal_andar[:2]:
                    is_hit = "✅ PASS" if val == act_a else ""
                    st.write(f"[{val}] - ({count} baar) {is_hit}")
                    
            with col2:
                st.success("🎯 **SUPER VIP BAHAR** (Rule + History)")
                for val, count in super_vip_bahar[:3]:
                    is_hit = "✅ PASS" if val == act_b else ""
                    st.write(f"**[{val}]** - (History mein {count} baar) {is_hit}")
                    
                st.warning("✔️ **Normal Bahar**")
                for val, count in normal_bahar[:2]:
                    is_hit = "✅ PASS" if val == act_b else ""
                    st.write(f"[{val}] - ({count} baar) {is_hit}")

    # --- 11-DAY HISTORY TABS PLACED AT THE BOTTOM ---
    st.markdown("---")
    st.subheader(f"📚 3-Way History Data ({parikshan_date_pd.strftime('%d-%m-%Y')} tak)")
    
    df_seq = df[df['DATE'] <= parikshan_date_pd].tail(11).copy()
    target_weekday = parikshan_date_pd.weekday()
    df_war = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.weekday == target_weekday)].tail(11).copy()
    target_day = parikshan_date_pd.day
    df_tarikh = df[(df['DATE'] <= parikshan_date_pd) & (df['DATE'].dt.day == target_day)].tail(11).copy()

    for d in [df_seq, df_war, df_tarikh]:
        d['DATE'] = d['DATE'].dt.strftime('%d-%m-%Y')

    tab1, tab2, tab3 = st.tabs(["1️⃣ Lagaatar (Seq) 11 Din", "2️⃣ War (Day) 11 Din", "3️⃣ Tareekh (Date) 11 Din"])
    with tab1: st.dataframe(df_seq[['DATE'] + cols].reset_index(drop=True), use_container_width=True)
    with tab2: st.dataframe(df_war[['DATE'] + cols].reset_index(drop=True), use_container_width=True)
    with tab3: st.dataframe(df_tarikh[['DATE'] + cols].reset_index(drop=True), use_container_width=True)

else:
    st.info("Kripya engine chalane ke liye 0DSP0 sheet upload karein.")
    
