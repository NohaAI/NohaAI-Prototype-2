from fastapi import FastAPI
from src.utils import logger as LOGGER
import uvicorn
#from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,
from src.dao.utils.execute_query import execute_query
from src.dao.utils.connect import get_db_connection
from src.dao.exceptions import UserNotFoundException
from src.dao.exceptions import DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError
from src.schemas.dao import UserRequest,UserResponse

app = FastAPI()

@app.get("/user-service/{user_id}", response_model=UserResponse)
async def get_user_metadata(user_id: int):
    """
    Retrieve user information by ID.
    
    Args:
        user_id (int): ID of the user to retrieve
        
    Returns:
        UserResponse: User details
        
    Raises:
        Exception: 404 if user not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            user = execute_query(
                conn,
                "SELECT user_id, name, email_id FROM Users WHERE user_id = %s",
                (user_id,)
            )
            
            if not user:
                raise UserNotFoundException(user_id)
            
            return {"user_id": user[0], "name": user[1], "email_id": user[2]}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e


@app.post("/user-service", response_model=UserResponse)
async def add_user(name: str, email_id: str):
    """
    Create a new user.
    
    Args:
        name (str): Name of the user to create
        
    Returns:
        UserResponse: Created user details
        
    Raises:
        Exception: 503 for connection issues, 400 for invalid data,
                      500 for other errors
    """
    try:
        with get_db_connection() as conn:
            
            cur_query = "INSERT INTO Users (name, email_id) VALUES (%s ,%s) RETURNING user_id, name, email_id"
            user = execute_query(
                conn,
                cur_query,
                (name, email_id, ),
                commit=True
            )
            
            return {"user_id": user[0], "name": user[1], "email_id": user[2]}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/user-service/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserRequest):
    """
    Update an existing user's information.
    
    Args:
        user_id (int): ID of the user to update
        user (UserRequest): Updated user information
        
    Returns:
        UserResponse: Updated user details
        
    Raises:
        Exception: 404 if user not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            update_query = "UPDATE Users SET name = %s WHERE user_id = %s RETURNING user_id, name"
            updated_user = execute_query(
                conn,
                update_query,
                (user.name, user_id),
                commit=True
            )
            
            if not updated_user:
                raise UserNotFoundException(user_id)
            
            return {"user_id": updated_user[0], "name": updated_user[1]}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/user-service/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    """
    Delete a user by ID.
    
    Args:
        user_id (int): ID of the user to delete
        
    Returns:
        dict: Success message
        
    Raises:
        Exception: 404 if user not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            delete_query = "DELETE FROM Users WHERE user_id = %s RETURNING user_id"
            deleted_user = execute_query(
                conn,
                delete_query,
                (user_id,),
                commit=True
            )
            
            if not deleted_user:
                raise UserNotFoundException(user_id)
            
            return {"message": "User deleted successfully"}
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e