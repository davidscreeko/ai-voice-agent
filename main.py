from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from dotenv import load_dotenv
import os, requests, json, asyncio, websockets

load_dotenv()
app = FastAPI()

# Claude + ElevenLabs function
def process_message(message: str):
    prompt = f"Du bist ein höflicher Assistent und sprichst Deutsch. Ein Gast sagt: '{message}' Antworte passend, kurz und freundlich."
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Authorization": "Bearer " + os.getenv("ANTHROPIC_API_KEY"),
            "Content-Type": "application/json"
        },
        json={
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    reply = response.json()['content'][0]['text']

    tts = requests.post(
        "https://api.elevenlabs.io/v1/text-to-speech/" + os.getenv("ELEVENLABS_VOICE_ID"),
        headers={
            "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
            "Content-Type": "application/json"
        },
        json={"text": reply, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
    )

    with open("static/response.mp3", "wb") as f:
        f.write(tts.content)

    return "/static/response.mp3"

@app.websocket("/media")
async def media_stream(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")

    # Connect to AssemblyAI real-time
    async with websockets.connect(
        "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000",
        extra_headers={"Authorization": os.getenv("ASSEMBLYAI_API_KEY")}
    ) as transcriber_ws:

        async def receive_from_assemblyai():
            while True:
                result = await transcriber_ws.recv()
                text = json.loads(result).get("text", "")
                if text:
                    print("Heard:", text)
                    path = process_message(text)
                    print("Generated reply audio:", path)
                    # TODO: stream this MP3 back to Twilio if possible

        # Start listening
        await receive_from_assemblyai()


    from fastapi.staticfiles import StaticFiles

    app.mount("/static", StaticFiles(directory="static"), name="static")
