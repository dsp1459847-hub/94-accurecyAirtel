# Yeh code aapke existing logic mein replace/add karein
def get_optimized_score(df, target_shift, inputs_a, inputs_b, window=5):
    # Dynamic weight: Pichle 5 din ke patterns ko priority dena
    scores = {str(i): 0 for i in range(10)}
    
    # Sirf pichle 5 din ka data lein (Rolling Window)
    recent_history = df.tail(window)
    
    for i in range(len(recent_history) - 1):
        match_score = 0
        # Correlation check
        for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']:
            h_a, h_b = extract_andar_bahar(recent_history.iloc[i][c])
            if inputs_a.get(c) == h_a: match_score += 3 # Recent match ko high weight
        
        if match_score > 0:
            t_a, t_b = extract_andar_bahar(recent_history.iloc[i+1][target_shift])
            if t_a: scores[t_a] += match_score
            if t_b: scores[t_b] += match_score
            
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
