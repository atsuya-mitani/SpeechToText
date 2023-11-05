"""
リアルタイム文字起こし

"""

import speech_recognition as sr
import wave
import time
from datetime import datetime
import pyaudio


FORMAT        = pyaudio.paInt16
SAMPLE_RATE   = 44100        # サンプリングレート
CHANNELS      = 1            # モノラルかバイラルか
INPUT_DEVICE_INDEX = 0       # マイクのチャンネル
CALL_BACK_FREQUENCY = 3      # コールバック呼び出しの周期[sec]

OUTPUT_TXT_FILE = "./" + datetime.now().strftime('%Y%m%d_%H_%M') +".txt" # テキスト

def look_for_audio_input():
    """
    デバイスうえでのオーディオ系の機器情報を表示する
    """
    pa = pyaudio.PyAudio()

    for i in range(pa.get_device_count()):
        print(pa.get_device_info_by_index(i))
        print()

    pa.terminate()


def callback(in_data, frame_count, time_info, status):
    """
    コールバック関数の定義
    """
    
    global sprec # speech_recognitionオブジェクトを毎回作成するのではなく、使いまわすために、グローバル変数で定義しておく

    try:
        audiodata  = sr.AudioData(in_data, SAMPLE_RATE, 2)
        sprec_text = sprec.recognize_google(audiodata, language='ja-JP')
        
        with open(OUTPUT_TXT_FILE,'a') as f: #ファイルの末尾に追記していく
            f.write("\n" + sprec_text)
    
    except sr.UnknownValueError:
        pass
    
    except sr.RequestError as e:
        pass
    
    finally:
        return (None, pyaudio.paContinue)


def realtime_textise():
    """
    リアルタイムで音声を文字起こしする
    """

    with open(OUTPUT_TXT_FILE, 'w') as f: #txtファイルの新規作成
        DATE = datetime.now().strftime('%Y%m%d_%H:%M:%S')
        f.write("日時 : " + DATE + "\n") # 最初の一行目に日時を記載する

    global sprec # speech_recognitionオブジェクトを毎回作成するのではなく、使いまわすために、グローバル変数で定義しておく
    
    # speech recogniserインスタンスを生成
    sprec = sr.Recognizer() 
    
    # Audio インスタンス取得
    audio  = pyaudio.PyAudio() 
    
    # ストリームオブジェクトを作成
    stream = audio.open(format             = FORMAT,
                        rate               = SAMPLE_RATE,
                        channels           = CHANNELS,
                        input_device_index = INPUT_DEVICE_INDEX,
                        input              = True, 
                        frames_per_buffer  = SAMPLE_RATE*CALL_BACK_FREQUENCY, # CALL_BACK_FREQUENCY 秒周期でコールバック
                        stream_callback    = callback)
    
    stream.start_stream()
    
    while stream.is_active():
        time.sleep(0.1)
    
    stream.stop_stream()
    stream.close()
    audio.terminate()


def main():
    look_for_audio_input()
    realtime_textise()


if __name__ == '__main__':
    main()


