#!/usr/bin/env python3
"""
Voice agent — speak to Claude, hear it respond.

Usage:
    python agent.py
    python agent.py --system "You are a concise assistant. Keep responses under 2 sentences."
"""
import argparse
import sys
import anthropic
from stt import record_until_silence, transcribe
from tts import speak

DEFAULT_SYSTEM = "You are a helpful voice assistant. Keep responses conversational and concise — aim for 2-3 sentences unless the question genuinely requires more."

def build_client() -> anthropic.Anthropic:
    return anthropic.Anthropic()

def chat(client: anthropic.Anthropic, history: list, system: str) -> str:
    full_response = ""
    print("Claude: ", end="", flush=True)
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=512,
        system=system,
        messages=history,
        thinking={"type": "adaptive"},
    ) as stream:
        for text in stream.text_stream:
            full_response += text
            print(text, end="", flush=True)
    print()
    return full_response

def main() -> None:
    parser = argparse.ArgumentParser(description="Voice agent powered by Claude + Whisper + edge-tts")
    parser.add_argument("--system", default=DEFAULT_SYSTEM, help="System prompt")
    parser.add_argument("--no-speak", action="store_true", help="Print responses only, skip TTS")
    args = parser.parse_args()

    client = build_client()
    history = []

    print("Voice Agent ready.")
    print("Speak after 'Listening...' appears. Pause to stop. Ctrl+C to quit.\n")

    while True:
        try:
            input("Press Enter to speak → ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            sys.exit(0)

        try:
            audio = record_until_silence()
        except Exception as e:
            print(f"Recording error: {e}")
            continue

        transcript = transcribe(audio)
        if not transcript:
            print("(nothing heard, try again)\n")
            continue

        print(f"You: {transcript}")
        history.append({"role": "user", "content": transcript})

        try:
            response = chat(client, history, args.system)
        except Exception as e:
            print(f"API error: {e}")
            history.pop()
            continue

        history.append({"role": "assistant", "content": response})

        if not args.no_speak:
            try:
                speak(response)
            except Exception as e:
                print(f"TTS error: {e}")

        print()

if __name__ == "__main__":
    main()
