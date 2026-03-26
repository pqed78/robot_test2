import os
import torch
from melo.api import TTS
import speech_recognition as sr
from faster_whisper import WhisperModel
import ollama
import json
import subprocess

# --- 설정 (귀 업그레이드: base -> large-v3) ---
STT_MODEL_SIZE = "large-v3" 
LLM_MODEL_NAME = "robot_commander"

# --- 초기화 ---
print(f"⚙️ 시스템 초기화 중 (최고 사양 STT: {STT_MODEL_SIZE} + MeloTTS)...")

# 1. MeloTTS 로드 (고품질 로컬 음성)
device = "cuda" if torch.cuda.is_available() else "cpu"
try:
    tts_model = TTS(language='KR', device=device)
    speaker_ids = tts_model.hps.data.spk2id
except Exception as e:
    print(f"❌ MeloTTS 로드 실패: {e}")
    exit(1)

# 2. STT 로드 (Faster-Whisper Large-v3)
# VRAM 24GB 활용: float16 연산으로 정확도와 속도 균형 최적화
stt_model = WhisperModel(STT_MODEL_SIZE, device="cuda", compute_type="float16")

def speak(text):
    """MeloTTS로 생성하고 시스템 aplay로 확실하게 재생"""
    print(f"🤖 로봇: {text}")
    output_file = "output.wav"
    try:
        tts_model.tts_to_file(text, speaker_ids['KR'], output_file, speed=1.0)
        subprocess.run(["aplay", "-q", output_file], check=True)
    except Exception as e:
        print(f"❌ TTS/재생 오류: {e}")

def listen_voice():
    """마이크 입력을 텍스트로 변환 (Large-v3 엔진 사용)"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n👂 듣고 있습니다 (고정밀 분석 모드)...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)
    
    try:
        temp_wav = "temp.wav"
        with open(temp_wav, "wb") as f:
            f.write(audio.get_wav_data())
        
        # beam_size=5 옵션으로 문맥 파악 능력을 더욱 높임
        segments, _ = stt_model.transcribe(temp_wav, language="ko", beam_size=5)
        text = "".join([s.text for s in segments]).strip()
        return text
    except Exception as e:
        print(f"STT 분석 오류: {e}")
        return ""

def main():
    state = "IDLE"
    pending_commands = []
    
    speak("고정밀 음성 인식 시스템이 가동되었습니다. 무엇을 도와드릴까요?")

    while True:
        voice_text = listen_voice()
        if not voice_text: continue
        
        print(f"👤 사용자: {voice_text}")

        if state == "IDLE":
            try:
                response = ollama.chat(model=LLM_MODEL_NAME, messages=[{'role': 'user', 'content': voice_text}])
                parsed = json.loads(response['message']['content'].strip())
                
                pending_commands = parsed.get("commands", [])
                confirm_msg = parsed.get("confirmation_message", "명령을 수행할까요?")
                
                if pending_commands:
                    speak(confirm_msg + " '응' 혹은 '아니'라고 대답해 주세요.")
                    state = "CONFIRMING"
                else:
                    speak("이해하지 못했습니다. 다시 말씀해 주세요.")
            except Exception as e:
                speak("명령 분석 중 오류가 발생했습니다.")

        elif state == "CONFIRMING":
            pos = ["응", "어", "그래", "수행", "해", "yes", "ok", "부탁해", "명령해", "수락", "해줘"]
            neg = ["아니", "취소", "그만", "하지마", "no", "거절"]

            if any(word in voice_text for word in pos):
                speak("알겠습니다. 작업을 시작합니다.")
                for cmd in pending_commands:
                    print(f"🚀 [ROS2 EXEC] {cmd}")
                speak("모든 작업을 완료했습니다. 다음 명령을 기다립니다.")
                state = "IDLE"
                pending_commands = []
            elif any(word in voice_text for word in neg):
                speak("명령을 취소했습니다. 다시 대기합니다.")
                state = "IDLE"
                pending_commands = []
            else:
                speak("잘 못 알아들었습니다. 수행할까요? '응' 혹은 '아니'라고 말씀해 주세요.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 시스템 종료")
