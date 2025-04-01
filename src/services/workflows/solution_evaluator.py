"""
This module implements the functionality for evaluating answers based on predefined criteria, 
including calculating scores using weighted averages, and storing results in a database.
"""

import sys, json, copy

print(sys.path)

from src.utils import logger as LOGGER 
from src.utils import interview_computation, json_helper
from src.services.llm.prompts import solution_evaluator_prompt
from src.services.llm import llm_service
from src.utils import helper as helper
from src.config import constants as CONST
from src.config import logging_config as LOGCONF
# from src.dao import subcriterion
# from src.dao import chat_history as chat_history


async def evaluate_solution(session_state, chat_history, assessment):
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
    LOGGER.log_info("\n\n\n>>>>>>>>>>>FUNCTION [evaluate_solution] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    # print (type(assessment))
    # print (len(assessment))
    # print (assessment[-1])

    assessment_record = assessment[-1]
    assessment_payload = assessment_record['assessment_payloads'][-1]

    LOGGER.pretty_log("session_state", session_state)
    LOGGER.pretty_log("chat_history", chat_history, LOGCONF.DEBUG1)
    LOGGER.pretty_log("assessment", assessment, LOGCONF.DEBUG2)
    LOGGER.pretty_log("criteria_scores", assessment_payload["criteria_scores"], LOGCONF.DEBUG2)
    LOGGER.pretty_log("subcriteria_scores", assessment_payload["subcriteria_scores"], LOGCONF.DEBUG2)

    prompt_bot_dialogue = session_state["bot_dialogue"]
    prompt_distilled_candidate_dialogue = session_state["candidate_dialogue"]
    prompt_distilled_chat_history = chat_history
    prompt_assessment_payload = assessment_payload

    llm_inputs = [] # initialize inputs for LLM preparation
    
    llm_inputs.append({"prompt_bot_dialogue": prompt_bot_dialogue,
                       "prompt_distilled_candidate_dialogue": prompt_distilled_candidate_dialogue,
                       "prompt_distilled_chat_history": prompt_distilled_chat_history, 
                       "prompt_assessment_payload": prompt_assessment_payload
                       })

    ### Preparing, invoking and calling LLM
    evaluate_solution_prompt = solution_evaluator_prompt.make_prompt_from_template()
    llm_model = llm_service.get_openai_model()
    evaluate_solution_chain = (evaluate_solution_prompt | llm_model)
    print("calling eval_chain.abatch ...")
    llm_response_evaluate_solution = await evaluate_solution_chain.abatch(llm_inputs)
    llm_content_evaluate_solution = json.loads(llm_response_evaluate_solution[0].content)
    
    LOGGER.log_info("EVALUATE SOLUTION LLM OUTPUT")
    
    updated_prompt_assessment_payload = llm_content_evaluate_solution["prompt_assessment_payload"]
    solution_evaluator_rationale = llm_content_evaluate_solution["rationale"]
    LOGGER.pretty_log("updated_prompt_assessment_payload", updated_prompt_assessment_payload, LOGCONF.DEBUG1, compact=True)
    subcriteria_scores = helper.get_subcriteria_scores(updated_prompt_assessment_payload)
    LOGGER.pretty_log("subcriteria_scores", subcriteria_scores)
    LOGGER.pretty_log("solution_evaluator_rationale", solution_evaluator_rationale)
    
    computed_assessment_payload = await interview_computation.compute_turn_score(updated_prompt_assessment_payload)
    # updated_json = json.loads(updated_assessment_payload)
    print("(1) " + json.dumps(computed_assessment_payload))
    
    # Update the assessment record with the new assessment payload
    assessment_record['assessment_payloads'][-1] = computed_assessment_payload
    # print("(2) \n" + json.dumps(assessment_record['assessment_payloads'][-1]))
    # print("(3) \n" + json.dumps(assessment_record['assessment_payloads']))
    # print("(4) \n" + json.dumps(assessment_record))
    assessment_record['primary_question_score'] = computed_assessment_payload['final_score']
    # new_assessment_payload = helper.get_assessment_payload()
    assessment_payload_copy =  copy.deepcopy(computed_assessment_payload) 
    assessment_record['assessment_payloads'].append(assessment_payload_copy)
    print("(5) \n" + json.dumps(assessment_record))
    print("(6) \n" + json.dumps(assessment))

    LOGGER.pretty_log("session_state", session_state)
    LOGGER.pretty_log("chat_history", chat_history, LOGCONF.DEBUG1)
    LOGGER.pretty_log("assessment", assessment, LOGCONF.DEBUG2)
    LOGGER.pretty_log("criteria_scores", assessment_payload["criteria_scores"], LOGCONF.DEBUG2)
    LOGGER.pretty_log("subcriteria_scores", assessment_payload["subcriteria_scores"], LOGCONF.DEBUG2)
    
    return assessment, solution_evaluator_rationale


  

def return_max_eval(eval1, eval2):
    """
    Combines two evaluation dictionaries by taking the maximum score for each question.
    Includes LOGGER.log_info statements to compare scores from eval1, eval2, and the resulting eval3.
    
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


# def score_subcriteria(criterion_weights, subcriteria_score):
#     total_weight = sum(criterion_weights)
#     weighted_score = sum(weight * int(score) for weight, score in zip(criterion_weights, subcriteria_score))
#     criterion_score = (round((weighted_score / total_weight), 2) if total_weight != 0 else 0)/10.0
#     criterion_score=round(criterion_score,2)
#     return criterion_score

# async def main():
#     ### criteria and subcriteria scores list
#     subcriteria_scores_1 = [] # for first turn
#     subcriteria_scores_2 = [] # for second turn
#     criteria_scores_1 = [] # for first turn
#     criteria_scores_2 = [] # for second turn

#     ### Call the evaluate_answer function once
#     print(">>>>>>>>>>FIRST ITERATION BEGINS >>>>>>>>>")
#     question_id = "1"
#     bot_dialogue = "Return an index in an array of integers such that the left sum of integers is equal to the right sum"
#     distilled_candidate_dialogue = "I would try to use a prefix approach where I keep a running sum of the numbers as I iterate and keep checking the condition by subtracting the running total from the total sum of integers. Also this would mean O(n) time complexity and constant space complexity"
#     distilled_chat_history = []
#     print ("BOT:", bot_dialogue)
#     print ("CAND:", distilled_candidate_dialogue)
#     print ("CHAT:", distilled_chat_history)
#     assessment_payload =  await get_assessment_payload()
#     print(json.dumps(assessment_payload, indent=3))
#     updated_assessment_payload = await evaluate_solution(bot_dialogue, distilled_candidate_dialogue, distilled_chat_history, assessment_payload)
#     subcriteria_scores_1 = updated_assessment_payload['subcriteria_scores']
#     criteria_scores_1 = updated_assessment_payload['criteria_scores']
#     print("********* FIRST ITERATION OVER *******")

#     print(">>>>>>>>>>SECOND ITERATION BEGINS >>>>>>>>>")
#     ### Call the evaluate_answer function twice (to check the variation in scores and ensure that its monotonically increaasing)
#     question_id = "1"
#     bot_dialogue = "Elaborate on this problem of in terms of any assumptions or corner cases do you might suppose?"
#     distilled_candidate_dialogue = "I would look out for corner cases like array length of one or zero, and if there is a possibility of multiple valid indices"
#     distilled_chat_history = ["Return an index in an array of integers such that the left sum of integers is equal to the right sum",
#                               "I would try to use a prefix approach where I keep a running sum of the numbers as I iterate and keep checking the condition by subtracting the running total from the total sum of integers. Also this would mean O(n) time complexity and constant space complexity",
#                               "Elaborate on this problem of in terms of any assumptions or corner cases do you might suppose?"
#                               ]
#     print ("BOT:", bot_dialogue)
#     print ("CAND:", distilled_candidate_dialogue)
#     print ("CHAT:", distilled_chat_history)
#     # updated_assessment_payload = await interview_computation.compute_turn_score_gold_for_later(assessment_payload)
#     print(json.dumps(updated_assessment_payload, indent=3))
#     updated_assessment_payload["criteria_scores"] = []
#     updated_assessment_payload["subcriteria_scores"] = []
#     updated_assessment_payload["final_score"] = 0.0
#     updated_assessment_payload = await evaluate_solution(bot_dialogue, distilled_candidate_dialogue, distilled_chat_history, updated_assessment_payload)
#     subcriteria_scores_2 = updated_assessment_payload['subcriteria_scores']
#     criteria_scores_2 = updated_assessment_payload['criteria_scores']
#     print("********* SECOND ITERATION OVER *******")
    
#     print(subcriteria_scores_1)
#     print(subcriteria_scores_2)
#     print(criteria_scores_1)
#     print(criteria_scores_2)

# if __name__ == "__main__":
#     # Preparing the arguments for the evaluate_answer function
#     # Use asyncio.run() to run the async function
#     asyncio.run(main())
