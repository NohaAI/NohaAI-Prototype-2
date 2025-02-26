from flask import Flask, request, jsonify
import logging
from src.schemas.endpoints.schema import EvaluateAnswerRequest
from dotenv import load_dotenv
from noha_dialogue import get_noha_dialogue
from src.dao.interview_session_state import get_interview_session_state, update_interview_session_state, add_interview_session_state,delete_interview_session_state
from src.dao.chat_history import delete_chat_history
from src.utils.logger import get_logger
import traceback
import json
from src.dao.chat_history import get_chat_history, delete_chat_history
from flask_cors import CORS

logging.basicConfig(level=logging.DEBUG)  # Ensure logs are visible
logger = logging.getLogger(__name__)

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

interview_id = 1 #hard-coded; should be fetched from DB
initial_session_state = {
    "chat_history": [],
    "rationale_logs": [],
    "hint_count": [0, 0, 0, 0, 0],
    "turn": 1,
    "consecutive_termination_requests": 0,
    "interview_id": 1,
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
            interview_id=1,
            answer="Python",
            eval_distribution=[0, 0, 0, 0, 0, 0, 0]
        ),
    "eval_distribution": [0, 0, 0, 0, 0, 0, 0],
    "final_score": 0,
    "messages": [{"role": "bot", "content": "Hello Arun, I am Noha..."}]
}


async def process_text(text):
    """
    Sends the received text to GPT and streams back the response.
    """
    logger.info(f"USER INPUT BEFORE CALLING get_noha_dialogue : {text} \n")
    print(f"Sending text to noha-bot recieved from frontend :\n {text}")
    try:
        if not text.strip():
            print("❌ Empty transcription; skipping dialogue generation request.")
            return
        user_input=text
        session_state_db_data = await get_interview_session_state(interview_id)
        session_state_db_data=session_state_db_data[0]
        session_state_db_data_loaded=json.loads(session_state_db_data)
        if isinstance(session_state_db_data_loaded['meta_payload'], dict):
            session_state_db_data_loaded["meta_payload"] = EvaluateAnswerRequest(**session_state_db_data_loaded["meta_payload"])
        session_state = session_state_db_data_loaded
        print(f"SESSION STATE BEFORE CALLING get_bot_dialogue : \n {session_state}")
        response_list = await get_noha_dialogue(user_input, session_state) # response_list contains bot_dialogue and latest session_state
        response = response_list[0]
        session_state = response_list[1]
        interview_conclude_flag=session_state['conclude'] #False/True handles exiting the interview
        print(f"SESSION STATE AFTER CALLING get_bot_dialogue : \n {session_state}")
        print(f"NOHA BOT RESPONSE : {response}")
        if not isinstance(session_state['meta_payload'], dict):
            session_state['meta_payload'] = session_state['meta_payload'].model_dump()
        await update_interview_session_state(interview_id, json.dumps(session_state)) #update session state
        return response
    except Exception as e:
        print(f"⚠️ Error in process_text: {e}")
        print("Full traceback:")
        traceback.print_exc()
        print(f"An error occurred: {str(e)}")


@app.route('/hello', methods=['GET'])
def hello():
    return "Hello, World!"

@app.route('/chat', methods=['POST'])
async def chat():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in request body"}), 400
    text = data["text"]
    process_text_response  =  await process_text(text)
    print(f"PROCESS TEXT RESPONSE : {process_text_response}")
    return jsonify({"message": process_text_response}), 200

@app.route('/connect', methods=['GET'])
async def connect():
    try:
        logger.info("Client connected successfully.")
        chat_history = await get_chat_history(interview_id)
        if chat_history:
            await delete_chat_history(interview_id)
        check_session_state = await get_interview_session_state(interview_id)
        if check_session_state:
            await delete_interview_session_state(interview_id)
        if isinstance(initial_session_state["meta_payload"], dict):
            initial_session_state["meta_payload"] = EvaluateAnswerRequest(**initial_session_state["meta_payload"])
        initial_session_state["meta_payload"] = initial_session_state["meta_payload"].model_dump()
        await add_interview_session_state(interview_id, json.dumps(initial_session_state))
        
        return jsonify({'message': 'Connected successfully'}), 200
    
    except Exception as e:
        logger.error(f"Error in /connect: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/disconnect', methods=['GET'])
async def disconnect():
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