#!/usr/bin/env python3
"""
SurMohini - Chord Detection using Librosa
Usage: python chord_detect.py <input_path> <output_dir>
"""
import sys, json, numpy as np
from pathlib import Path

def chord_detect(input_path, output_dir):
    import librosa

    y, sr = librosa.load(input_path, sr=None)
    hop_length = 4096
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    times = librosa.times_like(chroma, sr=sr, hop_length=hop_length)

    CHORD_TEMPLATES = {
        'C Major': [1,0,0,0,1,0,0,1,0,0,0,0], 'C Minor': [1,0,0,1,0,0,0,1,0,0,0,0],
        'D Major': [0,0,1,0,0,0,1,0,0,1,0,0], 'D Minor': [0,0,1,0,0,1,0,0,0,1,0,0],
        'E Major': [0,0,0,0,1,0,0,0,1,0,0,1], 'E Minor': [0,0,0,0,1,0,0,1,0,0,0,1],
        'F Major': [1,0,0,0,0,1,0,0,0,1,0,0], 'F Minor': [1,0,0,0,0,1,0,0,1,0,0,0],
        'G Major': [0,0,1,0,0,0,0,1,0,0,0,1], 'G Minor': [0,0,1,0,0,0,0,1,0,0,1,0],
        'A Major': [1,0,0,1,0,0,0,0,1,0,0,0], 'A Minor': [1,0,0,1,0,0,0,0,0,1,0,0],
        'B Major': [0,1,0,0,1,0,0,0,0,1,0,0], 'B Minor': [0,1,0,0,0,1,0,0,0,1,0,0],
    }
    templates = {k: np.array(v, dtype=float) for k, v in CHORD_TEMPLATES.items()}

    chords = []
    prev_chord = None
    for i, t in enumerate(times):
        frame = chroma[:, i]
        frame_norm = frame / (np.linalg.norm(frame) + 1e-6)
        scores = {name: float(np.dot(frame_norm, tmpl / (np.linalg.norm(tmpl) + 1e-6)))
                  for name, tmpl in templates.items()}
        best = max(scores, key=scores.get)
        confidence = scores[best]
        if best != prev_chord and confidence > 0.7:
            chords.append({"time": round(float(t), 2), "chord": best, "confidence": round(confidence, 3)})
            prev_chord = best

    result = {"chords": chords}
    print(json.dumps(result))
    return result

if __name__ == "__main__":
    chord_detect(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ".")