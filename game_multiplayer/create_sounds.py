"""Script tạo file âm thanh đơn giản cho game"""
import wave
import numpy as np
import os

def create_beep_sound(filename, frequency=440, duration=0.1, sample_rate=44100):
    """Tạo file WAV với âm beep đơn giản"""
    # Tạo mảng samples
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Tạo sóng sin
    wave_data = np.sin(2 * np.pi * frequency * t)
    # Normalize về range [-1, 1] và chuyển sang int16
    wave_data = (wave_data * 32767).astype(np.int16)
    
    # Tạo file WAV
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())
    
    print(f"✓ Đã tạo: {filename}")

def create_click_sound(filename):
    """Tạo âm thanh click ngắn"""
    create_beep_sound(filename, frequency=800, duration=0.05, sample_rate=44100)

def create_join_sound(filename):
    """Tạo âm thanh join (tăng dần)"""
    sample_rate = 44100
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Tạo âm thanh tăng dần từ 400Hz đến 800Hz
    frequency = 400 + (800 - 400) * (t / duration)
    wave_data = np.sin(2 * np.pi * frequency * t)
    # Thêm envelope để mượt hơn
    envelope = np.linspace(0, 1, len(wave_data))
    wave_data = wave_data * envelope
    wave_data = (wave_data * 32767).astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())
    
    print(f"✓ Đã tạo: {filename}")

def create_all_sounds():
    """Tạo tất cả file âm thanh cần thiết"""
    base_dir = os.path.dirname(__file__)
    sounds_dir = os.path.join(base_dir, 'client', 'assets', 'sounds')
    
    # Tạo thư mục nếu chưa có
    os.makedirs(sounds_dir, exist_ok=True)
    
    print("Đang tạo file âm thanh...")
    print("=" * 50)
    
    # Tạo các file âm thanh
    create_click_sound(os.path.join(sounds_dir, 'click.wav'))
    create_join_sound(os.path.join(sounds_dir, 'join.wav'))
    create_beep_sound(os.path.join(sounds_dir, 'beep.wav'), frequency=600, duration=0.1)
    create_beep_sound(os.path.join(sounds_dir, 'footstep.wav'), frequency=200, duration=0.05)
    create_beep_sound(os.path.join(sounds_dir, 'leave.wav'), frequency=300, duration=0.2)
    create_beep_sound(os.path.join(sounds_dir, 'level.wav'), frequency=500, duration=0.3)
    create_beep_sound(os.path.join(sounds_dir, 'dead.wav'), frequency=200, duration=0.4)
    create_beep_sound(os.path.join(sounds_dir, 'goal.wav'), frequency=800, duration=0.5)
    create_beep_sound(os.path.join(sounds_dir, 'versus.wav'), frequency=400, duration=0.6)
    create_beep_sound(os.path.join(sounds_dir, 'fight.wav'), frequency=600, duration=0.4)
    create_beep_sound(os.path.join(sounds_dir, 'dash.wav'), frequency=300, duration=0.1)
    
    print("=" * 50)
    print("✓ Hoàn tất! Đã tạo tất cả file âm thanh.")
    print(f"Thư mục: {sounds_dir}")

if __name__ == '__main__':
    try:
        create_all_sounds()
    except ImportError:
        print("ERROR: Cần cài đặt numpy và wave")
        print("Chạy: pip install numpy")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

