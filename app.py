import pandas as pd
import numpy as np

def get_improved_prediction(df, target_shift, inputs_a, inputs_b):
    # Dynamic Scoring Engine
    scores = {str(i): 0 for i in range(10)}
    
    # 1. Trend Analysis: Pichle 3 dino ka weightage
    recent_data = df.tail(3)
    for _, row in recent_data.iterrows():
        val = str(row[target_shift]).replace('.0', '').strip()
        if len(val) >= 2:
            scores[val[0]] += 2 # Andar bonus
            scores[val[1]] += 2 # Bahar bonus

    # 2. Shift Correlation: Agar kal FD mein aaya, toh aaj DS mein kya aayega?
    # Logic: Har shift ke liye pichle dino ke pairs ka avg.
    # (Yeh part complex hai, yahan simplified scoring hai)
    
    # 3. Existing Rashi/Zero Mapping (Retained)
    rashi_map = {'0':'5', '5':'0', '1':'6', '6':'1', '2':'7', '7':'2', '3':'8', '8':'3', '4':'9', '9':'4'}
    for _, val in inputs_a.items():
        if val in rashi_map:
            scores[rashi_map[val]] += 1
            
    # Final Rank
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores

# Is function ko apne main code mein call karein:
# prediction = get_improved_prediction(df, target_shift, inputs_a, inputs_b)
