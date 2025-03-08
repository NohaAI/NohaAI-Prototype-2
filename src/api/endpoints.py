"""Interview router module for handling interview-related API endpoints.

This module provides FastAPI router endpoints for generating sub-criteria and
evaluating answers in the interview process.
"""
import uvicorn
import json
from fastapi import FastAPI
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.schemas.endpoints.schema import GenerateSubCriteriaRequest,EvaluateAnswerRequest, GenerateHintRequest
from src.services.workflows import subcriteria_generator,answer_evaluator
from src.utils.logger import get_logger
from typing import List
from src.utils.helper import decorate_response
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.question import get_question_metadata
from src.dao.exceptions import QuestionNotFoundException,InterviewNotFoundException
from src.services.workflows.candidate_greeter import generate_greeting
from src.services.workflows import answer_evaluator
from src.services.workflows.hint_generator import generate_hint
from test.simulate_candidate_response import simulate_candidate_response
from src.dao.chat_history import get_chat_history
from src.dao.interview import get_interview_metadata
from src.dao.chat_history import add_chat_history
from src.dao.question import get_initial_question_metadata,get_question_metadata
from src.dao.chat_history import delete_chat_history
from src.dao.question import add_question
# Initialize logger

logger = get_logger(__name__)

# Initialize the router
router = APIRouter(tags=["Execute Interview"])

app=FastAPI()

@router.get("/greeter-service")
async def greet_candidate(user_id: int):
    question_id=1
    try:
        greeting_response=await generate_greeting(user_id,question_id)
        return decorate_response(True,greeting_response)
    except Exception as e:
        logger.critical("Failed to generate candidate greeting: %s", e)
        return decorate_response(
            False,
            "Failed to generate candidate greeting",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/generate_subcriteria", status_code=status.HTTP_200_OK)
async def generate_subcriteria(input_request: GenerateSubCriteriaRequest) -> JSONResponse:
    """Generates sub-criteria based on the given question.

    Args:
        input_request: Request object containing:
            - question_id: Unique ID for database insertion
            - question: Content used to generate sub-criteria.
            - question_type_id (int): The identifier representing the type of question .


    Returns:
        JSONResponse containing:
            - succeeded: Operation success status
            - message: Generated sub-criteria or error message
            - httpStatusCode: HTTP status code.
    """
    try:
        subcriteria = await subcriteria_generator.generate_subcriteria(input_request)
        logger.info("Successfully generated sub-criteria: %s", subcriteria)
        return decorate_response(True, subcriteria)

    except Exception as ex:
        logger.critical("Failed to generate sub-criteria: %s", ex)
        return decorate_response(
            False,
            "Failed to generate sub-criteria",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/evaluate_answer", status_code=status.HTTP_200_OK)
async def evaluate_answer(input_request: EvaluateAnswerRequest) -> JSONResponse:
    """Evaluates an answer based on provided criteria.

    Args:
        evaluation_request_input: Request object containing evaluation details

    Returns:
        JSONResponse containing:
            - succeeded: Operation success status
            - message: Evaluation results or error message
            - httpStatusCode: HTTP status code
    """
    try:
        response = await answer_evaluator.evaluate_answer(input_request)
        logger.info("Successfully evaluated answer")
        # return decorate_response(True, response)
        return response
    
    except Exception as ex:
        logger.critical("Failed to evaluate answer: %s", ex)
        return decorate_response(False,"Failed to evaluate answer",status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post("/generate_hint")
# remodel takes input chat_history and answer_evaluation
async def generate_hint(chat_history,answer_evaluation,hint_count):
    try:
        hint = await generate_hint(chat_history,answer_evaluation,hint_count)
        return decorate_response(True,hint)
    except Exception as e:
        logger.critical("Failed to generate hint: %s", e)
        return decorate_response(
            False,
            "Failed to generate hint",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# @router.post("/generate_solution_hint", status_code=status.HTTP_200_OK)
# async def generate_solution_hint(input_request: GenerateHintRequest) -> JSONResponse:
#     """Evaluates an answer based on provided criteria.

#     Args:
#         evaluation_request_input: Request object containing evaluation details

#     Returns:
#         JSONResponse containing:
#             - succeeded: Operation success status
#             - message: Evaluation results or error message
#             - httpStatusCode: HTTP status code
#     """
#     try:
#         response = await generate_hint(input_request)
#         logger.info("Successfully generated hint")
#         return decorate_response(True, response)
    
#     except Exception as ex:
#         logger.critical("Failed to generate hint: %s", ex)
#         return decorate_response(False,"Failed to generate hint",status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#add question complexity
@router.post("/onboard_question",status_code=status.HTTP_200_OK)
async def onboard_question(question: str, question_type_id: int ,complexity: int):
    question_metadata=await add_question(question,question_type_id,complexity)
    question_id=question_metadata['question_id']
    question=question_metadata['question']
    question_type_id=question_metadata['question_type_id']
    subcriteria_payload={
        'question_id': question_id,
        'question': question,
        'question_type_id': question_type_id
    }
    subcriteria_request=GenerateSubCriteriaRequest(**subcriteria_payload)
    subcriteria=await generate_subcriteria(subcriteria_request)
    return {
        "question_metadata": question_metadata,
        "subcriteria": subcriteria
    }

@router.post("/onboard_multiple_questions", status_code=status.HTTP_200_OK)
async def onboard_multiple_questions(questions: List[dict]):
    """
    Onboard multiple questions in a single request.

    Args:
        questions: A list of dictionaries, where each dictionary contains:
            - question: The question text.
            - question_type_id: The type ID of the question.
            - complexity: The complexity level of the question.

    Returns:
        JSONResponse containing:
            - succeeded: Operation success status.
            - message: List of onboarded questions or error message.
            - httpStatusCode: HTTP status code.
    """
    try:
        results = []
        for question_data in questions:
            question = question_data.get("question")
            question_type_id = question_data.get("question_type_id")
            complexity = question_data.get("complexity")
            
            # if not all([question, question_type_id, complexity]):
            #     raise ValueError("Missing required fields in one or more questions.")
            
            result = await onboard_question(question, question_type_id, complexity)
            results.append(result)
        
        logger.info("Successfully onboarded multiple questions")
        return decorate_response(True, results)
    
    except Exception as ex:
        logger.critical("Failed to onboard multiple questions: %s", ex)
        return decorate_response(
            False,
            "Failed to onboard multiple questions",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
#condcut interview
@router.post("/conduct_interview", status_code=status.HTTP_200_OK)
# async def conduct_interview(interview_id) :
#     return interview_id

async def conduct_interview_orig(interview_id) :
    hint_count=[0,0,0,0,0]
    initial_eval_distribution=[0,0,0,0,0,0,0]
    # if len(chat_history) == 0: call greeter  
    # use dao calls for interview_question for question_id, interview for user_id/name, chat_history for turn_input/output
    # call greeting and generate greeting
    # call chat_history.add_chat_history and write the first turn to the database
    # get answers from the user and update chat_history (answer_evaluator)
    # pass the answer to the answer evaluator and generate scores 
    # pass the scores and the updated chat history to hint generator
    # get the generated hint and update chat history
    # repeat the loop from step no.3 until the average interview score crosses the predefined threshold
    # if the interview score crossed the threshold, call the reporting api and generate the report
    # for now assuming that question_id = 1
    
    chat_history= await get_chat_history(interview_id)
    if chat_history:
        await delete_chat_history(interview_id)
    chat_history= await get_chat_history(interview_id)    
    if not chat_history:
        question_id=0

        interview_metadata=await get_interview_metadata(interview_id)
        user_id=interview_metadata.user_id
        greeting_response = await greet_candidate(user_id)

        greeting_response_body = greeting_response.body.decode()
        greeting_response_data = json.loads(greeting_response_body)
        
        greeting = greeting_response_data["message"]
        simulated_candidate_greeting_response="Hey I am ready let's begin the interview"
        #check whether the candidate is readfy for interview by a logic
        added_chat_history_data=await add_chat_history(interview_id, question_id, greeting, simulated_candidate_greeting_response,'greeting')

    #initial_question_metadata=await get_initial_question_metadata()
    initial_question_metadata=await get_question_metadata(10)
    initial_question=initial_question_metadata['question']

    
    ##################################################################################################
    # subcriteria_weight_list_norm=[]
    # for key,value in subcriteria.items():
    #     subcriterion_weight_list=subcriteria['key'][0]
    #     for dict_el in subcriterion_weight_list:
    #         subcriteria_weight_list_norm.append(dict_el['weight'])
    # logger.info(f"SUBCRITERIA NORM {subcriteria_weight_list_norm}")
    ##################################################################################################
    
    #candidate_response=await simulate_candidate_response(initial_question_metadata['question_id'])
    candidate_response=input(f"Answer for initial question : ")
    added_chat_history=await add_chat_history(interview_id,initial_question_metadata['question_id'],initial_question,candidate_response,'question')
    
    answer_evaluation_payload={
        "question_id":initial_question_metadata['question_id'],
        "question":initial_question,
        "interview_id":interview_id,
        "answer":candidate_response,
        "eval_distribution":initial_eval_distribution
    }
    #logger.info(f"ANSWER EVALUATION PAYLOAD : {answer_evaluation_payload}")
    answer_evaluation_request=EvaluateAnswerRequest(**answer_evaluation_payload)
    answer_evaluation=await evaluate_answer(answer_evaluation_request)
    chat_history=await get_chat_history(interview_id)
    logger.info(f"HINT GENERATOR PAYLOAD : {chat_history} {answer_evaluation} {hint_count}")
    while(answer_evaluation['final_score'] < 9.5):
        hint_response=await generate_hint(chat_history,answer_evaluation,hint_count)
        hint_response_body = hint_response.body.decode()
        hint_response_data = json.loads(hint_response_body)
        hint = hint_response_data["message"]
        
        logger.info("\n################################################################################")  
        logger.info("\n######################################## CHAT HISTORY ####################")
        for dict_el in chat_history:
            for key, value in dict_el.items():
                logger.info(f"\t[{key}]: {value}")
        logger.info("\n######################################### ASSESSMENT ####################")
        for dict_el in answer_evaluation["evaluation_results"]:
            for key, value in dict_el.items():
                logger.info(f"\t{key}: [{value}]")
        logger.info(f"\n########################## CRITERIA LEVEL SCORES: {answer_evaluation['criteria_scores']}")
        logger.info(f"\n############################### FINAL SCORE: {answer_evaluation['final_score']}")
        logger.info(f"\n########################### HINT: {hint}")
        #candidate_response=await simulate_candidate_response(initial_question_metadata['question_id'])
        candidate_response=input("Enter your answer : " )
        added_chat_history=await add_chat_history(interview_id,initial_question_metadata['question_id'],hint,candidate_response,'hint_question')
        answer_evaluation_payload={
        "question_id":initial_question_metadata['question_id'],
        "question":initial_question,
        "interview_id":interview_id,
        "answer":candidate_response,
        "eval_distribution":initial_eval_distribution
    }
        #logger.info(f"ANSWER EVALUATION PAYLOAD : {answer_evaluation_payload}")
        answer_evaluation_request=EvaluateAnswerRequest(**answer_evaluation_payload)
        answer_evaluation=await evaluate_answer(answer_evaluation_request)
        chat_history=await get_chat_history(interview_id)
        logger.info(f"\n############################### UPDATED SCORE {len(chat_history)}: {answer_evaluation['final_score']} ")
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9030)