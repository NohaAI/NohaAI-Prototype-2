from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import importlib.resources as res
import traceback
from typing import Dict, Any
from src.utils import helper as helper

# Import statements remain the same as in the original Flask app
# from src.dao.interview_session_state import add_interview_session_state
from src.utils import logger as log
from src.api.chat_history import batch_insert_chat_history
# from src.dao.interview_question_evaluation import batch_insert_interview_question_evaluation
from src.services.workflows.graph import get_next_response
from src.api.demo_user import initialize_interview
from src.services.workflows.candidate_greeter import generate_greeting
from src.dao.chat_history_data.chat_history_record import ChatHistoryRecord
from src.dao.assessment_data.assessment_record import AssessmentRecord
from src.dao.chat_history import ChatHistoryDAO
from src.dao.assessment import AssessmentDAO
from src.dao.live_code import LiveCodeDAO
from src.config import constants as CONST
from src.dao.exceptions import LiveCodeNotFoundException
from src.services.interview_evaluation_generation.interview_evaluation_generator import generate_evaluation_report_from_session_state
# Ensure logs are visible
logger = log.get_logger(__name__)

app = FastAPI()


# Allow frontend domain or allow all (*) for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://34.47.214.185:3000", "https://test.noha.ai"],  # Change "*" to a specific domain in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


## CORS middleware configuration
#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["http://localhost:3000"],  # Add your frontend URL
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)

@app.get('/connect')
async def connect():
    logger.info("\n>>>>>>>>>>>FUNCTION [connect] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    #TODO: USE ONLY FOR WEBSOCKETS
    logger.info("\n\n\n Client connected successfully.............................")
    return {"message": "Connected successfully ......"}
    
@app.post('/initialize')
async def initialize(request: Request):
    logger.info("\n>>>>>>>>>>>FUNCTION [initialize] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    try:
        # () call library function: fastapi.Request.request
        initialization_request = await request.json()
        logger.info(f"INITIALIZATION REQUEST FROM CLIENT {initialization_request}")
        
        if not initialization_request:
            raise HTTPException(status_code=400, detail="Missing request body")
        
        if "user_name" not in initialization_request:
            raise HTTPException(status_code=400, detail="Missing 'user_name' in initialization_request body")
        
        if "user_email" not in initialization_request:
            raise HTTPException(status_code=400, detail="Missing 'user_email' in initialization_request body")
        
        if "live_code" not in initialization_request:
            raise HTTPException(status_code=400, detail="Missing 'live_code' in initialization_request body")

        user_name = initialization_request['user_name']
        user_email = initialization_request['user_email']   
        live_code = initialization_request['live_code']

        LiveCodeDAO.check_live_code(live_code=live_code) # returns True otherwise raise LiveCodeNotFoundException
        # () call function: initialize_interview after checking live_code from DB
        user_id, interview_id = await initialize_interview(user_name, user_email) 

        if live_code == CONST.DEVELOPER_LIVE_CODE: # measures taken for development
            print("DEV LIVE CODE BEING USED")
        else:
            LiveCodeDAO.delete_live_code(live_code) # live code is deleted after the user is initialized
            print("DELETED LIVE CODE AFTER USER INITIALIZATION")
        helper.pretty_log("interview_id", interview_id, 1)

        log.write_to_report(f"Candidate Interview Report\nInterview ID: {interview_id}\nCandidate Name: {user_name}\nPosition: Software Engineer (DSA Evaluation)\nCandidate Name: {user_name}\nInterview Conducted By: Noha\nDate: {helper.get_current_datetime()}\nOverall Score: 4.7 / 10")
      
        # () call function: generate_greeting
        greeting = await generate_greeting(user_id) 

        helper.pretty_log("greeting", greeting, 1)


        session_state = {
            "primary_question": CONST.DEF_PRIMARY_QUESTION,
            "question_id" :CONST.DEF_QUESTION_ID,
            "interview_id": interview_id,   # has to be dynamically assigned
            "bot_dialogue": greeting,   # has to be dynamically assigned
            "candidate_dialogue": CONST.DEF_CANDIDATE_DIALOGUE, # has to be dynamically assigned
            "turn_number": CONST.DEF_TURN_NUMBER,
            "label_class1": CONST.DEF_LABEL_CLASS1,
            "label_class2": CONST.DEF_LABEL_CLASS2,
            "solution_classifier_executed": CONST.DEF_SOLUTION_CLASSIFIER_EXECUTED,
            "next_action": CONST.DEF_NEXT_ACTION,
            "termination": CONST.DEF_TERMINATION,
            "guardrail_count": CONST.DEF_GUARDRAIL_COUNT,
            "consecutive_termination_request_count": CONST.DEF_CONSECUTIVE_TERMINATION_REQUEST_COUNT,
            "contiguous_technical_guardrail_count": CONST.DEF_CONTIGUOUS_TECHNICAL_GUARDRAIL_COUNT,
            "contiguous_non_technical_guardrail_count": CONST.DEF_CONTIGUOUS_NON_TECHNICAL_GUARDRAIL_COUNT,
            "questions_asked": CONST.DEF_QUESTIONS_ASKED,
            "bot_dialogue_type": CONST.DEF_BOT_DIALOGUE_TYPE,
            "complexity": CONST.DEF_COMPLEXITY
        }

        # todo: check if you can replace this with ChatHistoryRecord()
        chat_history_record = {
            "interview_id": interview_id,
            "question_id": CONST.DEF_QUESTION_ID,
            "bot_dialogue_type": "greeting",
            "bot_dialogue": greeting,
            "candidate_dialogue": CONST.DEF_CANDIDATE_DIALOGUE,
            "distilled_candidate_dialogue": CONST.DEF_DISTILLED_CANDIDATE_DIALOGUE
        }

        # todo: check if you can replace this with AssessmentRecord()
        assessment_record = {
            "interview_id": interview_id,
            "question_id": CONST.DEF_QUESTION_ID,
            "primary_question_score": CONST.DEF_PRIMARY_QUESTION_SCORE,
            "assessment_payloads": [helper.get_assessment_payload()]
        }
        
        # TODO: initialize an instance each of ChatHistoryDAO and AssessmentDAO
        # TODO: second thought: possibly this should be instantiated in terminate/ and collectively batch inserted for both payloads, chat_history and assessment
        # chat_history_dao = ChatHistoryDAO()
        # chat_history = chat_history_dao.get_chat_history(interview_id=interview_id)
        # chat_history.append(chat_history_record)

        # assessment_dao = AssessmentDAO()
        # assessment = assessment_dao.get_assessments(interview_id=interview_id)
        # assessment.append(assessment_record)
        ########################################################
        chat_history = [chat_history_record]
        assessment = [assessment_record]

        initialization_response = {
            "session_state": session_state,
            "chat_history": chat_history,
            "assessment": assessment
        }

        ################## THE FOLLOWING CODE ALONGWITH THE LARGE RESPONSE, IS IT REQUIRED?? ############
        # assessment_payload_record = AssessmentPayloadRecord()

        # chat_history_dao = ChatHistoryDAO()
        # chat_history_record = ChatHistoryRecord()
        
        # initialization_response = {
        #     "message": f"INTERVIEW INTIALIZED WITH INTERVIEW ID : {interview_id}",
        #     "greeting": greeting,
        #     "session_state": json.dumps(session_state),
        #     "chat_history": json.dumps(chat_history_record),
        #     "assessment_payload_record": json.dumps(assessment_payload_record)
        # }
        ############ END BLOCK, DISCUSS AND DELETE ##################


        helper.pretty_log("session_state", session_state, 1)
        helper.pretty_log("chat_history", chat_history, 1)
        helper.pretty_log("assessment", assessment, 1)

        logger.info("\n\n\n\n>>>>>>>>>>>FUNCTION EXIT [initialize] >>> SENDING ABOVE PAYLOADS AS FRONT-END RESPONSE >>>>>>>>>>>>>>>>>>>>>>>\n\n")

        return initialization_response
    except LiveCodeNotFoundException:
        raise HTTPException(status_code = 404, detail = f"INVALID LIVE CODE")
    except Exception as e:
        logger.critical(f"ERROR INITIALIZING THE INTERVIEW : {e}")
        raise HTTPException(status_code=500, detail=f"ERROR INITIALIZING THE INTERVIEW : {e}")


@app.post('/chat')
async def chat(request: Request):
    logger.info("\n\n\n\n<<<<<<<<<<< FUNCTION ENTER [chat] <<< RECEIVING PAYLOADS FROM FRONT-END REQUESTS <<<<<<<<<<<<<<<<<<<<< \n\n")

    logger.info("\n>>>>>>>>>>>FUNCTION [chat] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    try:
        chat_request = await request.json()
        # logger.info(f"CHAT REQUEST FROM CLIENT : {json.dumps(chat_request, indent=4)} ")

        # Validate request body
        if not chat_request:
            raise HTTPException(status_code=400, detail="Missing request body")
        
        required_fields = [
            "session_state", 
            "chat_history", 
            "assessment",
        ]
        
        for field in required_fields:
            if field not in chat_request:
                raise HTTPException(status_code=400, detail=f"Missing '{field}' field in candidate request")
        
        session_state = chat_request["session_state"]
        chat_history = chat_request["chat_history"]
        assessment = chat_request["assessment"]

        helper.pretty_log("session_state", session_state, 1)
        helper.pretty_log("chat_history", chat_history, 1)
        
        # chat_history = ChatHistoryRecord()  
        # chat_history.extend(chat_history_data)  

        # assessment_payload_record = AssessmentPayloadRecord()  
        # assessment_payload_record.extend(assessment_payload_data)
        
        session_state, chat_history, assessment = await get_next_response( 
            session_state, 
            chat_history, 
            assessment
        )

        logger.info("\n>>>>>>>>>>>RE-ENTERING FUNCTION [chat] ?????????>>>>>>^^^^^^^^^>>>>>>>>?????")
        helper.pretty_log("session_state", session_state)
        helper.pretty_log("chat_history", chat_history)

        chat_response = {
            "session_state": session_state,
            "chat_history": chat_history,
            "assessment": assessment
        }
        
        logger.info("\n\n\n\n>>>>>>>>>>>FUNCTION EXIT [chat] >>> SENDING PAYLOADS AS FRONT-END RESPONSE >>>>>>>>>>>>>>>>>>>>>>>\n\n")
        return chat_response
    except Exception as e:
        logger.critical(f"ERROR PROCESSING CANDIDATE CHAT REQUEST : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ERROR PROCESSING CANDIDATE CHAT REQUEST : {e}") from e   

@app.post('/terminate')
async def terminate(request: Request):
    logger.info("\n>>>>>>>>>>>FUNCTION [terminate] >>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    termination_request = await request.json()
    
    # Validate request body
    if not termination_request:
        raise HTTPException(status_code=400, detail="Missing request body")
    
    required_fields = [
        "session_state", 
        "chat_history", 
        "assessment"
    ]
    
    for field in required_fields:
        if field not in termination_request:
            raise HTTPException(status_code=400, detail=f"Missing '{field}' in termination_request body")
    
    session_state = termination_request["session_state"]
    chat_history = termination_request["chat_history"]
    assessment = termination_request["assessment"]
    print(f"SESSION STATE: {session_state}")
    print(f"ASSESSMENT: {assessment}")
    print(f"CHAT HISTORY: {chat_history}") 

    if not session_state['question_id']:
        print("NO REPORT TO BE GENERATED")
        pass
    else: 
        #generating evaluation report from session_state
        print("GENERATING REPORT")
        generate_evaluation_report_from_session_state(session_state = session_state, chat_history = chat_history, assessment_payloads = assessment, code_snippet = None)

    chat_history_dao = ChatHistoryDAO()
    chat_history_dao.batch_insert_chat_history(chat_history)

    assessment_dao = AssessmentDAO()
    assessment_dao.batch_insert_assessments(assessment)


    # try:
    #     batch_insert_chat_history(chat_history)
    #     logger.info(f"DATA ADDED TO CHAT HISTORY TABLE")

    #     batch_insert_interview_question_evaluation(assessment_payload_record)
    #     logger.info(f"DATA ADDED TO INTERVIEW QUESTION EVALUATION TABLE")

    #     add_interview_session_state(
    #         session_state['interview_id'], 
    #         session_state['turn_number'], 
    #         session_state['consecutive_termination_request_count'], 
    #         session_state['bot_dialogue'], 
    #         session_state['guardrail_count'], 
    #         session_state['contiguous_technical_guardrail_count'], 
    #         session_state['contiguous_non_technical_guardrail_count'], 
    #         session_state['termination'], 
    #         session_state['current_question'], 
    #         session_state['next_action'], 
    #         session_state['questions_asked'], 
    #         session_state['bot_dialogue_type'], 
    #         session_state['complexity']
    #     )
    #     logger.info(f"DATA ADDED TO INTERVIEW SESSION STATE TABLE")

    #     return {"message": "DATABASE WRITE OPERATIONS SUCCESSFULL FOR CHAT_HISTORY, INTERVIEW_QUESTION_EVALUATION, INTERVIEW_SESSION_STATE"}
    # except Exception as e:
    #     logger.critical(f"ERROR TERMINATING THE INTERVIEW {e}")
    #     raise HTTPException(status_code=500, detail=f"ERROR TERMINATING THE INTERVIEW : {e}")
    helper.pretty_log("session_state", session_state)
    helper.pretty_log("chat_history", chat_history)

    terminate_response = {
        "session_state": session_state,
        "chat_history": chat_history,
        "assessment": assessment
    }

    logger.info("\n\n\n\n>>>>>>>>>>>FUNCTION EXIT [terminate] >>> SENDING PAYLOADS AS FRONT-END RESPONSE >>>>>>>>>>>>>>>>>>>>>>>\n\n")
    return terminate_response

@app.get('/disconnect')
async def disconnect():
    logger.info("Client disconnect successfully......................................\n\n\n")
    return {"message": "Disconnected successfully"}
