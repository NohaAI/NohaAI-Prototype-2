from fastapi import FastAPI
import logging
import uvicorn
import json
from psycopg2.extras import execute_values
from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,connection_pool
from src.dao.exceptions import ChatHistoryNotFoundException,InterviewNotFoundException,QuestionNotFoundException
from src.schemas.dao import ChatHistoryRequest,ChatHistoryResponse
from src.dao.data_objects.chat_history import ChatHistoryRecord
# Configure application-wide logging to track and record application events and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Initialize FastAPI application for creating chat history service endpoints
app = FastAPI()

@app.get("/chat_history")
async def get_chat_history(interview_id: int):
    """
    Retrieve the complete chat history for a specific interview, including questions and answers.
    
    Args:
        interview_id (int): The unique identifier of the interview.
    
    Returns:
        list[dict]: A list of dictionaries containing the chat history, where each dictionary
                   contains:
                   - question (str): The interview question
                   - answer (str): The candidate's answer
    
    Raises:
        Exception: If there's an error retrieving the chat history
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            
            chat_history_query = """ 
                SELECT interview_id, question_id, turn_input_type, turn_input, turn_output, distilled_turn_output 
                FROM chat_history
                WHERE interview_id = %s    
            """
            chat_history_records = execute_query(
                conn,
                chat_history_query,
                (interview_id,),
                fetch_one = False
            )
            chat_history = ChatHistoryRecord()
            for record in chat_history_records:
                chat_history.add_record(*record)
            return chat_history
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.put("/chat_history/{chat_history_turn_id}", response_model=ChatHistoryResponse)
async def update_candidate_answer(chat_history_turn_id: int, chat_history_request: ChatHistoryRequest):
    """
    Update an existing chat history in the chat history.
    
    Args:
        chat_history_turn_id (int): The unique identifier of the chat history entry to update.
        chat_history_request (ChatHistoryRequest): The new answer details, must be 2-500 characters.
    
    Returns:
        ChatHistoryResponse: The updated chat history details.
    
    Raises:
        Exception (404): If no chat history entry is found with the specified ID
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            # Check existence
            check_query = "SELECT chat_history_turn_id FROM chat_history WHERE chat_history_turn_id = %s"
            exists = execute_query(conn, check_query, (chat_history_turn_id,), fetch_one=True)
            if not exists:
                raise ChatHistoryNotFoundException(chat_history_turn_id)

            # Build dynamic update
            update_fields = []
            update_params = []
            if chat_history_request.turn_input is not None:
                update_fields.append("turn_input = %s")
                update_params.append(chat_history_request.turn_input)
            if chat_history_request.turn_output is not None:
                update_fields.append("turn_output = %s")
                update_params.append(chat_history_request.turn_output)
            if chat_history_request.turn_input_type is not None:
                update_fields.append("turn_input_type = %s")
                update_params.append(chat_history_request.turn_input_type)
            
            if not update_fields:
                raise Exception("No update fields provided")
            
            update_params.append(chat_history_turn_id)

            update_query = f"""
                UPDATE chat_history
                SET {', '.join(update_fields)}
                WHERE chat_history_turn_id = %s
                RETURNING chat_history_turn_id, question_id, interview_id, turn_input, turn_output, turn_input_type
            """
            updated_record = execute_query(
                conn, 
                update_query, 
                update_params, 
                fetch_one=True,
                commit=True
            )
            
            return ChatHistoryResponse(
                chat_history_turn_id=updated_record[0],
                question_id=updated_record[1],
                interview_id=updated_record[2],
                turn_input=updated_record[3],
                turn_output=updated_record[4],
                turn_input_type=updated_record[5],
            )
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.post("/chat_history", response_model=dict)
async def add_chat_history(interview_id: int, question_id: int, turn_input: str,turn_output: str, distilled_turn_output: str ,turn_input_type: str):
    """
    Add a new chat history for a specific interview and question.
    
    Args:
        interview_id (int): The unique identifier of the interview.
        question_id (int): The unique identifier of the question being answered.
        candidate_answer (str): The candidate's answer to the question, must be 2-500 characters.
    
    Returns:
        dict: A dictionary containing:
            - chat_history_turn_id (int): The ID of the newly created chat history entry
            - interview_id (int): The interview ID
            - question_id (int): The question ID
            - candidate_answer (str): The stored answer
    
    Raises:
        Exception: If there's an error adding the chat history
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            interview_check_query="SELECT interview_id FROM interview WHERE interview_id = %s"
            interview=execute_query(conn,interview_check_query,(interview_id,))
            if not interview:
                raise InterviewNotFoundException
            question_check_query="SELECT question FROM question WHERE question_id = %s"
            question=execute_query(conn,question_check_query,(question_id,))
            if not question:
                raise QuestionNotFoundException
            insert_query = """
                INSERT INTO chat_history (interview_id, question_id, turn_input, turn_output, distilled_turn_output,turn_input_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING chat_history_turn_id, interview_id, question_id, turn_input, turn_output, distilled_turn_output,turn_input_type
            """
            result = execute_query(
                conn,
                insert_query,
                (interview_id, question_id, turn_input,turn_output,turn_input_type),
                fetch_one=True,
                commit=True
            )
            
            return {
                "chat_history_turn_id": result[0],
                "interview_id": result[1],
                "question_id": result[2],
                "turn_input": result[3],
                "turn_output": result[4],
                "distilled_turn_output": result[5],
                "turn_input_type": result[6]
            } 
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

@app.post("/batch_chat_history")
async def batch_insert_chat_history(chat_history_data):
    try:
        with get_db_connection() as conn:
            values = []
            for record in chat_history_data:
                interview_id = record["interview_id"]
                question_id = record["question_id"]
                turn_input_type = record["turn_input_type"]
                turn_input = record["turn_input"]
                turn_output = record["turn_output"]
                distilled_turn_output = record["distilled_turn_output"]
                
                values.append((
                    interview_id,
                    question_id,
                    turn_input_type,
                    turn_input,
                    turn_output,
                    distilled_turn_output
                ))
                
            if not values:
                return f"NO CHAT HISTORY TO INSERT"
            
            query = """
            INSERT INTO chat_history 
            (interview_id, question_id, turn_input_type, turn_input, turn_output, distilled_turn_output) 
            VALUES %s
            """
            
            cursor = conn.cursor()
            
            execute_values(cursor, query, values)
           
            conn.commit()
            
            return f"CHAT HISTORY ADDED TO THE DATABASE"
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
    
@app.delete("/chat_history/{interview_id}")
async def delete_chat_history(interview_id: int):
    """
    Delete a specific chat history from the chat history.
    
    Args:
        interview_id (int): The unique identifier of the interview chat history entry to delete.
    
    Returns:
        dict: A message confirming successful deletion:
            {"message": "chat history deleted successfully"}
    
    Raises:
        Exception (404): If no chat history entry is found with the specified ID
        DatabaseConnectionError: If database connection fails
        DatabaseQueryError: If there's an error executing the query
        DatabaseOperationError: If there's an error with database operations
    """
    try:
        with get_db_connection() as conn:
            try:
                delete_query = """
                    DELETE FROM chat_history 
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
                
                if not deleted_feedback:
                    raise InterviewNotFoundException(interview_id)
                
                return {"message": "chat history deleted successfully"}
            except Exception as e:
                logger.error(f"Error deleting chat history : {e}")
                raise
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9094)