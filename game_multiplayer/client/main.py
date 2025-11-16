"""Client entry point with pygame game loop."""
import pygame
import sys
import os
import random
import socket
import threading
import time
from client.src.config import SERVER_IP, SERVER_PORT, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from client.src.client import ClientNetwork
from client.src.game import GameState, Player, Obstacle
from client.src.graphics import GameRenderer

def main():
    # Khởi tạo pygame
    pygame.init()
    
    # Hỏi người dùng có muốn bật âm thanh không (hữu ích khi ở lớp học)
    audio_enabled_by_user = True
    try:
        audio_choice = input("\nBật âm thanh? (Y/n, mặc định Y): ").strip().lower()
        if audio_choice == 'n' or audio_choice == 'no':
            audio_enabled_by_user = False
            print("[AUDIO] Âm thanh đã được TẮT")
    except:
        pass  # Nếu không thể input, mặc định bật
    
    # Khởi tạo âm thanh
    audio_enabled = False
    sounds = {}
    if audio_enabled_by_user:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            audio_enabled = True
            print("[AUDIO] Mixer initialized")
            base_dir = os.path.dirname(__file__)
            sounds_dir = os.path.join(base_dir, 'assets', 'sounds')
            music_dir = os.path.join(base_dir, 'assets', 'music')
            # Mức âm lượng tổng
            master_volume = 0.6

            def load_sound(filename, volume=0.6):
                """Load a sound, fallback to click.wav if specific file is missing."""
                primary_path = os.path.join(sounds_dir, filename)
                fallback_path = os.path.join(sounds_dir, 'click.wav')
                chosen_path = None
                if os.path.isfile(primary_path):
                    chosen_path = primary_path
                elif os.path.isfile(fallback_path):
                    chosen_path = fallback_path
                    print(f"[AUDIO] Missing {filename}, using click.wav as fallback")
                else:
                    print(f"[AUDIO] Missing {filename} and no fallback click.wav")
                    return None
                try:
                    s = pygame.mixer.Sound(chosen_path)
                    s.set_volume(volume)
                    return s
                except Exception as e:
                    print(f"[AUDIO] Failed to load {chosen_path}: {e}")
                    return None

            sounds = {
                'footstep': load_sound('footstep.wav', volume=0.25),
                'join': load_sound('join.wav', volume=0.6),
                'leave': load_sound('leave.wav', volume=0.6),
                'level': load_sound('level.wav', volume=0.7),
                'dead': load_sound('dead.wav', volume=0.7),
                'goal': load_sound('goal.wav', volume=0.7),
                'versus': load_sound('versus.wav', volume=0.9),      # hiệu ứng vào trận
                'fight': load_sound('fight.wav', volume=0.9),        # hô "FIGHT!"
                'countdown': load_sound('beep.wav', volume=0.6),     # beep đếm ngược
                'crowd': load_sound('crowd.wav', volume=0.25),       # tiếng khán giả nền (loop)
                'dash': load_sound('dash.wav', volume=0.7),          # lao nhanh khi Shift
            }

            def set_master_volume(vol: float):
                """Cập nhật âm lượng chung cho tất cả hiệu ứng và nhạc nền."""
                v = max(0.0, min(1.0, vol))
                try:
                    if pygame.mixer.music:
                        pygame.mixer.music.set_volume(v * 0.35)
                except Exception:
                    pass
                for k, s in sounds.items():
                    if s:
                        try:
                            # mỗi sound đã có volume riêng, nhân với master
                            s.set_volume(v)
                        except Exception:
                            pass
                return v
            # Log tình trạng âm thanh đã nạp
            for k, v in list(sounds.items()):
                print(f"[AUDIO] {'OK' if v else 'MISS'} sound: {k}")

            # BGM: ưu tiên bgm.ogg, fallback bgm.wav nếu có
            try:
                bgm_path = None
                for fname in ('bgm.ogg', 'bgm.wav'):
                    p = os.path.join(music_dir, fname)
                    if os.path.isfile(p):
                        bgm_path = p
                        break
                if bgm_path:
                    pygame.mixer.music.load(bgm_path)
                    pygame.mixer.music.set_volume(0.35)
                    pygame.mixer.music.play(-1)
                    print(f"[AUDIO] BGM playing: {os.path.basename(bgm_path)}")
                else:
                    print("[AUDIO] No BGM file found (bgm.ogg/wav)")
            except Exception as e:
                print(f"[AUDIO] BGM error: {e}")
            # Phát thử âm thanh ngắn để xác minh đầu ra (chỉ nếu có sound hợp lệ)
            try:
                test_sound = sounds.get('join') or sounds.get('footstep')
                if test_sound:
                    # Phát test sound nhẹ để xác nhận hệ thống âm thanh hoạt động
                    test_sound.set_volume(0.3)  # Âm lượng thấp để không quá to
                    test_sound.play()
                    print("[AUDIO] ✓ Sound system ready - test sound played")
                else:
                    print("[AUDIO] No valid sound files found - game will run silently")
            except Exception as e:
                print(f"[AUDIO] Test sound error: {e}")
        except Exception as e:
            audio_enabled = False
            print(f"[AUDIO] Mixer disabled: {e}")
    else:
        print("[AUDIO] Âm thanh đã được tắt bởi người dùng")
        audio_enabled = False
    pygame.display.set_caption("Multiplayer Game")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    # Thông báo controls sẽ được in sau khi chọn chế độ
    
    # Tạo renderer và game state
    renderer = GameRenderer(screen)
    game_state = GameState()
    
    # Lấy tên và ID phòng từ input/env
    try:
        default_name = os.environ.get('PLAYER_NAME') or 'player1'
        default_room = os.environ.get('ROOM_ID') or 'default'
        print("Enter your player name (press Enter to use default):", default_name)
        inp_name = input().strip()
        if inp_name:
            default_name = inp_name
        print("Enter room ID to join (press Enter to use default):", default_room)
        inp_room = input().strip()
        if inp_room:
            default_room = inp_room
        
        # Chọn điều khiển
        print("\nChọn điều khiển:")
        print("1. WASD (khuyến nghị cho Player 1)")
        print("2. Mũi tên (khuyến nghị cho Player 2)")
        print("3. Numpad (phím số bên phải)")
        print("4. Tất cả (mặc định)")
        control_choice = input("Chọn (1-4, mặc định 4): ").strip()
    except Exception:
        default_name = 'player1'
        default_room = 'default'
        control_choice = '4'
    
    # Thiết lập điều khiển dựa trên lựa chọn
    use_wasd = control_choice == '1'  # Player 1: WASD
    use_arrows = control_choice == '2'  # Player 2: Mũi tên
    use_numpad = control_choice == '3'  # Numpad
    use_all = control_choice not in ['1', '2', '3']  # Mặc định dùng tất cả

    # Hỏi chế độ 2 người 1 màn hình (WASD + Mũi tên)
    local_multiplayer = False
    try:
        lm = input("\nBật chế độ 2 người 1 màn hình (WASD + Mũi tên)? (y/N): ").strip().lower()
        local_multiplayer = lm == 'y'
    except Exception:
        local_multiplayer = False

    # Kết nối server
    network = None
    networks = []  # nếu local_multiplayer: 2 kết nối
    my_player_id = None
    player_ids = []  # nếu local_multiplayer: [p1_id, p2_id]
    
    try:
        if local_multiplayer:
            # Player 1 (WASD)
            print(f"Connecting Player 1 to {SERVER_IP}:{SERVER_PORT}...")
            net1 = ClientNetwork(SERVER_IP, SERVER_PORT)
            net1.connect()
            print("Player 1 connected!")
            net1.send({"type": "join", "name": default_name or "player1", "room": default_room})
            p1_id = None
            print("Waiting for Player 1 ID...")
            timeout_count = 0
            max_attempts = 50
            while p1_id is None and timeout_count < max_attempts:
                try:
                    msg = net1.receive()
                    if msg is None:
                        timeout_count += 1
                        print(f"[CLIENT] Player 1: No message, attempt {timeout_count}/{max_attempts}")
                        continue
                    print(f"[CLIENT] Player 1 received: {msg.get('type')}")  # Debug log
                    if msg and msg.get('type') == 'joined':
                        p1_id = msg.get('id')
                        print(f"✓ Player 1 ID: {p1_id} (room: {msg.get('room', 'default')})")
                        game_state.add_player(p1_id)
                        # Phát âm thanh vào game cho Player 1
                        if audio_enabled:
                            try:
                                if sounds.get('join'):
                                    sounds['join'].play()
                                    print("[AUDIO] Player 1: ✓ Played join sound")
                                if sounds.get('versus'):
                                    def play_versus_p1():
                                        time.sleep(0.2)
                                        if sounds.get('versus'):
                                            sounds['versus'].play()
                                            print("[AUDIO] Player 1: ✓ Played versus sound")
                                    threading.Thread(target=play_versus_p1, daemon=True).start()
                                if sounds.get('fight'):
                                    def play_fight_p1():
                                        time.sleep(0.7)
                                        if sounds.get('fight'):
                                            sounds['fight'].play()
                                            print("[AUDIO] Player 1: ✓ Played fight sound")
                                    threading.Thread(target=play_fight_p1, daemon=True).start()
                            except Exception as e:
                                print(f"[AUDIO] Player 1 error: {e}")
                        break
                    elif msg:
                        print(f"[CLIENT] Player 1: Received {msg.get('type')} while waiting for 'joined'")
                        if msg.get('type') == 'state':
                            handle_server_message(msg, game_state, sounds, audio_enabled)
                except socket.timeout:
                    timeout_count += 1
                    print(f"[CLIENT] Player 1: Socket timeout, attempt {timeout_count}/{max_attempts}")
                except Exception as e:
                    print(f"[CLIENT] Player 1 error: {e}")
                    timeout_count += 1
                    import traceback
                    traceback.print_exc()
            
            if p1_id is None:
                print("ERROR: Failed to get Player 1 ID")
                sys.exit(1)

            # Player 2 (Arrows)
            print(f"Connecting Player 2 to {SERVER_IP}:{SERVER_PORT}...")
            net2 = ClientNetwork(SERVER_IP, SERVER_PORT)
            net2.connect()
            print("Player 2 connected!")
            net2.send({"type": "join", "name": "player2", "room": default_room})
            p2_id = None
            print("Waiting for Player 2 ID...")
            timeout_count = 0
            max_attempts = 50
            while p2_id is None and timeout_count < max_attempts:
                try:
                    msg = net2.receive()
                    if msg is None:
                        timeout_count += 1
                        print(f"[CLIENT] Player 2: No message, attempt {timeout_count}/{max_attempts}")
                        continue
                    print(f"[CLIENT] Player 2 received: {msg.get('type')}")  # Debug log
                    if msg and msg.get('type') == 'joined':
                        p2_id = msg.get('id')
                        print(f"✓ Player 2 ID: {p2_id} (room: {msg.get('room', 'default')})")
                        game_state.add_player(p2_id)
                        # Phát âm thanh vào game cho Player 2
                        if audio_enabled:
                            try:
                                if sounds.get('join'):
                                    sounds['join'].play()
                                    print("[AUDIO] Player 2: ✓ Played join sound")
                                if sounds.get('versus'):
                                    def play_versus_p2():
                                        time.sleep(0.2)
                                        if sounds.get('versus'):
                                            sounds['versus'].play()
                                            print("[AUDIO] Player 2: ✓ Played versus sound")
                                    threading.Thread(target=play_versus_p2, daemon=True).start()
                                if sounds.get('fight'):
                                    def play_fight_p2():
                                        time.sleep(0.7)
                                        if sounds.get('fight'):
                                            sounds['fight'].play()
                                            print("[AUDIO] Player 2: ✓ Played fight sound")
                                    threading.Thread(target=play_fight_p2, daemon=True).start()
                            except Exception as e:
                                print(f"[AUDIO] Player 2 error: {e}")
                        break
                    elif msg:
                        print(f"[CLIENT] Player 2: Received {msg.get('type')} while waiting for 'joined'")
                        if msg.get('type') == 'state':
                            handle_server_message(msg, game_state, sounds, audio_enabled)
                except socket.timeout:
                    timeout_count += 1
                    print(f"[CLIENT] Player 2: Socket timeout, attempt {timeout_count}/{max_attempts}")
                except Exception as e:
                    print(f"[CLIENT] Player 2 error: {e}")
                    timeout_count += 1
                    import traceback
                    traceback.print_exc()
            
            if p2_id is None:
                print("ERROR: Failed to get Player 2 ID")
                sys.exit(1)

            networks = [net1, net2]
            player_ids = [p1_id, p2_id]
            # Giữ biến cũ để không sửa nhiều chỗ
            network = net1
            my_player_id = p1_id
        else:
            network = ClientNetwork(SERVER_IP, SERVER_PORT)
            print(f"Connecting to {SERVER_IP}:{SERVER_PORT}...")
            network.connect()
            print("Connected successfully!")
            
            # Gửi message join
            network.send({"type": "join", "name": default_name, "room": default_room})
            
            # Chờ nhận player_id từ server
            print("Waiting for server to assign ID...")
            timeout_count = 0
            max_attempts = 50  # Tăng số lần thử
            while my_player_id is None and timeout_count < max_attempts:
                try:
                    msg = network.receive()
                    if msg is None:
                        timeout_count += 1
                        print(f"[CLIENT] No message received, attempt {timeout_count}/{max_attempts}")
                        continue
                    print(f"[CLIENT] Received message type: {msg.get('type')}")  # Debug log
                    if msg and msg.get('type') == 'joined':
                        my_player_id = msg.get('id')
                        print(f"✓ Received player ID: {my_player_id} (room: {msg.get('room', 'default')})")
                        # Thêm player vào game state
                        game_state.add_player(my_player_id)
                        # Phát âm thanh vào game khi vừa vào
                        if audio_enabled:
                            try:
                                # Phát âm thanh join ngay lập tức
                                if sounds.get('join'):
                                    sounds['join'].play()
                                    print("[AUDIO] ✓ Played join sound")
                                # Phát âm thanh versus sau một chút (không block)
                                if sounds.get('versus'):
                                    def play_versus():
                                        time.sleep(0.2)  # 200ms delay
                                        if sounds.get('versus'):
                                            sounds['versus'].play()
                                            print("[AUDIO] ✓ Played versus sound")
                                    threading.Thread(target=play_versus, daemon=True).start()
                                # Phát âm thanh fight sau versus
                                if sounds.get('fight'):
                                    def play_fight():
                                        time.sleep(0.7)  # 700ms total delay (200ms + 500ms)
                                        if sounds.get('fight'):
                                            sounds['fight'].play()
                                            print("[AUDIO] ✓ Played fight sound")
                                    threading.Thread(target=play_fight, daemon=True).start()
                            except Exception as e:
                                print(f"[AUDIO] Error playing join sounds: {e}")
                        break
                    elif msg:
                        # Lưu các message khác để xử lý sau (state, level, etc.)
                        print(f"[CLIENT] Received {msg.get('type')} message while waiting for 'joined', will process later")
                        # Có thể xử lý state ngay nếu muốn
                        if msg.get('type') == 'state':
                            handle_server_message(msg, game_state, sounds, audio_enabled)
                except socket.timeout:
                    timeout_count += 1
                    print(f"[CLIENT] Socket timeout, attempt {timeout_count}/{max_attempts}")
                except Exception as e:
                    print(f"[CLIENT] Error receiving message: {e}")
                    timeout_count += 1
                    import traceback
                    traceback.print_exc()
            
            if my_player_id is None:
                print("ERROR: Failed to receive player ID from server after multiple attempts.")
                print("Please check if server is running and try again.")
                sys.exit(1)
        
        print("\n=== CONTROLS ===")
        if local_multiplayer:
            print("2P một màn hình:")
            print("- Player 1: WASD (+ Shift chạy nhanh)")
            print("- Player 2: Mũi tên ↑↓←→")
        else:
            if use_wasd:
                print("WASD: W/A/S/D để di chuyển (Player 1)")
            elif use_arrows:
                print("Mũi tên: ↑↓←→ để di chuyển (Player 2)")
            elif use_numpad:
                print("Numpad: 2,4,6,8 để di chuyển, 7,9,1,3 để di chuyển chéo")
            else:
                print("WASD, Mũi tên, hoặc Numpad (2,4,6,8) để di chuyển")
                print("Numpad 7,9,1,3 để di chuyển chéo")
        print("Shift để chạy nhanh, ESC để thoát\n")
        
        # Không cần cổng vào
        gate_unlocked = True
        coins = 10
        last_goal_collect = 0
        awaiting_next_level = False

        # Thiết lập "trận đấu" kiểu đối kháng cho chế độ 2 người 1 màn hình
        fight_started = not local_multiplayer  # nếu single thì vào luôn
        countdown_started = False
        countdown_start_ticks = 0
        last_countdown_second = None
        dash_sfx_cooldown = 0.0
        dash_sfx_interval = 0.6

        # Khi đủ 2 player => phát nhạc/hiệu ứng đối đầu + đếm ngược
        if local_multiplayer and len(player_ids) >= 2:
            try:
                if sounds.get('versus'):
                    sounds['versus'].play()
            except Exception:
                pass
            # crowd loop
            try:
                if sounds.get('crowd'):
                    sounds['crowd'].play(loops=-1)
            except Exception:
                pass
            countdown_started = True
            countdown_start_ticks = pygame.time.get_ticks()
            last_countdown_second = 3
            try:
                if sounds.get('countdown'):
                    sounds['countdown'].play()
            except Exception:
                pass
        # Game loop
        running = True
        footstep_cooldown = 0.0
        footstep_interval = 0.25
        while running:
            dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
            footstep_cooldown = min(footstep_cooldown + dt, 10.0)
            dash_sfx_cooldown = min(dash_sfx_cooldown + dt, 10.0)
            
            # Update particles
            renderer.particle_system.update(dt)
            
            # Xử lý events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # Điều khiển âm thanh
                    if audio_enabled:
                        if event.key in (pygame.K_m,):
                            # Toggle mute
                            try:
                                current = pygame.mixer.music.get_volume() if pygame.mixer.music else 0.35
                            except Exception:
                                current = 0.35
                            new_vol = 0.0 if current > 0.01 else 0.35
                            try:
                                if pygame.mixer.music:
                                    pygame.mixer.music.set_volume(new_vol)
                            except Exception:
                                pass
                            for s in sounds.values():
                                try:
                                    if s:
                                        s.set_volume(0.0 if new_vol == 0.0 else 0.6)
                                except Exception:
                                    pass
                            print(f"[AUDIO] {'Muted' if new_vol == 0.0 else 'Unmuted'}")
                        if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                            try:
                                v = pygame.mixer.music.get_volume()
                            except Exception:
                                v = 0.35
                            v = min(1.0, v + 0.1)
                            try:
                                if pygame.mixer.music:
                                    pygame.mixer.music.set_volume(v)
                            except Exception:
                                pass
                            for s in sounds.values():
                                try:
                                    if s:
                                        s.set_volume(min(1.0, (s.get_volume() or 0.6) + 0.1))
                                except Exception:
                                    pass
                            print(f"[AUDIO] Volume: {int(v*100)}%")
                        if event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                            try:
                                v = pygame.mixer.music.get_volume()
                            except Exception:
                                v = 0.35
                            v = max(0.0, v - 0.1)
                            try:
                                if pygame.mixer.music:
                                    pygame.mixer.music.set_volume(v)
                            except Exception:
                                pass
                            for s in sounds.values():
                                try:
                                    if s:
                                        s.set_volume(max(0.0, (s.get_volume() or 0.6) - 0.1))
                                except Exception:
                                    pass
                            print(f"[AUDIO] Volume: {int(v*100)}%")
            
            # Xử lý input & gửi move
            keys = pygame.key.get_pressed()
            base_speed = 200 * dt
            speed_boost = 1.8 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 1.0
            speed = base_speed * speed_boost

            # Đếm ngược trước khi bắt đầu (chỉ local 2P)
            if local_multiplayer and countdown_started and not fight_started:
                now_ms = pygame.time.get_ticks()
                elapsed = (now_ms - countdown_start_ticks) // 1000  # giây
                remaining = max(0, 3 - int(elapsed))
                if last_countdown_second != remaining and remaining > 0:
                    # beep mỗi giây
                    try:
                        if sounds.get('countdown'):
                            sounds['countdown'].play()
                    except Exception:
                        pass
                    last_countdown_second = remaining
                if elapsed >= 3:
                    fight_started = True
                    countdown_started = False
                    last_countdown_second = None
                    # hô FIGHT!
                    try:
                        if sounds.get('fight'):
                            sounds['fight'].play()
                    except Exception:
                        pass

            if local_multiplayer and len(player_ids) >= 2 and len(networks) >= 2 and fight_started:
                # Player 1: WASD
                dx1 = (-speed if keys[pygame.K_a] else 0) + (speed if keys[pygame.K_d] else 0)
                dy1 = (-speed if keys[pygame.K_w] else 0) + (speed if keys[pygame.K_s] else 0)
                # Player 2: Arrows
                dx2 = (-speed if keys[pygame.K_LEFT] else 0) + (speed if keys[pygame.K_RIGHT] else 0)
                dy2 = (-speed if keys[pygame.K_UP] else 0) + (speed if keys[pygame.K_DOWN] else 0)

                # Update + send P1
                p1 = player_ids[0]
                if p1 in game_state.players:
                    new_x1 = max(0, min(SCREEN_WIDTH, game_state.players[p1].x + dx1))
                    new_y1 = max(0, min(SCREEN_HEIGHT, game_state.players[p1].y + dy1))
                    game_state.players[p1].x = new_x1
                    game_state.players[p1].y = new_y1
                    if dx1 != 0 or dy1 != 0:
                        if audio_enabled and sounds.get('footstep') and footstep_cooldown >= footstep_interval:
                            try: sounds['footstep'].play()
                            except Exception: pass
                            footstep_cooldown = 0.0
                        # Dash sfx khi đang giữ Shift
                        if speed_boost > 1.0 and audio_enabled and sounds.get('dash') and dash_sfx_cooldown >= dash_sfx_interval:
                            try: sounds['dash'].play()
                            except Exception: pass
                            dash_sfx_cooldown = 0.0
                        # Thêm particles cho Player 1
                        p1_obj = game_state.players[p1]
                        vel_x1 = dx1 / dt if dt > 0 else 0
                        vel_y1 = dy1 / dt if dt > 0 else 0
                        for _ in range(3):
                            renderer.particle_system.add_particle(
                                p1_obj.x, p1_obj.y,
                                color=(150, 150, 150),
                                velocity_x=-vel_x1 * 0.3,
                                velocity_y=-vel_y1 * 0.3
                            )
                        networks[0].send({"type": "move", "id": p1, "x": new_x1, "y": new_y1})

                # Update + send P2
                p2 = player_ids[1]
                if p2 in game_state.players:
                    new_x2 = max(0, min(SCREEN_WIDTH, game_state.players[p2].x + dx2))
                    new_y2 = max(0, min(SCREEN_HEIGHT, game_state.players[p2].y + dy2))
                    game_state.players[p2].x = new_x2
                    game_state.players[p2].y = new_y2
                    if dx2 != 0 or dy2 != 0:
                        if audio_enabled and sounds.get('footstep') and footstep_cooldown >= footstep_interval:
                            try: sounds['footstep'].play()
                            except Exception: pass
                            footstep_cooldown = 0.0
                        # Dash sfx khi đang giữ Shift (áp dụng chung)
                        if speed_boost > 1.0 and audio_enabled and sounds.get('dash') and dash_sfx_cooldown >= dash_sfx_interval:
                            try: sounds['dash'].play()
                            except Exception: pass
                            dash_sfx_cooldown = 0.0
                        # Thêm particles cho Player 2
                        p2_obj = game_state.players[p2]
                        vel_x2 = dx2 / dt if dt > 0 else 0
                        vel_y2 = dy2 / dt if dt > 0 else 0
                        for _ in range(3):
                            renderer.particle_system.add_particle(
                                p2_obj.x, p2_obj.y,
                                color=(150, 150, 150),
                                velocity_x=-vel_x2 * 0.3,
                                velocity_y=-vel_y2 * 0.3
                            )
                        networks[1].send({"type": "move", "id": p2, "x": new_x2, "y": new_y2})
            else:
                # Single-player theo lựa chọn điều khiển
                dx = dy = 0
                if use_wasd or use_all:
                    dx += (-speed if keys[pygame.K_a] else 0) + (speed if keys[pygame.K_d] else 0)
                    dy += (-speed if keys[pygame.K_w] else 0) + (speed if keys[pygame.K_s] else 0)
                if use_arrows or use_all:
                    dx += (-speed if keys[pygame.K_LEFT] else 0) + (speed if keys[pygame.K_RIGHT] else 0)
                    dy += (-speed if keys[pygame.K_UP] else 0) + (speed if keys[pygame.K_DOWN] else 0)
                if use_numpad or use_all:
                    # ưu tiên chéo
                    if keys[pygame.K_KP7]: dx, dy = -speed, -speed
                    elif keys[pygame.K_KP9]: dx, dy = speed, -speed
                    elif keys[pygame.K_KP1]: dx, dy = -speed, speed
                    elif keys[pygame.K_KP3]: dx, dy = speed, speed
                    else:
                        dx += (-speed if keys[pygame.K_KP4] else 0) + (speed if keys[pygame.K_KP6] else 0)
                        dy += (-speed if keys[pygame.K_KP8] else 0) + (speed if keys[pygame.K_KP2] else 0)

                if my_player_id and my_player_id in game_state.players:
                    new_x = max(0, min(SCREEN_WIDTH, game_state.players[my_player_id].x + dx))
                    new_y = max(0, min(SCREEN_HEIGHT, game_state.players[my_player_id].y + dy))
                    game_state.players[my_player_id].x = new_x
                    game_state.players[my_player_id].y = new_y
                    if dx != 0 or dy != 0:
                        if audio_enabled and sounds.get('footstep') and footstep_cooldown >= footstep_interval:
                            try: sounds['footstep'].play()
                            except Exception: pass
                            footstep_cooldown = 0.0
                        if speed_boost > 1.0 and audio_enabled and sounds.get('dash') and dash_sfx_cooldown >= dash_sfx_interval:
                            try: sounds['dash'].play()
                            except Exception: pass
                            dash_sfx_cooldown = 0.0
                        # Thêm particles khi di chuyển
                        player = game_state.players[my_player_id]
                        # Tính velocity từ hướng di chuyển
                        vel_x = dx / dt if dt > 0 else 0
                        vel_y = dy / dt if dt > 0 else 0
                        # Thêm 3-5 particles
                        for _ in range(3):
                            renderer.particle_system.add_particle(
                                player.x, player.y,
                                color=(150, 150, 150),
                                velocity_x=-vel_x * 0.3,
                                velocity_y=-vel_y * 0.3
                            )
                        network.send({"type": "move", "id": my_player_id, "x": new_x, "y": new_y})
            
            # Nhận messages từ server (non-blocking)
            if local_multiplayer and networks:
                for net in networks:
                    try:
                        net.sock.settimeout(0.01)
                        msg = net.receive()
                        if msg:
                            handle_server_message(msg, game_state, sounds, audio_enabled)
                    except Exception:
                        pass
            else:
                try:
                    network.sock.settimeout(0.01)
                    msg = network.receive()
                    if msg:
                        handle_server_message(msg, game_state, sounds, audio_enabled)
                except Exception:
                    pass
            
            # Update game state
            game_state.update(dt)
            
            # Render
            renderer.clear((30, 30, 50))  # Nền xanh đậm

            # Hiển thị đếm ngược "3 2 1 FIGHT!" nếu cần
            if local_multiplayer and countdown_started and not fight_started:
                if font:
                    now_ms = pygame.time.get_ticks()
                    elapsed = (now_ms - countdown_start_ticks) // 1000
                    remaining = max(0, 3 - int(elapsed))
                    txt = str(remaining) if remaining > 0 else "FIGHT!"
                    surf = font.render(txt, True, (255, 215, 0))
                    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    renderer.screen.blit(surf, rect)
            
            # Vẽ goal (đích)
            goal = getattr(game_state, 'goal', None)
            if goal:
                renderer.draw_goal(goal.get('x', 0), goal.get('y', 0), goal.get('width', 0), goal.get('height', 0))
                if my_player_id and my_player_id in game_state.players:
                    px = game_state.players[my_player_id].x
                    py = game_state.players[my_player_id].y
                    gx, gy = goal.get('x', 0), goal.get('y', 0)
                    gw, gh = goal.get('width', 40), goal.get('height', 40)
                    collide = (gx <= px <= gx+gw and gy <= py <= gy+gh)
                    now = pygame.time.get_ticks()
                    if collide and now - last_goal_collect > 1000 and not awaiting_next_level:
                        print(f"[CLIENT] Reached GOAL! (send goal to server)")
                        try:
                            network.send({"type": "goal", "id": my_player_id})
                        except Exception as e:
                            print("[CLIENT] Error sending goal to server:", e)
                        last_goal_collect = now
                        awaiting_next_level = True
            # Vẽ obstacles trước (để players hiển thị phía trên)
            for obs_id, obstacle in game_state.obstacles.items():
                renderer.draw_obstacle(
                    obstacle.x, obstacle.y, 
                    obstacle.width, obstacle.height
                )
            
            # Vẽ tất cả players
            for pid, player in game_state.players.items():
                if local_multiplayer and pid in player_ids:
                    idx = player_ids.index(pid)
                    color = (0, 255, 0) if idx == 0 else (255, 255, 0)
                else:
                    color = (0, 255, 0) if (my_player_id and pid == my_player_id) else (255, 0, 0)
                renderer.draw_player(player.x or 400, player.y or 300, color)
                renderer.draw_name(player.x or 400, (player.y or 300), getattr(player, 'name', ''))
            
            # VẼ HUD XU lên canvas nhỏ để không bị ghi đè
            try:
                if renderer._font:
                    hud_text = renderer._font.render(f"Xu: {coins}", True, (255, 255, 0))
                    renderer.canvas.blit(hud_text, (6, 6))
            except Exception as e:
                print("HUD render error:", e)

            renderer.present(
                players=game_state.players,
                obstacles=game_state.obstacles,
                goal=getattr(game_state, 'goal', None),
                my_player_id=my_player_id
            )
        
        # Gửi message leave và đóng kết nối
        if local_multiplayer and networks and player_ids:
            for i, pid in enumerate(player_ids):
                try:
                    networks[i].send({"type": "leave", "id": pid})
                except Exception:
                    pass
            for net in networks:
                try: net.close()
                except Exception: pass
        else:
            if my_player_id:
                network.send({"type": "leave", "id": my_player_id})
            if network:
                network.close()
        
    except Exception as e:
        print(f"Connection error: {e}")
        print("Make sure the server is running!")
    
    pygame.quit()
    sys.exit()

def handle_server_message(msg, game_state, sounds, audio_enabled):
    """Xử lý messages nhận được từ server."""
    msg_type = msg.get('type')
    
    if msg_type == 'state':
        # Cập nhật state từ server
        players_data = msg.get('players', {})
        for pid, data in players_data.items():
            if pid not in game_state.players:
                game_state.add_player(pid)
            # cập nhật tên (nếu có)
            if 'name' in data:
                game_state.players[pid].name = data.get('name') or ''
            game_state.players[pid].x = data.get('x', 0)
            game_state.players[pid].y = data.get('y', 0)
            game_state.players[pid].hp = data.get('hp', 100)
        
        # Cập nhật obstacles từ server
        obstacles_data = msg.get('obstacles', {})
        for obs_id, obs_data in obstacles_data.items():
            if obs_id not in game_state.obstacles:
                game_state.obstacles[obs_id] = Obstacle(
                    id=obs_id,
                    x=obs_data.get('x', 0),
                    y=obs_data.get('y', 0),
                    width=obs_data.get('width', 40),
                    height=obs_data.get('height', 40)
                )
            else:
                # Cập nhật vị trí nếu obstacles có thể di chuyển
                game_state.obstacles[obs_id].x = obs_data.get('x', 0)
                game_state.obstacles[obs_id].y = obs_data.get('y', 0)

        # Cập nhật goal và level
        game_state.goal = msg.get('goal')
        game_state.level = msg.get('level', getattr(game_state, 'level', 1))
    elif msg_type == 'join':
        # Có player mới join
        new_id = msg.get('id')
        if new_id and new_id not in game_state.players:
            game_state.add_player(new_id)
        if audio_enabled and sounds.get('join'):
            try:
                sounds['join'].play()
            except Exception:
                pass
    elif msg_type == 'dead':
        print("You died! Respawning...")
        if audio_enabled and sounds.get('dead'):
            try:
                sounds['dead'].play()
            except Exception:
                pass
    elif msg_type == 'level':
        print(f"[CLIENT] SERVER switched to LEVEL {msg.get('level')}")
        obstacles_data = msg.get('obstacles', {})
        game_state.obstacles.clear()
        for obs_id, obs_data in obstacles_data.items():
            game_state.obstacles[obs_id] = Obstacle(
                id=obs_id,
                x=obs_data.get('x', 0),
                y=obs_data.get('y', 0),
                width=obs_data.get('width', 40),
                height=obs_data.get('height', 40)
            )
        game_state.goal = msg.get('goal')
        game_state.level = msg.get('level', getattr(game_state, 'level', 1))
        if audio_enabled and sounds.get('level'):
            try:
                sounds['level'].play()
            except Exception:
                pass
        # --- cộng xu 10 nếu vừa về goal ---
        global awaiting_next_level, coins
        try:
            if awaiting_next_level:
                coins +=10
                print("[CLIENT] +10 xu! Tổng xu:", coins)
            awaiting_next_level = False
        except Exception:
            pass
    elif msg_type == 'leave':
        # Có player rời
        leave_id = msg.get('id')
        if leave_id:
            game_state.remove_player(leave_id)
        if audio_enabled and sounds.get('leave'):
            try:
                sounds['leave'].play()
            except Exception:
                pass

if __name__ == '__main__':
    main()
