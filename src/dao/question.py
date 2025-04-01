from fastapi import FastAPI
import uvicorn
from src.dao.utils.execute_query import execute_query
from src.dao.utils.connect import get_db_connection
from src.dao.exceptions import DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError
from src.dao.exceptions import QuestionNotFoundException, QuestionTypeNotFoundException, NoQuestionForComplexityException
from src.schemas.dao import QuestionResponse,QuestionRequest
# Logging Configuration
from src.utils import logger as LOGGER

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
        Exception: 404 if question not found, 503 for connection issues,
                      400 for invalid data, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            question_query = """
                SELECT question_id, question, question_type, question_type_id, complexity 
                FROM Question
                WHERE question_id = %s
            """
            question_metadata = execute_query(conn, question_query, (question_id,))
            
            if not question_metadata:
                LOGGER.log_error(f"Question with ID {question_id} not found in the database")
                raise QuestionNotFoundException(question_id)
                
            return {
                "question_id": question_metadata[0],
                "question": question_metadata[1],
                "question_type": question_metadata[2],
                "question_type_id": question_metadata[3],
                "comeplxity": question_metadata[4]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
#TODO: SHOULD TAKE IN DIFFICULTY TYPE AND FETCH A RANDOM QUESTION
@app.get("/question-service")
async def get_random_question_metadata(complexity: int, question_list: list[int]):
    try:
        with get_db_connection() as conn:
            LOGGER.log_info(f"QUESTION LIST RECEIVED IN QUESTION.PY {question_list} \n")
            LOGGER.log_info(f"TYPE OF QUESTION LIST RECEIVED IN QUESTION.PY {type(question_list)} \n")
            if len(question_list) == 0: 
                question_query = """
                    SELECT question_id, question,question_type_id, complexity FROM question
                    WHERE complexity =%s
                    ORDER BY RANDOM()
                    LIMIT 1;
                """
                get_question_metadata = execute_query(conn, question_query, (complexity,))
                if not get_question_metadata:
                    LOGGER.log_error(f"NO QUESTIONS FOUND IN THE DATABASE")
                    raise NoQuestionForComplexityException(complexity)
            else:
                question_query = """
                    SELECT question_id, question,question_type_id, complexity FROM question
                    WHERE complexity =%s AND question_id NOT IN %s
                    ORDER BY RANDOM()
                    LIMIT 1;
                """
                get_question_metadata = execute_query(conn, question_query, (complexity, tuple(question_list),))
                if not get_question_metadata:
                    LOGGER.log_error(f"NO QUESTIONS FOUND IN THE DATABASE")
                    raise NoQuestionForComplexityException(complexity)
            return {
                "question_id": get_question_metadata[0],
                "question": get_question_metadata[1],
                "question_type_id": get_question_metadata[2],
                "complexity": get_question_metadata[3]
            }
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.post("/question-service", response_model=QuestionResponse)
async def add_question(question: str, question_type_id: int, complexity: int):
    """
    Create a new question.
    
    Args:
        question (QuestionRequest): Question details for creation
    
    Returns:
        QuestionResponse: Created question details
        
    Raises:
        Exception: 503 for connection issues, 400 for invalid data,
                      500 for other errors
    """
    try:
        with get_db_connection() as conn:     
            question_type_query="SELECT question_type FROM question_type WHERE question_type_id = %s"
            question_type=execute_query(conn,question_type_query,(question_type_id,))[0]

            insert_query = """
                INSERT INTO Question (question, question_type, question_type_id,complexity)
                VALUES (%s, %s, %s, %s)
                RETURNING question_id, question, question_type, question_type_id,complexity
            """
            new_question = execute_query(
                conn, 
                insert_query, 
                (question, question_type, question_type_id,complexity,), 
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
        Exception: 404 if question not found, 400 if no update fields provided,
                      503 for connection issues, 500 for other errors
    """
    try:
        with get_db_connection() as conn:
            verify_type_query = "SELECT question_type FROM Question WHERE question_type_id = %s LIMIT 1"
            existing_type = execute_query(conn, verify_type_query, (question_type_id,))
            
            if not existing_type:
                LOGGER.log_error(f"Question type with ID {question_type_id} not found in the database ", exc_info = True)
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
                LOGGER.log_error(f"Empty update fields provided to update_question", exc_info = True)
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
                LOGGER.log_error(f"Question with ID {question_id} not found in the database", exc_info=True)
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
        Exception: 404 if question not found, 503 for connection issues,
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
                LOGGER.log_error(f"Question with ID {question_id} not found in the database", exc_info = True)
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