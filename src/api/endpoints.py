"""Interview router module for handling interview-related API endpoints.

This module provides FastAPI router endpoints for generating sub-criteria and
evaluating answers in the interview process.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.schema import GenerateSubCriteriaRequest,EvaluateAnswerRequest
from app.interactors import subcriteria_generator,answer_evaluator
from app.utils.logger import get_logger
from app.utils.response_helper import decorate_response

# Initialize logger
logger = get_logger(__name__)

# Initialize the router
router = APIRouter(tags=["Execute Interview"])


@router.post("/generate_subcriteria", status_code=status.HTTP_200_OK)
async def route_generate_subcriteria(input_request: GenerateSubCriteriaRequest) -> JSONResponse:
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
async def route_evaluate_answer(input_request: EvaluateAnswerRequest) -> JSONResponse:
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
        return decorate_response(True, response)
    
    except Exception as ex:
        logger.critical("Failed to evaluate answer: %s", ex)
        return decorate_response(False,"Failed to evaluate answer",status.HTTP_500_INTERNAL_SERVER_ERROR)