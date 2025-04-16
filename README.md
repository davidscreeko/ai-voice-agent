# Real-Time AI Voice Agent v2

Adds real-time streaming and conversational loop using:
- AssemblyAI for live transcription
- Claude for replies in German
- ElevenLabs for voice generation
- Twilio media stream compatible endpoint

## Endpoints
- `/media` (WebSocket): receives Twilio audio stream and transcribes
- `/static/response.mp3`: plays generated audio file

## Next Steps
- Handle incoming Twilio stream audio
- Return audio stream or `Play` instructions live
- Host MP3 publicly if using TwiML <Play>

## Run Locally
```bash
uvicorn main:app --reload
```
