import pandas as pd
import streamlit as st
import numpy as np

st.title("🔥 Supreme Platinum v4.0 - ±1 Year Dates")

uploaded_file = st.file_uploader("Upload Excel", type=['xlsx'])
df = None

if uploaded_file:
    df = pd.read_excel(uploadfile)
    st.success(f"✅ {len(df)} rows loaded")

if df is not None:
    
    # 🔥 1 YEAR RANGE SELECTOR
    col1, col2, col3 = st.columns(3)
    
    with col1:
        base_date = st.selectbox("📅 Base Date", df['DATE'].dropna().tail(30).tolist())
    
    with col2:
        months_before = st.slider("⏪ Months Before", 0, 12, 3)
    
    with col3:
        months_after = st.slider("⏩ Months After", 0, 12, 3)
    
    # 🔥 DATE TO INDEX CONVERSION
    df['DATE_NUM'] = pd.to_numeric(df['DATE'], errors='coerce')
    base_num = df[df['DATE'].astype(str).str.contains(base_date, na=False)]['DATE_NUM']
    
    if len(base_num) > 0:
        base_idx = df[df['DATE_NUM'] == base_num.iloc[0]].index[0]
        
        # 1 month ~ 30 rows approx
        before_rows = int(months_before * 30)
        after_rows = int(months_after * 30)
        
        start_idx = max(0, base_idx - before_rows)
        end_idx = min(len(df), base_idx + after_rows + 1)
        
        range_df = df.iloc[start_idx:end_idx]
        st.info(f"📊 **{months_before}M before + {months_after}M after** = {len(range_df)} rows")
    
    else:
        range_df = df.tail(90)
        st.warning("Base date not found, using last 90 days")
    
    # SHIFT
    target_shift = st.selectbox("🎯 Shift", ['DS','FD','GD','GL','DB','SG','ZA'])
    
    # 🔥 SUPREME PREDICTION
    def supreme_predict(data, shift):
        scores = {}
        for i in range(len(data)-2):
            try:
                val1 = data.iloc[i][shift]
                val2 = data.iloc[i+1][shift]
                val3 = data.iloc[i+2][shift]
                
                if all(pd.notna([val1, val2, val3])):
                    pred = f"{int(val3):02d}"
                    scores[pred] = scores.get(pred, 0) + 1.0
            except:
                pass
        
        top_preds = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:12]
        return top_preds
    
    # BUTTON
    if st.button(f"🚀 PREDICT {target_shift} (±1 YEAR)", use_container_width=True):
        predictions = supreme_predict(range_df, target_shift)
        
        st.markdown("## 🎯 **1 YEAR RANGE PREDICTIONS**")
        cols = st.columns(4)
        for i, (pred, score) in enumerate(predictions):
            with cols[i%4]:
                st.metric(f"#{i+1}", pred, f"{score:.0f}x")
        
        # EXCEL LINE
        top3 = [p[0] for p in predictions[:3]]
        st.code(f'"{base_date}",{target_shift},"{top3[0]}","{top3[1]}","{top3[2]}"')
    
    # DOWNLOAD
    if st.button("💾 1-Year CSV"):
        predictions = supreme_predict(range_df, target_shift)
        csv = f"Date,Shift,Pred1,Pred2,...,Pred10\
"{base_date}",{target_shift},"
        csv += '","'.join([p[0] for p in predictions[:10]]) + '"\
'
        st.download_button("Download", csv, f"1year_{base_date}_{target_shift}.csv")

# PREVIEW
st.dataframe(df[['DATE','DB']].tail(5) if df is not None else pd.DataFrame())
