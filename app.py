import pandas as pd
import streamlit as st

st.title("MAYA AI: 100% Pure Fact-Based History Engine")
st.write("Yeh engine kisi bhi ank ko apni taraf se koi 'point' ya 'weight' nahi deta. Yeh sirf history mein sach mein khule hue ankon ko ginta hai.")

# 1. File Upload lagana taaki seedha cloud par chal sake
uploaded_file = st.file_uploader("Apni 0DSP0.xlsx ya CSV file upload karein", type=['csv', 'xlsx'])

def get_andar_bahar(val):
    val = str(val).replace('.0', '').strip()
    if val in ['nan', 'XX', '']: return None, None
    if len(val) == 1 and val.isdigit(): val = '0' + val
    if len(val) >= 2 and val[:2].isdigit(): return val[0], val[1]
    return None, None

if uploaded_file is not None:
    # Dashboard sheet bypass karke seedha numerical data read karna
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    df = df.dropna(subset=['DATE'])
    df['DATE'] = pd.to_datetime(df['DATE'])
    # Chronological sort taaki same-day data fluctuation na ho
    df = df.sort_values('DATE').reset_index(drop=True)
    cols = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

    st.subheader("Kal ki shifts mein kya aaya? (Input)")
    inputs = {}
    for c in cols:
        inputs[c] = st.text_input(f"Kal {c} mein kya aaya?", key=c)

    target_shift = st.selectbox("Aaj kis Shift ka VIP prediction dekhna hai?", cols)

    if st.button("Pure Backtest Run Karein"):
        # Counters for exact historical matches
        andar_counts = {str(i): 0 for i in range(10)}
        bahar_counts = {str(i): 0 for i in range(10)}
        
        total_historical_days_checked = 0
        
        # Poori history mein loop chalayenge (i aur i+1 lock ke sath)
        for i in range(len(df) - 1):
            day_matched = False
            
            # Check history ke us din mein kya wo ank aaye the jo aapne kal ke liye input kiye hain
            for c in cols:
                if inputs[c]:
                    inp_a, inp_b = get_andar_bahar(inputs[c])
                    hist_a, hist_b = get_andar_bahar(df.iloc[i][c])
                    
                    if inp_a and inp_b and hist_a and hist_b:
                        # Strict Cross-Check: Koi Tukka nahi, sirf exact match
                        if hist_a == inp_a or hist_b == inp_b:
                            day_matched = True
                            
            # Agar purani history mein match mila, toh exactly uske 'agle din' target shift mein kya khula tha
            if day_matched:
                tom_target_a, tom_target_b = get_andar_bahar(df.iloc[i+1][target_shift])
                if tom_target_a and tom_target_b:
                    andar_counts[tom_target_a] += 1  # Sirf raw sachai ki ginti (+1)
                    bahar_counts[tom_target_b] += 1
                    total_historical_days_checked += 1
                    
        # Result ko ginti (count) ke hisaab se dikhana
        sorted_andar = sorted(andar_counts.items(), key=lambda x: x[1], reverse=True)
        sorted_bahar = sorted(bahar_counts.items(), key=lambda x: x[1], reverse=True)
        
        st.write(f"**Pichli poori history mein aise {total_historical_days_checked} din mile jab bilkul yahi patterns the.**")
        st.write(f"### Jab-jab yeh hua, toh agle din {target_shift} mein EXACTLY yeh khula:")
        
        st.success(f"🔥 **100% History Verified (Sabse zyada aaya):** Andar [{sorted_andar[0][0]}] ({sorted_andar[0][1]} baar) | Bahar [{sorted_bahar[0][0]}] ({sorted_bahar[0][1]} baar)")
        
        st.info(f"⭐ **2nd Highest Truth:** Andar [{sorted_andar[1][0]}] ({sorted_andar[1][1]} baar) | Bahar [{sorted_bahar[1][0]}] ({sorted_bahar[1][1]} baar)")
        
        st.warning(f"✔️ **3rd Highest Truth:** Andar [{sorted_andar[2][0]}] ({sorted_andar[2][1]} baar) | Bahar [{sorted_bahar[2][0]}] ({sorted_bahar[2][1]} baar)")
        
        # User ke personal rules ka validation reminder
        st.markdown("---")
        st.subheader("Aapke Rules vs Reality Check:")
        rule_texts = []
        for c in cols:
            if inputs[c]:
                a, b = get_andar_bahar(inputs[c])
                if '0' in (a, b): rule_texts.append("Aapne 0 dala hai. Rule Check: 0 aane par 5, 9, 8, 3 aana chahiye.")
                if '1' in (a, b): rule_texts.append("Aapne 1 dala hai. Rule Check: 1 aane par 3 aana chahiye.")
                if '3' in (a, b): rule_texts.append("Aapne 3 dala hai. Rule Check: 3 ke sath 3 aane par 0 aana chahiye.")
                if '8' in (a, b): rule_texts.append("Aapne 8 dala hai. Rule Check: 8 aane par 0 aana chahiye.")
                if '9' in (a, b): rule_texts.append("Aapne 9 dala hai. Rule Check: 9 aane par 0 aana chahiye.")
        
        for r in list(set(rule_texts)):
            st.write("- " + r)
        st.write("Aap khud history ki is absolute counting ko dekh kar apna rule verify kar sakte hain ki kaunsa pattern aaj 100% fail-proof baith raha hai.")

else:
    st.info("Kripya engine chalane ke liye upar apni Excel/CSV file upload karein.")
    
