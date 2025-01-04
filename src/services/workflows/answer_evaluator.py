"""
This module implements the functionality for evaluating answers based on predefined criteria, 
including calculating scores using weighted averages, and storing results in a database.
"""

import json
import src.utils as utils
import src.services.llm.prompts.answer_evaluator_prompt as make_prompt_from_template
import src.services.llm.prompts.answer_evaluator_prompt as prompts
import src.services.llm as llm
from src import dao 

# Initialize logger
logger = utils.get_logger(__name__)


async def evaluate_answer(input_request):
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

    try:
        try:
            question_id = input_request.question_id
            question = input_request.question
            interview_id = input_request.interview_id
            candidate_answer = input_request.answer
        except AttributeError as attr_err:
            logger.critical(f"Input object missing required attributes: {attr_err}")
            raise AttributeError(f"Input object missing required attributes: {attr_err}") from attr_err

        evaluation_criteria = await dao.fetch_subcriteria(question_id)
        chat_history = await dao.get_chat_history(interview_id)

        chat_history = []
        chat_history.append({"question": question, "answer": candidate_answer})

        llm_inputs = []
        subcriteria_weights = []
        criteria_scores = []
        evaluation_results = []

        for criterion in evaluation_criteria.keys():
            llm_inputs.append({"question": question, "answer": candidate_answer, "chat_history": chat_history, "subcriteria": evaluation_criteria[criterion]})
            subcriteria_weights.append([int(subcriterion['weight']) for subcriterion in evaluation_criteria[criterion]])

        evaluation_prompt = prompts.make_prompt_from_template()
        evaluation_llm = llm.get_openai_model(model = "gpt-4o-mini")
        evaluation_chain = evaluation_prompt | evaluation_llm
        llm_response = await evaluation_chain.abatch(llm_inputs)

        for criterion_result, criterion_weights in zip(llm_response, subcriteria_weights):
            subcriteria_score = (json.loads(criterion_result.content)).values()
            criteria_scores.append(score_subcriteria(criterion_weights, subcriteria_score))
            evaluation_results.append(json.loads(criterion_result.content))

        total_score_count = sum(criteria_scores)
        final_score = round(total_score_count / len(evaluation_criteria.keys()), 2)

        return {
            "evaluation_results": evaluation_results,
            "criteria_scores": criteria_scores,
            "final_score": final_score
        }
    
    except Exception as ex:
        logger.critical(f"Unexpected error in evaluation process: {ex}")
        raise Exception(f"Unexpected error in evaluation process: {ex}")
    

def score_subcriteria(criterion_weights, subcriteria_score):
    total_weight = sum(criterion_weights)
    weighted_score = sum(weight * int(score) for weight, score in zip(criterion_weights, subcriteria_score))
    criterion_score = (round((weighted_score / total_weight), 2) if total_weight != 0 else 0)/10.0
    criterion_score=round(criterion_score,2)
    return criterion_score