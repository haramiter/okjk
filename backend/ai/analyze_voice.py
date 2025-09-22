import io
import numpy as np
import soundfile as sf
import librosa

# -------------------------
# 피치 범위에 따른 톤 매핑
# -------------------------
TONE_RANGES = {}
pitch_start = 50
pitch_end = 430
step = 20
for i in range(pitch_start, pitch_end, step):
    category_name = f"{i}~{i+step}Hz"
    TONE_RANGES[category_name] = {"min": i, "max": i + step}

# -------------------------
# 피치 변동성 범위
# -------------------------
VARIABILITY_RANGES = {
    "단조로운": {"min": 0, "max": 20},
    "보통 변동": {"min": 21, "max": 50},
    "다이나믹한": {"min": 51, "max": 100},
}

# -------------------------
# 톤-동물 소리 매핑
# -------------------------
COMPLEX_MAPPING = {
    ("50~70Hz", "단조로운"): "하품하는 아기 하마",
    ("50~70Hz", "보통 변동"): "깊은 굴속에서 우는 아기 곰",
    ("50~70Hz", "다이나믹한"): "포효하는 사자",
    ("70~90Hz", "단조로운"): "단조롭게 으르렁거리는 팬더",
    ("70~90Hz", "보통 변동"): "무언가를 쫓는 스컹크",
    ("70~90Hz", "다이나믹한"): "지나가는 기차에 울부 짖는 늑대",
    ("90~110Hz", "단조로운"): "나뭇가지에 앉은 부엉이",
    ("90~110Hz", "보통 변동"): "심술 난 코뿔소",
    ("90~110Hz", "다이나믹한"): "분노에 찬 코끼리",
    ("110~130Hz", "단조로운"): "그윽한 고양이",
    ("110~130Hz", "보통 변동"): "밥 달라고 애교 부리는 강아지",
    ("110~130Hz", "다이나믹한"): "주인에게 투정 부리는 코끼리",
    ("130~150Hz", "단조로운"): "조용히 멍 때리는 시바견",
    ("130~150Hz", "보통 변동"): "신나게 뛰어 노는 돼지",
    ("130~150Hz", "다이나믹한"): "정신없이 짖는 댕댕이",
    ("150~170Hz", "단조로운"): "소리를 억누르는 펭귄",
    ("150~170Hz", "보통 변동"): "애처롭게 우는 아기 원숭이",
    ("150~170Hz", "다이나믹한"): "경보를 알리는 침팬지",
    ("170~190Hz", "단조로운"): "귀여운 비명을 지르는 다람쥐",
    ("170~190Hz", "보통 변동"): "숲 속을 뛰는 고라니",
    ("170~190Hz", "다이나믹한"): "위협하는 고릴라",
    ("190~210Hz", "단조로운"): "하염없이 우는 길 잃은 염소",
    ("190~210Hz", "보통 변동"): "엄마를 찾는 새끼 양",
    ("190~210Hz", "다이나믹한"): "산 정상에서 짖는 염소",
    ("210~230Hz", "단조로운"): "수풀 속에 숨은 토끼",
    ("210~230Hz", "보통 변동"): "겁에 질린 사슴",
    ("210~230Hz", "다이나믹한"): "겁 먹은 생쥐",
    ("230~250Hz", "단조로운"): "정신없는 원숭이",
    ("230~250Hz", "보통 변동"): "심장이 쿵쾅거리는 사슴",
    ("230~250Hz", "다이나믹한"): "흥분한 토끼",
    ("250~270Hz", "단조로운"): "조심스럽게 움직이는 기린",
    ("250~270Hz", "보통 변동"): "심심해서 우는 어린 사슴",
    ("250~270Hz", "다이나믹한"): "지쳐서 우는 기린",
    ("270~290Hz", "단조로운"): "한가로운 새의 비행",
    ("270~290Hz", "보통 변동"): "엄마를 찾는 아기 새",
    ("270~290Hz", "다이나믹한"): "새의 폭풍 비행",
    ("290~310Hz", "단조로운"): "신호 보내는 사슴",
    ("290~310Hz", "보통 변동"): "하품하는 어린 양",
    ("290~310Hz", "다이나믹한"): "질주하는 사슴",
    ("310~330Hz", "단조로운"): "풀 뜯어먹는 토끼",
    ("310~330Hz", "보통 변동"): "길을 잃어 울부 짖는 토끼",
    ("310~330Hz", "다이나믹한"): "위협하는 토끼",
    ("330~350Hz", "단조로운"): "숲 속을 걷는 코끼리",
    ("330~350Hz", "보통 변동"): "물가에 멈춰선 코끼리",
    ("330~350Hz", "다이나믹한"): "경계하는 코끼리",
    ("350~370Hz", "단조로운"): "정처없이 떠도는 하마",
    ("350~370Hz", "보통 변동"): "배고파서 우는 하마",
    ("350~370Hz", "다이나믹한"): "호수에 빠진 하마",
    ("370~390Hz", "단조로운"): "졸음에 겨운 새",
    ("370~390Hz", "보통 변동"): "엄마 젖을 찾는 새",
    ("370~390Hz", "다이나믹한"): "겁 먹은 새",
    ("390~410Hz", "단조로운"): "평화롭게 밥을 먹는 비둘기",
    ("390~410Hz", "보통 변동"): "날지 못해 슬피 우는 비둘기",
    ("390~410Hz", "다이나믹한"): "비명을 지르는 비둘기",
    ("410~430Hz", "단조로운"): "평화로운 닭",
    ("410~430Hz", "보통 변동"): "병아리를 잃어버린 닭",
    ("410~430Hz", "다이나믹한"): "세상에서 제일 화가 난 닭"
}

# -------------------------
# 분석 함수
# -------------------------
def analyze_voice_for_fun(audio_data):
    try:
        y, sr = sf.read(io.BytesIO(audio_data), dtype='float32')

        if len(y.shape) > 1:
            y = np.mean(y, axis=1)

        intervals = librosa.effects.split(y, top_db=25)
        if not intervals.any():
            return {"status": "failure", "message": "유효한 음성 구간이 없습니다."}

        y_voice = np.concatenate([y[start:end] for start, end in intervals])
        if len(y_voice) == 0:
            return {"status": "failure", "message": "분석할 음성 데이터가 너무 짧습니다."}

        pitches, magnitudes = librosa.piptrack(y=y_voice, sr=sr)
        valid_pitches = pitches[magnitudes > np.mean(magnitudes) * 0.7]
        valid_pitches = valid_pitches[(valid_pitches >= 50) & (valid_pitches <= 430)]
        if valid_pitches.size == 0:
            return {"status": "failure", "message": "허용 범위 내 유효한 피치를 감지할 수 없습니다."}

        median_pitch = np.median(valid_pitches)
        std_pitch = np.std(valid_pitches)

        pitch_category = next(
            (cat for cat, r in TONE_RANGES.items() if r["min"] <= median_pitch <= r["max"]),
            "알 수 없는 피치"
        )

        variability_category = next(
            (cat for cat, r in VARIABILITY_RANGES.items() if r["min"] <= std_pitch <= r["max"]),
            "알 수 없는 변동성"
        )

        mapped_sound = COMPLEX_MAPPING.get((pitch_category, variability_category), "알 수 없는 소리")

        return {
            "status": "success",
            "median_pitch": float(round(median_pitch, 2)),
            "pitch_std": float(round(std_pitch, 2)),
            "tone_category": pitch_category,
            "variability_category": variability_category,
            "mapped_sound": mapped_sound
        }

    except Exception as e:
        return {"status": "failure", "message": f"음성 분석 중 오류 발생: {str(e)}"}

# -------------------------
# 테스트 예제
# -------------------------
if __name__ == "__main__":
    # 테스트용 WAV 파일 경로
    test_file_path = "example_voice.wav"  # 실제 WAV 파일로 교체 필요
    try:
        with open(test_file_path, "rb") as f:
            audio_bytes = f.read()
        result = analyze_voice_for_fun_stable(audio_bytes)
        print("분석 결과:", result)
    except FileNotFoundError:
        print(f"테스트 WAV 파일을 찾을 수 없습니다: {test_file_path}")
