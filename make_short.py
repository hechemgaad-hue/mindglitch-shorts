#!/usr/bin/env python3
"""Générateur de Shorts v2 (1080x1920, 30 fps) optimisé rétention.

- sous-titres mot par mot avec "pop", mot actif en jaune, mots-clés en couleur
- fond animé (dégradé qui dérive, bokeh, vignette), zoom lent + punch-in à chaque phrase
- bande son : voix + musique d'ambiance synthétisée + whoosh à chaque transition
- l'image 1 montre déjà l'accroche (pas de noir), barre de progression discrète

Usage: python3 make_short.py script.json out.mp4
JSON: {"title","hook","facts":[...],"outro" (optionnel),"palette":0-4,"voice":"am_michael"}
Dans le texte, entourer un mot de *astérisques* pour le mettre en couleur (ex: *25%*).
"""
import json, os, re, subprocess, sys, tempfile
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from kokoro_onnx import Kokoro

W, H, FPS = 1080, 1920, 30
MODELS = os.path.expanduser("~/models") if os.path.isdir(os.path.expanduser("~/models")) else "/home/claude/models"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PALETTES = [  # (haut, bas, accent)
    ((18, 8, 50), (130, 40, 170), (255, 214, 64)),
    ((4, 24, 48), (0, 130, 150), (255, 120, 90)),
    ((45, 8, 20), (200, 60, 60), (255, 230, 120)),
    ((8, 36, 28), (60, 170, 100), (255, 240, 130)),
    ((12, 12, 34), (80, 100, 220), (120, 255, 220)),
]
SR = 24000


def ease_out_back(t):
    t = min(max(t, 0), 1)
    c1 = 1.9
    return 1 + (c1 + 1) * (t - 1) ** 3 + c1 * (t - 1) ** 2


# ---------- audio ----------
def whoosh(n_sec=0.45):
    n = int(SR * n_sec)
    noise = np.random.randn(n)
    k = np.linspace(4, 60, n)
    out = np.empty(n)
    acc = 0.0
    for i in range(n):  # filtre passe-bas dont la coupure monte
        acc += (noise[i] - acc) / k[::-1][i]
        out[i] = acc
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out / (np.abs(out).max() + 1e-9) * env * 0.5


def boom(n_sec=0.6):
    t = np.arange(int(SR * n_sec)) / SR
    f = 90 * np.exp(-t * 4) + 35
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 0.9


def music(dur, seed):
    rng = np.random.default_rng(seed)
    t = np.arange(int(SR * dur)) / SR
    roots = [57, 53, 48, 55]  # Am F C G (MIDI)
    chords = [[0, 3, 7], [0, 4, 7], [0, 4, 7], [0, 4, 7]]
    beat = 60 / (78 + rng.integers(0, 12))
    bar = beat * 4
    out = np.zeros_like(t)
    for i, ti in enumerate(t[:: int(SR * 0.01)] if False else []):
        pass
    for b in range(int(dur / bar) + 1):
        r = roots[b % 4]
        s, e = int(b * bar * SR), min(len(t), int((b + 1) * bar * SR))
        if s >= len(t):
            break
        tt = t[s:e] - t[s]
        env = np.minimum(tt / 0.6, 1) * np.minimum((bar - tt) / 0.6, 1)
        for iv in chords[b % 4]:
            fr = 440 * 2 ** ((r + iv - 69) / 12)
            out[s:e] += (np.sin(2 * np.pi * fr * tt) + 0.4 * np.sin(2 * np.pi * 2 * fr * tt)) * env * 0.05
        # arpège pentatonique léger
        scale = [0, 3, 5, 7, 10, 12]
        for q in range(8):
            ts = q * beat / 2
            if ts >= tt[-1] - 0.3:
                break
            note = r + 12 + scale[rng.integers(0, len(scale))]
            fr = 440 * 2 ** ((note - 69) / 12)
            m = (tt >= ts) & (tt < ts + 0.5)
            lt = tt[m] - ts
            out[s:e][m] += np.sin(2 * np.pi * fr * lt) * np.exp(-lt * 7) * 0.035
        # pouls grave sur les temps
        for q in range(4):
            ts = q * beat
            m = (tt >= ts) & (tt < ts + 0.25)
            lt = tt[m] - ts
            out[s:e][m] += np.sin(2 * np.pi * (55 + 40 * np.exp(-lt * 25)) * lt) * np.exp(-lt * 9) * 0.10
    fade = np.minimum(t / 1.0, 1) * np.minimum((dur - t) / 1.2, 1)
    return out * fade


# ---------- texte ----------
def parse_words(sentence):
    words = []
    for tok in sentence.split():
        hl = tok.startswith("*") or tok.endswith("*")
        clean = tok.strip("*")
        words.append((clean, hl))
    return words


def word_weights(words):
    ws = []
    for w, _ in words:
        x = len(re.sub(r"\W", "", w)) + 2.0
        if w.endswith((".", "!", "?")):
            x += 5
        elif w.endswith((",", ":", ";")):
            x += 3
        ws.append(x)
    return np.array(ws)


def pages(words, per=3):
    """Découpe en pages de ≤per mots, coupe aussi après ponctuation forte."""
    out, cur = [], []
    for i, (w, hl) in enumerate(words):
        cur.append(i)
        if len(cur) >= per or w.endswith((".", "!", "?", ",")):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def gradient_half(c1, c2, accent, t, w=540, h=960):
    y = np.linspace(0, 1, h)[:, None]
    shift = 0.5 + 0.5 * np.sin(t * 0.5)
    k = np.clip(y * (0.8 + 0.4 * shift) + 0.08 * np.sin(y * 6 + t), 0, 1)[:, :, None]
    base = np.array(c1) * (1 - k) + np.array(c2) * k
    x = np.linspace(-1, 1, w)[None, :, None]
    glow = np.exp(-((x - 0.5 * np.sin(t * 0.4)) ** 2) * 2.2) * 0.18
    base = base + glow * np.array(accent) * 0.35
    xx = np.linspace(-1, 1, w)[None, :]
    yy = np.linspace(-1, 1, h)[:, None]
    vig = 1 - 0.35 * np.clip(xx ** 2 * 0.6 + yy ** 2 * 0.5, 0, 1)
    return (base * vig[:, :, None]).clip(0, 255).astype("uint8")


def bokeh_sprite(r, color):
    im = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((r, r, 3 * r, 3 * r), fill=color + (70,))
    return im.filter(ImageFilter.GaussianBlur(r * 0.35))


def layout(words, idxs, font, maxw):
    """Retourne lignes (liste d'indices) pour un groupe de mots."""
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines, cur, cw = [], [], 0
    sp = d.textlength(" ", font=font)
    for i in idxs:
        wl = d.textlength(words[i][0].upper(), font=font)
        if cur and cw + sp + wl > maxw:
            lines.append(cur)
            cur, cw = [], 0
        cur.append(i)
        cw += wl + (sp if len(cur) > 1 else 0)
    if cur:
        lines.append(cur)
    return lines


def main(script_path, out):
    s = json.load(open(script_path))
    sentences = [s["hook"]] + s["facts"] + ([s["outro"]] if s.get("outro") else [])
    pal = PALETTES[s.get("palette", 0) % len(PALETTES)]
    c1, c2, accent = pal
    kok = Kokoro(f"{MODELS}/kokoro.onnx", f"{MODELS}/voices.bin")
    voice = s.get("voice", "am_michael")

    # --- voix & timing ---
    segs, t0 = [], 0.0
    audio_parts = []
    for si, sent in enumerate(sentences):
        plain = sent.replace("*", "")
        a, sr = kok.create(plain, voice=voice, speed=1.1, lang="en-us")
        assert sr == SR
        gap = 0.18 if si < len(sentences) - 1 else 0.55
        a = np.concatenate([a, np.zeros(int(SR * gap), dtype=a.dtype)])
        words = parse_words(sent)
        dur = len(a) / SR
        spoken = dur - gap
        wts = word_weights(words)
        edges = np.concatenate([[0], np.cumsum(wts) / wts.sum()]) * spoken
        segs.append(dict(start=t0, dur=dur, words=words, edges=edges + t0, pages=pages(words)))
        audio_parts.append(a)
        t0 += dur
    total = t0
    voice_track = np.concatenate(audio_parts)

    # --- mix audio ---
    seed = abs(hash(s["hook"])) % (2 ** 32)
    mix = np.zeros(len(voice_track))
    mus = music(total, seed)
    mix += mus[: len(mix)] * 1.0
    sfx = np.zeros_like(mix)
    wsh = whoosh()
    for i, sg in enumerate(segs):
        st = int(max(sg["start"] - 0.08, 0) * SR)
        w_ = wsh[: len(sfx) - st]
        sfx[st: st + len(w_)] += w_ * 0.45
    b = boom()
    sfx[: len(b)] += b[: len(sfx)] * 0.5
    peak = np.abs(voice_track).max() + 1e-9
    mixed = voice_track / peak * 0.85 + mix + sfx
    mixed = mixed / max(1.0, np.abs(mixed).max() / 0.95)
    tmp = tempfile.mkdtemp()
    wav = f"{tmp}/mix.wav"
    sf.write(wav, mixed.astype("float32"), SR)

    # --- vidéo ---
    rng = np.random.default_rng(seed)
    sprites = []
    for _ in range(14):
        r = int(rng.integers(14, 46))
        col = [accent, (255, 255, 255), c2][int(rng.integers(0, 3))]
        sprites.append(dict(img=bokeh_sprite(r, tuple(int(v) for v in col)),
                            x=rng.uniform(0, 540), y=rng.uniform(0, 960), vx=rng.uniform(-8, 8), vy=-rng.uniform(10, 40)))
    f_title = ImageFont.truetype(FONT, 40)
    nframes = int(total * FPS) + 1
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    fonts = {}
    for fi in range(nframes):
        t = fi / FPS
        # phrase courante
        si = next((i for i, sg in enumerate(segs) if t < sg["start"] + sg["dur"]), len(segs) - 1)
        sg = segs[si]
        local = t - sg["start"]
        bgh = Image.fromarray(gradient_half(c1, c2, accent, t))
        for sp in sprites:
            x = (sp["x"] + sp["vx"] * t) % 560 - 10
            y = (sp["y"] + sp["vy"] * t) % 980 - 10
            bgh.paste(sp["img"], (int(x - sp["img"].width / 2), int(y - sp["img"].height / 2)), sp["img"])
        # zoom lent + punch-in au début de phrase
        zoom = 1.0 + 0.05 * (local / max(sg["dur"], 0.1)) + 0.05 * (1 - ease_out_back(min(local / 0.25, 1))) * -1
        zoom = max(1.0, 1.0 + 0.045 * (local / max(sg["dur"], 0.1)) + 0.06 * max(0, 1 - local / 0.22))
        cw, ch = 540 / zoom, 960 / zoom
        bgh = bgh.crop((int((540 - cw) / 2), int((960 - ch) / 2), int((540 + cw) / 2), int((960 + ch) / 2)))
        im = bgh.resize((W, H), Image.BILINEAR)
        d = ImageDraw.Draw(im, "RGBA")
        # barre de progression
        d.rounded_rectangle((80, 135, W - 80, 143), 4, fill=(255, 255, 255, 60))
        d.rounded_rectangle((80, 135, 80 + int((W - 160) * t / total), 143), 4, fill=accent + (255,))
        d.text((W // 2, 100), "MINDGLITCH", font=f_title, fill=(255, 255, 255, 190), anchor="mm")
        # page de sous-titres courante
        words, edges = sg["words"], sg["edges"]
        cur_w = max(0, int(np.searchsorted(edges, t, side="right") - 1))
        cur_w = min(cur_w, len(words) - 1)
        page = next(p for p in sg["pages"] if cur_w in p) if any(cur_w in p for p in sg["pages"]) else sg["pages"][-1]
        size = 150 if len(page) <= 2 else 128
        font = fonts.setdefault(size, ImageFont.truetype(FONT, size))
        lines = layout(words, page, font, W - 150)
        lh = size * 1.22
        y0 = H * 0.42 - lh * len(lines) / 2 + lh / 2
        pop_t = (t - edges[cur_w]) / 0.16
        for li, ln in enumerate(lines):
            widths = [d.textlength(words[i][0].upper(), font=font) for i in ln]
            sp_w = d.textlength(" ", font=font)
            tw = sum(widths) + sp_w * (len(ln) - 1)
            x = W / 2 - tw / 2
            for i, wd in zip(ln, widths):
                txt = words[i][0].upper()
                cx, cy = x + wd / 2, y0 + li * lh
                active = i == cur_w
                hl = words[i][1]
                col = accent if (active or hl) else (255, 255, 255)
                if i > cur_w:
                    col = (255, 255, 255)
                fnt = font
                if active:
                    sc = 1 + 0.22 * (1 - ease_out_back(pop_t)) * -1 if pop_t < 1 else 1.0
                    sc = 1.0 + 0.18 * ease_out_back(pop_t) if pop_t < 1 else 1.18 - 0.0
                    sc = min(sc, 1.2)
                    fnt = fonts.setdefault(int(size * sc), ImageFont.truetype(FONT, int(size * sc)))
                d.text((cx + 6, cy + 8), txt, font=fnt, fill=(0, 0, 0, 200), anchor="mm")
                d.text((cx, cy), txt, font=fnt, fill=col, anchor="mm", stroke_width=6, stroke_fill=(10, 10, 20))
                x += wd + sp_w
        ff.stdin.write(im.tobytes())
    ff.stdin.close()
    ff.wait()
    print("OK", out, f"{total:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
