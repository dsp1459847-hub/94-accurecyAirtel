import pandas as pd
import streamlit as st
import numpy as np

st.title("🔥 Supreme v4.3 - ±1 Year PERFECT")

uploaded_file = st.file_uploader("Upload Excel", type=['xlsx'])
df = None

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ {len(df)} rows loaded")

if df is not None:

    col1, col2, col3 = st.columns(3)
    
    with col1:
        base_date = st.selectbox("📅 Base Date", df['DATE'].dropna().tail(30).tolist())
    
    with col2:
        months_before = st.slider("⏪ Months Before", 0, 12, 3)
    
    with col3:
        months_after = st.slider("⏩ Months After", 0, 12, 3)
    
    df['DATE_STR'] = df['DATE'].astype(str)
    base_mask = df['DATE_STR'].str.contains(base_date[:8], na=False)
    
    if base_mask.any():
        base_idx = df[base_mask].index[0]
        before_rows = int(months_before * 30)
        after_rows = int(months_after * 30)
        
        start_idx = max(0, base_idx - before_rows)
        end_idx = min(len(df), base_idx + after_rows + 1)
        
        range_df = df.iloc[start_idx:end_idx].copy()
        st.info(f"📊 {len(range_df)} rows selected")
    else:
        range_df = df.tail(90)
        st.warning("Using last 90 rows")
    
    target_shift = st.selectbox("🎯 Shift", ['DS','FD','GD','GL','DB','SG','ZA'])
    
    def get_predictions(data, shift):
        scores = {}
        for i in range(len(data)-2):
            try:
                v1 = pd.to_numeric(data.iloc[i][shift], errors='coerce')
                v2 = pd.to_numeric(data.iloc[i+1][shift], errors='coerce')
                v3 = pd.to_numeric(data.iloc[i+2][shift], errors='coerce')
                if pd.notna(v1) and pd.notna(v2) and pd.notna(v3):
                    pred = str(int(v3)).zfill(2)
                    scores[pred] = scores.get(pred, 0) + 1
            except:
                pass
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:12]
    
    if st.button(f"🚀 PREDICT {target_shift}", use_container_width=True):
        predictions = get_predictions(range_df, target_shift)
        
        st.markdown("## 🎯 PREDICTIONS")
        cols = st.columns(4)
        for i, (pred, score) in enumerate(predictions):
            with cols[i % 4]:
                st.metric(f"#{i+1}", pred, f"{score}x")
        
        top3 = [p[0] for p in predictions[:3]]
        excel_line = '"' + str(base_date) + '","' + target_shift + '","' + '","'.join(top3) + '"'
        st.code(excel_line)
    
    if st.button("💾 CSV Download"):
        predictions = get_predictions(range_df, target_shift)
        top10 = [p[0] for p in predictions[:10]]
        
        csv_header = 'Date,Shift,Pred1,Pred2,Pred3,Pred4,Pred5,Pred6,Pred7,Pred8,Pred9,Pred10'
        csv_line = '"' + str(base_date) + '","' + target_shift + '","' + '","'.join(top10) + '"'
        csv_data = csv_header + '
' + csv_line
        
        st.download_button(
            "📥 Download", 
            data=csv_data,
            file_name=f"predictions_{target_shift}.csv",
            mime="text/csv"
        )

st.dataframe(df[['DATE','DB']].tail(5) if df is not None else pd.DataFrame())
