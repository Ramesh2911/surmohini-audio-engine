#!/usr/bin/env python3
"""
SurMohini - Stem Separation Script
Uses Demucs 6-stem model to isolate/mute instruments
Usage: python stem_separation.py <input> <output_dir> <keep_json> <mute_json>
"""
import sys, os, json, subprocess, shutil
from pathlib import Path
from uuid import uuid4

STEMS = ["drums", "bass", "other", "vocals", "guitar", "piano"]

def stem_separation(input_path, output_dir, stems_to_keep, stems_to_mute):
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    job_id = str(uuid4())[:8]
    temp_out = output_dir / f"stems_{job_id}"

    # Run 6-stem Demucs
    subprocess.run([
        "python3", "-m", "demucs",
        "--six-stems",
        "-o", str(temp_out),
        "--mp3", "--mp3-bitrate", "320",
        str(input_path)
    ], check=True, capture_output=True)

    model_dir = temp_out / "htdemucs_6s" / input_path.stem

    outputs = []
    # Export individual stems
    for stem in STEMS:
        stem_file = model_dir / f"{stem}.mp3"
        if stem_file.exists():
            dst = output_dir / f"{job_id}_{stem}.mp3"
            shutil.move(str(stem_file), str(dst))
            outputs.append({"label": stem, "path": str(dst), "size": dst.stat().st_size})

    # Create mix with selected stems using ffmpeg
    if stems_to_keep:
        keep_files = [o for o in outputs if o["label"] in stems_to_keep]
        if keep_files:
            inputs = []
            for f in keep_files:
                inputs += ["-i", f["path"]]
            mix_out = output_dir / f"{job_id}_custom_mix.mp3"
            filter_complex = f"amix=inputs={len(keep_files)}:duration=longest[out]"
            subprocess.run([
                "ffmpeg", *inputs,
                "-filter_complex", filter_complex,
                "-map", "[out]", "-b:a", "320k",
                str(mix_out), "-y"
            ], check=True, capture_output=True)
            outputs.insert(0, {"label": "custom_mix", "path": str(mix_out), "size": mix_out.stat().st_size})

    shutil.rmtree(str(temp_out), ignore_errors=True)

    result = {"outputs": outputs}
    print(json.dumps(result))
    return result

if __name__ == "__main__":
    stems_keep = json.loads(sys.argv[3]) if len(sys.argv) > 3 else []
    stems_mute = json.loads(sys.argv[4]) if len(sys.argv) > 4 else []
    stem_separation(sys.argv[1], sys.argv[2], stems_keep, stems_mute)