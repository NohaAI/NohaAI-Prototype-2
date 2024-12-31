from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import List, Optional
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import uvicorn
from src.dao.utils.DB_Utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.Exceptions import QuestionNotFoundException,QuestionTypeNotFoundException
# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionResponse(BaseModel):
    """
    Pydantic model representing the response structure for a question.
    
    Attributes:
        question_id (int): Unique identifier for the question
        question (str): The actual question text, length between 10-500 characters
        question_type (str): Category or type of the question, length between 3-50 characters
        question_type_id (int): Unique identifier for the question type
    """
    question_id: int
    question: str = Field(..., min_length=10, max_length=500)
    question_type: str = Field(..., min_length=3, max_length=50)
    question_type_id: int

class QuestionRequest(BaseModel):
    """
    Pydantic model for incoming question requests (creation/updates).
    
    Attributes:
        question (Optional[str]): Question text, optional for partial updates
        question_type (Optional[str]): Question category, optional for partial updates
    """
    question: Optional[str] = Field(None, min_length=10, max_length=500)
    question_type: Optional[str] = Field(None, min_length=3, max_length=50)
    

app = FastAPI()

@app.get("/question-service/{question_id}", response_model=QuestionResponse)
async def get_question_metadata(question_id: int):
    """
    Retrieve a question by its ID.
    
    Args:
        question_id (int): ID of the question to retrieve
    
    Returns:
        QuestionResponse: Question details
        
    Raises:
        HTTPException: 404 if question not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            question_query = """
                SELECT question_id, question, question_type, question_type_id 
                FROM Question
                WHERE question_id = %s
            """
            question = execute_query(conn, question_query, (question_id,))
            
            if not question:
                logger.erro(f"Question with ID {question_id} not found in the database")
                raise QuestionNotFoundException(question_id)
                
            return {
                "question_id": question[0],
                "question": question[1],
                "question_type": question[2],
                "question_type_id": question[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.post("/question-service", response_model=QuestionResponse)
async def add_question(question: QuestionRequest):
    """
    Create a new question.
    
    Args:
        question (QuestionRequest): Question details for creation
    
    Returns:
        QuestionResponse: Created question details
        
    Raises:
        HTTPException: 503 for connection issues, 400 for invalid data,
                      500 for other errors
    """
    try:
        with get_db_connection() as conn:      
            insert_query = """
                INSERT INTO Question (question, question_type, question_type_id)
                VALUES (%s, %s, %s)
                RETURNING question_id, question, question_type, question_type_id
            """
            new_question = execute_query(
                conn, 
                insert_query, 
                (question.question, question.question_type, 1), 
                commit=True
            )
            
            return {
                "question_id": new_question[0],
                "question": new_question[1],
                "question_type": new_question[2],
                "question_type_id": new_question[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/question-service/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question: QuestionRequest, question_type_id: int):
    """
    Update an existing question by its ID.
    
    Args:
        question_id (int): ID of the question to update
        question (QuestionRequest): Updated question details
        question_type_id (int): New question type ID
    
    Returns:
        QuestionResponse: Updated question details
        
    Raises:
        HTTPException: 404 if question not found, 400 if no update fields provided,
                      503 for connection issues, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            verify_type_query = "SELECT question_type FROM Question WHERE question_type_id = %s LIMIT 1"
            existing_type = execute_query(conn, verify_type_query, (question_type_id,))
            
            if not existing_type:
                logger.error(f"Question type with ID {question_type_id} not found in the database ")
                raise QuestionTypeNotFoundException(question_type_id)
            
            update_fields = []
            params = []
            
            if question.question is not None:
                update_fields.append("question = %s")
                params.append(question.question)
            
            update_fields.append("question_type_id = %s")
            params.append(question_type_id)
            
            if question.question_type is not None:
                update_fields.append("question_type = %s")
                params.append(question.question_type)
            
            if not update_fields:
                logger.error(f"Empty update fields provided to update_question")
                raise Exception("No update fields provided")
            
            update_query = f"""
                UPDATE Question
                SET {', '.join(update_fields)}
                WHERE question_id = %s
                RETURNING question_id, question, question_type, question_type_id
            """
            params.append(question_id)
            
            updated_question = execute_query(
                conn, 
                update_query, 
                tuple(params), 
                commit=True
            )
            
            if not updated_question:
                logger.error(f"Question with ID {question_id} not found in the database")
                raise QuestionNotFoundException(question_id)
            return {
                "question_id": updated_question[0],
                "question": updated_question[1],
                "question_type": updated_question[2],
                "question_type_id": updated_question[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.delete("/question-service/{question_id}", response_model=dict)
async def delete_question(question_id: int):
    """
    Delete a question by its ID.
    
    Args:
        question_id (int): ID of the question to delete
    
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if question not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            delete_query = "DELETE FROM Question WHERE question_id = %s RETURNING question_id"
            deleted_question = execute_query(
                conn, 
                delete_query, 
                (question_id,), 
                commit=True
            )
            
            if not deleted_question:
                logger.error(f"Question with ID {question_id} not found in the database")
                raise QuestionNotFoundException(question_id)
            return {"message": "Question deleted successfully"}

    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9095)