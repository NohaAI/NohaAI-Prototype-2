"""Interview router module for handling interview-related API endpoints.

This module provides FastAPI router endpoints for generating sub-criteria and
evaluating answers in the interview process.
"""
import uvicorn
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
from src.dao.query import get_user_query
from src.services.workflows.candidate_greeter import generate_greeting
import src.services.workflows as workflows
from src.services.workflows.solution_hint_generator import generate_hint
from src.services.workflows import hint_generator
# Initialize logger
logger = get_logger(__name__)

# Initialize the router
router = APIRouter(tags=["Execute Interview"])

app=FastAPI()

@router.get("/greeter-service")
async def greet_candidate(user_id: int):
    question_id=2
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
        response = await workflows.evaluate_answer(input_request)
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
    #  
    return s
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9030)