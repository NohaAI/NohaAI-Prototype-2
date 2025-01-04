# import statements

def compute_interview_score():
    return None

def compute_turn_score(turn_assessment_payload = None):
    computed_payload = {}
    if turn_assessment_payload:
        weight_base = 0
        score_base = 0
        weight_list = []
        score_list = []
        norm_score_list = []
        for key in turn_assessment_payload.keys():
            weight_base = weight_base + turn_assessment_payload[key][0] 
            score_base = score_base + float(turn_assessment_payload[key][1]) ### need to use float function because the score is a string; why?
        for key in turn_assessment_payload.keys():
            weight = turn_assessment_payload[key][0] 
            score = float(turn_assessment_payload[key][1])
            norm_score = (weight / weight_base) * (score / 210) # added a fix score_base of 210(21*10), this could change later
            #  norm_score = (weight / weight_base) * (score / score_base) 
            weight_list.append(weight)
            score_list.append(score)
            norm_score_list.append(norm_score)
            computed_payload[key] = [weight, score, norm_score]
        print("weight_base", weight_base)
        print("score_base", score_base)
        print(weight_list)
        print(score_list)
        print(norm_score_list)
        print("\n")
        for key, values in computed_payload.items():
            print (key, values)
    else:
        print("Turn assessment payload is empty")