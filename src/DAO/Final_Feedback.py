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

# Configure application-wide logging to track and record application events and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables to securely configure database connection parameters
load_dotenv()


# Custom Exceptions
class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    pass

class DatabaseQueryError(Exception):
    """Raised when query execution fails"""
    pass

class DatabaseOperationError(Exception):
    """Raised for general database operations failures"""
    pass


# Define database configuration using environment variables with fallback default values
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 5432))
}
# Create a connection pool to manage database connections efficiently and reduce connection overhead
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)

# Pydantic model to define the response structure for final evaluation with input validation
class FinalDecisionResponse(BaseModel):
    """
    Response model for FinalDecision.

    Attributes:
        final_evaluation_id (int): Unique identifier to the table final_evaluations
        interview_id (int): Unique indentifier for interviews
        final_feedback (str): A string that contains closing remarks of an interview
    """
    final_evaluation_id : int
    interview_id : int
    final_feedback : str = Field(...,max_length=500)

# Pydantic model to validate incoming final decision requests
class FinalDecisionRequest(BaseModel):
    """
    Request model for updating and adding final decision.

    Attributes:
        final_feedback (str): A string that contains closing remarks of an interview
    """
    final_feedback : str = Field(...,max_length=500)

# Context manager to manage database connections
@contextmanager
def get_db_connection():
    """
    Database connection management with error handling.
    
    Yields:
        connection: Database connection from the connection pool
        
    Raises:
        DatabaseConnectionError: If connection cannot be established
    """
    connection = None
    try:
        connection = connection_pool.getconn()
        yield connection
    except psycopg2.OperationalError as e:
        logger.error(f"Failed to get database connection: {e}")
        raise DatabaseConnectionError(f"Cannot establish database connection: {str(e)}")
    finally:
        if connection is not None:
            try:
                connection_pool.putconn(connection)
            except Exception as e:
                logger.error(f"Failed to return connection to pool: {e}")

def execute_query(connection, query, params=None, fetch_one=True, commit=False):
    """
    Execute database queries with enhanced error handling.
    
    Args:
        connection: Database connection
        query (str): SQL query to execute
        params (tuple, optional): Query parameters
        fetch_one (bool): If True, fetch single row
        commit (bool): If True, commit transaction
        
    Returns:
        Query results
        
    Raises:
        DatabaseConnectionError: For connection issues
        DatabaseQueryError: For query execution issues
        DatabaseOperationError: For other database operations issues
    """
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        
        if commit:
            try:
                connection.commit()
            except psycopg2.Error as e:
                connection.rollback()
                logger.error(f"Transaction commit failed: {e}")
                raise DatabaseOperationError(f"Failed to commit transaction: {str(e)}")
        
        result = cursor.fetchone() if fetch_one else cursor.fetchall()
        if result is None and fetch_one:
            return None
        return result

    except psycopg2.OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseConnectionError(f"Database connection failed: {str(e)}")
    
    except psycopg2.DataError as e:
        logger.error(f"Invalid data format: {e}")
        raise DatabaseQueryError(f"Invalid data format: {str(e)}")
    
    except psycopg2.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise DatabaseOperationError(f"Database constraint violation: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        raise DatabaseOperationError(f"Unexpected error: {str(e)}")
    
    finally:
        if cursor is not None:
            cursor.close()

app = FastAPI()

# Endpoint to retrieve a specific final feedback by final evaluation ID
@app.get("/feedback/{final_evaluation_id}", response_model=FinalDecisionResponse)
async def get_feedback(final_evaluation_id: int):
    """
    Retrieves final feedback from final_evaluations table.

    Args:
        final_evaluaiaton_id (int): Unique indentifier for final evaluation.

    Returns:
        FinalDecisionResponse: Details of the final evaluation

    Raises:
        HTTPException: 404 for Evaluation not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # SQL query to fetch final evaluation details from final_evaluations table
                query = """
                    SELECT final_evaluation_id, interview_id, final_feedback
                    FROM final_evaluations
                    WHERE final_evaluation_id = %s
                """
                result = execute_query(conn, query, (final_evaluation_id,), fetch_one=True)
                
                # Raise 404 error if no matching record is found
                if not result:
                    raise HTTPException(status_code=404, detail="Evaluation not found")
                
                # Return the final decision response with retrieved details
                return FinalDecisionResponse(
                    final_evaluation_id=result[0],
                    interview_id=result[1],
                    final_feedback=result[2]
                )
            except Exception as e:
                # Log any unexpected errors during feedback retrieval
                logger.error(f"Error retrieving feedback: {e}")
                raise e
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
        
# Endpoint to update an existing final feedback
@app.put("/feedback/{final_evaluation_id}", response_model=FinalDecisionResponse)
async def update_feedback(final_evaluation_id: int, feedback_request: FinalDecisionRequest):
    """
    Updates final feedback .

    Args:
        final_evaluaiaton_id (int): Unique indentifier for final evaluation.
        feedback_request (FinalDecisionRequest): New data for final feedback
    Returns:
        FinalDecisionResponse: Details of updated final evaluation

    Raises:
        HTTPException: 404 for Evaluation not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # SQL query to update final feedback and return updated record
                update_query = """
                    UPDATE final_evaluations
                    SET final_feedback = %s
                    WHERE final_evaluation_id = %s
                    RETURNING final_evaluation_id, interview_id, final_feedback
                """
                updated_record = execute_query(
                    conn, 
                    update_query, 
                    (feedback_request.final_feedback, final_evaluation_id), 
                    fetch_one=True,
                    commit=True
                )
                
                # Raise 404 error if no record was updated
                if not updated_record:
                    raise HTTPException(status_code=404, detail="Evaluation not found")
                
                # Return the updated final decision response
                return FinalDecisionResponse(
                    final_evaluation_id=updated_record[0],
                    interview_id=updated_record[1],
                    final_feedback=updated_record[2]
                )
            except Exception as e:
                # Log any unexpected errors during feedback update
                logger.error(f"Error updating feedback: {e}")
                raise
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseQueryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseOperationError as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to add a new final feedback for a specific interview
@app.post("/feedback", response_model=FinalDecisionResponse)
async def add_feedback(interview_id: int, feedback_request: FinalDecisionRequest):
    """
    Add a new question evaluation to the database.
    
    Args:
        interview_id (int): ID of the interview
        feedback_request(FinalDecisionRequest): New data for final feedback
    Returns: 
        QuestionEvaluationResponse:Added question evaluation details

    Raises: 
        HTTPException: 404 for interview/question not found, 400 for validation errors, 503 for connection issues,
                      500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Check if an existing evaluation for the interview has a null feedback
                check_query = """
                    SELECT final_evaluation_id FROM final_evaluations 
                    WHERE interview_id = %s AND final_feedback IS NULL
                """
                existing_evaluation = execute_query(conn, check_query, (interview_id,), fetch_one=True)
                
                if existing_evaluation:
                    # Update existing evaluation with the new feedback
                    update_query = """
                        UPDATE final_evaluations
                        SET final_feedback = %s
                        WHERE interview_id = %s AND final_feedback IS NULL
                        RETURNING final_evaluation_id, interview_id, final_feedback
                    """
                    result = execute_query(
                        conn,
                        update_query,
                        (feedback_request.final_feedback, interview_id),
                        fetch_one=True,
                        commit=True
                    )
                    
                    return FinalDecisionResponse(
                        final_evaluation_id=result[0],
                        interview_id=result[1],
                        final_feedback=result[2]
                    )
                
                # If no existing evaluation with null feedback, insert a new one
                insert_query = """
                    INSERT INTO final_evaluations (interview_id, final_feedback)
                    VALUES (%s, %s)
                    RETURNING final_evaluation_id, interview_id, final_feedback
                """
                result = execute_query(
                    conn,
                    insert_query,
                    (interview_id, feedback_request.final_feedback),
                    fetch_one=True,
                    commit=True
                )
                
                return FinalDecisionResponse(
                    final_evaluation_id=result[0],
                    interview_id=result[1],
                    final_feedback=result[2]
                )
            except Exception as e:
                # Log any unexpected errors during feedback addition
                logger.error(f"Error adding feedback: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# Endpoint to delete a final feedback by final evaluation ID
@app.delete("/feedback/{final_evaluation_id}")
async def delete_feedback(final_evaluation_id: int):
    """
    Delete a final feedback by ID.
    
    Args:
        final_evaluation_id (int): ID of the final feedback to delete
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if evaluation not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # SQL query to delete record and return deleted record's ID
                delete_query = """
                    DELETE FROM final_evaluations 
                    WHERE final_evaluation_id = %s 
                    RETURNING final_evaluation_id
                """
                deleted_feedback = execute_query(
                    conn, 
                    delete_query, 
                    (final_evaluation_id,), 
                    fetch_one=True,
                    commit=True
                )
                
                # Raise 404 error if no record was deleted
                if not deleted_feedback:
                    raise HTTPException(status_code=404, detail="Evaluation not found")
                
                # Return success message
                return {"message": "Feedback deleted successfully"}
            except Exception as e:
                # Log any unexpected errors during feedback deletion
                logger.error(f"Error deleting feedback: {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9100)