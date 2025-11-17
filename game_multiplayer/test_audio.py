"""Script test âm thanh đơn giản"""
import pygame
import os
import sys

def test_audio():
    print("=" * 50)
    print("KIỂM TRA ÂM THANH")
    print("=" * 50)
    
    # Khởi tạo pygame
    try:
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        print("[OK] Pygame mixer đã khởi tạo thành công")
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo mixer: {e}")
        return False
    
    # Kiểm tra file âm thanh
    base_dir = os.path.dirname(__file__)
    sounds_dir = os.path.join(base_dir, 'client', 'assets', 'sounds')
    click_path = os.path.join(sounds_dir, 'click.wav')
    
    print(f"\nĐang kiểm tra file: {click_path}")
    
    if not os.path.isfile(click_path):
        print(f"[ERROR] Không tìm thấy file click.wav")
        pygame.mixer.quit()
        pygame.quit()
        return False
    
    print("[OK] File click.wav tồn tại")
    
    # Load và phát thử
    try:
        sound = pygame.mixer.Sound(click_path)
        sound.set_volume(0.3)  # Âm lượng 30% để không quá to
        print("\n[INFO] Đang phát thử âm thanh (0.5 giây)...")
        print("[INFO] Bạn có nghe thấy âm thanh không?")
        sound.play()
        
        # Đợi âm thanh phát xong (tối đa 1 giây)
        import time
        time.sleep(0.5)  # Đợi 0.5 giây
        
        print("[OK] Âm thanh đã được phát")
        result = True
    except Exception as e:
        print(f"[ERROR] Không thể phát âm thanh: {e}")
        import traceback
        traceback.print_exc()
        result = False
    finally:
        pygame.mixer.quit()
        pygame.quit()
    
    return result

if __name__ == '__main__':
    try:
        result = test_audio()
        print("\n" + "=" * 50)
        if result:
            print("✓ KIỂM TRA HOÀN TẤT - Âm thanh hoạt động bình thường")
        else:
            print("✗ KIỂM TRA THẤT BẠI - Có vấn đề với âm thanh")
        print("=" * 50)
    except KeyboardInterrupt:
        print("\n[INFO] Đã hủy kiểm tra")
    except Exception as e:
        print(f"\n[ERROR] Lỗi: {e}")
        import traceback
        traceback.print_exc()

