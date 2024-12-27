from fastapi import FastAPI, HTTPException
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

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Connection Configuration
load_dotenv()  # Load environment variables from a .env file

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


DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 5432))
}

# Create a connection pool for PostgreSQL database
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)

# Define the schema for update requests
class QuestionEvaluationUpdateRequest(BaseModel):
    """
    Request model for updating question evaluation.

    Attributes:
        score (Optional[float]): Score to be updated
        question_evaluation_json (Optional[str]): Question evaluation json to be updated
    """
    score: Optional[float] = None
    question_evaluation_json: Optional[str] = Field(default=None,min_length=2,max_length=500    )

# Define the schema for adding new evaluations
class QuestionEvaluationRequest(QuestionEvaluationUpdateRequest):
    """
    Request model for adding question evaluation.

    Attributes:
        interview_id (int): ID of the interview
        question_id (int): ID of the question that was asked in interview with provided interview_id
    """
    interview_id: int
    question_id: int

# Define the response schema for question evaluations
class QuestionEvaluationResponse(BaseModel):
    """
    Response model for question evaluation.

    Attributes:
        question_evaluation_id (int): Unique identifier for interview question evaluation table
        interview_id (int): ID of the interview
        question_id (int): ID of the question that was asked in interview with provided interview_id
        score (Optional[float]): Score obtained by the candidate
        question_evaluation_json (Optional[str]): A string that contains question evaluation in a JSON format
    """
    question_evaluation_id: int
    interview_id: int
    question_id: int
    score: Optional[float]
    question_evaluation_json: Optional[str]

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
        HTTPException: 404 for Evaluation not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            try:
                query = """
                    SELECT question_evaluation_id, interview_id, question_id, score, question_evaluation_json
                    FROM interview_question_evaluations
                    WHERE question_evaluation_id = %s
                """
                result = execute_query(conn, query, (question_evaluation_id,), fetch_one=True)
                if not result:
                    raise HTTPException(status_code=404, detail="Evaluation not found")
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
        HTTPException: 404 if question evaluation not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Check if evaluation exists
                check_query = """
                    SELECT question_evaluation_id FROM interview_question_evaluations 
                    WHERE question_evaluation_id = %s
                """
                exists = execute_query(conn, check_query, (question_evaluation_id,), fetch_one=True)
                if not exists:
                    raise HTTPException(status_code=404, detail="Evaluation not found")
                
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
                    raise HTTPException(status_code=400, detail="No update fields provided")
                update_params.append(question_evaluation_id)

                # Execute the update query
                update_query = f"""
                    UPDATE interview_question_evaluations
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
        HTTPException: 404 for interview/question not found, 400 for validation errors, 503 for connection issues,
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
                    SELECT interview_id FROM interviews 
                    WHERE interview_id = %s
                """
                interview_exists = execute_query(conn, interview_check_query, (interview_id,), fetch_one=True)
                if not interview_exists:
                    logger.error(f"Interview")
                    raise HTTPException(status_code=404, detail="Interview not found")
                
                # Validate question existence
                question_check_query = """
                    SELECT question_id FROM questions 
                    WHERE question_id = %s
                """
                question_exists = execute_query(conn, question_check_query, (question_id,), fetch_one=True)
                if not question_exists:
                    raise HTTPException(status_code=404, detail="Question not found")
                
                # Insert the new evaluation
                insert_query = """
                    INSERT INTO interview_question_evaluations (
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
        HTTPException: 404 if evaluation not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            try:
                # Delete the evaluation and return its ID
                delete_query = """
                    DELETE FROM interview_question_evaluations 
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
                    raise HTTPException(status_code=404, detail="Evaluation not found")
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