"""
GCPのSpeech-To-Textで、非同期型の文字起こしを行うコード

"""

import os
from google.cloud import texttospeech
from google.cloud import speech
import sys
import pyaudio
from six.moves import queue

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../../key/speech-to-text.json"

from google.cloud import speech

def run_quickstart() -> speech.RecognizeResponse:
    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")


run_quickstart()