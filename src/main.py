import os
from google.cloud import texttospeech
from google.cloud import speech
import sys
import pyaudio
from six.moves import queue

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../../key/speech-to-text.json"

# マイク音声のストリーム
class MicStream:
    # 初期化
    def __init__(self, rate, chunk):
        self._rate = rate # サンプルレート
        self._chunk = chunk # チャンクサイズ
        self._buff = queue.Queue() # マイク入力データを貯めるバッファ
        self.closed = True # クローズ

    # リソース確保
    def __enter__(self):
        # PyAudioでマイク入力を開始
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16, # フォーマット
            channels=1, # チャンネル数
            rate=self._rate, # サンプルレート
            input=True, # 入力
            frames_per_buffer=self._chunk, # チャンクサイズ
            stream_callback=self._fill_buffer, # コールバック
        )
        self.closed = False # オープン
        return self

    # リソース破棄
    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream() # ストリーム停止
        self._audio_stream.close() # ストリームクローズ
        self.closed = True # クローズ
        self._buff.put(None) # バッファ解放
        self._audio_interface.terminate() # オーディオ解放

    # マイク入力データをバッファに貯める
    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    # ストリームの生成
    def generator(self):
        while not self.closed:
            # 少なくとも1つのチャンクがあることを確認
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # バッファリングされているデータを全て消費
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

# ストリーミング音声認識の結果の取得
def listen_print_loop(responses):
    num_chars_printed = 0

    # メインループ
    for response in responses:
        # 入力リクエストが有効かどうか
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue

        # テキストの取得
        transcript = result.alternatives[0].transcript
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        # 音声認識中のテキスト出力
        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            num_chars_printed = len(transcript)

        # 音声認識確定後のテキスト出力
        else:
            print(transcript + overwrite_chars)
            num_chars_printed = 0
            '''Text-to-Speechの処理'''
            text= transcript + overwrite_chars

            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code='ja-JP',
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16
            )

            client = texttospeech.TextToSpeechClient()
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            with open('parrot.wav', 'wb') as out:
                out.write(response.audio_content)
            #作成した音声ファイルの再生    
            from playsound import playsound
            playsound("parrot.wav")
            print('end')
            break



# 録音パラメータの準備
RATE = 16000 # サンプルレート
CHUNK = int(RATE / 10)  # チャンクサイズ (100ms)

# 音声認識設定の準備
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, # オーディオ種別
    sample_rate_hertz=RATE, # サンプルレート
    language_code='ja',
)

# ストリーミング音声認識設定の準備
streaming_config = speech.StreamingRecognitionConfig(
    config=config, # 音声認識設定
    interim_results=True # 中間結果の取得
)


# マイク音声のストリームの生成
with MicStream(RATE, CHUNK) as stream:
    audio_generator = stream.generator()

    # 入力リクエストの準備
    requests = (
        speech.StreamingRecognizeRequest(audio_content=content)
        for content in audio_generator
    )

    # ストリーミング音声認識の実行
    client = speech.SpeechClient()
    responses = client.streaming_recognize(
        config=streaming_config, # ストリーミング音声認識設定
        requests=requests) # 入力リクエスト

    # ストリーミング音声認識の結果の取得
    listen_print_loop(responses)








