import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.title("🔥 Supreme Platinum - FULL DATE SELECTION")
st.markdown("---")

# File upload
uploaded_file = st.file_uploader("📁 Upload 0DSP0.xlsx", type=['xlsx', 'csv'])

if uploaded_file is not None:
    # Load data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    df.columns = df.columns.str.strip()
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('DATE').reset_index(drop=True)
    
    st.success(f"✅ Loaded {len(df)} records")
    
    cols = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']
    
    def extract_andar_bahar(val):
        val = str(val).replace('.0', '').strip()
        if val == 'nan' or val == 'XX' or val == '': return None, None
        if len(val) == 1 and val.isdigit(): val = '0' + val
        if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
        return None, None
    
    # ========== FIXED DATE SELECTION - 3 OPTIONS ==========
    st.subheader("📆 **COMPLETE DATE SELECTION**")
    
    date_option = st.radio("Choose date method:", 
                          ["1. Date Picker (All Dates)", 
                           "2. Recent 30 Days", 
                           "3. Manual Date Entry"])
    
    selected_date = None
    
    if date_option == "1. Date Picker (All Dates)":
        # FULL CALENDAR - From first date to today
        min_date = df['DATE'].min().date()
        max_date = datetime.now().date()
        selected_date = st.date_input("Select ANY date:", 
                                    value=datetime.now().date(),
                                    min_value=min_date,
                                    max_value=max_date)
    
    elif date_option == "2. Recent 30 Days":
        # Last 30 days dropdown
        available_dates = sorted(df['DATE'].dt.date.unique(), reverse=True)[:30]
        selected_date = st.selectbox("Recent dates:", available_dates)
    
    else:  # Manual entry
        selected_date = st.date_input("Enter date manually:", 
                                    value=datetime.now().date())
    
    st.success(f"✅ **Selected: {selected_date.strftime('%Y-%m-%d')}")
    
    # ========== YESTERDAY AUTO FILL ==========
    selected_date_obj = pd.to_datetime(selected_date)
    yesterday_date = selected_date_obj - timedelta(days=1)
    yesterday_row = df[df['DATE'] == yesterday_date]
    
    st.info(f"📅 **Yesterday:** {yesterday_date.strftime('%Y-%m-%d')}")
    
    # ========== INPUTS ==========
    st.subheader("📝 Yesterday Results (Auto-filled)")
    
    inputs_a, inputs_b = {}, {}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ds_val = yesterday_row.iloc[0]['DS'] if len(yesterday_row)>0 else 'XX'
        st.text_input("DS:", value=str(ds_val) if pd.notna(ds_val) else 'XX', key="ds_fix")
    with col2:
        fd_val = yesterday_row.iloc[0]['FD'] if len(yesterday_row)>0 else 'XX'
        st.text_input("FD:", value=str(fd_val) if pd.notna(fd_val) else 'XX', key="fd_fix")
    with col3:
        gd_val = yesterday_row.iloc[0]['GD'] if len(yesterday_row)>0 else 'XX'
        st.text_input("GD:", value=str(gd_val) if pd.notna(gd_val) else 'XX', key="gd_fix")
    
    col4, col5, col6 = st.columns(3)
    with col4:
        gl_val = yesterday_row.iloc[0]['GL'] if len(yesterday_row)>0 else 'XX'
        st.text_input("GL:", value=str(gl_val) if pd.notna(gl_val) else 'XX', key="gl_fix")
    with col5:
        db_val = yesterday_row.iloc[0]['DB'] if len(yesterday_row)>0 else 'XX'
        st.text_input("DB:", value=str(db_val) if pd.notna(db_val) else 'XX', key="db_fix")
    with col6:
        sg_val = yesterday_row.iloc[0]['SG'] if len(yesterday_row)>0 else 'XX'
        st.text_input("SG:", value=str(sg_val) if pd.notna(sg_val) else 'XX', key="sg_fix")
    
    # Extract inputs
    for c in cols:
        val = st.session_state.get(c.lower()+'_fix', '')
        a, b = extract_andar_bahar(val)
        inputs_a[c] = a
        inputs_b[c] = b
    
    target_shift = st.selectbox("🎯 Target Shift:", cols)
    
    # ========== GENERATE BUTTON ==========
    if st.button("🚀 **GENERATE PREDICTIONS**", type="primary"):
        # Prediction engine
        target_andar_score = {str(i): 0 for i in range(10)}
        target_bahar_score = {str(i): 0 for i in range(10)}
        
        match_count = 0
        for i in range(len(df) - 1):
            match_score = 0
            
            for c in cols:
                hist_a, hist_b = extract_andar_bahar(df.iloc[i][c])
                if inputs_a[c] and inputs_b[c] and hist_a and hist_b:
                    if inputs_a[c] == hist_a or inputs_b[c] == hist_b:
                        match_score += 3
                    elif inputs_a[c] in (hist_a, hist_b) or inputs_b[c] in (hist_a, hist_b):
                        match_score += 1
            
            if match_score > 0:
                match_count += 1
                next_a, next_b = extract_andar_bahar(df.iloc[i+1][target_shift])
                if next_a: target_andar_score[next_a] += match_score
                if next_b: target_bahar_score[next_b] += match_score
        
        # Results
        top5_andar = sorted(target_andar_score.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_bahar = sorted(target_bahar_score.items(), key=lambda x: x[1], reverse=True)[:5]
        
        st.markdown("---")
        st.markdown(f"## 🎯 **PREDICTIONS: {selected_date} - {target_shift}**")
        st.info(f"📊 Based on {match_count} matches found")
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("**🔥 ANDAR Top 5**")
            for i, (digit, score) in enumerate(top5_andar):
                st.write(f"{i+1}. **{digit}**")
        
        with col2:
            st.success("**🎲 BAHAR Top 5**")
            for i, (digit, score) in enumerate(top5_bahar):
                st.write(f"{i+1}. **{digit}**")
        
        # BACKTEST (if date exists in data)
        selected_row = df[df['DATE'].dt.date == selected_date]
        if len(selected_row) > 0:
            st.markdown("---")
            st.subheader("✅ **ACTUAL RESULT (Backtest)**")
            actual_row = selected_row.iloc[0]
            actual_a, actual_b = extract_andar_bahar(actual_row[target_shift])
            
            top5_a = [x[0] for x in top5_andar]
            top5_b = [x[0] for x in top5_bahar]
            
            st.info(f"**Actual:** Andar={actual_a}, Bahar={actual_b}")
            st.success(f"**Hit:** Andar ✅{'✅' if actual_a in top5_a else '❌'}, Bahar {'✅' if actual_b in top5_b else '❌'}")
    
    # ========== 10-DAY BACKTEST ==========
    st.subheader("📊 **LAST 10 DAYS BACKTEST**")
    if st.button("Show Last 10 Days Results"):
        recent_df = df.tail(10)
        st.write(recent_df[['DATE', 'DS', 'FD', 'GD', 'GL', 'DB', 'SG']].tail(10).to_html(), unsafe_allow_html=True)

else:
    st.warning("👆 First upload your Excel file!")
