#!/usr/bin/env python3
"""
SurMohini - Pitch Shift Script
Uses Rubberband for high-quality pitch shifting without tempo change
Usage: python pitch_shift.py <input_path> <output_dir> <semitones>
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from uuid import uuid4

def pitch_shift(input_path: str, output_dir: str, semitones: int) -> dict:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_id = str(uuid4())[:8]
    # Convert to WAV first for rubberband processing
    temp_wav = output_dir / f"{job_id}_temp.wav"
    output_path = output_dir / f"{job_id}_pitched_{semitones:+d}.mp3"

    # Convert to WAV
    subprocess.run([
        "ffmpeg", "-i", str(input_path),
        "-ar", "44100", "-ac", "2",
        str(temp_wav), "-y"
    ], check=True, capture_output=True)

    # Apply pitch shift with rubberband
    temp_out_wav = output_dir / f"{job_id}_pitched.wav"
    subprocess.run([
        "rubberband",
        "--pitch", str(semitones),
        "--pitch-hq",
        "--realtime",
        str(temp_wav),
        str(temp_out_wav)
    ], check=True, capture_output=True)

    # Convert back to MP3 at 320kbps
    subprocess.run([
        "ffmpeg", "-i", str(temp_out_wav),
        "-b:a", "320k",
        str(output_path), "-y"
    ], check=True, capture_output=True)

    # Cleanup temp files
    temp_wav.unlink(missing_ok=True)
    temp_out_wav.unlink(missing_ok=True)

    result = {
        "outputs": [
            {"label": f"pitched_{semitones:+d}", "path": str(output_path), "size": output_path.stat().st_size}
        ]
    }
    print(json.dumps(result))
    return result

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Usage: pitch_shift.py <input_path> <output_dir> <semitones>"}))
        sys.exit(1)
    pitch_shift(sys.argv[1], sys.argv[2], int(sys.argv[3]))