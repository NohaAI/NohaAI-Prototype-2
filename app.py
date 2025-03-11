from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import traceback
from typing import Dict, Any

# Import statements remain the same as in the original Flask app
from src.dao.interview_session_state import add_interview_session_state
from src.utils.logger import get_logger
from src.dao.chat_history import batch_insert_chat_history
from src.dao.interview_question_evaluation import batch_insert_interview_question_evaluation
from src.services.workflows.graph import get_next_response
from src.api.demo_user import initialize_interview
from src.services.workflows.candidate_greeter import generate_greeting
from src.dao.data_objects.chat_history import ChatHistoryRecord
from src.dao.data_objects.assessment_payload import AssessmentPayloadRecord

# Ensure logs are visible
logger = get_logger(__name__)

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/connect')
async def connect():
    #TODO: USE ONLY FOR WEBSOCKETS
    logger.info("Client connected successfully. release branch ")
    return {"message": "Connected successfully from release branch"}
    
@app.post('/initialize')
async def intialize(request: Request):
    try:
        initialization_request = await request.json()
        logger.info(f"INITIALIZATION REQUEST{initialization_request}")
        
        if not initialization_request:
            raise HTTPException(status_code=400, detail="Missing request body")
        
        if "user_name" not in initialization_request:
            raise HTTPException(status_code=400, detail="Missing 'user_name' in initialization_request body")
        
        if "user_email" not in initialization_request:
            raise HTTPException(status_code=400, detail="Missing 'user_email' in initialization_request body")
        
        user_name = initialization_request['user_name']
        user_email = initialization_request['user_email']   
        
        user_id, interview_id = await initialize_interview(user_name, user_email)
        logger.info(f"NEW INTERVIEW ID FOR USER: {interview_id}")
        logger.info(f"USER ID FOR USER: {user_id}")
        greeting = await generate_greeting(user_id) 

        session_state = {
            "interview_id": interview_id,
            "turn_number": 0,
            "consecutive_termination_request_count": 0,
            "bot_dialogue": greeting,
            "guardrail_count": 0,
            "contiguous_technical_guardrail_count": 0,
            "contiguous_non_technical_guardrail_count": 0,
            "termination": False,
            "current_question": "",
            "next_action": "get_new_question",
            "questions_asked": [],
            "bot_dialogue_type": "greeting",
            "complexity": None
        }
        
        assessment_payload_record = AssessmentPayloadRecord()
        chat_history = ChatHistoryRecord()
        
        initialization_response = {
            "message": f"INTERVIEW INTIALIZED WITH INTERVIEW ID : {interview_id}",
            "greeting": greeting,
            "session_state": json.dumps(session_state),
            "chat_history": json.dumps(chat_history),
            "assessment_payload_record": json.dumps(assessment_payload_record)
        }
        
        logger.info(f"INITIALIZEATION RESPONSE : {initialization_response}")
        return initialization_response
    except Exception as e:
        logger.critical(f"ERROR INITIALIZING THE INTERVIEW : {e}")
        raise HTTPException(status_code=500, detail=f"ERROR INITIALIZING THE INTERVIEW : {e}")


@app.post('/chat')
async def chat(request: Request):
    try:
        candidate_request = await request.json()
        logger.info(f"REQUEST BODY RECIEVED FROM USER : {candidate_request} ")
        
        # Validate request body
        if not candidate_request:
            raise HTTPException(status_code=400, detail="Missing request body")
        
        required_fields = [
            "candidate_dialogue", 
            "session_state", 
            "chat_history", 
            "assessment_payload_record"
        ]
        
        for field in required_fields:
            if field not in candidate_request:
                raise HTTPException(status_code=400, detail=f"Missing '{field}' field in candidate request")
        
        candidate_dialogue = candidate_request["candidate_dialogue"]
        session_state = json.loads(candidate_request["session_state"])
        chat_history_data = json.loads(candidate_request["chat_history"])
        assessment_payload_data = json.loads(candidate_request["assessment_payload_record"])

        chat_history = ChatHistoryRecord()  
        chat_history.extend(chat_history_data)  

        assessment_payload_record = AssessmentPayloadRecord()  
        assessment_payload_record.extend(assessment_payload_data)

        logger.info(f"TEXT RECIVED FROM THE USER : {candidate_dialogue}")
        
        bot_dialogue, session_state, chat_history, assessment_payload_record = await get_next_response(
            candidate_dialogue, 
            session_state, 
            chat_history, 
            assessment_payload_record
        )

        logger.info(f"BOT RESPONSE : {bot_dialogue}")
        logger.info(f"UPDATED SESSION STATE : {session_state}")
        logger.info(f"CHAT HISTORY : {chat_history}")
        logger.info(f"ASSESSMENT PAYLOAD : {assessment_payload_record}")
        
        chat_response = {
            "bot_dialogue": bot_dialogue,
            "termination": session_state['termination'],
            "session_state": json.dumps(session_state),
            "chat_history": json.dumps(chat_history),
            "assessment_payload_record": json.dumps(assessment_payload_record)
        }
        
        logger.info(f"CHAT RESPONSE : {chat_response}")
        return chat_response
    except Exception as e:
        logger.critical(f"ERROR PROCESSING CANDIDATE CHAT REQUEST : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ERROR PROCESSING CANDIDATE CHAT REQUEST : {e}")    

@app.post('/terminate')
async def terminate(request: Request):
    termination_request = await request.json()
    
    # Validate request body
    if not termination_request:
        raise HTTPException(status_code=400, detail="Missing request body")
    
    required_fields = [
        "session_state", 
        "chat_history", 
        "assessment_payload_record"
    ]
    
    for field in required_fields:
        if field not in termination_request:
            raise HTTPException(status_code=400, detail=f"Missing '{field}' in termination_request body")
    
    session_state = json.loads(termination_request["session_state"])
    chat_history_data = json.loads(termination_request["chat_history"])
    assessment_payload_data = json.loads(termination_request["assessment_payload_record"])

    chat_history = ChatHistoryRecord()  
    chat_history.extend(chat_history_data)  

    assessment_payload_record = AssessmentPayloadRecord()  
    assessment_payload_record.extend(assessment_payload_data)

    try:
        batch_insert_chat_history(chat_history)
        logger.info(f"DATA ADDED TO CHAT HISTORY TABLE")

        batch_insert_interview_question_evaluation(assessment_payload_record)
        logger.info(f"DATA ADDED TO INTERVIEW QUESTION EVALUATION TABLE")

        add_interview_session_state(
            session_state['interview_id'], 
            session_state['turn_number'], 
            session_state['consecutive_termination_request_count'], 
            session_state['bot_dialogue'], 
            session_state['guardrail_count'], 
            session_state['contiguous_technical_guardrail_count'], 
            session_state['contiguous_non_technical_guardrail_count'], 
            session_state['termination'], 
            session_state['current_question'], 
            session_state['next_action'], 
            session_state['questions_asked'], 
            session_state['bot_dialogue_type'], 
            session_state['complexity']
        )
        logger.info(f"DATA ADDED TO INTERVIEW SESSION STATE TABLE")

        return {"message": "DATABASE WRITE OPERATIONS SUCCESSFULL FOR CHAT_HISTORY, INTERVIEW_QUESTION_EVALUATION, INTERVIEW_SESSION_STATE"}
    except Exception as e:
        logger.critical(f"ERROR TERMINATING THE INTERVIEW {e}")
        raise HTTPException(status_code=500, detail=f"ERROR TERMINATING THE INTERVIEW : {e}")

@app.get('/disconnect')
async def disconnect():
    logger.info("Client disconnect successfull.")
    return {"message": "disconnect successfully"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)