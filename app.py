import pandas as pd
import streamlit as st
import numpy as np

st.title("🔥 Supreme Platinum v4.1 - ±1 Year Dates (FIXED!)")

uploaded_file = st.file_uploader("Upload Excel", type=['xlsx'])
df = None

if uploaded_file:
    df = pd.read_excel(uploaded_file)  # FIXED: uploaded_file → uploaded_file
    st.success(f"✅ {len(df)} rows loaded")

if df is not None:
    
    # 🔥 1 YEAR RANGE SELECTOR (FIXED)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        base_date = st.selectbox("📅 Base Date", df['DATE'].dropna().tail(30).tolist())
    
    with col2:
        months_before = st.slider("⏪ Months Before", 0, 12, 3)
    
    with col3:
        months_after = st.slider("⏩ Months After", 0, 12, 3)
    
    # 🔥 DATE INDEXING (IMPROVED)
    df['DATE'] = df['DATE'].astype(str)
    base_mask = df['DATE'].str.contains(base_date[:8], na=False)  # MMDDYYYY match
    
    if base_mask.any():
        base_idx = df[base_mask].index[0]
        before_rows = int(months_before * 30)
        after_rows = int(months_after * 30)
        
        start_idx = max(0, base_idx - before_rows)
        end_idx = min(len(df), base_idx + after_rows + 1)
        
        range_df = df.iloc[start_idx:end_idx].copy()
        st.info(f"📊 **{months_before}M before + {months_after}M after** = {len(range_df)} rows")
    else:
        range_df = df.tail(90)
        st.warning("⚠️ Base date not exact, using last 90 days")
    
    # SHIFT SELECT
    target_shift = st.selectbox("🎯 Shift", ['DS','FD','GD','GL','DB','SG','ZA'])
    
    # 🔥 SUPREME PREDICTION ALGO
    def supreme_predict(data, shift):
        scores = {}
        for i in range(len(data)-2):
            try:
                val1 = pd.to_numeric(data.iloc[i][shift], errors='coerce')
                val2 = pd.to_numeric(data.iloc[i+1][shift], errors='coerce')
                val3 = pd.to_numeric(data.iloc[i+2][shift], errors='coerce')
                
                if all(pd.notna([val1, val2, val3])):
                    pred = f"{int(val3):02d}"
                    scores[pred] = scores.get(pred, 0) + 1.0
            except:
                continue
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:12]
    
    # 🔥 PREDICT BUTTON
    if st.button(f"🚀 PREDICT {target_shift} (±1 YEAR)", use_container_width=True):
        predictions = supreme_predict(range_df, target_shift)
        
        st.markdown("## 🎯 **1 YEAR RANGE PREDICTIONS**")
        cols = st.columns(4)
        for i, (pred, score) in enumerate(predictions):
            with cols[i%4]:
                st.metric(f"#{i+1}", pred, f"{score:.0f}x")
        
        # FIXED CSV LINE (PROPER STRING)
        top3 = [p[0] for p in predictions[:3]]
        csv_line = f'"{base_date}","{target_shift}","{"","".join(top3)}"'
        st.code(csv_line)
    
    # 🔥 DOWNLOAD (IMPROVED)
    if st.button("💾 Download 1-Year CSV"):
        predictions = supreme_predict(range_df, target_shift)
        csv_content = f"Date,Shift,Pred1,Pred2,Pred3,Pred4,Pred5,Pred6,Pred7,Pred8,Pred9,Pred10
"
        csv_content += f'"{base_date}","{target_shift}","{"","".join([p[0] for p in predictions[:10]])}"
'
        
        st.download_button(
            label="📥 Download CSV", 
            data=csv_content, 
            file_name=f"1year_{base_date}_{target_shift}.csv",
            mime="text/csv"
        )

# 📊 DATA PREVIEW
if df is not None:
    st.dataframe(df[['DATE','DB']].tail(5))
else:
    st.info("📤 Upload 0DSP0.xlsx to start!")
