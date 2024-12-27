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
from DB_Utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from app.DAO.Exceptions import UserNotFoundException,InterviewNotFoundException
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request and response validation
class InterviewResponse(BaseModel):
    """
    Response model for interview data.

    Attributes:
        interview_id (int): Unique indentifier for interviews
        user_id (int): ID of the user giving the interview
        interview_date(datetime): Date at which the interview is scheduled
        interview_recording_url(str): Link to the interview recording url
    """
    interview_id: int
    user_id: int
    interview_date: datetime
    interview_recording_url: str

class InterviewRequest(BaseModel):
    """
    Request model for creating or updating Interview data.

    Attributes:
        interview_date(datetime): Date at the which is the interview is scheduled
        interview_recording_url(str): Link to the interview recording url
    """
    interview_date: Optional[datetime] = None
    interview_recording_url: Optional[str] = None

app = FastAPI()

@app.post("/interviews", response_model=InterviewResponse)
async def add_interview(user_id: int, interview_date: datetime, interview_recording_url: str):
    """
    Add a new interview to the database.
    
    Args:
        user_id (int): ID of the user giving the interview
        interview_date(datetime): Date at the which is the interview is scheduled
        interview_recording_url(str): Link to the interview recording url
    Returns: 
        InterviewResponse:Added interview details

    Raises: 
        HTTPException: 400 for validation errors, 503 for connection issues,
                      500 for other database errors
    """
    try: 
        with get_db_connection() as conn:
            # Check if the user exists in the database
            user_check_query = "SELECT name FROM Users WHERE user_id = %s"
            user_exists = execute_query(conn, user_check_query, (user_id,))[0]
            if not user_exists:
                logger.error(f"User with ID {user_id} not found in the database")
                raise UserNotFoundException(user_id)

            # Insert the new interview into the database
            insert_query = """
                INSERT INTO Interviews ( user_id, interview_date, interview_recording_url)
                VALUES (%s, %s, %s)
                RETURNING interview_id, user_id, interview_date, interview_recording_url
            """
            interview = execute_query(
                conn,
                insert_query,
                ( user_id, interview_date, interview_recording_url),
                commit=True,
            )

            # Return the newly added interview as a response
            return InterviewResponse(
                interview_id=interview[0],
                user_id=interview[1],
                interview_date=interview[2],
                interview_recording_url=interview[3],
            )
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.get("/interviews/{interview_id}", response_model=InterviewResponse)
async def get_interview(interview_id: int):
    """
    Retrieves interview details by ID

    Args:
        interview_id (int): ID of the interview to retrieve the details
    
    Returns:
        InterviewResponse:Interview Details
    
    Raises:
        HTTPException: 404 if interview not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            # Query to fetch interview details by ID
            query = """
                SELECT interview_id, user_id, interview_date, interview_recording_url
                FROM Interviews
                WHERE interview_id = %s
            """
            interview = execute_query(conn, query, (interview_id,))
            if not interview:
                logger.error(f"Interview with ID {interview_id} not found in the database")
                raise InterviewNotFoundException(interview_id)

            # Return the interview details
            return InterviewResponse(
                interview_id=interview[0],
                user_id=interview[1],
                interview_date=interview[2],
                interview_recording_url=interview[3],
            )
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/interviews/{interview_id}", response_model=InterviewResponse)
async def update_interview(interview_id: int, interview: InterviewRequest):
    """
    Update details of an interview.
    
    Args:
        interview_id (int): ID of the interview to update
        interview (InterviewRequest): New data for the interview
        
    Returns:
        InterviewResponse: Updated interview details
        
    Raises:
        HTTPException: 404 if interview not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            #Dynamic update query based on provided fields
            update_fields = []
            params = []
            if interview.interview_date:
                update_fields.append("interview_date = %s")
                params.append(interview.interview_date)
            if interview.interview_recording_url:
                update_fields.append("interview_recording_url = %s")
                params.append(interview.interview_recording_url)

            if not update_fields:
                raise Exception("No update fields")

            params.append(interview_id)  # Add interview ID to the parameters

            # Update the interview in the database
            update_query = f"""
                UPDATE Interviews
                SET {', '.join(update_fields)}
                WHERE interview_id = %s
                RETURNING interview_id, user_id, interview_date, interview_recording_url
            """
            updated_interview = execute_query(conn, update_query, params, commit=True)
            if not updated_interview:
                error.logger(f"Interview with ID {interview_id} not found in the database")
                raise InterviewNotFoundException(interview_id)

            # Return the updated interview details
            return InterviewResponse(
                interview_id=updated_interview[0],
                user_id=updated_interview[1],
                interview_date=updated_interview[2],
                interview_recording_url=updated_interview[3],
            )
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/interviews/{interview_id}")
async def delete_interview(interview_id: int):
    """
    Delete an interview by ID.
    
    Args:
        interview_id (int): ID of the interview to delete
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if interview not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            # Delete query to remove the interview from the database
            delete_query = """
                DELETE FROM Interviews
                WHERE interview_id = %s
                RETURNING interview_id
            """
            deleted_interview = execute_query(conn, delete_query, (interview_id,), commit=True)
            if not deleted_interview:
                logger.error(f"Interview with ID {interview_id} not found in the database")
                raise InterviewNotFoundException(interview_id)

            # Return success message
            return {"message": "Interview deleted successfully"}
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9097)