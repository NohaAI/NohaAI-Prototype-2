from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
import psycopg2
from psycopg2.pool import SimpleConnectionPool
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import uvicorn
import json
from src.dao.exceptions import QuestionEvaluationNotFoundException,QuestionNotFoundException,InterviewNotFoundException
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.schemas.dao.schema import QuestionEvaluationUpdateRequest,QuestionEvaluationResponse,QuestionEvaluationRequest

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the schema for update requests


app = FastAPI()

# API endpoint to fetch question evaluation details by ID
@app.get("/question_evaluation/{question_evaluation_id}", response_model=QuestionEvaluationResponse)
async def get_question_evaluation(question_evaluation_id: int):
    """
    Retrieves data of question evaluation table.

    Args:
        question_evaluaiaton_id (int): Unique indentifier for question evaluation.

    Returns:
        QuestionEvaluationResponse: Details of the evaluated question

    Raises:
        Exception: 404 for Evaluation not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                query = """
                    SELECT question_evaluation_id, interview_id, question_id, score, question_evaluation_json
                    FROM Interview_Question_Evaluation
                    WHERE question_evaluation_id = %s
                """
                result = execute_query(conn, query, (question_evaluation_id,), fetch_one=True)
                if not result:
                    raise QuestionEvaluationNotFoundException(question_evaluation_id)
                return QuestionEvaluationResponse(
                    question_evaluation_id=result[0],
                    interview_id=result[1],
                    question_id=result[2],
                    score=result[3],
                    question_evaluation_json=result[4]
                )
            except Exception as e:
                logger.error(f"Error retrieving evaluation: {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
# API endpoint to update an existing question evaluation
@app.put("/question_evaluation/{question_evaluation_id}", response_model=QuestionEvaluationResponse)
async def update_question_evaluation(question_evaluation_id: int,evaluation_request: QuestionEvaluationUpdateRequest):
    """
    Update details of a question evaluation.
    
    Args:
        question_evaluation_id (int): ID of the question evaluation to update
        evaluation_request (QuestionEvaluationRequest): New data for the question evaluation
        
    Returns:
        QuestionEvaluationResponse: Updated question evaluation details
        
    Raises:
        Exception: 404 if question evaluation not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Check if evaluation exists
                check_query = """
                    SELECT question_evaluation_id FROM Interview_Question_Evaluation 
                    WHERE question_evaluation_id = %s
                """
                exists = execute_query(conn, check_query, (question_evaluation_id,), fetch_one=True)
                if not exists:
                    raise QuestionEvaluationNotFoundException(question_evaluation_id)
                
                # Prepare update query with optional fields
                update_fields = []
                update_params = []
                if evaluation_request.score is not None:
                    update_fields.append("score = %s")
                    update_params.append(evaluation_request.score)
                if evaluation_request.question_evaluation_json is not None:
                    update_fields.append("question_evaluation_json = %s")
                    update_params.append(evaluation_request.question_evaluation_json)
                if not update_fields:
                    raise Exception("No update fields provided")
                update_params.append(question_evaluation_id)

                # Execute the update query
                update_query = f"""
                    UPDATE Interview_Question_Evaluation
                    SET {', '.join(update_fields)}
                    WHERE question_evaluation_id = %s
                    RETURNING question_evaluation_id, interview_id, question_id, score, question_evaluation_json
                """
                updated_record = execute_query(
                    conn, 
                    update_query, 
                    update_params, 
                    fetch_one=True,
                    commit=True
                )
                return QuestionEvaluationResponse(
                    question_evaluation_id=updated_record[0],
                    interview_id=updated_record[1],
                    question_id=updated_record[2],
                    score=updated_record[3],
                    question_evaluation_json=updated_record[4]
                )
            except Exception as e:
                logger.error(f"Error updating evaluation: {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
    
# API endpoint to add a new question evaluation
@app.post("/question_evaluation", response_model=QuestionEvaluationResponse)
async def add_question_evaluation(interview_id: int, question_id: int, score: float, evaluation_results, accumulated_results):
    """
    Add a new question evaluation to the database.
    
    Args:
        interview_id (int): ID of the interview
        question_id (int): ID of that question that was asked in the interview
        score (float):Score achieved by the candidate on a subcriteria
        evaluation_results: Result of the evaluation for a subcriteria
        accumulated_results: Accumulated result for a criteria
    Returns: 
        QuestionEvaluationResponse:Added question evaluation details

    Raises: 
        Exception: 404 for interview/question not found, 400 for validation errors, 503 for connection issues,
                      500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                question_evaluation_json = json.dumps({
                    "evaluation_results": evaluation_results,
                    "accumulated_results_all_categories": accumulated_results,
                })
                # Validate interview existence
                interview_check_query = """
                    SELECT interview_id FROM Interview 
                    WHERE interview_id = %s
                """
                interview_exists = execute_query(conn, interview_check_query, (interview_id,), fetch_one=True)
                if not interview_exists:
                    logger.error(f"Interview")
                    raise InterviewNotFoundException(interview_id)
                
                # Validate question existence
                question_check_query = """
                    SELECT question_id FROM Question 
                    WHERE question_id = %s
                """
                question_exists = execute_query(conn, question_check_query, (question_id,), fetch_one=True)
                if not question_exists:
                    raise QuestionNotFoundException(question_id)
                
                # Insert the new evaluation
                insert_query = """
                    INSERT INTO Interview_Question_Evaluation (
                        interview_id, 
                        question_id, 
                        score, 
                        question_evaluation_json
                    ) VALUES (%s, %s, %s, %s)
                    RETURNING question_evaluation_id, interview_id, question_id, score, question_evaluation_json
                """
                result = execute_query(
                    conn,
                    insert_query,
                    (interview_id, question_id, score, question_evaluation_json),
                    fetch_one=True,
                    commit=True
                )
                return QuestionEvaluationResponse(
                    question_evaluation_id=result[0],
                    interview_id=result[1],
                    question_id=result[2],
                    score=result[3],
                    question_evaluation_json=result[4]
                )
            except Exception as e:
                logger.error(f"Error adding evaluation: {e}")
                raise Exception(f"Error adding evaluation: {e}")
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# API endpoint to delete a question evaluation
@app.delete("/question_evaluation/{question_evaluation_id}")
async def delete_question_evaluation(question_evaluation_id: int):
    """
    Delete a question evaluation by ID.
    
    Args:
        question_evaluation_id (int): ID of the question evaluation to delete
        
    Returns:
        dict: Success message
        
    Raises:
        Exception: 404 if evaluation not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Delete the evaluation and return its ID
                delete_query = """
                    DELETE FROM Interview_Question_Evaluation 
                    WHERE question_evaluation_id = %s 
                    RETURNING question_evaluation_id
                """
                deleted_evaluation = execute_query(
                    conn, 
                    delete_query, 
                    (question_evaluation_id,), 
                    fetch_one=True,
                    commit=True
                )
                if not deleted_evaluation:
                    logger.error(f"Question evaluation with ID {question_evaluation_id} not found in the database")
                    raise QuestionEvaluationNotFoundException(question_evaluation_id)
                return {"message": "Evaluation deleted successfully"}
            except Exception as e:
                logger.error(f"Error deleting evaluation: {e}")
                raise e
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
        
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9099)