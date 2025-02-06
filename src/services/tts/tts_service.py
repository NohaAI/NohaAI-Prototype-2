from gtts import gTTS
import tempfile
import os
import base64
import time
import torch
from TTS.api import TTS

# Supported accents mapping
SUPPORTED_ACCENTS = {
    "Australian English": ("en", "com.au"),
    "British English": ("en", "co.uk"),
    "Indian English": ("en", "co.in"),
    "American English": ("en", "com"),
    "Irish English": ("en", "ie"),
    "South African English": ("en", "co.za"),
    "Canadian English": ("en", "ca"),
    "Filipino English": ("en", "ph"),
    "Spanish (Spain)": ("es", "es"),
    "French (France)": ("fr", "fr"),
    "German": ("de", "de"),
    "Italian": ("it", "it"),
    "Japanese": ("ja", "co.jp"),
    "Korean": ("ko", "co.kr")
}

def text_to_speech(text: str, lang: str = 'en', tld: str = "com.au") -> str:
    try:
        tts = gTTS(text=text, lang=lang, tld=tld)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        return temp_file.name 
    
    except Exception as e:
        return None
    
def text_to_speech_cq(text, lang='en'):
    try:
        if lang == 'en':
            model_name = "tts_models/en/ljspeech/tacotron2-DDC" #English model
        elif lang == 'es':
            model_name = "tts_models/es/css10/vits"  # Spanish model
        elif lang == 'fr':
            model_name = "tts_models/fr/css10/vits"  # French model
        else:
            return None

        tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            output_file = temp_file.name
            tts.tts_to_file(text=text, file_path=output_file)
        return output_file
    except Exception as e:
        return None
