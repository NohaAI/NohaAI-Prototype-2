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
from src.utils.response_helper import decorate_response
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.question import get_question_metadata
from src.dao.exceptions import QuestionNotFoundException,InterviewNotFoundException
from src.services.workflows.candidate_greeter import generate_greeting
from src.services.workflows import answer_evaluator
from src.services.workflows.solution_hint_generator import generate_hint
from src.services.workflows import hint_generator
from test.simulate_candidate_response import simulate_candidate_response
from src.dao.chat_history import get_chat_history
from src.dao.interview import get_interview_metadata
from src.dao.chat_history import add_chat_history
from src.dao.question import get_initial_question_metadata
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
async def generate_hint(chat_history,answer_evaluation):
    try:
        hint = await hint_generator.generate_hint(chat_history,answer_evaluation)
        return decorate_response(True,hint)
    except Exception as e:
        logger.critical("Failed to generate hint: %s", e)
        return decorate_response(
            False,
            "Failed to generate hint",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/generate_solution_hint", status_code=status.HTTP_200_OK)
async def generate_solution_hint(input_request: GenerateHintRequest) -> JSONResponse:
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
        response = await generate_hint(input_request)
        logger.info("Successfully generated hint")
        return decorate_response(True, response)
    
    except Exception as ex:
        logger.critical("Failed to generate hint: %s", ex)
        return decorate_response(False,"Failed to generate hint",status.HTTP_500_INTERNAL_SERVER_ERROR)
#add question complexity
@router.post("/onboard_question",status_code=status.HTTP_200_OK)
async def onboard_question(question,question_type_id):
    question_metadata=await add_question(question,question_type_id)
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

#condcut interview
@router.post("/conduct_interview", status_code=status.HTTP_200_OK)
async def conduct_interview(interview_id) :
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

    initial_question_metadata=await get_initial_question_metadata()
    initial_question=initial_question_metadata['question']

    
    ##################################################################################################
    # subcriteria_weight_list_norm=[]
    # for key,value in subcriteria.items():
    #     subcriterion_weight_list=subcriteria['key'][0]
    #     for dict_el in subcriterion_weight_list:
    #         subcriteria_weight_list_norm.append(dict_el['weight'])
    # logger.info(f"SUBCRITERIA NORM {subcriteria_weight_list_norm}")
    ##################################################################################################
    
    candidate_response=await simulate_candidate_response(initial_question_metadata['question_id'])
    added_chat_history=await add_chat_history(interview_id,initial_question_metadata['question_id'],initial_question,candidate_response,'question')
    
    answer_evaluation_payload={
        "question_id":initial_question_metadata['question_id'],
        "question":initial_question,
        "interview_id":interview_id,
        "answer":candidate_response
    }
    #logger.info(f"ANSWER EVALUATION PAYLOAD : {answer_evaluation_payload}")
    answer_evaluation_request=EvaluateAnswerRequest(**answer_evaluation_payload)
    answer_evaluation=await evaluate_answer(answer_evaluation_request)
    logger.info("################################################################################")
    logger.info(f"ANSWER EVALUATION PAYLOAD {answer_evaluation}")
    logger.info(f"ANSWER EVALUATION {answer_evaluation['criteria_scores']}")
    logger.info(f"ANSWER EVALUATION {answer_evaluation['final_score']}")
    chat_history=await get_chat_history(interview_id)
    logger.info(f"CHAT_HISTORY : {chat_history}")

    hint_response=await generate_hint(chat_history,answer_evaluation)
    hint_response_body = hint_response.body.decode()
    hint_response_data = json.loads(hint_response_body)
    
    hint = hint_response_data["message"]
    logger.info(f"HINT : {hint}")
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9030)