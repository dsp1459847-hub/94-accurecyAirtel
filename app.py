import pandas as pd
import streamlit as st
import numpy as np

st.title("🔥 Supreme Platinum v3.0 - PERFECT")

# FILE UPLOAD
uploaded_file = st.file_uploader("Upload Excel", type=['xlsx'])
df = None

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"✅ Loaded {len(df)} rows")
    except:
        st.error("File error")
        df = None

# CONTROLS - ONLY IF FILE
if df is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        selected_date = st.selectbox("📅 Date", ["LATEST"] + df['DATE'].dropna().astype(str).tail(10).tolist())
    
    with col2:
        shifts = ['DS','FD','GD','GL','DB','SG','ZA']
        target_shift = st.selectbox("🎯 Shift", [s for s in shifts if s in df.columns])

    # SUPREME PREDICT
    def supreme_predict(df, target_shift):
        scores = {f"{i:02d}": 0.0 for i in range(100)}
        recent = df.tail(30).copy()
        
        for i in range(len(recent)-1):
            try:
                next_val = recent.iloc[i+1][target_shift]
                if pd.notna(next_val):
                    pred = f"{int(float(str(next_val))):02d}"
                    scores[pred] += 1 + (29-i)*0.03
            except:
                pass
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:8]

    # BIG BUTTON
    if st.button(f"🚀 PREDICT {target_shift}", use_container_width=True):
        top8 = supreme_predict(df, target_shift)
        
        st.markdown(f"## 🎯 {target_shift} PREDICTIONS")
        for i, (pred, score) in enumerate(top8, 1):
            st.write(f"**{i}. {pred}** - Score: {score:.1f}")

    # CSV
    if st.button("📥 CSV Download"):
        top8 = supreme_predict(df, target_shift)
        csv = "Rank,Pred,Score\
"
        for i, (pred, score) in enumerate(top8, 1):
            csv += f"{i},{pred},{score:.1f}\
"
        st.download_button("Download", csv, f"{target_shift}_pred.csv")

# PREVIEW
if df is not None:
    st.dataframe(df[['DATE','DS','FD','DB']].tail(3))
