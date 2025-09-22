import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import soundfile as sf
import io
import librosa
import os
import sys
import csv

# 1. YAMNet 모델 로드
# 모델은 처음 로드할 때만 다운로드됩니다.
try:
    model = hub.load('https://tfhub.dev/google/yamnet/1')
except Exception as e:
    print(f"YAMNet 모델 로드 중 오류 발생: {e}")
    # 필요한 경우 오류 처리 로직 추가

# 2. 클래스 맵 파일 로드
try:
    yamnet_class_map_path = os.path.join(os.path.dirname(__file__), 'yamnet_class_map.csv')
    class_names = []
    with open(yamnet_class_map_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            class_names.append(row[2])
    class_names = class_names[1:] # 헤더 제외
except FileNotFoundError:
    print(f"Error: {yamnet_class_map_path} 파일을 찾을 수 없습니다. TensorFlow Hub에서 직접 다운로드하세요.")
    sys.exit()

def analyze_noise_from_file(file_content: bytes):
    """
    업로드된 오디오 파일을 YAMNet 모델로 분석하여 가장 가능성 높은 소음 카테고리를 반환합니다.
    """
    try:
        y, sr = sf.read(io.BytesIO(file_content), dtype='float32')

        if y.ndim > 1:
            y = np.mean(y, axis=1)
        
        if sr != 16000:
            y = librosa.resample(y=y, orig_sr=sr, target_sr=16000)
            sr = 16000
        
        if len(y) == 0:
            raise ValueError("Audio data is empty or too short after processing.")
        
        scores, embeddings, spectrogram = model(y)
        prediction = np.mean(scores, axis=0)
        top_indices = np.argsort(prediction)[::-1]
        
        results = []
        for i in range(5):
            label = class_names[top_indices[i]]
            score = float(prediction[top_indices[i]])
            results.append({"label": label, "score": score})
        
        rms = librosa.feature.rms(y=y)
        db = float(librosa.core.amplitude_to_db(rms, ref=1.0).mean())

        return {"analysis": results, "db": round(db, 2)}
    
    except Exception as e:
        print(f"Error during noise analysis: {e}")
        return {"error": str(e), "analysis": None, "db": None}