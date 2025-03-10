from fastapi import FastAPI, HTTPException
import logging
import uvicorn
from src.dao.chat_history import ChatHistoryDAO  # Correct import: Import the DAO, not the data object!
from src.schemas.dao import ChatHistoryRequest, ChatHistoryResponse
from typing import List, Optional, Dict

# Configure application-wide logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI()

# Instantiate the DAO
chat_history_dao = ChatHistoryDAO()

@app.get("/chat_history", response_model=List[Dict[str, str]])  # type: ignore[valid-type]
async def get_chat_history(interview_id: int, question_id: Optional[int] = None):
    """
    Retrieve chat history for an interview, optionally filtered by question.

    Args:
        interview_id: The ID of the interview.
        question_id: The ID of the question (optional).

    Returns:
        A list of chat history entries as dictionaries.
    """
    try:
        # Get the filtered chat history from the DAO
        chat_history = chat_history_dao.get_filtered_chat_history(interview_id, question_id)
        return chat_history
    except Exception as e:
        logger.exception("Error retrieving chat history")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/chat_history/{chat_history_turn_id}", response_model=ChatHistoryResponse)
async def update_chat_history(chat_history_turn_id: int, chat_history_request: ChatHistoryRequest):
    """Update a chat history entry."""
    try:
        updated_record = chat_history_dao.update_chat_history(
            chat_history_turn_id,
            chat_history_request.turn_input,
            chat_history_request.turn_output,
            chat_history_request.turn_input_type
        )
        return ChatHistoryResponse(**updated_record)  # type: ignore[arg-type]
    except ChatHistoryNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Error updating chat history")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat_history", response_model=Dict)
async def add_chat_history(interview_id: int, question_id: int, turn_input: str, turn_output: str, distilled_turn_output: str, turn_input_type: str):
    """Add a new chat history entry."""
    try:
        new_chat_history = chat_history_dao.add_chat_history(
            interview_id, question_id, turn_input, turn_output, distilled_turn_output, turn_input_type
        )
        return new_chat_history
    except InterviewNotFoundException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except QuestionNotFoundException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error adding chat history")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_chat_history")
async def batch_insert_chat_history(chat_history_data: List[Dict]):
    """Add multiple chat history entries in a batch."""
    try:
        # Implement batch insertion in the DAO (ChatHistoryDAO)
        raise NotImplementedError("Batch insert not implemented")
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        logger.exception("Error adding batch chat history")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat_history/{interview_id}")
async def delete_chat_history(interview_id: int):
    """Delete chat history for a given interview."""
    try:
        result = chat_history_dao.delete_chat_history(interview_id)
        return result
    except InterviewNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Error deleting chat history")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9094)
