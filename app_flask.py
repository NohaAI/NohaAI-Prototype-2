from flask import Flask, request, jsonify
# from src.services.workflows.dialogue_flow import get_next_response
from src.dao.interview_session_state import add_interview_session_state
from src.utils.logger import get_logger
import json
import traceback
from src.dao.chat_history import batch_insert_chat_history
from src.dao.interview_question_evaluation import batch_insert_interview_question_evaluation
from flask_cors import CORS
from src.services.workflows.graph import get_next_response
from src.api.demo_user import initialize_interview
from src.services.workflows.candidate_greeter import generate_greeting
from src.dao.data_objects.chat_history import ChatHistoryRecord
from src.dao.data_objects.assessment_payload import AssessmentPayloadRecord
  # Ensure logs are visible
logger = get_logger(__name__)

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/connect', methods=['GET'])
def connect():
    #TODO: USE ONLY FOR WEBSOCKETS
    logger.info("Client connected successfully.")
    return jsonify({'message': 'Connected successfully'}), 200
    
@app.route('/initialize', methods=['POST'])
async def intialize():
    try:
        initialization_request = request.get_json()
        logger.info(f"INITIALIZATION REQUEST{initialization_request}")
        if not initialization_request:
            return jsonify({"error": "Missing request body"}), 400
        if "user_name" not in initialization_request:
            return jsonify({"error": "Missing 'user_name' in initialization_request body"}), 400   
        if "user_email" not in initialization_request:
            return jsonify({"error": "Missing 'user_email' in initialization_request body"}), 400
        
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
        initialization_response = jsonify({"message": f"INTERVIEW INTIALIZED WITH INTERVIEW ID : {interview_id}",
                        "greeting": greeting,
                        "session_state": json.dumps(session_state),
                        "chat_history": json.dumps(chat_history),
                        "assessment_payload_record": json.dumps(assessment_payload_record)
                        })
        logger.info(f"INITIALIZEATION RESPONSE : {initialization_response}")
        return initialization_response, 200
    except Exception as e:
        logger.critical(f"ERROR INITIALIZING THE INTERVIEW : {e}")
        return jsonify({'error': f"ERROR INITIALIZING THE INTERVIEW : {e}"}), 500


@app.route('/chat', methods=['POST'])
async def chat():
    try:
        candidate_request = request.get_json()
        logger.info(f"REQUEST BODY RECIEVED FROM USER : {candidate_request} ")
        if not candidate_request:
            return jsonify({"error": "Missing request body"}), 400
        if "candidate_dialogue" not in candidate_request:
            return jsonify({"error": "Missing 'candidate_dialogue' field in candidate request"}), 400
        if "candidate_dialogue" == "":
            return jsonify({"error": "'candidate_dialogue' field was empty"}), 400
        if "session_state" not in candidate_request:
            return jsonify({"error": "Missing 'session_state' field in candidate request "}),400
        if "chat_history" not in candidate_request:
            return jsonify({"error": "Missing 'chat_history' field in candidate request "}),400
        if "assessment_payload_record" not in candidate_request:
            return jsonify({"error": "Missing 'assessment_payload_record' field in candidate request "}),400
       
        candidate_dialogue = candidate_request["candidate_dialogue"]
        session_state_json=candidate_request["session_state"]
        chat_history_json = candidate_request["chat_history"]
        assessment_payload_record_json =candidate_request["assessment_payload_record"]

        session_state = json.loads(session_state_json)

        chat_history_data = json.loads(chat_history_json)  
        assessment_payload_data = json.loads(assessment_payload_record_json)  

        chat_history = ChatHistoryRecord()  
        chat_history.extend(chat_history_data)  

        assessment_payload_record = AssessmentPayloadRecord()  
        assessment_payload_record.extend(assessment_payload_data)

        logger.info(f"TEXT RECIVED FROM THE USER : {candidate_dialogue}")
        
        bot_dialogue, session_state, chat_history, assessment_payload_record = await get_next_response(candidate_dialogue, session_state, chat_history, assessment_payload_record)

        logger.info(f"BOT RESPONSE : {bot_dialogue}")
        logger.info(f"UPDATED SESSION STATE : {session_state}")
        logger.info(f"CHAT HISTORY : {chat_history}")
        logger.info(f"ASSESSMENT PAYLOAD : {assessment_payload_record}")
        chat_response = jsonify({
            "bot_dialogue": bot_dialogue,
            "termination": session_state['termination'],
            "session_state": json.dumps(session_state),
            "chat_history": json.dumps(chat_history),
            "assessment_payload_record": json.dumps(assessment_payload_record)
        })
        logger.info(f"CHAT RESPONSE : {chat_response}")
        return chat_response, 200 
    except Exception as e:
        logger.critical(f"ERROR PROCESSING CANDIDATE CHAT REQUEST : {e}", exc_info=True)
        return jsonify({'error': f"ERROR PROCESSING CANDIDATE CHAT REQUEST : {e}"}), 500    

@app.route('/terminate', methods=['POST'])
def terminate():
    termination_request = request.get_json()
    if not termination_request:
        return jsonify({"error": "Missing request body"}), 400
    if "session_state" not in termination_request:
        return jsonify({"error": "Missing 'session_state' in termination_request body"}), 400
    if "chat_history" not in termination_request:
        return jsonify({"error": "Missing 'chat_history' in termination_request body"}), 400 
    if "assessment_payload_record" not in termination_request:
        return jsonify({"error": "Missing 'assessment_payload_record' in termination_request body"}), 400 
    
    session_state_json = termination_request["session_state"]
    chat_history_json = termination_request["chat_history"]
    assessment_payload_record_json = termination_request["assessment_payload_record"]

    session_state = json.loads(session_state_json)

    chat_history_data = json.loads(chat_history_json)  
    assessment_payload_data = json.loads(assessment_payload_record_json)  

    chat_history = ChatHistoryRecord()  
    chat_history.extend(chat_history_data)  

    assessment_payload_record = AssessmentPayloadRecord()  
    assessment_payload_record.extend(assessment_payload_data)

    try:
        batch_insert_chat_history(chat_history)
        logger.info(f"DATA ADDED TO CHAT HISTORY TABLE")

        batch_insert_interview_question_evaluation(assessment_payload_record)
        logger.info(f"DATA ADDED TO INTERVIEW QUESTION EVALUATION TABLE")

        add_interview_session_state(session_state['interview_id'], session_state['turn_number'], session_state['consecutive_termination_request_count'], session_state['bot_dialogue'], session_state['guardrail_count'], session_state['contiguous_technical_guardrail_count'], session_state['contiguous_non_technical_guardrail_count'], session_state['termination'], session_state['current_question'], session_state['next_action'], session_state['questions_asked'], session_state['bot_dialogue_type'], session_state['complexity'])
        logger.info(f"DATA ADDED TO INTERVIEW SESSION STATE TABLE")

        return jsonify({"message": f"DATABASE WRITE OPERATIONS SUCCESSFULL FOR CHAT_HISTORY, INTERVIEW_QUESTION_EVALUATION, INTERVIEW_SESSION_STATE"})
    except Exception as e:
        logger.critical(f"ERROR TERMINATING THE INTERVIEW {e}")
        return jsonify({'error': f"ERROR TERMINATING THE INTERVIEW : {e}"}), 500

@app.route('/disconnect', methods=['GET'])
def disconnect():
    logger.info("Client disconnect successfull.")
    return jsonify({'message': 'disconnect successfully'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)