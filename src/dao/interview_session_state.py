from fastapi import FastAPI
import logging
from src.dao.utils.execute_query import execute_query
from src.dao.utils.connect import get_db_connection
from src.dao.exceptions import DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError
from src.dao.exceptions import InterviewNotFoundException, InterviewSessionStateNotFoundException
import uvicorn
# Configure application-wide logging to track and record application events and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Endpoint to retrieve a specific final evaluation JSON by final evaluation ID
@app.get("/interview-session-state/{interview_id}")
async def get_interview_session_state(interview_id: int):
    """
    Retrieve a specific final evaluation JSON by ID.

    Args:
        interview_id (int): Unique identifier for the final evaluation

    Returns:
        interview_session_state: Details of interview_session_state for an interview_id

    Raises:
        Exception: 404 for Interview not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            
                # SQL query to fetch final evaluation JSON details from interview_session_states table
            query = """
                
                SELECT turn_number, consecutive_termination_request_count, bot_dialogue, guardrail_count, contiguous_technical_guardrail_count, contiguous_non_technical_guardrail_count, termination, current_question, next_action, questions_asked, bot_dialogue_type, complexity
                FROM INTERVIEW_SESSION_STATE
                WHERE interview_id = %s

            """
            result = execute_query(conn, query, (interview_id,), fetch_one=True)
            if not result:
                raise InterviewSessionStateNotFoundException
            turn_number = result[0]
            consecutive_termination_request_count = result[1]
            bot_dialogue = result[2]
            guardrail_count = result[3]
            contiguous_technical_guardrail_count = result[4]
            contiguous_non_technical_guardrail_count = result[5]
            termination = result[6]
            current_question = result[7]
            next_action = result[8]
            questions_asked = result[9]
            bot_dialogue_type = result[10]
            complexity = result[11]
            # Raise 404 error if no matching record is found
            # Return the final evaluation JSON response with retrieved details
            #TODO: - ADD A NULL CHECK FOR THE RESULT AND THROW AN EXCEPTION
            return {
                "interview_id" : interview_id,
                "turn_number": turn_number,
                "consecutive_termination_request_count" : consecutive_termination_request_count ,
                "bot_dialogue" : bot_dialogue,
                "guardrail_count" : guardrail_count,
                "contiguous_technical_guardrail_count" : contiguous_technical_guardrail_count,
                "contiguous_non_technical_guardrail_count" : contiguous_non_technical_guardrail_count,
                "termination" : termination,
                "current_question" : current_question,
                "next_action" : next_action,
                "questions_asked" : questions_asked,
                "bot_dialogue_type": bot_dialogue_type,
                "complexity": complexity
            }
                
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# Endpoint to update an existing final evaluation JSON
@app.put("/interview_session_state/{interview_id}")
async def update_interview_session_state(interview_id: int, turn_number:int, consecutive_termination_request_count: int, bot_dialogue: str, guardrail_count: int, contiguous_technical_guardrail_count: int, contiguous_non_technical_guardrail_count: int, termination: bool, current_question: str, next_action: str, questions_asked: list[int],bot_dialogue_type: str, complexity: int):
    """
    Update an existing final evaluation JSON.

    Args:
        interview_id (int): ID of the evaluation to update
        interview_session_state:  New interview_session_state

    Returns:
        True: Returns True suggesting update was made

    Raises:
        Exception: 404 for interview_session_state not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:        
            # Check if evaluation exists
            check_query = """
                SELECT interview_id FROM interview 
                WHERE interview_id = %s
            """
            exists = execute_query(conn, check_query, (interview_id,), fetch_one=True)
            if not exists:
                raise InterviewNotFoundException(interview_id)
            
            # Execute the update query
            update_query = f"""
                UPDATE interview_session_state
                SET turn_number=%s , consecutive_termination_request_count=%s, bot_dialogue=%s, guardrail_count=%s, contiguous_technical_guardrail_count=%s, contiguous_non_technical_guardrail_count=%s, termination=%s, current_question=%s, next_action=%s, questions_asked=%s, bot_dialogue_type=%s, complexity= %s
                WHERE interview_id = %s
                RETURNING interview_id
            """
            if not update_query:
                raise InterviewSessionStateNotFoundException(interview_id)
            updated_record = execute_query(
                conn, 
                update_query, 
                (turn_number, consecutive_termination_request_count, bot_dialogue, guardrail_count, contiguous_technical_guardrail_count, contiguous_non_technical_guardrail_count, termination, current_question, next_action, questions_asked,bot_dialogue_type,complexity, interview_id,), 
                fetch_one=True,
                commit=True
            )
            
            return f"INTERVIEW SESSION STATE SUCCESSFULY UPDATED FOR INTERVIEW_ID : {interview_id}"
            
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e
        
# Endpoint to add a new final evaluation JSON for a specific interview
@app.post("/interview_session_state")
async def add_interview_session_state(interview_id: int, turn_number:int , consecutive_termination_request_count: int, bot_dialogue: str, guardrail_count: int, contiguous_technical_guardrail_count: int, contiguous_non_technical_guardrail_count: int, termination: bool, current_question: str, next_action: str, questions_asked: list[int], bot_dialogue_type: str, complexity: int):
    """
    Add a new final evaluation JSON for a specific interview.

    Args:
        interview_id (int): ID of the interview
        interview_session_state : interview_session_state to be added for provided interview ID

    Returns:
        FinalEvaluationResponse: added session_state_details details

    Raises:
        Exception: 404 for interview_session_state not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    #TODO: refactor the addition func should only take session_state dict instead of 13 parameters
    try:
        with get_db_connection() as conn:
            # Check if an existing evaluation for the interview has a null evaluation JSON
            check_query = """
                SELECT interview_id FROM Interview
                WHERE interview_id = %s
            """
            check_interview = execute_query(conn, check_query, (interview_id,), fetch_one=True)
            
            if not check_interview:
                raise InterviewNotFoundException
                # Update existing evaluation with the new evaluation JSON
            add_interview_session_state_query = """
                INSERT INTO interview_session_state(interview_id, turn_number, consecutive_termination_request_count, bot_dialogue, guardrail_count, contiguous_technical_guardrail_count, contiguous_non_technical_guardrail_count, termination, current_question, next_action, questions_asked, bot_dialogue_type, complexity)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING interview_id
            """
            result = execute_query(
                conn,
                add_interview_session_state_query,
                (interview_id, turn_number, consecutive_termination_request_count, bot_dialogue, guardrail_count, contiguous_technical_guardrail_count, contiguous_non_technical_guardrail_count, termination, current_question, next_action, questions_asked,bot_dialogue_type,complexity,),
                fetch_one=True,
                commit=True
            )
            
            return {f"SUCCESSFULLY ADDED DATA IN INTERVIEW_SESSION_STATE FOR interview_id : {interview_id}"}
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

# Endpoint to delete a final evaluation JSON by final evaluation ID
@app.delete("/interview_session_state/{interview_id}")
async def delete_interview_session_state(interview_id: int):
    """
    Delete a final evaluation JSON by ID.

    Args:
        interview_id (int): ID of the evaluation to delete

    Returns:
        dict: Success message
    Raises:
        Exception: 404 for interview_session_state not found, 400 for validation errors, 
            503 for connection issues, 500 for other database errors
    """
    try:
        with get_db_connection() as conn:
            check_query = """
            SELECT interview_id FROM Interview
            WHERE interview_id = %d
        """
            check_interview = execute_query(conn, check_query, (interview_id,), fetch_one=True)
            
            if not check_query:
                raise InterviewNotFoundException(interview_id)
            # SQL query to delete record and return deleted record's ID
            delete_query = """
                DELETE FROM interview_session_state 
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
            
            # Raise 404 error if no record was deleted
            if not deleted_feedback:
                raise InterviewSessionStateNotFoundException(interview_id)
            
            # Return success message
            return {f"INTERVIEW SESSION STATE DELETED FOR INTERVIEW ID : {interview_id}"}
        
    except DatabaseConnectionError as e:
        raise e
    except DatabaseQueryError as e:
        raise e
    except DatabaseOperationError as e:
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9100)