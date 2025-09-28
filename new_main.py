import os

# This line MUST be before importing torch or whisper
# It resolves a common issue on macOS where two different OpenMP libraries are loaded.
os.environ['KMP_DUPLICATE_LIB_OK']='True'

import urllib.request
import whisper
import torch

def format_time(seconds):
    """
    Format the given time in seconds into HH:MM:SS.
    Rounds to the nearest whole second.
    """
    rounded_seconds = int(round(seconds))
    hrs = rounded_seconds // 3600
    mins = (rounded_seconds % 3600) // 60
    secs = rounded_seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

def whisper_transcribe(url: str, model_size: str = "base", language: str = None):
    """
    Transcribes an audio file from a URL using OpenAI's Whisper model.

    Args:
        url (str): The URL of the audio file to transcribe.
        model_size (str): The size of the Whisper model to use 
                          (e.g., "tiny", "base", "small", "medium", "large").
        language (str): The language of the audio. Set to None for auto-detection.

    Returns:
        str: The formatted transcript with timestamps, or None if transcription fails.
    """
    temp_audio_file = "temp_audio.wav"
    try:
        # Download the audio file from the URL
        print(f"Downloading audio from {url}...")
        urllib.request.urlretrieve(url, temp_audio_file)
        print("Download complete.")

        # --- Transcription ---
        print(f"Loading Whisper model: {model_size}...")
        model = whisper.load_model(model_size)
        print("Model loaded.")
        
        print("Starting transcription...")
        # Check for GPU and use fp16 if available
        use_fp16 = torch.cuda.is_available()
        
        # Set up transcription options, including language if specified
        transcribe_options = {"fp16": use_fp16}
        if language:
            transcribe_options["language"] = language
            print(f"Transcription language set to: {language}")

        result = model.transcribe(temp_audio_file, **transcribe_options)
        print("Transcription complete.")

        # --- Format Transcript ---
        print("Formatting transcript...")
        full_text = []
        for segment in result['segments']:
            start_time = format_time(segment['start'])
            end_time = format_time(segment['end'])
            text = segment['text'].strip()
            formatted_segment = f"[{start_time} - {end_time}] {text}"
            full_text.append(formatted_segment)

        return "\n".join(full_text)

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        # Clean up the downloaded audio file
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
            print(f"Removed temporary file: {temp_audio_file}")


if __name__ == "__main__":
    URL = "https://storage.googleapis.com/radiotransdata/audio-files/redfm_TESTER_06_28_24_08_28_00%20(1)%20(1).wav"
    
    # You can choose the model size. "base" is a good starting point.
    # Other options: "tiny", "small", "medium", "large"
    MODEL_SIZE = "base"

    # Set the language for transcription.
    # For English, use "en".
    # For Punjabi, use "pa".
    # Set to None to let Whisper auto-detect the language.
    LANGUAGE = "pa"

    transcript = whisper_transcribe(URL, model_size=MODEL_SIZE, language=LANGUAGE)
    if transcript:
        print("\n--- TRANSCRIPT ---")
        print(transcript)
    else:
        print("Transcription failed.")

