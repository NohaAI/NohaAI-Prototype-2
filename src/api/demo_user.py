from fastapi import FastAPI

import logging
import re
import uvicorn
#from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,
from src.dao.utils.execute_query import execute_query
from src.dao.utils.connect import get_db_connection
from src.schemas.dao import UserRequest
from src.utils.response_helper import decorate_response
from fastapi import status
from datetime import datetime
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

async def initialize_interview(user_name, user_email):
    """
    Create a new user with input validation.
    
    Args:
        user_request (UserRequest): Request containing user name and email
        
    Returns:
        JSONResponse: Standardized response with interview ID
        
    Raises:
        HTTPException: 500 for errors
    """
    try:
        #TODO: CHECK USER_ID FIRST IF DOESN'T CREATE NEW
        with get_db_connection() as conn:
            if not is_valid_email(user_email):
                raise ValueError("INVALID EMAIL FORMAT !!")
            if not user_name:
                raise ValueError("USER NAME CAN NOT BE EMPTY !!")
            check_user_query = """
                SELECT user_id
                FROM Users
                WHERE name = %s
            """
            insert_user_query = """
                INSERT INTO Users (name, email_id)
                VALUES (%s, %s)
                RETURNING user_id
            """
            check_user = execute_query(
                conn,
                check_user_query,
                (user_name,)
            )
            if check_user:
                user_id = check_user[0]
            else:
                user_id = execute_query(
                    conn,
                    insert_user_query,
                    (user_name, user_email),
                    commit=True
                )
                user_id = user_id[0]
            insert_interview_query = """
                INSERT INTO Interview (user_id, interview_date, interview_recording_url)
                VALUES (%s, %s, %s)
                RETURNING interview_id
            """
            interview_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            interview_recording_url=f"N/A"
            interview_id = execute_query(
                conn,
                insert_interview_query,
                (user_id, interview_date, interview_recording_url),
                commit=True,
            )
            return user_id, interview_id[0] # executre query returns a tuple 
            
    except Exception as e:
        raise e
    
    
app = FastAPI()

@app.post("/demo-service/", response_model=None)
async def initialize_interview_API(user_request: UserRequest):
    """
    Create a new user with input validation.
    
    Args:
        user_request (UserRequest): Request containing user name and email
        
    Returns:
        JSONResponse: Standardized response with interview ID
        
    Raises:
        HTTPException: 500 for errors
    """
    try:
        with get_db_connection() as conn:
            
            insert_user_query = """
                INSERT INTO Users (name, email_id)
                VALUES (%s, %s)
                RETURNING user_id
            """
            
            user_id = execute_query(
                conn,
                insert_user_query,
                (user_request.name, user_request.email_id),
                commit=True
            )
            insert_interview_query = """
                INSERT INTO Interview ( user_id, interview_date, interview_recording_url)
                VALUES (%s, %s, %s)
                RETURNING interview_id
            """
            interview_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            interview_recording_url=f"https://recordings.example.com/{user_request.name}.mp3"
            interview_id = execute_query(
                conn,
                insert_interview_query,
                ( user_id, interview_date, interview_recording_url),
                commit=True,
            )
            if not user_id:
                return decorate_response(
                    succeeded=False,
                    message="Failed to create user",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return decorate_response(
                succeeded=True,
                message={"interview_id": interview_id},
                status_code=status.HTTP_200_OK
            )
            
    except Exception as e:
        return decorate_response(
            succeeded=False,
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9400)