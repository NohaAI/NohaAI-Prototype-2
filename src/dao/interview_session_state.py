from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import Optional
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.exceptions import InterviewNotFoundException
import uvicorn
# Configure application-wide logging to track and record application events and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Endpoint to retrieve a specific final evaluation JSON by final evaluation ID
@app.get("/interview-session-state/{interview_id}")
async def get_interview_session_state(interview_id: int):
    """
    Retrieve a specific final evaluation JSON by ID.

    Args:
        interview_id (int): Unique identifier for the final evaluation

    Returns:
        interview_session_state: Details of interview_session_state for an interview_id

    Raises:
        Exception: 404 for Interview not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            
                # SQL query to fetch final evaluation JSON details from interview_session_states table
            query = """
                SELECT interview_session_state
                FROM interview_session_state
                WHERE interview_id = %s
            """
            result = execute_query(conn, query, (interview_id,), fetch_one=True)
            
            # Raise 404 error if no matching record is found
            
            # Return the final evaluation JSON response with retrieved details
            return result[0]
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# Endpoint to update an existing final evaluation JSON
@app.put("/interview_session_state/{interview_id}")
async def update_interview_session_state(interview_id: int, interview_session_state :str):
    """
    Update an existing final evaluation JSON.

    Args:
        interview_id (int): ID of the evaluation to update
        interview_session_state:  New interview_session_state

    Returns:
        True: Returns True suggesting update was made

    Raises:
        Exception: 404 for interview_session_state not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Check if evaluation exists
                check_query = """
                    SELECT interview_id FROM interview_session_state 
                    WHERE interview_id = %s
                """
                exists = execute_query(conn, check_query, (interview_id,), fetch_one=True)
                if not exists:
                    raise InterviewNotFoundException(interview_id)
                
                # Prepare update query with optional fields
                

                # Execute the update query
                update_query = f"""
                    UPDATE interview_session_state
                    SET interview_session_state = %s
                    WHERE interview_id = %s
                    RETURNING interview_session_state
                """
                updated_record = execute_query(
                    conn, 
                    update_query, 
                    (interview_session_state, interview_id, ), 
                    fetch_one=True,
                    commit=True
                )
                
                return f"INTERVIEW SESSION STATE SUCCESSFULY UPDATED : {update_interview_session_state}"
            except Exception as e:
                logger.error(f"Error updating final evaluation: {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
        
# Endpoint to add a new final evaluation JSON for a specific interview
@app.post("/interview_session_state")
async def add_interview_session_state(interview_id: int, interview_session_state):
    """
    Add a new final evaluation JSON for a specific interview.

    Args:
        interview_id (int): ID of the interview
        interview_session_state : interview_session_state to be added for provided interview ID

    Returns:
        FinalEvaluationResponse: added session_state_details details

    Raises:
        Exception: 404 for interview_session_state not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            # Check if an existing evaluation for the interview has a null evaluation JSON
            check_query = """
                SELECT user_id FROM Interview
                WHERE interview_id = %s
            """
            check_interview = execute_query(conn, check_query, (interview_id,), fetch_one=True)
            
            if not check_query:
                raise InterviewNotFoundException
                # Update existing evaluation with the new evaluation JSON
            add_interview_session_state_query = """
                INSERT INTO interview_session_state(interview_id,interview_session_state)
                VALUES(%s, %s)
                RETURNING interview_id, interview_session_state
            """
            result = execute_query(
                conn,
                add_interview_session_state_query,
                (interview_id, interview_session_state,),
                fetch_one=True,
                commit=True
            )
            
            return {"interview_id" : result[0], "interview_session_state" : result[1] }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# Endpoint to delete a final evaluation JSON by final evaluation ID
@app.delete("/interview_session_state/{interview_id}")
async def delete_interview_session_state(interview_id: int):
    """
    Delete a final evaluation JSON by ID.

    Args:
        interview_id (int): ID of the evaluation to delete

    Returns:
        dict: Success message
    Raises:
        Exception: 404 for interview_session_state not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # SQL query to delete record and return deleted record's ID
                delete_query = """
                    DELETE FROM interview_session_state 
                    WHERE interview_id = %s 
                    RETURNING interview_id
                """
                deleted_feedback = execute_query(
                    conn, 
                    delete_query, 
                    (interview_id,), 
                    fetch_one=True,
                    commit=True
                )
                
                # Raise 404 error if no record was deleted
                if not deleted_feedback:
                    raise InterviewNotFoundException(interview_id)
                
                # Return success message
                return {"message": "Interview session state deleted successfully"}
            except Exception as e:
                # Log any unexpected errors during evaluation JSON deletion
                logger.error(f"Error deleting interview session state : {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9100)