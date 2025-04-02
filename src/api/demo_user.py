from fastapi import FastAPI
import logging
import re
import uvicorn
#from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,
from src.dao.utils.execute_query import execute_query
from src.dao.utils.connect import get_db_connection
from src.schemas.dao import UserRequest
from fastapi import status
from datetime import datetime
from src.utils import logger as LOGGER
from src.config import logging_config as LOGCONF
from src.config import constants as CONST
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

async def initialize_interview(user_name, user_email):
    LOGGER.log_info("\n>>>>>>>>>>>FUNCTION [initialize_interview] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")
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
            LOGGER.pretty_log("inserting interview_query ...", user_id, LOGCONF.DEBUG2)
            
            insert_interview_query = """
                INSERT INTO Interview (user_id, interview_date, interview_recording_url)
                VALUES (%s, %s, %s)
                RETURNING interview_id
            """
            LOGGER.pretty_log("inserting interview_query statement ...", insert_interview_query,  LOGCONF.DEBUG2)
            interview_date = datetime.now(CONST.IST).strftime('%Y-%m-%d %H:%M:%S.%f')
            interview_recording_url="N/A"
            LOGGER.pretty_log("interview_date", interview_date,  LOGCONF.DEBUG2)
            LOGGER.pretty_log("interview_recording_url", interview_recording_url,  LOGCONF.DEBUG2)

            interview_id = execute_query(
                conn,
                insert_interview_query,
                (user_id, interview_date, interview_recording_url),
                commit=True,
            )
            LOGGER.pretty_log("interview_id", interview_id,  LOGCONF.DEBUG2)
            LOGGER.pretty_log("interview_id"[0], interview_id[0],  LOGCONF.DEBUG2)
            return user_id, interview_id[0] # execute query returns a tuple 
            
    except Exception as e:
        raise e
    LOGGER.log_info("\n>>>>>>>>>>>FUNCTION EXIT [initialize_interview] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    
app = FastAPI()

# @app.post("/demo-service/", response_model=None)
# async def initialize_interview_API(user_request: UserRequest):
#     """
#     Create a new user with input validation.
    
#     Args:
#         user_request (UserRequest): Request containing user name and email
        
#     Returns:
#         JSONResponse: Standardized response with interview ID
        
#     Raises:
#         HTTPException: 500 for errors
#     """
#     try:
#         with get_db_connection() as conn:
            
#             insert_user_query = """
#                 INSERT INTO Users (name, email_id)
#                 VALUES (%s, %s)
#                 RETURNING user_id
#             """
            
#             user_id = execute_query(
#                 conn,
#                 insert_user_query,
#                 (user_request.name, user_request.email_id),
#                 commit=True
#             )
#             insert_interview_query = """
#                 INSERT INTO Interview ( user_id, interview_date, interview_recording_url)
#                 VALUES (%s, %s, %s)
#                 RETURNING interview_id
#             """
#             interview_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
#             interview_recording_url=f"https://recordings.example.com/{user_request.name}.mp3"
#             interview_id = execute_query(
#                 conn,
#                 insert_interview_query,
#                 ( user_id, interview_date, interview_recording_url),
#                 commit=True,
#             )
#             if not user_id:
#                 return decorate_response(
#                     succeeded=False,
#                     message="Failed to create user",
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )
            
#             return decorate_response(
#                 succeeded=True,
#                 message={"interview_id": interview_id},
#                 status_code=status.HTTP_200_OK
#             )
            
#     except Exception as e:
#         return decorate_response(
#             succeeded=False,
#             message="An unexpected error occurred",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )