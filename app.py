import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
from src.schemas.endpoints.schema import EvaluateAnswerRequest
from noha_dialogue import get_bot_dialogue
from src.dao.interview_session_state import (
    get_interview_session_state, update_interview_session_state,
    add_interview_session_state, delete_interview_session_state
)

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

guest_namespace = '/guest'
interview_id = 1  # Hardcoded for now; should be fetched from DB

initial_session_state = {
    "interim_chat_history": [],
    "rationale_logs": [],
    "hint_count": [0, 0, 0, 0, 0],
    "turn": 1,
    "interview_id": interview_id,
    "previous_bot_dialogue": "Find an index in an array where the sum of elements to the left equals the sum to the right.",
    "assessment_payload": None,
    "guardrails_count": 0,
    "contiguous_unacceptable_answer_count": 0,
    "conversation_turn": 1,
    "contigous_guardrails_count": 0,
    "conclude": False,
    "current_question": "Find an index in an array where the sum of elements to the left equals the sum to the right.",
    "action_flag": "Pass",
    "conclude_message": "",
    "interview_question_list": [2, 10],
    "class_label": None,
    "meta_payload": EvaluateAnswerRequest(
        question_id=1,
        question="What is your favorite programming language?",
        interview_id=interview_id,
        answer="Python",
        eval_distribution=[0, 0, 0, 0, 0, 0, 0]
    ),
    "eval_distribution": [0, 0, 0, 0, 0, 0, 0],
    "final_score": 0,
    "messages": [{"role": "bot", "content": "Hello Arun, I am Noha..."}]
}

@socketio.on('connect', namespace=guest_namespace)
def handle_connect():
    logger.info(f"✅ Client connected: {request.sid}")

@socketio.on('disconnect', namespace=guest_namespace)
def handle_disconnect():
    delete_interview_session_state(interview_id)
    logger.info(f"❌ Client disconnected: {request.sid}")

@socketio.on("STOP", namespace=guest_namespace)
def handle_stop(text):
    logger.info(f"📩 Received text from, {text}")
    # process_text_response = process_text(text)
    socketio.emit('streamBack', 'Hi Nice to meet you', namespace=guest_namespace)

def process_text(text):
    logger.info(f"Sending text to Noha bot: {text}")
    if not text.strip():
        logger.warning("❌ Empty transcription; skipping dialogue generation request.")
        return
    
    session_state_db_data = get_interview_session_state(interview_id)
    if session_state_db_data:
        session_state = json.loads(session_state_db_data[0])
        session_state["meta_payload"] = EvaluateAnswerRequest(**session_state["meta_payload"])
    else:
        initial_session_state["meta_payload"] = initial_session_state["meta_payload"].model_dump()
        add_interview_session_state(interview_id, json.dumps(initial_session_state))
        session_state = initial_session_state
    
    logger.debug(f"SESSION STATE BEFORE CALLING get_bot_dialogue: {session_state}")
    response_list = get_bot_dialogue(text, session_state)
    response = response_list[0]
    session_state = response_list[1]
    
    logger.debug(f"SESSION STATE AFTER CALLING get_bot_dialogue: {session_state}")
    logger.info(f"NOHA BOT RESPONSE: {response}")
    
    if not isinstance(session_state['meta_payload'], dict):
        session_state['meta_payload'] = session_state['meta_payload'].model_dump()
    update_interview_session_state(interview_id, json.dumps(session_state))
    
    return response

@app.route('/hello', methods=['GET'])
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    socketio.run(app, host="localhost", port=5000, debug=True)


