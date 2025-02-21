import json
import sounddevice as sd
import soundfile as sf
import websocket
import wave
import io
import queue
import asyncio
import threading
from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import time
from src.schemas.endpoints.schema import EvaluateAnswerRequest
from src.dao.interview_session_state import get_interview_session_state,update_interview_session_state,add_interview_session_state
SERVER_URL = "ws://localhost:8000"
samplerate = 16000

def run_async(func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(func)

# Parameters for chunking and overlap
chunk_duration = 30  # seconds per full chunk
chunk_samples = int(samplerate * chunk_duration)
overlap_percent = 0.5  # increased overlap to 50%
overlap_samples = int(chunk_samples * overlap_percent)
callback_blocksize = 1024  # for frequent audio callbacks

# Thread-safe queue for audio blocks
audio_queue = queue.Queue()
stop_event = threading.Event()

# Flags and timers
capture_enabled = True
last_non_silence_time = time.time()
# silence_detection_timeout = 8  # seconds
silence_detection_timeout = 10  # kept for Toyesh
silence_threshold = 0.04  # Adjust if needed


import sounddevice as sd
import numpy as np
from gtts import gTTS
import io
import wave

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    with wave.open(audio_buffer, 'rb') as wav_file:
        samplerate = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.int16)
    sd.play(audio_data, samplerate)
    sd.wait()  

def play_audio_bytes(audio_bytes):
    """
    Play audio from bytes data using sounddevice
    
    Parameters:
        audio_bytes (bytes): Audio data in bytes format
    """
    try:
        # Convert bytes to AudioSegment
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        
        # Convert to wav format in-memory
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        
        # Read the WAV data using soundfile
        data, samplerate = sf.read(wav_io)
        
        # Play the audio
        print("🎵 Playing audio...")
        sd.play(data, samplerate)
        sd.wait()  # Wait until audio is finished playing
        
        print("✅ Audio playback completed")
        
    except Exception as e:
        print(f"❌ Error playing audio: {e}")

def audio_callback(indata, frames, time_info, status):
    global last_non_silence_time, capture_enabled
    if status:
        print(f"⚠️ Audio stream error: {status}")
    if not capture_enabled:
        return

    # Compute RMS for silence detection
    float_data = indata.astype(np.float32) / 32768.0
    rms = (float_data ** 2).mean() ** 0.5
    # print(f"RMS: {rms:.4f}")  # Debug: print RMS value

    if rms > silence_threshold:
        last_non_silence_time = time.time()
    audio_queue.put(indata.copy())

def process_and_send_chunk(chunk, ws, final=False):
    if final:
        print("✅ Processing final audio chunk due to silence.")
    else:
        print("✅ Processing full 30-second audio chunk.")
    wav_buffer = io.BytesIO()
    try:
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit audio = 2 bytes per sample
            wav_file.setframerate(samplerate)
            wav_file.writeframes(chunk.tobytes())
    except Exception as e:
        print(f"❌ Error writing WAV file: {e}")
        return

    wav_data = wav_buffer.getvalue()
    duration = len(chunk) / samplerate
    print(f"Audio chunk duration: {duration:.2f} seconds")
    try:
        ws.send_binary(wav_data)
        print("📤 Sent audio chunk to server.")
    except Exception as e:
        print(f"❌ Error sending audio chunk: {e}")

def send_audio():
    global last_non_silence_time, capture_enabled
    try:
        ws = websocket.create_connection(SERVER_URL)
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return

    greeting = "Hello interviewee, I'm Noha, I'll be conducting your interview today. Let's get started with your first question: Find an index in an array where the sum of elements to the left equals the sum to the right"
    time.sleep(2)
    # initialize session_state for an interview right now interview_id = 1
    interview_id = 1 # hardcoded as 1 for now
    session_state = {
        "interim_chat_history": [],
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
        "interview_question_list": [2, 10], #questions in list are hard coded for now there should be a logic for this
        "class_label": None,
        "meta_payload": EvaluateAnswerRequest(
                #use pop here
                question_id=1, 
                question="What is your favorite programming language?",
                interview_id=1,
                answer="Python",
                eval_distribution=[0, 0, 0, 0, 0, 0, 0]
            ),
        "eval_distribution": [0, 0, 0, 0, 0, 0, 0],
        "final_score": 0,
        "messages": [{"role": "bot", "content": "Hello Arun, I am Noha..."}]
    }
    session_state['interview_id'] = interview_id
    session_state_db_data = run_async(get_interview_session_state(interview_id))
    if session_state_db_data:
        session_state['meta_payload'] = session_state['meta_payload'].model_dump()
        run_async(update_interview_session_state(interview_id, json.dumps(session_state)))
    else:
        session_state['meta_payload'] = session_state['meta_payload'].model_dump()
        run_async(add_interview_session_state(interview_id, json.dumps(session_state)))

    start_time = time.time()
    #update session_state/add session state for first turn
    accumulated_audio = np.empty((0,), dtype=np.int16)
    transcription_buffer = ""
    

    while not stop_event.is_set():
        # Force turn end after 250 seconds
        if time.time() - start_time >= 250:
            print("⏰ 250 seconds reached. Ending current turn.")
            # Drain any pending audio blocks
            while not audio_queue.empty():
                try:
                    block = audio_queue.get_nowait()
                    block = block.flatten()
                    accumulated_audio = np.concatenate((accumulated_audio, block))
                except Exception:
                    break
            if len(accumulated_audio) > 0:
                process_and_send_chunk(accumulated_audio, ws, final=True)
                accumulated_audio = np.empty((0,), dtype=np.int16)
            capture_enabled = False
            try:
                ws.send("STOP")
            except Exception as e:
                print(f"❌ Error sending STOP: {e}")
            start_time = time.time()

        # Check for silence detection
        if capture_enabled and (time.time() - last_non_silence_time >= silence_detection_timeout):
            print(f"🔇 Detected silence for {silence_detection_timeout} seconds. Preparing to end turn.")
            # Stop capturing new audio immediately
            capture_enabled = False
            # Allow a short extra period to ensure any pending audio is in the queue
            time.sleep(1)
            # Drain the queue into accumulated_audio
            while not audio_queue.empty():
                try:
                    block = audio_queue.get_nowait()
                    block = block.flatten()
                    accumulated_audio = np.concatenate((accumulated_audio, block))
                except Exception:
                    break
            if len(accumulated_audio) > 0:
                process_and_send_chunk(accumulated_audio, ws, final=True)
                accumulated_audio = np.empty((0,), dtype=np.int16)
            try:
                ws.send("STOP")
                print("🚦 STOP signal sent after flushing audio.")
            except Exception as e:
                print(f"❌ Error sending STOP: {e}")
            last_non_silence_time = time.time()

        # Accumulate audio blocks if capturing is enabled
        if capture_enabled:
            try:
                audio_block = audio_queue.get(timeout=0.1)
                audio_block = audio_block.flatten()
                accumulated_audio = np.concatenate((accumulated_audio, audio_block))
            except queue.Empty:
                pass

        # If accumulated audio reaches a full chunk, send it with overlap
        if len(accumulated_audio) >= chunk_samples:
            chunk = accumulated_audio[:chunk_samples]
            accumulated_audio = accumulated_audio[chunk_samples - overlap_samples:]
            process_and_send_chunk(chunk, ws)

        # Process incoming messages from the server
        try:
            ws.settimeout(0.1)
            response = ws.recv()
            if isinstance(response, bytes):
                print("🎵 Received TTS audio from server. Playing it...")
               # audio = AudioSegment.from_file(io.BytesIO(response), format="mp3")
                play_audio_bytes(response)
            elif isinstance(response, str):
                if response == "READY_TO_SPEAK":
                    print("💬 Popup: You can speak now!")
                    # Drain any pending audio blocks (if any) before starting a new turn
                    while not audio_queue.empty():
                        try:
                            block = audio_queue.get_nowait()
                            block = block.flatten()
                            accumulated_audio = np.concatenate((accumulated_audio, block))
                        except Exception:
                            break
                    start_time = time.time()
                    capture_enabled = True
                    last_non_silence_time = time.time()
                elif response == "DONE":
                    print("✅ Received DONE from server.")
                else:
                    transcription_buffer += " " + response
                    print(f"🎙️ Live Transcription: {transcription_buffer.strip()}")
        except websocket.WebSocketTimeoutException:
            pass
        except Exception as e:
            print(f"❌ Error receiving server message: {e}")

    try:
        ws.close()
    except Exception as e:
        print(f"❌ Error closing websocket: {e}")

def start_recording():
    print("🎤 Starting audio recording...")
    stream = sd.InputStream(
        samplerate=samplerate,
        channels=1,
        dtype='int16',
        callback=audio_callback,
        blocksize=callback_blocksize
    )
    stream.start()
    send_thread = threading.Thread(target=send_audio, daemon=True)
    send_thread.start()
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_event.set()
    stream.stop()
    stream.close()

if __name__ == "__main__":
    start_recording()