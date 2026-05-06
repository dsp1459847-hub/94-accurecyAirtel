import pandas as pd
import streamlit as st
from datetime import timedelta

st.set_page_config(layout="wide")
st.title("MAYA AI: Direct Ank (Jodi) Generator & Parso-Kal Logic")
st.write("Yeh engine 'Kal' aur 'Parso' dono dino ke Plus/Minus gap ko analyze karke seedha VIP Ank (Jodi) banata hai. Sirf PASS hone par Hara (Green) rang dikhayega.")

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
        selected_date = st.date_input("📅 Jis din ko INPUT (Kal) manna hai:", 
                                      value=max_date - timedelta(days=1), min_value=min_date, max_value=max_date)
    with col_shift:
        target_shift = st.selectbox("🎯 Aaj kis Shift ka Ank (Jodi) nikalna hai?", cols)

    sel_date_pd = pd.to_datetime(selected_date)
    
    # Ensure selected date exists in our dataframe
    if sel_date_pd not in df['DATE'].values:
        st.error("Sheet mein is Input date ka data nahi hai.")
    else:
        idx_kal = df[df['DATE'] == sel_date_pd].index[0]
        idx_parikshan = idx_kal + 1 if idx_kal + 1 < len(df) else None
        
        # We need at least index 2 to have Kal (T-1) and Parso (T-2)
        if idx_kal < 2:
            st.error("Parso ka data calculate karne ke liye isse purani date chahiye.")
        else:
            with st.spinner("MAYA AI Kal aur Parso ka Plus/Minus logic nikal rahi hai..."):
                
                # --- STEP 1: CALCULATE GLOBAL OFFSETS FOR THE SHIFT ---
                # Hum poori history (Target date se pehle tak) scan karke Parso aur Kal ka gap nikalenge
                offset_a1 = {i: 0 for i in range(10)} # Kal Andar se Aaj Andar
                offset_a2 = {i: 0 for i in range(10)} # Parso Andar se Aaj Andar
                offset_b1 = {i: 0 for i in range(10)} # Kal Bahar se Aaj Bahar
                offset_b2 = {i: 0 for i in range(10)} # Parso Bahar se Aaj Bahar
                
                for i in range(2, idx_kal + 1):
                    p_a, p_b = get_andar_bahar(df.iloc[i-2][target_shift]) # Parso
                    k_a, k_b = get_andar_bahar(df.iloc[i-1][target_shift]) # Kal
                    aaj_a, aaj_b = get_andar_bahar(df.iloc[i][target_shift]) # Aaj
                    
                    if p_a and k_a and aaj_a and p_b and k_b and aaj_b:
                        offset_a1[(int(aaj_a) - int(k_a)) % 10] += 1
                        offset_a2[(int(aaj_a) - int(p_a)) % 10] += 1
                        offset_b1[(int(aaj_b) - int(k_b)) % 10] += 1
                        offset_b2[(int(aaj_b) - int(p_b)) % 10] += 1

                # --- STEP 2: PREDICTION LOGIC FUNCTION ---
                # Yeh function Parso aur Kal ka input lekar direct VIP Jodis deta hai
                def predict_jodis(parso_val, kal_val):
                    p_a, p_b = get_andar_bahar(parso_val)
                    k_a, k_b = get_andar_bahar(kal_val)
                    
                    if not (p_a and k_a and p_b and k_b):
                        return [], [], []
                        
                    andar_scores = {str(i): 0 for i in range(10)}
                    bahar_scores = {str(i): 0 for i in range(10)}
                    
                    for d in range(10):
                        # Kal ko zyada weight (1.5x) aur Parso ko normal weight (1.0x)
                        req_off_a1 = (d - int(k_a)) % 10
                        req_off_a2 = (d - int(p_a)) % 10
                        andar_scores[str(d)] += (offset_a1[req_off_a1] * 1.5) + (offset_a2[req_off_a2] * 1.0)
                        
                        req_off_b1 = (d - int(k_b)) % 10
                        req_off_b2 = (d - int(p_b)) % 10
                        bahar_scores[str(d)] += (offset_b1[req_off_b1] * 1.5) + (offset_b2[req_off_b2] * 1.0)
                        
                    # Top 4 Andar aur Top 4 Bahar nikalna
                    top_a = [x[0] for x in sorted(andar_scores.items(), key=lambda x: x[1], reverse=True)[:4]]
                    top_b = [x[0] for x in sorted(bahar_scores.items(), key=lambda x: x[1], reverse=True)[:4]]
                    
                    # 16 Direct Jodis banayein (4x4)
                    jodis = [a+b for a in top_a for b in top_b]
                    return jodis, top_a, top_b

                # --- STEP 3: PREDICT FOR TODAY (PARIKSHAN) ---
                kal_actual = str(df.iloc[idx_kal][target_shift])
                parso_actual = str(df.iloc[idx_kal-1][target_shift])
                
                vip_jodis, top_andar, top_bahar = predict_jodis(parso_actual, kal_actual)
                
                parikshan_actual = ""
                parikshan_date_str = ""
                if idx_parikshan is not None:
                    parikshan_actual = str(df.iloc[idx_parikshan][target_shift]).replace('.0', '').strip()
                    if len(parikshan_actual) == 1 and parikshan_actual.isdigit(): parikshan_actual = '0' + parikshan_actual
                    parikshan_date_str = df.iloc[idx_parikshan]['DATE'].strftime('%d-%m-%Y')
                
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                with c1: st.info(f"⏪ **Parso ({df.iloc[idx_kal-1]['DATE'].strftime('%d-%m-%Y')}):** {parso_actual}")
                with c2: st.info(f"⬅️ **Kal/Input ({df.iloc[idx_kal]['DATE'].strftime('%d-%m-%Y')}):** {kal_actual}")
                with c3: st.warning(f"🎯 **Aaj/Parikshan ({parikshan_date_str}):** {parikshan_actual if parikshan_actual else 'Data Pending'}")
                st.markdown("---")

                # Display Results
                if vip_jodis:
                    st.write("### 💎 Target VIP Anks (Jodis)")
                    
                    # Agar Parikshan ka number match kar gaya to usko Hare rang me dikhana
                    if parikshan_actual in vip_jodis:
                        st.success(f"🎉 **SHANDAAR PASS!** Parikshan ka ank **[{parikshan_actual}]** hamare VIP Ankon mein direct paas ho gaya!")
                    elif parikshan_actual:
                        st.write(f"Target miss hua. Aaya: {parikshan_actual}")
                    
                    # Show the 16 Jodis in a nice grid
                    st.write(f"**Top Andar:** {', '.join(top_andar)} | **Top Bahar:** {', '.join(top_bahar)}")
                    
                    # Create HTML boxes for Jodis. If it matches parikshan_actual, make it GREEN. Else normal.
                    jodi_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>"
                    for j in vip_jodis:
                        if j == parikshan_actual:
                            jodi_html += f"<div style='background-color: #28a745; color: white; padding: 10px 20px; font-size: 20px; font-weight: bold; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>{j} ✅ PASS</div>"
                        else:
                            jodi_html += f"<div style='background-color: #f1f3f5; color: #333; padding: 10px 20px; font-size: 18px; font-weight: bold; border-radius: 8px; border: 1px solid #ccc;'>{j}</div>"
                    jodi_html += "</div>"
                    st.markdown(jodi_html, unsafe_allow_html=True)
                    
                else:
                    st.error("Input data theek nahi hai, Jodis nahi ban payin.")


                # --- 11-DAY HISTORY HTML TABLE (ONLY GREEN BOXES FOR PASS) ---
                st.markdown("---")
                st.subheader("📚 Pichle 11 Din Ka Cross-Check (Sirf Paas Hone Par Hara Dabba)")
                
                # Hum pichle 11 dino ke liye same logic lag

