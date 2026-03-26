# 🤖 Gemini Context: Voice-Controlled Robot Project

This document provides essential context and instructions for AI agents working within the `ollama_test` workspace. This project implements a sophisticated voice-control interface for a dual-arm robot using local LLMs and simulation.

## 🚀 Project Overview

*   **Purpose:** To control a differential-drive dual-arm robot in NVIDIA Isaac Sim 5.1 using natural language voice commands.
*   **Core Architecture:** 
    *   **STT (Speech-to-Text):** `Faster-Whisper` (Base model, running on CUDA/INT8).
    *   **LLM (Brain):** `Ollama` running a custom `robot_commander` model (based on Llama 3.1 8B).
    *   **TTS (Text-to-Speech):** `MeloTTS` (Local) for high-quality Korean voice synthesis.
    *   **Control Loop:** A state-machine in Python (`robot_continuous_loop.py`) managing the `IDLE -> Parsing -> Confirmation -> Execution` flow.
    *   **Middleware:** ROS2 Humble (integration pending for Nav2 and MoveIt2).
    *   **Simulator:** NVIDIA Isaac Sim 5.1.

## 🛠️ Environment & Tooling

*   **Package Manager:** `uv` (Fast Python package manager).
*   **Python Version:** Python 3.10+.
*   **Hardware Target:** Linux (Ubuntu 22.04) with NVIDIA GPU (24GB VRAM).
*   **Key Dependencies:** `ollama`, `faster-whisper`, `melo`, `pygame` (for audio), `SpeechRecognition`.

## 📖 Key Commands & Operations

### 1. Environment Setup
```bash
# Install system dependencies
sudo apt-get install -y portaudio19-dev libasound2-dev libsndfile1 espeak

# Install Python packages via uv
uv add ollama SpeechRecognition faster-whisper PyAudio pygame unidic-lite mecab-python3 torch torchvision torchaudio "melo @ git+https://github.com/myshell-ai/MeloTTS.git"
```

### 2. AI Model Registration
The LLM must be configured with specific robot action rules before running the loop.
```bash
ollama create robot_commander -f robot_modelfile
```

### 3. Running the System
Always use `uv run` to ensure the virtual environment is utilized.
```bash
uv run python robot_continuous_loop.py
```

## 📜 Development Conventions

*   **State Machine:** The primary interaction logic resides in `robot_continuous_loop.py`. Changes to the dialogue flow or command confirmation logic should happen here.
*   **Command Protocol:** The robot expects structured JSON from the LLM. 
    *   Format: `{"commands": [{"action": "...", "target": "..."}], "confirmation_message": "..."}`.
    *   Definitions for these actions are maintained in `robot_modelfile`.
*   **Audio Handling:** 
    *   Voice output uses `aplay` for reliability on Linux systems.
    *   Voice input is captured via `SpeechRecognition` and processed by `Faster-Whisper`.
*   **VRAM Management:** With 24GB total, Isaac Sim takes ~10-12GB, and Ollama/STT/TTS take ~8-10GB. Always prioritize efficient model loading (e.g., INT8 quantization).

## 🗺️ Implementation Roadmap (Context for AI)

1.  **Phase 1 (Complete):** Voice interaction loop (STT -> LLM -> TTS) with local high-quality voice.
2.  **Phase 2 (Current):** ROS2 Humble integration for robot movement (Nav2).
3.  **Phase 3 (Next):** Dual-arm manipulation control (MoveIt2) within Isaac Sim.
4.  **Phase 4 (Final):** Full integration and autonomous task execution based on voice.
