import pandas as pd
import streamlit as st
import numpy as np

st.title("🔥 Supreme Platinum v2.1 - BULLETPROOF")

# 🔥 FILE UPLOAD + ERROR PROTECTION
uploaded_file = st.file_uploader("Upload Excel", type=['xlsx'])
df = None

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"✅ Loaded {len(df)} rows | Columns: {len(df.columns)}")
    except Exception as e:
        st.error("❌ File error. Try again.")
        df = None
else:
    st.info("📤 Please upload Excel file")

# 🔥 SELECTORS - ONLY IF FILE LOADED
if df is not None:
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Predict For")
        # SAFE DATE SELECTOR
        try:
            if 'DATE' in df.columns:
                dates = df['DATE'].dropna().astype(str).unique()[-10:]
                selected_date = st.selectbox("Date", ["LATEST"] + list(dates))
            else:
                selected_date = "LATEST"
        except:
            selected_date = "LATEST"
    
    with col2:
        st.subheader("🎯 Target Shift")
        shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']
        available_shifts = [s for s in shifts if s in df.columns]
        target_shift = st.selectbox("Shift", available_shifts)
    
    # 🔥 SUPREME PREDICT FUNCTION
    def supreme_predict(df, target_shift, selected_date="LATEST"):
        scores = {f"{i:02d}": 0.0 for i in range(100)}
        
        predict_df = df.tail(30).copy()  # Recent 30
        
        count = 0
        for i in range(len(predict_df)-1):
            try:
                current_row = predict_df.iloc[i]
                next_row = predict_df.iloc[i+1]
                
                # TARGET CHECK
                if target_shift not in next_row.index:
                    continue
                    
                target_val = next_row[target_shift]
                if pd.isna(target_val):
                    continue
                
                pred_num = f"{int(float(str(target_val))):02d}"
                if len(pred_num) == 2:
                    weight = 1 + (29-i)*0.03  # Recency
                    scores[pred_num] += weight
                    count += 1
                    
            except Exception:
                continue
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:8]
    
    # 🔥 BIG PREDICT BUTTON
    col1, col2 = st.columns([3,1])
    with col1:
        if st.button(f"🚀 SUPREME PREDICT {target_shift}", use_container_width=True):
            top8 = supreme_predict(df, target_shift, selected_dat
