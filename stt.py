import numpy as np
import sounddevice as sd
import whisper

_model = None

def _get_model():
    global _model
    if _model is None:
        print("Loading Whisper model...")
        _model = whisper.load_model("base")
    return _model

def record_until_silence(
    sample_rate: int = 16000,
    silence_threshold: float = 0.015,
    silence_duration: float = 1.5,
    max_duration: float = 30.0,
) -> np.ndarray:
    """Record from mic until silence_duration seconds of quiet, or max_duration seconds total."""
    frames = []
    silent_frames = 0
    silence_limit = int(silence_duration * sample_rate / 512)
    max_frames = int(max_duration * sample_rate / 512)
    recording_started = False

    def callback(indata, frame_count, time_info, status):
        nonlocal silent_frames, recording_started
        frames.append(indata.copy())
        rms = np.sqrt(np.mean(indata ** 2))
        if rms > silence_threshold:
            recording_started = True
            silent_frames = 0
        elif recording_started:
            silent_frames += 1

    with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32",
                        blocksize=512, callback=callback):
        print("Listening...", end=" ", flush=True)
        while True:
            sd.sleep(50)
            if recording_started and silent_frames >= silence_limit:
                break
            if len(frames) >= max_frames:
                break

    print("Got it.")
    return np.concatenate(frames, axis=0).flatten()


def transcribe(audio: np.ndarray, sample_rate: int = 16000) -> str:
    model = _get_model()
    # Whisper expects float32 mono at 16kHz — pass array directly to skip ffmpeg
    audio_16k = audio.astype(np.float32)
    result = model.transcribe(audio_16k, fp16=False)
    return result["text"].strip()
