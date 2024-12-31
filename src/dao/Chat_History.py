from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import Optional
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import uvicorn
import httpx
from typing import List, Optional
from src.dao.Question import get_question_metadata
from src.dao.utils.DB_Utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.Exceptions import ChatHistoryNotFoundException,InterviewNotFoundException
# Configure application-wide logging to track and record application events and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models Documentation
class CandidateAnswerResponse(BaseModel):
    """
    Response model for candidate answer operations with length validation.
    
    Attributes:
        chat_history_id (int): Unique identifier for the chat history entry.
        question_id (int): Reference to the question being answered.
        interview_id (int): Reference to the interview session.
        candidate_answer (str): The answer provided by the candidate, must be between 2 and 500 characters.
    """
    chat_history_id: int
    question_id: int
    interview_id: int
    candidate_answer: str = Field(..., min_length=2, max_length=500)

class CandidateAnswerRequest(BaseModel):
    """
    Request model for candidate answer submissions with length validation.
    
    Attributes:
        candidate_answer (str): The answer provided by the candidate, must be between 2 and 500 characters.
    """
    candidate_answer: str = Field(..., min_length=2, max_length=500)

async def refine_chat_history(chat_history):
    chat_history = []
    for row in chat_history:
        question_id = row[0]  # Get question_id from the database row
        question_data = await get_question_metadata(question_id)

        # Add the question and answer to the chat_history
        chat_history.append({
            "question": question_data["question"],
            "answer": row[2]
        })

    return chat_history

# Initialize FastAPI application for creating candidate answer service endpoints
app = FastAPI()

@app.get("/candidate_answers/{interview_id}", response_model=List[str])
async def get_all_candidate_answers(interview_id: int):
    """
    Retrieve all candidate answers for a specific interview.
    
    Args:
        interview_id (int): The unique identifier of the interview.
    
    Returns:
        List[str]: A list of all candidate answers for the specified interview.
    
    Raises:
        HTTPException (404): 
            - If no interview is found with the specified ID
            - If no chat history exists for the specified interview
        HTTPException (500): If there's an internal server error
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            # First, verify that the interview exists
            interview_check_query = "SELECT user_id FROM interviews WHERE interview_id = %s"
            interview_exists = execute_query(conn, interview_check_query, (interview_id,))

            if not interview_exists or interview_exists[0] == 0:
                raise InterviewNotFoundException(interview_id)

            # Query to fetch all chat history entries for the interview
            query = """
                SELECT candidate_answer
                FROM chat_history 
                WHERE interview_id = %s
                ORDER BY chat_history_id
            """
            chat_history = execute_query(
                conn,
                query,
                (interview_id,),
                fetch_one=False
            )
            
            if not chat_history:
                raise InterviewNotFoundException(interview_id)
            
            # Extract and return only the candidate answers
            candidate_answers = [record[0] for record in chat_history]
            return candidate_answers
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.get("/candidate_answer/{chat_history_id}", response_model=CandidateAnswerResponse)
async def get_candidate_answer(chat_history_id: int):
    """
    Retrieve a specific candidate answer by its chat history ID.
    
    Args:
        chat_history_id (int): The unique identifier of the chat history entry.
    
    Returns:
        CandidateAnswerResponse: The candidate answer details including question and interview context.
    
    Raises:
        HTTPException (404): If no chat history entry is found with the specified ID
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            try:
                # SQL query to fetch candidate answer details from chat_history table
                query = """
                    SELECT chat_history_id, question_id, interview_id, candidate_answer
                    FROM chat_history
                    WHERE chat_history_id = %s
                """
                result = execute_query(conn, query, (chat_history_id,), fetch_one=True)
                
                # Raise 404 error if no matching record is found
                if not result:
                    raise ChatHistoryNotFoundException(chat_history_id)
                
                # Return the candidate answer response with retrieved details
                return CandidateAnswerResponse(
                    chat_history_id=result[0],
                    question_id=result[1],
                    interview_id=result[2],
                    candidate_answer=result[3]
                )
            except Exception as e:
                logger.error(f"Error retrieving CandidateAnswer: {e}")
                raise e
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.get("/candidate_answer/chat_history/", response_model=list[dict])
async def get_chat_history(interview_id: int):
    """
    Retrieve the complete chat history for a specific interview, including questions and answers.
    
    Args:
        interview_id (int): The unique identifier of the interview.
    
    Returns:
        list[dict]: A list of dictionaries containing the chat history, where each dictionary
                   contains:
                   - question (str): The interview question
                   - answer (str): The candidate's answer
    
    Raises:
        Exception: If there's an error retrieving the chat history
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            try:
                query = """
                    SELECT question_id, interview_id, candidate_answer
                    FROM chat_history
                    WHERE interview_id = %s
                """
                result = execute_query(conn, query, (interview_id,), fetch_one=False)
                
                if not result:
                    return []
                
                chat_history = await refine_chat_history(result)
                return chat_history
            except Exception as e:
                logger.error(f"Error retrieving Chat History: {e}")
                raise Exception(f"Error retrieving Chat History: {e}")
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/candidate_answer/{chat_history_id}", response_model=CandidateAnswerResponse)
async def update_candidate_answer(chat_history_id: int, candidate_answer_request: CandidateAnswerRequest):
    """
    Update an existing candidate answer in the chat history.
    
    Args:
        chat_history_id (int): The unique identifier of the chat history entry to update.
        candidate_answer_request (CandidateAnswerRequest): The new answer details, must be 2-500 characters.
    
    Returns:
        CandidateAnswerResponse: The updated candidate answer details.
    
    Raises:
        HTTPException (404): If no chat history entry is found with the specified ID
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            try:
                update_query = """
                    UPDATE chat_history
                    SET candidate_answer = %s
                    WHERE chat_history_id = %s
                    RETURNING chat_history_id, question_id, interview_id, candidate_answer
                """
                updated_record = execute_query(
                    conn, 
                    update_query, 
                    (candidate_answer_request.candidate_answer, chat_history_id), 
                    fetch_one=True,
                    commit=True
                )
                
                if not updated_record:
                    raise ChatHistoryNotFoundException(chat_history_id)
                
                return CandidateAnswerResponse(
                    chat_history_id=updated_record[0],
                    question_id=updated_record[1],
                    interview_id=updated_record[2],
                    candidate_answer=updated_record[3]
                )
            except Exception as e:
                logger.error(f"Error updating Candidate Answer: {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.post("/candidate_answer", response_model=dict)
async def add_candidate_answer(interview_id: int, question_id: int, candidate_answer: str):
    """
    Add a new candidate answer for a specific interview and question.
    
    Args:
        interview_id (int): The unique identifier of the interview.
        question_id (int): The unique identifier of the question being answered.
        candidate_answer (str): The candidate's answer to the question, must be 2-500 characters.
    
    Returns:
        dict: A dictionary containing:
            - chat_history_id (int): The ID of the newly created chat history entry
            - interview_id (int): The interview ID
            - question_id (int): The question ID
            - candidate_answer (str): The stored answer
    
    Raises:
        Exception: If there's an error adding the candidate answer
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            try:
                insert_query = """
                    INSERT INTO chat_history (interview_id, question_id, candidate_answer)
                    VALUES (%s, %s, %s)
                    RETURNING chat_history_id, interview_id, question_id, candidate_answer
                """
                result = execute_query(
                    conn,
                    insert_query,
                    (interview_id, question_id, candidate_answer),
                    fetch_one=True,
                    commit=True
                )
                
                return {
                    "chat_history_id": result[0],
                    "interview_id": result[1],
                    "question_id": result[2],
                    "candidate_answer": result[3]
                }
            except Exception as e:
                logger.error(f"Error adding candidate answer: {e}")
                raise Exception(f"Error adding candidate answer: {e}")
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/candidate_answer/{chat_history_id}")
async def delete_candidate_answer(chat_history_id: int):
    """
    Delete a specific candidate answer from the chat history.
    
    Args:
        chat_history_id (int): The unique identifier of the chat history entry to delete.
    
    Returns:
        dict: A message confirming successful deletion:
            {"message": "Candidate Answer deleted successfully"}
    
    Raises:
        HTTPException (404): If no chat history entry is found with the specified ID
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            try:
                delete_query = """
                    DELETE FROM chat_history 
                    WHERE chat_history_id = %s 
                    RETURNING chat_history_id
                """
                deleted_feedback = execute_query(
                    conn, 
                    delete_query, 
                    (chat_history_id,), 
                    fetch_one=True,
                    commit=True
                )
                
                if not deleted_feedback:
                    raise ChatHistoryNotFoundException(chat_history_id)
                
                return {"message": "Candidate Answer deleted successfully"}
            except Exception as e:
                logger.error(f"Error deleting candidate answer JSON : {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9094)