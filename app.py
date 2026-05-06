import pandas as pd
import streamlit as st

# Data ko load karna
df = pd.read_csv('0DSP0.xlsx - Sheet1.csv')

# Sirf numerical columns ko select karna (DS, FD, GD, GL etc.)
cols = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']

def get_next_day_patterns(df, columns):
    # Ek dictionary jisme har number (0-9) ke agle din aane wale numbers ka record hoga
    history_dict = {str(i): [] for i in range(10)}
    
    for i in range(len(df) - 1):
        today_row = df.iloc[i][columns].dropna().astype(str)
        tomorrow_row = df.iloc[i + 1][columns].dropna().astype(str)
        
        # Aaj ke numbers ke digits nikalna
        today_digits = set()
        for val in today_row:
            if val != 'XX': # Blank ya invalid entries ko hatana
                today_digits.update(list(val))
                
        # Kal ke numbers ke digits nikalna
        tomorrow_digits = set()
        for val in tomorrow_row:
            if val != 'XX':
                tomorrow_digits.update(list(val))
                
        # Pattern map karna: Aaj agar '0' aaya hai, toh kal kya kya aaya?
        for digit in today_digits:
            if digit.isdigit():
                history_dict[digit].extend(list(tomorrow_digits))
                
    return history_dict

# Backtesting Run
pattern_history = get_next_day_patterns(df, cols)

# Result ko frequency ke hisaab se dikhana
st.write("### 0 se 9 tak ke anko ki Backtesting History")
for ank in range(10):
    ank_str = str(ank)
    if pattern_history[ank_str]:
        # Har ank ke agle din aane wale numbers ko count karna
        counts = pd.Series(pattern_history[ank_str]).value_counts()
        st.write(f"**Jab {ank_str} aata hai, toh agle din sabse zyada yeh aate hain:**")
        st.write(counts.head(5)) # Top 5 possible aane wale ank
        
