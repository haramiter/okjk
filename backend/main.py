from fastapi import FastAPI
import uvicorn
from router import noise_router, voice_router # 새로 만든 라우터 import

app = FastAPI()

# 라우터들을 앱에 포함
app.include_router(noise_router.router, tags=["Noise Detection"])
app.include_router(voice_router.router, tags=["Voice Analysis"])

@app.get("/")
def read_root():
    return {"message": "AI Living Noise Solver is running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)