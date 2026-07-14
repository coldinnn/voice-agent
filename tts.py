import asyncio
import tempfile
import os
import platform
import subprocess
import edge_tts

VOICE = "en-US-AriaNeural"

async def _speak_async(text: str) -> None:
    communicate = edge_tts.Communicate(text, VOICE)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    await communicate.save(tmp_path)

    system = platform.system()
    if system == "Darwin":
        subprocess.run(["afplay", tmp_path], check=True)
    elif system == "Linux":
        subprocess.run(["mpg123", "-q", tmp_path], check=True)
    elif system == "Windows":
        subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{tmp_path}').PlaySync()"], check=True)

    os.unlink(tmp_path)


def speak(text: str) -> None:
    asyncio.run(_speak_async(text))
