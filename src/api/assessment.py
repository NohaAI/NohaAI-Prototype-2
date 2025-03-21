from fastapi import FastAPI, HTTPException
import logging
import uvicorn
import json
from src.dao.assessment import AssessmentDAO

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

assessment_dao = AssessmentDAO()

@app.get("/assessments/{interview_id}", response_model=list[AssessmentResponse])
async def get_assessments(interview_id: int):
    """
    Retrieve all assessments for a given interview.
    """
    try:
        return assessment_dao.get_assessments(interview_id)
    except ValueError as e:  # InterviewNotFoundException replaced
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_assessments: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/batch_insert_assessments")
async def batch_insert_assessments(assessment_payloads_record: list):
    """
    Batch insert multiple assessments.
    """
    try:
        return assessment_dao.batch_insert_assessments(assessment_payloads_record)
    except Exception as e:
        logger.error(f"Unexpected error in batch_insert_assessments: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/assessment/{assessment_id}", response_model=AssessmentResponse)
async def update_assessment(assessment_id: int, assessment_request: AssessmentUpdateRequest):
    """
    Update an assessment by ID.
    """
    try:
        return assessment_dao.update_assessment(
            assessment_id, assessment_request.score, assessment_request.assessment_payloads
        )
    except KeyError as e:  # AssessmentNotFoundException replaced
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in update_assessment: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/assessment", response_model=AssessmentResponse)
async def add_assessment(interview_id: int, question_id: int, score: float, assessment_results: list[dict]):
    """
    Add a new assessment.
    """
    try:
        return assessment_dao.add_assessment(interview_id, question_id, score, assessment_results)
    except (ValueError, KeyError) as e:  # InterviewNotFoundException & QuestionNotFoundException replaced
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in add_assessment: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/assessment/{assessment_id}")
async def delete_assessment(assessment_id: int):
    """
    Delete an assessment by ID.
    """
    try:
        return assessment_dao.delete_assessment(assessment_id)
    except KeyError as e:  # AssessmentNotFoundException replaced
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_assessment: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9099)
