import os
import openai
import socketio
from flask_socketio import emit
from flask import Flask
from flask_cors import CORS
import json
from src.schemas.endpoints.schema import EvaluateAnswerRequest
from dotenv import load_dotenv
# from noha_dialogue import get_noha_dialogue
from _personal.noha_dialogue_v2 import get_noha_dialogue
from src.dao.interview_session_state import get_interview_session_state, update_interview_session_state, add_interview_session_state,delete_interview_session_state
from src.dao.chat_history import delete_chat_history
from src.utils.logger import get_logger
app = Flask(__name__)
CORS(app)

logger = get_logger(__name__)


# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create an ASGI-compatible Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi", logger=True, engineio_logger=True)

# Wrap the Flask app with the ASGI app from socket.io
asgi_app = socketio.ASGIApp(sio, app)

interview_id = 1 #hard-coded; should be fetched from DB
initial_session_state = {
    "chat_history": [],
    "rationale_logs": [],
    "hint_count": [0, 0, 0, 0, 0],
    "turn": 1,
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
    "interview_question_list": [2, 10], #questions in list are hard coded for now there should be a logic for this
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

# Socket.IO Events
@sio.event
async def connect(sid, environ):
    #flushing session state and chat history before starting the interview
    try:
        await delete_chat_history(interview_id)
    except Exception as e:
        pass
    try:
        await delete_interview_session_state(interview_id)
    except Exception as e:
        pass
    print(f"✅ Client connected: {sid}")

@sio.event
async def disconnect(sid):
    #flushing session state and chat history after interview ends
    try:
        await delete_interview_session_state(interview_id)
    except Exception as e:
        pass
    print(f"❌ Client disconnected: {sid}")

@sio.on("STOP")
async def handle_message(sid, text):
    """
    WebSocket handler for processing text input and returning GPT responses.
    """
    print(f"📩 Received text from {sid}: {text}")
    #if text.strip().upper() == "STOP":
    process_text_response  =  await process_text(text, sid)
    print(f"PROCESS TEXT RESPONSE : {process_text_response}")
    await sio.emit('streamBack', process_text_response)
    await sio.send("Processing request...", to=sid)  # Use await with sio.send()
    #else:
     #   print("Listening for next text...")

async def process_text(text, sid):
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
        if session_state_db_data: # fetch session_state from DB
            session_state_db_data=session_state_db_data[0]
            session_state_db_data_loaded=json.loads(session_state_db_data)
            session_state_db_data_loaded["meta_payload"] = EvaluateAnswerRequest(**session_state_db_data_loaded["meta_payload"])
            session_state = session_state_db_data_loaded
        else:
            if isinstance(initial_session_state["meta_payload"], dict):
                initial_session_state["meta_payload"] = EvaluateAnswerRequest(**initial_session_state["meta_payload"])
            session_state = initial_session_state
            initial_session_state["meta_payload"] = initial_session_state["meta_payload"].model_dump()
            await add_interview_session_state(interview_id, json.dumps(initial_session_state))

        print(f"SESSION STATE BEFORE CALLING get_bot_dialogue : \n {session_state}")
        response_list = await get_noha_dialogue(user_input, session_state) # response_list contains bot_dialogue and latest session_state
        response = response_list[0]
        session_state = response_list[1]
        interview_conclude_flag=session_state['conclude'] #False/True handles exiting the interview
        print(f"SESSION STATE AFTER CALLING get_bot_dialogue : \n {session_state}")
        print(f"NOHA BOT RESPONSE : {response}")
        if not isinstance(session_state['meta_payload'], dict):
            session_state['meta_payload'] = session_state['meta_payload'].model_dump()
        await(update_interview_session_state(interview_id, json.dumps(session_state))) #update session state
        return response
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    import uvicorn
    #print("🚀 Starting server on http://0.0.0.0:8000") ## for prod
    print("🚀 Starting server on http://localhost:7000") ## for dev

    # uvicorn.run(asgi_app, host="0.0.0.0", port=8000, log_level="debug") ##for prod
    uvicorn.run(asgi_app, host="localhost", port=7000, log_level="debug") ##for dev


