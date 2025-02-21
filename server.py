import asyncio
import io
import os
import wave
import websockets
import numpy as np
import openai
import whisper
from gtts import gTTS
from dotenv import load_dotenv
from websockets.exceptions import ConnectionClosed
from noha_dialogue import get_bot_dialogue
from src.schemas.endpoints.schema import EvaluateAnswerRequest
# Load environment variables and API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Whisper model (adjust model size as needed)
model = whisper.load_model("medium")
from src.services.workflows.candidate_dialogue_classifier import classify_candidate_dialogue
from src.dao.question import get_question_metadata
import json
from src.dao.interview_session_state import get_interview_session_state, update_interview_session_state, delete_interview_session_state, add_interview_session_state
# async def async_get_get_question_metadata(question_id):
#     return await get_question_metadata(question_id)

# def run_async(func):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     return loop.run_until_complete(func)

interview_id = 1 #should be passed; right now hard coded as 1
async def stream_llm_response(text, websocket):
    print(f"TEXT BEFORE CALLING BOT DIALOGUE{text}")
    """
    Uses generate_dialogue_audio_integration to generate dialogue based on the transcription.
    Sends the dialogue response as text and TTS audio to the client, then signals "READY_TO_SPEAK".
    """
    if not text.strip():
        print("❌ Empty transcription; skipping dialogue generation request.")
        return

    print("🤖 Sending dialogue generation request...")
    try:
        print(f"USER INPUT TRY BLOCK : {text}")
        user_input=text
        session_state_db_data = await get_interview_session_state(interview_id) # fetch session_state from DB
        session_state_db_data_loaded=json.loads(session_state_db_data)
        session_state_db_data_loaded["meta_payload"] = EvaluateAnswerRequest(**session_state_db_data_loaded["meta_payload"])
        session_state = session_state_db_data_loaded
        response_list = await get_bot_dialogue(user_input, session_state) #response_list contains bot_dialogue and latest session_state

        print(f"BOT DIALOGUE INTEGRATED RESPONSE LIST : {response_list}") 
        
        dialogue_response = response_list[0]
        print("Dialogue response:", dialogue_response)
        session_state = response_list[1]
        interview_conclude_flag=session_state['conclude'] #False/True handles exiting the interview
        session_state['meta_payload'] = session_state['meta_payload'].model_dump()
        await(update_interview_session_state(interview_id, json.dumps(session_state))) #update session state 
        # Send the dialogue response text to the client.


        if not websocket.closed:
            try:
                await websocket.send(dialogue_response)
            except Exception as e:
                print(f"❌ Error sending dialogue response: {e}")
        
        # Generate and send TTS audio for the dialogue response.
        await send_tts_audio(dialogue_response, websocket,save_path="./audio.wav")
        
        # Finally, signal that the turn is complete.
        if not websocket.closed:
            try:
                await websocket.send("READY_TO_SPEAK")
                print("🟢 Sent READY_TO_SPEAK to client.")
            except Exception as e:
                print(f"❌ Error sending READY_TO_SPEAK: {e}")

    except Exception as e:
        print(f"❌ Error in dialogue generation: {e}")



"""
async def stream_llm_response(text, websocket):

    if not text.strip():
        print("❌ Empty transcription; skipping LLM request.")
        return

    print("🤖 Sending transcription to LLM...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ],
            stream=True
        )
        buffer = ""
        for chunk in response:
            if chunk["choices"] and chunk["choices"][0]["delta"].get("content"):
                llm_text = chunk["choices"][0]["delta"]["content"]
                buffer += llm_text
                if buffer.strip() and buffer.strip()[-1] in ".!?":
                    print(f"📨 Sending LLM chunk: {buffer.strip()}")
                    if not websocket.closed:
                        try:
                            await websocket.send(buffer.strip())
                        except ConnectionClosed as e:
                            print(f"❌ Error sending text: {e}")
                    await send_tts_audio(buffer.strip(), websocket)
                    buffer = ""
        if buffer.strip():
            if not websocket.closed:
                try:
                    await websocket.send(buffer.strip())
                except ConnectionClosed as e:
                    print(f"❌ Error sending final text: {e}")
            await send_tts_audio(buffer.strip(), websocket)

        if not websocket.closed:
            try:
                await websocket.send("READY_TO_SPEAK")
                print("🟢 Sent READY_TO_SPEAK to client.")
            except ConnectionClosed as e:
                print(f"❌ Error sending READY_TO_SPEAK: {e}")

    except openai.error.OpenAIError as e:
        print(f"❌ OpenAI API Error: {e}")
    except Exception as e:
        print(f"❌ Error in LLM streaming: {e}")
"""
async def send_tts_audio(text, websocket, save_path="./audio.wav"):
    """
    Converts text to speech, optionally saves the resulting audio to a file,
    and sends the audio to the client.
    """
    try:
        tts = gTTS(text, lang="en", tld="com.au")
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        # Save the audio to a file if save_path is provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(audio_buffer.getvalue())
            print(f"🔊 Audio saved to {save_path}")

        print("🔊 Sending TTS audio to client...")
        if not websocket.closed:
            try:
                await websocket.send(audio_buffer.getvalue())
            except ConnectionClosed as e:
                print(f"❌ Error sending TTS audio: {e}")
    except Exception as e:
        print(f"❌ Error generating TTS audio: {e}")

async def transcribe(websocket):
    """
    Receives audio chunks and control messages from the client. When a "STOP"
    message is received, it processes the accumulated transcription, sends it to
    the LLM, returns TTS audio for the response, and then signals "READY_TO_SPEAK".
    """
    transcription_buffer = ""
    turn_in_progress = True

    try:
        async for message in websocket:
            # If a new message comes after a turn ended, start a new turn.
            if not turn_in_progress:
                print("🟢 Starting new turn.")
                turn_in_progress = True
                transcription_buffer = ""

            if isinstance(message, str) and message == "STOP":
                if turn_in_progress:
                    print("🚦 Received STOP signal. Processing transcription...")
                    if transcription_buffer.strip():
                        await stream_llm_response(transcription_buffer.strip(), websocket)
                    else:
                        print("❌ No transcription data to process.")
                    transcription_buffer = ""
                    turn_in_progress = False
                else:
                    print("🚦 Duplicate STOP received; ignoring.")
                continue

            if isinstance(message, bytes):
                wav_buffer = io.BytesIO(message)
                try:
                    with wave.open(wav_buffer, 'rb') as wav_file:
                        audio_bytes = wav_file.readframes(wav_file.getnframes())
                    print(f"🎧 Received audio chunk of {len(audio_bytes)} bytes")
                except Exception as e:
                    print(f"❌ Error reading audio chunk: {e}")
                    continue

                try:
                    audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                except Exception as e:
                    print(f"❌ Error converting audio: {e}")
                    continue

                try:
                    result = model.transcribe(
                        audio, fp16=False, temperature=0.5,
                        no_speech_threshold=0.8, logprob_threshold=-1.0
                    )
                    transcribed_text = result["text"].strip()
                    print(f"🎙️ Transcribed text: {transcribed_text} \n")
                    transcription_buffer += " " + transcribed_text

                    if not websocket.closed and transcribed_text:
                        try:
                            await websocket.send(transcribed_text)
                        except ConnectionClosed as e:
                            print(f"❌ Error sending live transcription: {e}")
                except Exception as e:
                    print(f"❌ Error during transcription: {e}")
    except ConnectionClosed:
        print("🔴 Client disconnected.")
    except Exception as e:
        print(f"❌ Error in transcribe handler: {e}")

async def main():
    async with websockets.serve(transcribe, "localhost", 8000, ping_interval=None):
        print("🔗 WebSocket server running on ws://localhost:8000")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())