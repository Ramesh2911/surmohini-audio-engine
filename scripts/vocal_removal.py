#!/usr/bin/env python3
"""
SurMohini - Vocal Removal Script
Uses Demucs to separate vocals from instrumentals
Usage: python vocal_removal.py <input_path> <output_dir>
"""
import sys
import os
import json
import subprocess
import shutil
from pathlib import Path
from uuid import uuid4

def vocal_removal(input_path: str, output_dir: str) -> dict:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_id = str(uuid4())[:8]
    temp_out = output_dir / f"demucs_{job_id}"

    # Run Demucs
    cmd = [
        "python3", "-m", "demucs",
        "--two-stems=vocals",
        "-o", str(temp_out),
        "--mp3",
        "--mp3-bitrate", "320",
        str(input_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # Find output files
    model_dir = temp_out / "htdemucs" / input_path.stem
    instrumental_src = model_dir / "no_vocals.mp3"
    vocals_src = model_dir / "vocals.mp3"

    # Move to final location
    instrumental_dst = output_dir / f"{job_id}_instrumental.mp3"
    vocals_dst = output_dir / f"{job_id}_vocals.mp3"

    shutil.move(str(instrumental_src), str(instrumental_dst))
    shutil.move(str(vocals_src), str(vocals_dst))

    # Cleanup temp
    shutil.rmtree(str(temp_out), ignore_errors=True)

    result = {
        "outputs": [
            {"label": "instrumental", "path": str(instrumental_dst), "size": instrumental_dst.stat().st_size},
            {"label": "vocals", "path": str(vocals_dst), "size": vocals_dst.stat().st_size}
        ]
    }
    print(json.dumps(result))
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: vocal_removal.py <input_path> <output_dir>"}))
        sys.exit(1)
    vocal_removal(sys.argv[1], sys.argv[2])