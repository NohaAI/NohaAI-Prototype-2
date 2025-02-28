from flask import Flask, request, jsonify
from src.schemas.endpoints import EvaluateAnswerRequest
from src.services.workflows.dialogue_flow import get_next_response
from src.dao.interview_session_state import get_interview_session_state, update_interview_session_state, add_interview_session_state,delete_interview_session_state
from src.utils.logger import get_logger
import traceback
import json
from src.dao.chat_history import get_chat_history, delete_chat_history
from flask_cors import CORS
from src.schemas.dao import UserRequest
from src.api.demo_user import initialize_interview
  # Ensure logs are visible
logger = get_logger(__name__)

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

interview_id = 2 #hard-coded; should be fetched from DB
initial_session_state = {
    "chat_history": [],
    "rationale_logs": [],
    "hint_count": [0, 0, 0, 0, 0],
    "turn": 1,
    "consecutive_termination_requests": 0,
    "interview_id": 2,
    "previous_bot_dialogue": "Find an index in an array where the sum of elements to the left equals the sum to the right.", # question_id = 1
    "assessment_payload": None,
    "guardrails_count": 0,
    "contiguous_unacceptable_answer_count": 0,
    "conversation_turn": 1,
    "contigous_guardrails_count": 0,
    "conclude": False,
    "current_question": "Find an index in an array where the sum of elements to the left equals the sum to the right.", # question_id = 1
    "action_flag": "Pass",
    "conclude_message": "",
    "number_of_questions": 1,
    "interview_question_list": [12], #questions in list are hard coded for now there should be a logic for this
    "class_label": None,
    "meta_payload": EvaluateAnswerRequest(
            question_id=1,
            question="Find an index in an array where the sum of elements to the left equals the sum to the right.",
            interview_id=2,
            answer="Python",
            eval_distribution=[0, 0, 0, 0, 0, 0, 0]
        ),
    "eval_distribution": [0, 0, 0, 0, 0, 0, 0],
    "final_score": 0,
    "messages": [{"role": "bot", "content": "Hello Arun, I am Noha..."}]
}


# def process_text(text):
#     """
#     Sends the received text to GPT and streams back the response.
#     """
#     logger.info(f"USER INPUT BEFORE CALLING get_noha_dialogue : {text} \n")
#     print(f"Sending text to noha-bot recieved from frontend :\n {text}")
#     try:
#         response_list = await execute_workflow(user_input, session_state) # response_list contains bot_dialogue and latest session_state
#         response = response_list[0]
#         session_state = response_list[1]
#         interview_conclude_flag=session_state['conclude'] #False/True handles exiting the interview
#         print(f"SESSION STATE AFTER CALLING execute_workflow : \n {session_state}")
#         print(f"NOHA BOT RESPONSE : {response}")
#         return response
#     except Exception as e:
#         print(f"⚠️ Error in process_text: {e}")
#         print("Full traceback:")
#         traceback.print_exc()
#         print(f"An error occurred: {str(e)}")

#TODO initialize make a RESTAPI for initializing interview_session_state and making a ADD DB call
#TODO check whether async is necessary for connect/disconnect/chat

@app.route('/chat', methods=['POST'])
def chat():
    candidate_request = request.get_json()
    logger.info(f"REQUEST BODY RECIEVED FROM USER : {candidate_request} ")
    if not candidate_request:
        return jsonify({"error": "Missing request body"}), 400
    if "text" not in candidate_request:
        return jsonify({"error": "Missing 'text' field in candidate request"}), 400
    if "text" == "":
        return jsonify({"error": "'text' field was empty"}), 400
    if "session_state" not in candidate_request:
        return jsonify({"error": "Missing 'session_state' field in candidate request "}),400
    if "chat_history" not in candidate_request:
        return jsonify({"error": "Missing 'chat_history' field in candidate request "}),400
    if "assessment_payload" not in candidate_request:
        return jsonify({"error": "Missing 'assessment_payload' field in candidate request "}),400

    session_state=candidate_dialogue["session_state"]
    candidate_dialogue = candidate_request["text"]
    chat_history = candidate_request["chat_history"]
    assessment_payload = candidate_request["assessment_payload"]
    logger.info(f"TEXT RECIVED FROM THE USER : {candidate_dialogue}")
    response,session_state,chat_history, distilled_chat_history,assessment_payload = get_next_response(candidate_dialogue, session_state, chat_history, assessment_payload)

    #TODO: LOOK AT HOW JSONIFY RETURNS

    logger.info(f"BOT RESPONSE : {response}")
    logger.info(f"UPDATED SESSION STATE : {session_state}")
    logger.info(f"UPDATED DISTILLED CHAT HISTORY : {distilled_chat_history}")
    logger.info(f"CHAT HISTORY : {chat_history}")
    logger.info(f"ASSESSMENT PAYLOAD : {assessment_payload}")
    return jsonify({"message": response}), 200 #check jsonify returns to return all of the above



@app.route('/teriminate', methods=['POST'])
def terminate(session_state,chat_history, distilled_chat_history,assessment_payload):
    #TODO: WRITE THE CHAT HISTORY DISTILLED CHAT HISTORY ASSESSMENT PAYLOAD AND SESSION STATE TO THE DATABASE RETURN TRUE WHEN DONE

@app.route('/initialize', methods=['POST'])
def intialize(user_name, user_email):
    try:
        interview_id = initialize_interview(user_name, user_email)
        #add_interview_session_state(interview_id)
        # -> create a new interview session state and add it to database with the new fetched interview id
        initialize_session_state = {
            "interview_id": interview_id,
            "turn_number": 1,
            "consecutive_termination_request_count": 0,
            "bot_dialogue": "Find an index in an array where the sum of elements to the left equals the sum to the right.",
            "guardrails_count": 0,
            "contiguous_techincal_guardrail_count": 0,
            "contigous_non_technical_guardrail_count": 0,
            "termination": False,
            "current_question": "Find an index in an array where the sum of elements to the left equals the sum to the right.",
            "next_action": "Pass",
            "number_of_questions": 1,
            "bot_dialogue_type": "question" 
        }
        
        # TODO: load the assessment_payload
        return jsonify({"message": f"INTERVIEW INTIALIZED WITH INTERVIEW ID : {interview_id}"}), 200
    except Exception as e:
        logger.critical(f"ERROR INITIALIZING THE INTERVIEW : {e}")
        return jsonify({'message': f"ERROR INITIALIZING THE INTERVIEW : {e}"}), 500

@app.route('/connect', methods=['GET'])
def connect():
    #TODO: USE ONLY FOR WEBSOCKETS
    try:
        logger.info("Client connected successfully.")
        
        return jsonify({'message': 'Connected successfully'}), 200
    
    except Exception as e:
        logger.error(f"Error in /connect: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/disconnect', methods=['GET'])
def disconnect():
    try:
        logger.info("Client disconnect successfully.")
        check_session_state = await get_interview_session_state(interview_id)
        if check_session_state:
            await delete_interview_session_state(interview_id)
        return jsonify({'message': 'disconnect successfully'}), 200
    
    except Exception as e:
        logger.error(f"Error in /connect: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)