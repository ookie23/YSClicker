import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
import ctypes
import sys
import os
import json
import string
import winsound
from pynput import keyboard as pkb
from pynput import mouse as pms
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

# 全局状态
running = False
hotkey = "<f8>"
mouse_side_key = None
keyboard_controller = KeyboardController()
mouse_controller = MouseController()
current_mouse_pos = (0, 0)

CONFIG_FILE = "config.json"
AGREEMENT_FILE = "agreement_accepted.txt"

def generate_random_title():
    length = random.randint(5, 10)
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def play_start_sound():
    try:
        winsound.Beep(600, 100)
        time.sleep(0.05)
        winsound.Beep(900, 100)
        time.sleep(0.05)
        winsound.Beep(1200, 150)
    except:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)

def play_stop_sound():
    try:
        winsound.Beep(1200, 100)
        time.sleep(0.05)
        winsound.Beep(900, 100)
        time.sleep(0.05)
        winsound.Beep(600, 150)
    except:
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

def play_pause_sound():
    try:
        winsound.Beep(400, 200)
    except:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)

def play_resume_sound():
    try:
        winsound.Beep(1000, 200)
    except:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)

def load_config():
    global hotkey, mouse_side_key
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'hotkey' in config and config['hotkey']:
                    hotkey = config['hotkey']
                if 'mouse_side' in config and config['mouse_side']:
                    if config['mouse_side'] == 'x1':
                        mouse_side_key = Button.x1
                    elif config['mouse_side'] == 'x2':
                        mouse_side_key = Button.x2
    except:
        pass

def save_config():
    global hotkey, mouse_side_key
    try:
        config = {
            'hotkey': hotkey,
            'mouse_side': 'x1' if mouse_side_key == Button.x1 else 'x2' if mouse_side_key == Button.x2 else None
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f)
    except:
        pass

def check_agreement():
    """检查是否已同意免责声明"""
    return os.path.exists(AGREEMENT_FILE)

def mark_agreement_accepted():
    """标记已同意免责声明"""
    try:
        with open(AGREEMENT_FILE, 'w') as f:
            f.write("User has accepted the disclaimer.")
    except:
        pass

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.window_title = generate_random_title()
        self.root.title(self.window_title)
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # 隐藏主窗口直到同意免责声明
        self.root.withdraw()
        
        # 状态显示
        self.status_label = tk.Label(root, text="状态: 已停止", font=("微软雅黑", 14, "bold"), fg="red")
        self.status_label.pack(pady=5)
        
        # 功能选项
        options_frame = tk.LabelFrame(root, text="按键选项", font=("微软雅黑", 10), padx=10, pady=5)
        options_frame.pack(fill="x", padx=20, pady=3)
        
        self.space_var = tk.BooleanVar(value=True)
        self.f_var = tk.BooleanVar(value=True)
        self.click_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="空格键 (Space)", variable=self.space_var, font=("微软雅黑", 10)).pack(anchor="w")
        tk.Checkbutton(options_frame, text="F键", variable=self.f_var, font=("微软雅黑", 10)).pack(anchor="w")
        tk.Checkbutton(options_frame, text="鼠标左键 (随机偏移)", variable=self.click_var, font=("微软雅黑", 10)).pack(anchor="w")
        
        # 鼠标偏移设置
        offset_frame = tk.LabelFrame(root, text="鼠标点击偏移设置", font=("微软雅黑", 10), padx=10, pady=5)
        offset_frame.pack(fill="x", padx=20, pady=3)
        
        tk.Label(offset_frame, text="最小偏移(像素):", font=("微软雅黑", 9)).grid(row=0, column=0, sticky="w", pady=2)
        self.min_offset = tk.Entry(offset_frame, width=10)
        self.min_offset.insert(0, "3")
        self.min_offset.grid(row=0, column=1, padx=5)
        
        tk.Label(offset_frame, text="最大偏移(像素):", font=("微软雅黑", 9)).grid(row=1, column=0, sticky="w", pady=2)
        self.max_offset = tk.Entry(offset_frame, width=10)
        self.max_offset.insert(0, "14")
        self.max_offset.grid(row=1, column=1, padx=5)
        
        tk.Label(offset_frame, text="偏移说明: 以启动位置为锚点，累积偏移，超60像素拉回", 
                 font=("微软雅黑", 8), fg="gray").grid(row=2, column=0, columnspan=2, pady=3)
        
        # 热键设置
        hotkey_frame = tk.LabelFrame(root, text="启动/停止热键设置", font=("微软雅黑", 10), padx=10, pady=5)
        hotkey_frame.pack(fill="x", padx=20, pady=3)
        
        tk.Label(hotkey_frame, text="键盘热键:", font=("微软雅黑", 10)).pack(side="left")
        self.hotkey_label = tk.Label(hotkey_frame, text=hotkey.upper(), font=("微软雅黑", 10, "bold"), fg="blue")
        self.hotkey_label.pack(side="left", padx=5)
        
        tk.Button(hotkey_frame, text="设置键盘热键", command=self.set_hotkey, font=("微软雅黑", 9)).pack(side="right")
        
        # 鼠标侧键设置
        mouse_frame = tk.LabelFrame(root, text="鼠标侧键设置 (罗技G102)", font=("微软雅黑", 10), padx=10, pady=5)
        mouse_frame.pack(fill="x", padx=20, pady=3)
        
        if mouse_side_key == Button.x1:
            self.mouse_label = tk.Label(mouse_frame, text="已绑定: 鼠标侧键1", font=("微软雅黑", 10), fg="blue")
        elif mouse_side_key == Button.x2:
            self.mouse_label = tk.Label(mouse_frame, text="已绑定: 鼠标侧键2", font=("微软雅黑", 10), fg="blue")
        else:
            self.mouse_label = tk.Label(mouse_frame, text="未绑定鼠标侧键", font=("微软雅黑", 10), fg="gray")
        self.mouse_label.pack(side="left")
        
        tk.Button(mouse_frame, text="绑定侧键1", command=lambda: self.set_mouse_side("x1"), font=("微软雅黑", 9)).pack(side="right", padx=2)
        tk.Button(mouse_frame, text="绑定侧键2", command=lambda: self.set_mouse_side("x2"), font=("微软雅黑", 9)).pack(side="right", padx=2)
        
        # 启动/停止按钮
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        self.start_btn = tk.Button(btn_frame, text="▶ 启动", command=self.start, font=("微软雅黑", 12, "bold"), 
                                    bg="#4CAF50", fg="white", width=10, height=1)
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = tk.Button(btn_frame, text="■ 停止", command=self.stop, font=("微软雅黑", 12, "bold"),
                                   bg="#f44336", fg="white", width=10, height=1, state="disabled")
        self.stop_btn.pack(side="left", padx=10)
        
        # 功能说明按钮
        info_btn = tk.Button(root, text="📖 功能说明与免责声明", command=self.show_info, 
                              font=("微软雅黑", 10), bg="#2196F3", fg="white", padx=10, pady=3)
        info_btn.pack(pady=3)
        
        # 使用说明
        info_frame = tk.LabelFrame(root, text="使用说明", font=("微软雅黑", 10), padx=10, pady=5)
        info_frame.pack(fill="x", padx=20, pady=3)
        
        usage_text = (
            "【基本操作】\n"
            f"• 启动/停止: 热键 [{hotkey.upper()}] 或鼠标侧键\n"
            "• 按键选项: 勾选需要自动按的键\n"
            "• 偏移设置: 鼠标点击在锚点周围随机偏移\n\n"
            "【运行逻辑】\n"
            "• 每次按键间隔0-1秒随机(带拟人化节奏)\n"
            "• 运行30-40秒后自动暂停2-4秒\n"
            "• 鼠标点击带轨迹移动和累积偏移\n"
            "• 偶发漏按(3%)和双击(1%)模拟真人\n\n"
            "【注意事项】\n"
            "• 需要管理员权限运行\n"
            "• 设置自动保存，下次启动恢复\n"
            "• 本工具完全免费，仅供学习交流\n"
            "• 使用本工具产生的一切后果由使用者自行承担"
        )
        tk.Label(info_frame, text=usage_text, font=("微软雅黑", 8), justify="left", anchor="w").pack(anchor="w")
        
        # 鼠标位置相关
        self.anchor_pos = None
        self.last_click_pos = None
        self.click_count = 0
        
        self.mouse_listener = None
        self.keyboard_listener = None
        self.setup_listeners()
        
        # 检查是否已同意免责声明
        if not check_agreement():
            # 显示免责声明弹窗
            self.root.after(100, self.show_agreement)
        else:
            # 已同意，直接显示主窗口
            self.root.deiconify()
    
    def show_agreement(self):
        """显示强制免责声明弹窗"""
        agreement_text = """⚠️ 免责声明与使用条款

请仔细阅读以下内容：

【软件性质】
本软件完全免费，仅供学习交流和自动化测试使用。

【风险提示】
1. 使用本软件可能违反游戏用户协议
2. 存在账号被封禁的风险
3. 可能导致数据丢失或其他损失

【使用者责任】
1. 使用者应自行了解并遵守相关游戏规则和法律法规
2. 因使用本软件产生的一切后果由使用者自行承担
3. 软件作者不对任何直接或间接损失负责

【禁止行为】
1. 严禁将本软件用于商业用途
2. 严禁将本软件用于任何违法活动
3. 严禁在主要游戏账号上使用

【同意条款】
继续使用本软件即表示您：
✓ 已年满18周岁
✓ 已阅读并理解上述所有条款
✓ 自愿承担使用本软件的一切风险
✓ 同意本软件的所有免责声明

──────────────────────────────

如不同意，请点击关闭按钮退出软件。
"""
        
        # 创建弹窗
        agreement_window = tk.Toplevel(self.root)
        agreement_window.title("免责声明 - 请仔细阅读")
        agreement_window.geometry("550x650")
        agreement_window.resizable(False, False)
        agreement_window.attributes('-topmost', True)
        
        # 禁止关闭按钮
        agreement_window.protocol("WM_DELETE_WINDOW", self.on_agreement_close)
        
        # 居中显示
        agreement_window.update_idletasks()
        x = (agreement_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (agreement_window.winfo_screenheight() // 2) - (650 // 2)
        agreement_window.geometry(f"550x650+{x}+{y}")
        
        # 标题
        title_label = tk.Label(agreement_window, text="⚠️ 免责声明与使用条款", 
                                font=("微软雅黑", 14, "bold"), fg="red")
        title_label.pack(pady=15)
        
        # 正文（带滚动条）
        text_frame = tk.Frame(agreement_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(text_frame, yscrollcommand=scrollbar.set, 
                               font=("微软雅黑", 9), wrap="word", padx=10, pady=10)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", agreement_text)
        text_widget.config(state="disabled")
        
        scrollbar.config(command=text_widget.yview)
        
        # 强制阅读倒计时
        self.agreement_countdown = 5
        self.agree_btn = tk.Button(agreement_window, text=f"我已阅读并同意 ({self.agreement_countdown}秒后可点击)", 
                                    command=lambda: self.accept_agreement(agreement_window),
                                    font=("微软雅黑", 11, "bold"), bg="#4CAF50", fg="white", 
                                    padx=20, pady=8, state="disabled")
        self.agree_btn.pack(pady=15)
        
        # 倒计时
        def countdown():
            if self.agreement_countdown > 0:
                self.agreement_countdown -= 1
                self.agree_btn.config(text=f"我已阅读并同意 ({self.agreement_countdown}秒后可点击)")
                agreement_window.after(1000, countdown)
            else:
                self.agree_btn.config(text="我已阅读并同意", state="normal")
        
        countdown()
        
        # 保存窗口引用
        self.agreement_window = agreement_window
    
    def accept_agreement(self, window):
        """接受免责声明"""
        mark_agreement_accepted()
        window.destroy()
        # 显示主窗口
        self.root.deiconify()
    
    def on_agreement_close(self):
        """用户点击关闭按钮，退出整个软件"""
        self.root.destroy()
        os._exit(0)
    
    def show_info(self):
        """显示功能说明和免责声明"""
        info_text = """📖 功能设计思路说明

【1. 随机按键功能】
设计思路: 模拟真人按键的不规律性，避免固定间隔被识别。
实现方式: 在0-1秒范围内随机生成等待时间，每次按键间隔都不同。

【2. 鼠标随机偏移】
设计思路: 真人点击时会有微小偏移，不会每次都点在同一像素。
实现方式: 以启动位置为锚点，每次点击在锚点周围3-14像素内随机偏移，使用三角分布让偏移更集中在中间值。

【3. 累积偏移+轨迹移动】
设计思路: 真人连续点击时，手会自然漂移，且移动有轨迹。
实现方式: 每次以上次点击位置为基准继续偏移，鼠标分3-8步移动到目标位置，每步加入随机抖动。超过60像素自动拉回锚点。

【4. 自动暂停机制】
设计思路: 真人长时间操作会疲劳，需要休息。
实现方式: 每运行30-40秒(随机)后，自动暂停2-4秒(随机)，模拟人手休息。

【5. 拟人化细节】
• 按键时长: 使用正态分布，大多数在0.04-0.06秒，偶尔长按或短按
• 按键节奏: 基础节奏+随机抖动，运行后期间隔变长(疲劳模拟)
• 偶发行为: 3%概率漏按，1%概率双击
• 组合逻辑: 50%单键，30%双键，20%全按

【6. 热键系统】
设计思路: 全局热键方便快速启停，不干扰游戏操作。
实现方式: 支持键盘F1-F12等热键，支持罗技G102鼠标侧键。

【7. 配置保存】
设计思路: 用户不需要每次重新设置。
实现方式: 设置自动保存到config.json，下次启动自动加载。

【8. 提示音系统】
设计思路: 通过声音确认状态变化，无需看界面。
实现方式: 启动(上升音)、停止(下降音)、暂停(低音)、恢复(高音)。

【9. 随机窗口标题】
设计思路: 避免窗口标题被检测软件识别。
实现方式: 每次启动生成5-10位随机字母数字作为标题。

──────────────────────────────

⚠️ 免责声明

1. 本软件完全免费，仅供学习交流和自动化测试使用。

2. 严禁将本软件用于任何违反游戏服务条款的行为。

3. 使用本软件可能违反游戏用户协议，存在账号被封禁的风险。

4. 使用者应自行了解并遵守相关游戏规则和法律法规。

5. 因使用本软件产生的一切后果（包括但不限于账号封禁、数据丢失、法律责任等），由使用者自行承担。

6. 软件作者不对任何因使用本软件而导致的直接或间接损失负责。

7. 继续使用本软件即表示您已阅读并同意本免责声明。

──────────────────────────────

💡 使用建议
• 请勿在主要账号上使用
• 合理设置按键间隔，避免过于频繁
• 定期暂停，模拟真人操作节奏
• 关注游戏官方公告，及时停止使用
"""
        
        # 创建弹窗
        info_window = tk.Toplevel(self.root)
        info_window.title("功能说明与免责声明")
        info_window.geometry("500x600")
        info_window.attributes('-topmost', True)
        
        # 添加滚动条
        scrollbar = tk.Scrollbar(info_window)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(info_window, yscrollcommand=scrollbar.set, font=("微软雅黑", 9), wrap="word", padx=10, pady=10)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", info_text)
        text_widget.config(state="disabled")  # 只读
        
        scrollbar.config(command=text_widget.yview)
        
        # 关闭按钮
        close_btn = tk.Button(info_window, text="关闭", command=info_window.destroy, 
                               font=("微软雅黑", 10, "bold"), bg="#4CAF50", fg="white", padx=20, pady=5)
        close_btn.pack(pady=10)
    
    def get_random_offset(self):
        """获取随机偏移量（三角分布，集中在中间值）"""
        try:
            min_off = int(self.min_offset.get())
            max_off = int(self.max_offset.get())
            if min_off < 0:
                min_off = 0
            if max_off < min_off:
                max_off = min_off
        except:
            min_off = 3
            max_off = 14
        
        x_offset = int(random.triangular(-max_off, max_off, 0))
        y_offset = int(random.triangular(-max_off, max_off, 0))
        
        if abs(x_offset) < min_off:
            x_offset = min_off if x_offset >= 0 else -min_off
        if abs(y_offset) < min_off:
            y_offset = min_off if y_offset >= 0 else -min_off
        
        return x_offset, y_offset
    
    def get_human_press_duration(self):
        return max(0.01, min(0.15, random.gauss(0.05, 0.02)))
    
    def get_human_interval(self):
        base_interval = random.uniform(0.2, 0.5)
        jitter = random.uniform(-0.1, 0.15)
        return max(0.05, base_interval + jitter)
    
    def setup_listeners(self):
        global hotkey, mouse_side_key, current_mouse_pos
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        key_to_listen = None
        try:
            clean_hotkey = hotkey.replace('<', '').replace('>', '')
            if clean_hotkey.startswith('f') and len(clean_hotkey) > 1 and clean_hotkey[1:].isdigit():
                f_key = getattr(pkb.Key, clean_hotkey, None)
                if f_key:
                    key_to_listen = f_key
            elif hasattr(pkb.Key, clean_hotkey):
                key_to_listen = getattr(pkb.Key, clean_hotkey)
            elif len(clean_hotkey) == 1:
                key_to_listen = pkb.KeyCode.from_char(clean_hotkey.lower())
        except:
            key_to_listen = pkb.Key.f8
        
        def on_press(key):
            global running
            try:
                if key_to_listen and key == key_to_listen:
                    self.toggle()
            except:
                pass
        
        self.keyboard_listener = pkb.Listener(on_press=on_press)
        self.keyboard_listener.start()
        
        def on_move(x, y):
            global current_mouse_pos
            current_mouse_pos = (x, y)
        
        def on_click(x, y, button, pressed):
            global running, mouse_side_key
            if pressed and mouse_side_key and button == mouse_side_key:
                self.toggle()
        
        self.mouse_listener = pms.Listener(on_move=on_move, on_click=on_click)
        self.mouse_listener.start()
    
    def set_hotkey(self):
        global hotkey
        self.status_label.config(text="请按下新的键盘热键...", fg="orange")
        self.root.update()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        temp_listener = pkb.Listener(on_press=self._capture_hotkey)
        temp_listener.start()
        self.root.after(5000, lambda: self._timeout_hotkey(temp_listener))
    
    def _capture_hotkey(self, key):
        global hotkey
        try:
            if hasattr(key, 'name') and key.name:
                hotkey = f"<{key.name}>"
            elif hasattr(key, 'char') and key.char:
                hotkey = f"<{key.char}>"
            else:
                hotkey = f"<{key}>"
            self.hotkey_label.config(text=hotkey.upper())
            self.status_label.config(text=f"键盘热键已设置为: {hotkey.upper()}", fg="green")
            winsound.Beep(800, 100)
            save_config()
            self.root.after(100, self.setup_listeners)
            return False
        except:
            return True
    
    def _timeout_hotkey(self, listener):
        listener.stop()
        self.status_label.config(text="热键设置超时", fg="red")
        self.setup_listeners()
    
    def set_mouse_side(self, side):
        global mouse_side_key
        if side == "x1":
            mouse_side_key = Button.x1
            self.mouse_label.config(text="已绑定: 鼠标侧键1", fg="blue")
        else:
            mouse_side_key = Button.x2
            self.mouse_label.config(text="已绑定: 鼠标侧键2", fg="blue")
        self.status_label.config(text=f"鼠标侧键绑定成功！", fg="green")
        winsound.Beep(800, 100)
        save_config()
        self.setup_listeners()
    
    def toggle(self):
        if running:
            self.stop()
        else:
            self.start()
    
    def start(self):
        global running, current_mouse_pos
        if not running:
            running = True
            self.status_label.config(text="状态: 运行中", fg="green")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            self.anchor_pos = current_mouse_pos
            self.last_click_pos = current_mouse_pos
            self.click_count = 0
            
            threading.Thread(target=play_start_sound, daemon=True).start()
            threading.Thread(target=self.worker, daemon=True).start()
    
    def stop(self):
        global running
        running = False
        self.status_label.config(text="状态: 已停止", fg="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        threading.Thread(target=play_stop_sound, daemon=True).start()
    
    def move_with_trajectory(self, target_x, target_y):
        current_x, current_y = mouse_controller.position
        steps = random.randint(3, 8)
        for i in range(steps):
            progress = (i + 1) / steps
            next_x = current_x + (target_x - current_x) * progress + random.uniform(-1, 1)
            next_y = current_y + (target_y - current_y) * progress + random.uniform(-1, 1)
            mouse_controller.position = (next_x, next_y)
            time.sleep(random.uniform(0.003, 0.015))
    
    def click_with_offset(self):
        global current_mouse_pos
        
        if self.last_click_pos:
            base_x, base_y = self.last_click_pos
        else:
            base_x, base_y = self.anchor_pos if self.anchor_pos else current_mouse_pos
        
        x_offset, y_offset = self.get_random_offset()
        
        new_x = base_x + x_offset
        new_y = base_y + y_offset
        
        if self.anchor_pos:
            anchor_x, anchor_y = self.anchor_pos
            dist_from_anchor = ((new_x - anchor_x)**2 + (new_y - anchor_y)**2) ** 0.5
            if dist_from_anchor > 60:
                new_x = anchor_x + int(random.triangular(-20, 20, 0))
                new_y = anchor_y + int(random.triangular(-20, 20, 0))
        
        self.move_with_trajectory(new_x, new_y)
        
        mouse_controller.click(Button.left, 1)
        time.sleep(random.uniform(0.01, 0.03))
        
        self.last_click_pos = (new_x, new_y)
        self.click_count += 1
        
        if self.click_count % random.randint(8, 12) == 0 and self.anchor_pos:
            anchor_x, anchor_y = self.anchor_pos
            self.last_click_pos = (
                anchor_x + int(random.triangular(-10, 10, 0)),
                anchor_y + int(random.triangular(-10, 10, 0))
            )
        
        return new_x, new_y
    
    def worker(self):
        global running
        
        while running:
            run_duration = random.uniform(30, 40)
            run_start_time = time.time()
            
            self.root.after(0, lambda: self.status_label.config(text="状态: 运行中", fg="green"))
            
            while running and (time.time() - run_start_time) < run_duration:
                run_progress = (time.time() - run_start_time) / run_duration
                
                wait_time = self.get_human_interval()
                if run_progress > 0.7:
                    wait_time *= random.uniform(1.3, 1.6)
                
                time.sleep(wait_time)
                if not running:
                    break
                
                if random.random() < 0.03:
                    continue
                
                if random.random() < 0.01:
                    if self.click_var.get():
                        self.click_with_offset()
                        time.sleep(0.05)
                        self.click_with_offset()
                        continue
                
                actions = []
                if self.space_var.get():
                    actions.append('space')
                if self.f_var.get():
                    actions.append('f')
                if self.click_var.get():
                    actions.append('left_click')
                
                if not actions:
                    continue
                
                action_pattern = random.random()
                if action_pattern < 0.5:
                    num_actions = 1
                elif action_pattern < 0.8:
                    num_actions = min(2, len(actions))
                else:
                    num_actions = len(actions)
                
                selected_actions = random.sample(actions, num_actions)
                
                try:
                    if 'left_click' in selected_actions:
                        self.click_with_offset()
                        selected_actions.remove('left_click')
                        if not running:
                            break
                    
                    for action in selected_actions:
                        if action == 'space':
                            keyboard_controller.press(Key.space)
                        elif action == 'f':
                            keyboard_controller.press('f')
                    
                    press_duration = self.get_human_press_duration()
                    time.sleep(press_duration)
                    
                    for action in selected_actions:
                        if action == 'space':
                            keyboard_controller.release(Key.space)
                        elif action == 'f':
                            keyboard_controller.release('f')
                    
                except Exception as e:
                    print(f"执行动作时出错: {e}")
            
            if not running:
                break
            
            pause_duration = random.uniform(2, 4)
            self.root.after(0, lambda: self.status_label.config(text=f"状态: 暂停中 ({pause_duration:.1f}秒)", fg="orange"))
            threading.Thread(target=play_pause_sound, daemon=True).start()
            
            pause_start_time = time.time()
            while running and (time.time() - pause_start_time) < pause_duration:
                time.sleep(0.1)
            
            if not running:
                break
            
            self.root.after(0, lambda: self.status_label.config(text="状态: 运行中", fg="green"))
            threading.Thread(target=play_resume_sound, daemon=True).start()
    
    def on_closing(self):
        global running
        running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.root.destroy()
        os._exit(0)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
    
    load_config()
    
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()