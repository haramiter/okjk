from fastapi import APIRouter, File, UploadFile
from ai.yamnet_api import analyze_noise_from_file

router = APIRouter(prefix="/noise")

@router.post("/analyze")
async def analyze_noise(audio_file: UploadFile = File(...)):
    """
    업로드된 음성 파일을 분석하여 소음 카테고리 및 데시벨(db)을 반환합니다.
    """
    audio_data = await audio_file.read()
    
    # ai.yamnet_api 파일의 함수를 호출하여 분석 결과를 받아옵니다.
    result = analyze_noise_from_file(audio_data)
    
    return result