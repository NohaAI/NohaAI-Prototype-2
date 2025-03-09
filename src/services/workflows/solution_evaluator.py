"""
This module implements the functionality for evaluating answers based on predefined criteria, 
including calculating scores using weighted averages, and storing results in a database.
"""

import sys, json, asyncio

print(sys.path)
from src.utils import logger, interview_computation, json_helper
from src.services.llm.prompts import answer_evaluator_prompt
from src.services.llm import llm_service
# from src.dao import subcriterion
# from src.dao import chat_history as chat_history

# Initialize logger
logger = logger.get_logger(__name__)

################################################
### RMS refactor the following evaluate_answer function based on the call from dialogue_flow, namely
###  assessment_payload, assessment_payload_rationale = await evaluate_answer(session_state['question_id'], session_state['bot_dialogue'], distilled_candidate_dialogue, distilled_chat_history, assessment_payload)


async def evaluate_answer(session_state, chat_history, assessment):
    """
    Orchestrates the evaluation process for a given query.
    
    Args:
        input (GenerateEvaluation): The request body containing the evaluation details.
            - question_id (int): The unique identifier of the question to be evaluated.
            - question (str): The text of the question.
            - interview_id (int): The unique identifier of the interview session.
            - answer (str): The candidate's answer to be evaluated.
    
    Returns:
        dict: A response containing the evaluation results.
    """
    #TODO: returns assessment_payload and rationale
    print ("Inside evaluate_answer(...)")
    
    prompt_bot_dialogue = bot_dialogue
    prompt_distilled_candidate_dialogue = distilled_candidate_dialogue
    prompt_distilled_chat_history = distilled_chat_history
    prompt_assessment_payload = assessment_payload

    llm_inputs = [] # initialize inputs for LLM preparation
    assessment_payload["criteria_scores"] = []
    assessment_payload["subcriteria_scores"] = []
    assessment_payload["final_score"] = 0.0
    llm_inputs.append({"prompt_bot_dialogue": prompt_bot_dialogue,"prompt_distilled_candidate_dialogue": prompt_distilled_candidate_dialogue,"prompt_distilled_chat_history": prompt_distilled_chat_history, "prompt_assessment_payload": prompt_assessment_payload})

    ### Preparing, invoking and calling LLM
    evaluation_prompt = answer_evaluator_prompt.make_prompt_from_template()
    evaluation_llm = llm_service.get_openai_model()
    evaluation_chain = evaluation_prompt | evaluation_llm
    print("before calling eval_chain.abatch ...")
    llm_response = await evaluation_chain.abatch(llm_inputs)
    try:
        llm_response_content = llm_response[0].content
        # First, clean the JSON string
        cleaned_json_string = json_helper.fix_json(llm_response_content)

        # Then, attempt to parse
        llm_response_json = json.loads(cleaned_json_string)

        print("JSON parsed successfully!")
        # You can now work with llm_response_json
        #print(json.dumps(llm_response_json, indent=2)) # Optional: print the parsed JSON

    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        print("Original JSON string:")
        print(llm_response_content)  #Print the original string for inspection
        # Optionally, print the problematic part of the string:
        error_position = e.pos
        print(f"Problematic part of the string around position {error_position}:")
        start = max(0, error_position - 50)
        end = min(len(llm_response_content), error_position + 50)
        print(llm_response_content[start:end])

    assessment_payload = llm_response_json["prompt_assessment_payload"]
    rationale = llm_response_json["rationale"]
    print(json.dumps(assessment_payload, indent=3))
    print(rationale)
    updated_assessment_payload = await interview_computation.compute_turn_score(assessment_payload)
    # updated_json = json.loads(updated_assessment_payload)
    print(json.dumps(updated_assessment_payload, indent = 3))
    return(updated_assessment_payload, rationale)

    # llm_response_json = json.loads(llm_response)
    # print("LLM_RESPONSE: ",llm_response_json)

def return_max_eval(eval1, eval2):
    """
    Combines two evaluation dictionaries by taking the maximum score for each question.
    Includes logger.info statements to compare scores from eval1, eval2, and the resulting eval3.
    
    Args:
        eval1: List of dictionaries containing question-score pairs (scores as strings)
        eval2: Dictionary containing question-score pairs (scores as strings)
    
    Returns:
        List of dictionaries matching eval1's shape with maximum scores as strings
    """
    # Convert eval2 into a flat dictionary for easier lookup
    eval2_dict = {}
    for item in eval2:
        for question, score in item.items():
            eval2_dict[question] = score
    
    # Create eval3 by taking maximum scores
    eval3 = []
    for eval1_dict in eval1:
        new_dict = {}
        for question, score in eval1_dict.items():
            
            score1 = float(score)
            score2 = float(eval2_dict.get(question, '0')) 
            max_score = max(score1, score2)
            new_dict[question] = str(max_score)
        eval3.append(new_dict)
    
    return eval3


def score_subcriteria(criterion_weights, subcriteria_score):
    total_weight = sum(criterion_weights)
    weighted_score = sum(weight * int(score) for weight, score in zip(criterion_weights, subcriteria_score))
    criterion_score = (round((weighted_score / total_weight), 2) if total_weight != 0 else 0)/10.0
    criterion_score=round(criterion_score,2)
    return criterion_score


async def get_assessment_payload():
    ###### Loading the file for now; the assessment json structure will later be received as an argument
    # # Define the file path
    file_path = "src/schemas/evaluation/assessment_payload_expt.json"  # Adjust path as needed

    # Open and load the JSON file
    with open(file_path, "r", encoding="utf-8") as file:
        assessment_payload = json.load(file)

    # Print the loaded JSON
    # print(assessment_payload)
    # Pretty print the JSON output
    # print(json.dumps(assessment_payload, indent=3))
    return assessment_payload

async def main():
    ### criteria and subcriteria scores list
    subcriteria_scores_1 = [] # for first turn
    subcriteria_scores_2 = [] # for second turn
    criteria_scores_1 = [] # for first turn
    criteria_scores_2 = [] # for second turn

    ### Call the evaluate_answer function once
    print(">>>>>>>>>>FIRST ITERATION BEGINS >>>>>>>>>")
    question_id = "1"
    bot_dialogue = "Return an index in an array of integers such that the left sum of integers is equal to the right sum"
    distilled_candidate_dialogue = "I would try to use a prefix approach where I keep a running sum of the numbers as I iterate and keep checking the condition by subtracting the running total from the total sum of integers. Also this would mean O(n) time complexity and constant space complexity"
    distilled_chat_history = []
    print ("BOT:", bot_dialogue)
    print ("CAND:", distilled_candidate_dialogue)
    print ("CHAT:", distilled_chat_history)
    assessment_payload =  await get_assessment_payload()
    print(json.dumps(assessment_payload, indent=3))
    updated_assessment_payload = await evaluate_answer(bot_dialogue, distilled_candidate_dialogue, distilled_chat_history, assessment_payload)
    subcriteria_scores_1 = updated_assessment_payload['subcriteria_scores']
    criteria_scores_1 = updated_assessment_payload['criteria_scores']
    print("********* FIRST ITERATION OVER *******")

    print(">>>>>>>>>>SECOND ITERATION BEGINS >>>>>>>>>")
    ### Call the evaluate_answer function twice (to check the variation in scores and ensure that its monotonically increaasing)
    question_id = "1"
    bot_dialogue = "Elaborate on this problem of in terms of any assumptions or corner cases do you might suppose?"
    distilled_candidate_dialogue = "I would look out for corner cases like array length of one or zero, and if there is a possibility of multiple valid indices"
    distilled_chat_history = ["Return an index in an array of integers such that the left sum of integers is equal to the right sum",
                              "I would try to use a prefix approach where I keep a running sum of the numbers as I iterate and keep checking the condition by subtracting the running total from the total sum of integers. Also this would mean O(n) time complexity and constant space complexity",
                              "Elaborate on this problem of in terms of any assumptions or corner cases do you might suppose?"
                              ]
    print ("BOT:", bot_dialogue)
    print ("CAND:", distilled_candidate_dialogue)
    print ("CHAT:", distilled_chat_history)
    # updated_assessment_payload = await interview_computation.compute_turn_score_gold_for_later(assessment_payload)
    print(json.dumps(updated_assessment_payload, indent=3))
    updated_assessment_payload["criteria_scores"] = []
    updated_assessment_payload["subcriteria_scores"] = []
    updated_assessment_payload["final_score"] = 0.0
    updated_assessment_payload = await evaluate_answer(bot_dialogue, distilled_candidate_dialogue, distilled_chat_history, updated_assessment_payload)
    subcriteria_scores_2 = updated_assessment_payload['subcriteria_scores']
    criteria_scores_2 = updated_assessment_payload['criteria_scores']
    print("********* SECOND ITERATION OVER *******")
    
    print(subcriteria_scores_1)
    print(subcriteria_scores_2)
    print(criteria_scores_1)
    print(criteria_scores_2)

if __name__ == "__main__":
    # Preparing the arguments for the evaluate_answer function
    # Use asyncio.run() to run the async function
    asyncio.run(main())
