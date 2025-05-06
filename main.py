from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from tts import TTS

tts = TTS()

app = FastAPI()

class TTSRequest(BaseModel):
    text: str
    spk_id: str = ""

@app.post("/tts")
async def tts_endpoint(request: TTSRequest):
    return StreamingResponse(tts.call(request.text, request.spk_id), media_type="audio/wav")

@app.get("/list_spk")
async def list_spk():
    return tts.list_spk()

@app.get("/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)