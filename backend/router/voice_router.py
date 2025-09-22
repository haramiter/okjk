from fastapi import APIRouter, File, UploadFile
from ai.analyze_voice import analyze_voice_for_fun

router = APIRouter(prefix="/voice")

@router.post("/analyze")
async def analyze_voice(file: UploadFile = File(...)):
    """
    마이크에서 전송된 음성 데이터를 분석하여 톤과 피치 변동성을 기반으로 동물 소리를 반환합니다.
    """
    audio_data = await file.read()
    
    # 목소리 분석 로직이 있는 함수를 호출합니다.
    result = analyze_voice_for_fun(audio_data)
    
    return result