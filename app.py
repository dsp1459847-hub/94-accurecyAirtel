import pandas as pd
import streamlit as st
from datetime import datetime
import numpy as np

st.title("🔥 Supreme Platinum v2.0 - Date & Shift Selector")

# FILE UPLOAD
uploaded_file = st.file_uploader("Upload Excel", type=['xlsx'])
df = None

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ Loaded {len(df)} rows")

# 🔥 DATE & SHIFT SELECTOR
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Predict For Date")
    # Date dropdown
    dates = df['DATE'].dropna().unique() if 'DATE' in df.columns else []
    selected_date = st.selectbox("Select Date", dates[-10:] if len(dates)>0 else ["No Dates"])

with col2:
    st.subheader("🎯 Target Shift")
    shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']
    available_shifts = [s for s in shifts if s in df.columns]
    target_shift = st.selectbox("Select Shift", available_shifts)

# 🔥 SUPREME EXTRACT
def extract_andar_bahar(number):
    try:
        if pd.isna(number) or str(number).upper() in ['XX', 'NAN', '']:
            return None
        num = int(float(str(number)))
        return f"{num:02d}"
    except:
        return None

# 🔥 ULTIMATE PREDICTOR
def supreme_predict(df, target_shift, selected_date=None):
    scores = {f"{i:02d}": 0.0 for i in range(100)}
    
    if len(df) < 10:
        return list(scores.items())[:5]
    
    # Filter by date if selected
    predict_df = df.tail(50).copy()
    if selected_date and 'DATE' in df.columns:
        predict_df = predict_df[predict_df['DATE'].astype(str).str.contains(selected_date, na=False)]
    
    for i in range(len(predict_df)-2):
        try:
            row = predict_df.iloc[i]
            next_row = predict_df.iloc[i+1]
            
            target_val = next_row.get(target_shift, np.nan)
            if pd.isna(target_val):
                continue
                
            next_pred = extract_andar_bahar(target_val)
            if next_pred:
                weight = 1.0 + (49-i)*0.05  # Recency
                scores[next_pred] += weight
                
        except:
            continue
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:7]

# 🔥 MAIN PREDICTION
if df is not None:
    col1, col2 = st.columns([2,1])
    
    with col1:
        if st.button("🚀 GENERATE SUPREME PREDICTIONS 👑", use_container_width=True):
            top7 = supreme_predict(df, target_shift, selected_date)
            
            st.markdown("## 🎯 SUPREME PREDICTIONS")
            st.markdown(f"**📅 Date:** {selected_date or 'Latest'} | **🎯 Shift:** {target_shift}")
            
            for i, (pred, score) in enumerate(top7, 1):
                st.markdown(f"""
                **{i}. {pred}** 💎 *(Score: {score:.1f})*
                """)
    
    with col2:
        if st.button("📊 Excel Download"):
            top7 = supreme_predict(df, target_shift, selected_date)
            csv = f"Date,Shift,PREDICTION,SCORE\
{selected_date or 'Latest'},{target_shift},,,\
"
            for pred, score in top7:
                csv += f",,{pred},{score:.1f}\
"
            st.download_button("⬇️ Download", csv, f"{selected_date}_{target_shift}_predictions.csv")

# 🔥 QUICK PREVIEW
if df is not None:
    st.markdown("---")
    st.subheader("📋 Latest Data Preview")
    preview_cols = ['DATE', 'DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']
    preview_cols = [c for c in preview_cols if c in df.columns]
    st.dataframe(df[preview_cols].tail(5), use_container_width=True)
