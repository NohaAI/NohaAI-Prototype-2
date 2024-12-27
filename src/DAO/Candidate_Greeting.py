from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import List, Optional
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from DB_Utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool

class GreeterResponse(BaseModel):
    # Defines the structure of the response for the greeter service
    user_id: int
    user_name: str
    question_id: int
    question: str
    greeting: str

# Initialize FastAPI application
app = FastAPI()

@app.get("/greeter-service", response_model=GreeterResponse)
async def greet_candidate(user_id: int):
    """
    Generate a personalized greeting for a candidate with a random interview question.
    
    Workflow:
    1. Retrieve user details based on user_id
    2. Select a random interview question
    3. Create a personalized greeting
    
    Raises:
        HTTPException: If user not found or no questions available
    """
    with get_db_connection() as conn:
        try:
            # Fetch user details
            user_query = "SELECT user_id, name FROM Users WHERE user_id = %s"
            user = execute_query(conn, user_query, (user_id,))
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Select a random interview question
            question_query = "SELECT question_id, question, question_type FROM Questions ORDER BY RANDOM() LIMIT 1"
            question = execute_query(conn, question_query)
            
            if not question:
                raise HTTPException(status_code=404, detail="No questions found")
            
            # Generate personalized greeting with user and question details
            greeting = (
                f"Hi {user[1]}, let's get started with the interview. "
                f"I want you to answer the following {question[2]} question for me : {question[1]}"
            )
            
            return {
                "user_id": user[0],
                "user_name": user[1],
                "question_id": question[0],
                "question": question[1],
                "question_type": question[2],
                "greeting": greeting
            }
        
        except Exception as e:
            logger.error(f"Error in greeter service: {e}")
            raise e