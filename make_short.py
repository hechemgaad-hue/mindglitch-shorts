#!/usr/bin/env python3
"""Génère un YouTube Short 1080x1920 à partir d'un JSON de script.

Usage: python3 make_short.py script.json out.mp4
JSON: {"title": str, "hook": str, "facts": [str,...], "outro": str, "palette": 0-4 (optionnel)}
"""
import json, subprocess, sys, tempfile, os, textwrap
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from kokoro_onnx import Kokoro

W, H, FPS = 1080, 1920, 30
MODELS = os.path.expanduser("~/models") if os.path.isdir(os.path.expanduser("~/models")) else "/home/claude/models"
PALETTES = [((20, 10, 60), (120, 40, 160)), ((5, 30, 50), (0, 120, 140)),
            ((50, 10, 20), (190, 60, 50)), ((10, 40, 30), (60, 160, 90)),
            ((15, 15, 35), (70, 90, 200))]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def gradient(c1, c2):
    t = np.linspace(0, 1, H)[:, None, None]
    a = np.array(c1)[None, None, :] * (1 - t) + np.array(c2)[None, None, :] * t
    return Image.fromarray(np.repeat(a, W, axis=1).astype("uint8"))


def chunks(sentence, n=4):
    words = sentence.split()
    return [" ".join(words[i:i + n]) for i in range(0, len(words), n)]


def frame(bg, text, idx, total, title):
    im = bg.copy()
    d = ImageDraw.Draw(im)
    f_small = ImageFont.truetype(FONT, 46)
    d.text((W // 2, 150), title.upper()[:40], font=f_small, fill=(255, 255, 255, 200), anchor="mm")
    d.rounded_rectangle((90, 215, W - 90, 227), 6, fill=(255, 255, 255, 60))
    d.rounded_rectangle((90, 215, 90 + int((W - 180) * (idx + 1) / total), 227), 6, fill=(255, 220, 80))
    size = 120
    while True:
        f = ImageFont.truetype(FONT, size)
        lines = textwrap.wrap(text, width=max(8, int(W * 0.84 / (size * 0.62))))
        bh = len(lines) * size * 1.25
        if bh < 800 and all(d.textlength(l, font=f) < W - 140 for l in lines):
            break
        size -= 6
    y = H // 2 - bh / 2 + size * 0.6
    for l in lines:
        d.text((W // 2 + 4, y + 4), l, font=f, fill=(0, 0, 0), anchor="mm")
        d.text((W // 2, y), l, font=f, fill=(255, 255, 255), anchor="mm")
        y += size * 1.25
    return im


def main(script_path, out):
    s = json.load(open(script_path))
    sentences = [s["hook"]] + s["facts"] + [s["outro"]]
    k = Kokoro(f"{MODELS}/kokoro.onnx", f"{MODELS}/voices.bin")
    bg = gradient(*PALETTES[s.get("palette", 0) % len(PALETTES)])
    tmp = tempfile.mkdtemp()
    segs, i = [], 0
    for si, sent in enumerate(sentences):
        speed = 1.08
        audio, sr = k.create(sent, voice=s.get("voice", "am_michael"), speed=speed, lang="en-us")
        pad = np.zeros(int(sr * 0.25), dtype=audio.dtype)
        audio = np.concatenate([audio, pad])
        dur = len(audio) / sr
        parts = chunks(sent)
        weights = np.array([len(p) for p in parts], float)
        for p, w in zip(parts, weights):
            # une image par chunk, durée proportionnelle ; audio découpé en conséquence
            pass
        wav = f"{tmp}/a{si}.wav"
        sf.write(wav, audio, sr)
        bounds = np.cumsum(weights) / weights.sum() * dur
        start = 0.0
        for p, b in zip(parts, bounds):
            png = f"{tmp}/f{i}.png"
            frame(bg, p, si, len(sentences), s["title"]).save(png)
            segs.append((png, b - start))
            start = b
            i += 1
        segs.append((wav, None))
    # concat vidéo (images) + audio
    vlist, alist = [], []
    for a, d in segs:
        if d is None:
            alist.append(a)
        else:
            vlist.append((a, d))
    with open(f"{tmp}/v.txt", "w") as f:
        for p, d in vlist:
            f.write(f"file '{p}'\nduration {d:.3f}\n")
        f.write(f"file '{vlist[-1][0]}'\n")
    with open(f"{tmp}/a.txt", "w") as f:
        for a in alist:
            f.write(f"file '{a}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/a.txt",
                    f"{tmp}/all.wav"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/v.txt",
                    "-i", f"{tmp}/all.wav", "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    print("OK", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
