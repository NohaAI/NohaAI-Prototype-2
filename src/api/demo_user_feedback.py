from fastapi import FastAPI

import logging

import uvicorn
#from src.dao.utils.db_utils import get_db_connection,execute_query,DatabaseConnectionError,DatabaseOperationError,DatabaseQueryError,DB_CONFIG,

from src.schemas.dao.schema import UserFeedbackRequest
from src.utils.response_helper import decorate_response
from fastapi import status

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/user-feedback/")
async def post_user_feedback(user_feedback_request: UserFeedbackRequest):
    """
    Return the provided user feedback rating.
    
    Args:
        user_feedback_request (UserFeedbackRequest): Request containing user rating
        
    Returns:
        JSONResponse: Standardized response with the feedback value
    """
    try:
        return decorate_response(
            succeeded=True,
            message={"rating": user_feedback_request.user_feedback},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return decorate_response(
            succeeded=False,
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9500)