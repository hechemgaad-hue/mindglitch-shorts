#!/bin/sh
# Installe les dépendances et télécharge le modèle de voix (à lancer au début de chaque session)
pip install --break-system-packages -q kokoro-onnx soundfile pillow numpy
mkdir -p ~/models && cd ~/models
[ -f kokoro.onnx ] || curl -sSL -o kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
[ -f voices.bin ] || curl -sSL -o voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
