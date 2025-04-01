import json
from src.config import constants as CONST
def parse_criteria(text):
    lines = text.strip().split("\n")
    criteria_list = []
    current_criterion = None
    
    for line in lines:
        if line.startswith("\t"):  # Subcriteria
            description, weight = line.strip().rsplit(", ", 1)
            subcriterion = {
                "description": description,
                "weight": float(weight),
                "score": 0.0
            }
            if current_criterion:
                current_criterion["subcriteria"].append(subcriterion)
        else:  # Main criteria
            if current_criterion:
                criteria_list.append(current_criterion)
            description, weight = line.rsplit(", ", 1)
            current_criterion = {
                "description": description,
                "weight": float(weight),
                "calculated_score": 0.0,
                "subcriteria": []
            }
    
    if current_criterion:
        criteria_list.append(current_criterion)
    
    result = {
        "criteria": criteria_list,
        "criteria_scores": [],
        "subcriteria_scores": [],
        "final_score": 0.0
    }
    
    return result

def main():
    input_filename = "criteria.txt"
    output_filename = "X.json"
    
    with open(input_filename, "r", encoding="utf-8") as f:
        input_text = f.read()
    
    json_output = parse_criteria(input_text)
    
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2)

if __name__ == "__main__":
    main()