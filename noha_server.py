import os
import openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
import json
from src.schemas.endpoints.schema import EvaluateAnswerRequest
from noha_dialogue import get_bot_dialogue
from src.dao.interview_session_state import get_interview_session_state, update_interview_session_state
# Load environment variables and set API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

interview_id = 1 #hardcoded as 1 should be fetched from DB
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for processing text input and returning noha-bot responses.
    """
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            if text.strip().upper() == "STOP":
                await websocket.send_text("Session ended.")
                break
            await process_text(text, websocket)
    except WebSocketDisconnect:
        print("Client disconnected.")

async def process_text(text: str, websocket: WebSocket):
    """
    Sends the received text to noha-bot and streams back the response.
    """
    print(f"Sending text to noha-bot : {text}")
    try:
        if not text.strip():
            print("❌ Empty transcription; skipping dialogue generation request.")
            return
        user_input=text
        session_state_db_data = await get_interview_session_state(interview_id) # fetch session_state from DB
        session_state_db_data_loaded=json.loads(session_state_db_data)
        session_state_db_data_loaded["meta_payload"] = EvaluateAnswerRequest(**session_state_db_data_loaded["meta_payload"])
        session_state = session_state_db_data_loaded
        response_list = await get_bot_dialogue(user_input, session_state) #response_list contains bot_dialogue and latest session_state

        #print(f"BOT DIALOGUE INTEGRATED RESPONSE LIST : {response_list}") 
        
        response = response_list[0]
        # print("Dialogue response:", response)
        session_state = response_list[1]
        interview_conclude_flag=session_state['conclude'] #False/True handles exiting the interview
        session_state['meta_payload'] = session_state['meta_payload'].model_dump()
        await(update_interview_session_state(interview_id, json.dumps(session_state))) #update session state 
		
        buffer = ""
        for chunk in response:
            if chunk["choices"] and chunk["choices"][0]["delta"].get("content"):
                llm_text = chunk["choices"][0]["delta"]["content"]
                buffer += llm_text

                # When a sentence-ending punctuation is encountered, send the buffered text
                if buffer.strip() and buffer.strip()[-1] in ".!?":
                    print(f"Sending: {buffer.strip()}")
                    await websocket.send_text(buffer.strip())
                    buffer = ""

        # Send any remaining text
        if buffer.strip():
            await websocket.send_text(buffer.strip())

        # Signal that the response is complete
        await websocket.send_text("READY_TO_SPEAK")
    except openai.error.OpenAIError as e:
        print(f"noha-bot Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)