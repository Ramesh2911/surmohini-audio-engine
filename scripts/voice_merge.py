#!/usr/bin/env python3
"""
SurMohini - Voice Merge Script
Merges user vocal recording with instrumental track
Usage: python voice_merge.py <instrumental_path> <voice_path> <output_dir>
"""
import sys, json, subprocess
from pathlib import Path
from uuid import uuid4

def voice_merge(instrumental_path, voice_path, output_dir):
    instrumental_path = Path(instrumental_path)
    voice_path = Path(voice_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_id = str(uuid4())[:8]
    output_path = output_dir / f"{job_id}_merged.mp3"

    subprocess.run([
        "ffmpeg",
        "-i", str(instrumental_path),
        "-i", str(voice_path),
        "-filter_complex", "amix=inputs=2:duration=first:dropout_transition=3[out]",
        "-map", "[out]",
        "-b:a", "320k",
        str(output_path), "-y"
    ], check=True, capture_output=True)

    result = {
        "outputs": [
            {"label": "merged", "path": str(output_path), "size": output_path.stat().st_size}
        ]
    }
    print(json.dumps(result))
    return result

if __name__ == "__main__":
    voice_merge(sys.argv[1], sys.argv[2], sys.argv[3])