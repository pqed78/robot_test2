# 🤖 Voice-Controlled Dual-Arm Robot (Ollama + ROS2 + Isaac Sim)

이 프로젝트는 음성 명령을 통해 차동 구동 로봇 및 양팔 로봇을 제어하는 시스템입니다. 로컬 LLM(Ollama)을 사용하여 사용자의 의도를 분석하고, 이를 구조화된 명령(JSON)으로 변환하여 로봇에게 전달합니다.

## 🌟 주요 기능
- **STT (Speech-to-Text)**: **Faster-Whisper Large-v3** 엔진을 사용한 고정밀 실시간 한국어 음성 인식 (Beam size 5, float16 연산 적용).
- **Intelligence (LLM)**: Ollama(**Qwen 2.5 7B**) 기반 `robot_commander` 모델을 통한 자연어 명령 파싱 및 의도 추출 (영문 시스템 프롬프트 기반 고성능 추론, **순수 JSON 출력 최적화**).
- **TTS (Text-to-Speech)**: **MeloTTS**를 이용한 고품질 로컬 한국어 음성 안내 및 `aplay` 기반 재생.
- **Verification Loop**: 명령 실행 전 사용자에게 확인을 받는 안전 로직(IDLE -> CONFIRMING 상태 머신) 포함.
- **Simulation**: NVIDIA Isaac Sim 5.1 및 ROS2 Humble 연동 지원.

## 🛠️ 시스템 환경
- **OS**: Ubuntu 22.04 (Jammy Jellyfish)
- **Middleware**: ROS2 Humble
- **Simulator**: NVIDIA Isaac Sim 5.1
- **Hardware**: **NVIDIA GPU (VRAM 24GB 권장)** - Isaac Sim + Large-v3 STT + LLM 병행 구동 최적화.
- **Python**: 3.10 (uv 패키지 매니저 사용, CUDA 12.8 최적화)

## 📦 설치 방법

### 1. 시스템 의존성 설치
```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio espeak libasound2-dev libsndfile1 aplay
```

### 2. Python 환경 설정 (uv 사용)
```bash
# 가상환경 동기화 (pyproject.toml 기반)
uv sync
```

### 3. Ollama 로봇 모델 등록
```bash
# robot_modelfile이 있는 디렉토리에서 실행
ollama create robot_commander -f robot_modelfile
```

## 🚀 실행 가이드

### 1. 지능형 음성 제어 루프 실행
사용자의 음성을 듣고, 분석하여 확인 메시지를 내보내는 메인 루프를 실행합니다.
```bash
python -m unidic download # 한국어 사전 다운로드 (처음 실행전에만 필요)
uv run python robot_continuous_loop.py
```

### 2. 인터랙션 시나리오
1.  **대기**: 로봇이 "고정밀 음성 인식 시스템이 가동되었습니다."라고 인사합니다.
2.  **명령**: 사용자가 마이크에 대고 명령을 내립니다. (*예: "거실로 가서 오른팔로 물병 좀 집어줘"*)
3.  **확인**: 로봇이 분석 결과로 확인 질문을 합니다. (*예: "거실로 이동하여 오른팔로 물병을 집을까요? '응' 혹은 '아니'라고 대답해 주세요."*)
4.  **실행**: "응"이라고 답하면 `[ROS2 EXEC]` 명령(JSON)이 생성됩니다.

## 📂 파일 구조
- `robot_continuous_loop.py`: 메인 상태 머신 및 음성 대화 루프 (Large-v3 + MeloTTS).
- `robot_modelfile`: Ollama용 시스템 프롬프트 및 액션 정의 (Llama 3.1 8B 기반).
- `pyproject.toml`: CUDA 12.8 및 PyTorch 2.4+ 의존성 관리.
- `robot_voice_control_plan.txt`: 프로젝트 전체 아키텍처 및 상세 구현 계획.

## ⚠️ 참고 사항 (Troubleshooting)
- **VRAM 부족**: Isaac Sim 구동 시 메모리가 부족하면 `robot_continuous_loop.py`에서 `STT_MODEL_SIZE`를 `base`로 변경하고 `compute_type="int8"`을 고려하세요.
- **MeloTTS**: 최초 실행 시 한국어 사전(unidic) 다운로드가 필요할 수 있습니다. (`python3 -m unidic download`)

