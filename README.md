# Voice Agent

A real-time voice assistant loop: speak into your mic → Whisper transcribes → Claude responds → edge-tts reads it back.

![Model: claude-opus-4-8](https://img.shields.io/badge/model-claude--opus--4--8-6c63ff)
![STT: Whisper base](https://img.shields.io/badge/STT-Whisper%20base-blue)
![TTS: edge-tts](https://img.shields.io/badge/TTS-edge--tts-green)

## How it works

```
mic → Whisper (local STT) → Claude Opus 4.8 (streaming) → edge-tts (free TTS) → speaker
```

1. Press Enter to start a recording session
2. Speak — silence detection automatically stops the recording after ~1.5s of quiet
3. Whisper transcribes your speech locally
4. Claude streams a response (printed token by token)
5. edge-tts converts the response to audio and plays it back

Multi-turn: conversation history is preserved across turns so Claude remembers context.

## Setup

**Prerequisites:** Python 3.9+

```bash
git clone https://github.com/coldinnn/voice-agent
cd voice-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

python agent.py
```

## Usage

```bash
# Default (conversational assistant, responds out loud)
python agent.py

# Custom system prompt
python agent.py --system "You are a Socratic tutor. Answer questions with questions."

# Text only — skip TTS playback
python agent.py --no-speak
```

## Example session

```
Voice Agent ready.
Speak after 'Listening...' appears. Pause to stop. Ctrl+C to quit.

Press Enter to speak →
Listening... Got it.
You: What's the capital of Japan?
Claude: Tokyo is the capital of Japan. It's one of the world's most populous cities and serves as the country's political, economic, and cultural center.
[speaks response]

Press Enter to speak →
Listening... Got it.
You: How many people live there?
Claude: Tokyo's greater metropolitan area is home to roughly 37 to 38 million people, making it the largest urban agglomeration in the world.
[speaks response]
```

## Stack

| Component | Tool | Why |
|---|---|---|
| STT | [OpenAI Whisper](https://github.com/openai/whisper) `base` model | Runs locally, no API cost, fast enough for real-time use |
| LLM | Claude Opus 4.8 via Anthropic API | Streaming, adaptive thinking |
| TTS | [edge-tts](https://github.com/rany2/edge-tts) | Free, high-quality Microsoft voices, no API key needed |
| Audio I/O | `sounddevice` | Cross-platform mic recording with energy-based VAD |

## Project structure

```
voice-agent/
├── agent.py        # Main loop — records, transcribes, calls Claude, speaks
├── stt.py          # Whisper wrapper with silence-based VAD
├── tts.py          # edge-tts wrapper (cross-platform playback)
├── requirements.txt
```

## Notes

- First run downloads the Whisper `base` model (~140MB)
- `edge-tts` requires an internet connection for TTS synthesis
- On Linux, install `mpg123` for audio playback: `sudo apt install mpg123`
- Silence threshold (`0.015` RMS) may need tuning in noisy environments — edit `stt.py`
