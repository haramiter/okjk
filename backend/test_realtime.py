import sounddevice as sd
import soundfile as sf
import numpy as np
import io
import time
from ai.analyze_voice import analyze_voice_for_fun

def record_audio(duration, filename, samplerate=44100, channels=1):
    print("마이크 녹음을 시작합니다. 5초 동안 말씀해주세요...")
    try:
        # 녹음
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='float32')
        sd.wait()
        print("녹음이 완료되었습니다.")
        
        # NumPy 배열을 메모리 버퍼에 WAV 파일로 저장
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, audio_data, samplerate, format='WAV')
        audio_buffer.seek(0)
        
        return audio_buffer.read()

    except Exception as e:
        print(f"녹음 중 오류가 발생했습니다: {e}")
        return None

if __name__ == "__main__":
    # 마이크로 5초 녹음
    audio_bytes = record_audio(duration=5, filename='recorded_voice.wav')

    if audio_bytes:
        # 녹음된 데이터를 분석 함수에 전달
        print("음성 분석을 시작합니다...")
        result = analyze_voice_for_fun(audio_bytes)
        print("\n--- 분석 결과 ---")
        for key, value in result.items():
            print(f"{key}: {value}")
        print("------------------")