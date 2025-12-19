import sys
import random
import tkinter as tk
from typing import Callable, Optional

try:
    import win32con
    import win32gui
except Exception:
    win32con = None
    win32gui = None

from .pet import PetAnimator
from .runtime_tracker import RuntimeTracker
from .data_manager import DataManager  # Added import


class PixelContextMenu:
    """自定义像素风格右键菜单"""
    def __init__(self, master: tk.Misc, items: list) -> None:
        self.master = master
        self.items = items
        self.window: Optional[tk.Toplevel] = None
        self.submenu_window: Optional[tk.Toplevel] = None

    def show(self, x: int, y: int) -> None:
        self.hide()
        
        self.window = tk.Toplevel(self.master)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.geometry(f"+{x}+{y}")
        
        # 样式常量
        BORDER_COLOR = "#FFD700"  # 金色边框
        BG_COLOR = "#222222"      # 深色背景
        FG_COLOR = "#FFFFFF"      # 白色文字
        HOVER_BG = "#FFD700"      # 悬停背景
        HOVER_FG = "#000000"      # 悬停文字
        
        # 边框容器
        border = tk.Frame(self.window, bg=BORDER_COLOR, padx=2, pady=2)
        border.pack(fill="both", expand=True)
        
        # 内容容器
        content = tk.Frame(border, bg=BG_COLOR)
        content.pack(fill="both", expand=True)
        
        for item in self.items:
            if item.get("separator"):
                tk.Frame(content, bg="#555", height=1).pack(fill="x", padx=4, pady=4)
                continue
                
            cmd = item.get("command")
            sub_items = item.get("submenu")
            label_text = f" {item['label']} "
            if sub_items:
                label_text += " ▶" # 添加子菜单指示箭头
            
            lbl = tk.Label(
                content, 
                text=label_text, 
                fg=FG_COLOR, 
                bg=BG_COLOR,
                font=("微软雅黑", 10),
                anchor="w",
                padx=12,
                pady=8
            )
            lbl.pack(fill="x")
            
            # 交互事件
            def on_enter(e, l=lbl, s=sub_items):
                l.configure(bg=HOVER_BG, fg=HOVER_FG)
                if s:
                    # 显示子菜单
                    self._show_submenu(l, s)
                else:
                    # 隐藏已有子菜单（如果有）
                    self._hide_submenu()
            
            def on_leave(e, l=lbl):
                l.configure(bg=BG_COLOR, fg=FG_COLOR)
                # 注意：这里不能立即隐藏子菜单，否则鼠标移动到子菜单时会消失
                # 依靠 _check_close 或其他逻辑处理
                
            def on_click(e, c=cmd):
                if not sub_items:
                    self.hide()
                    if c: c()
            
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", on_click)

        # 点击外部关闭逻辑
        self.window.grab_set()
        self.window.focus_set()
        self.window.bind("<Button-1>", self._check_close)
        
    def _show_submenu(self, parent_widget: tk.Widget, items: list) -> None:
        self._hide_submenu()
        
        x = parent_widget.winfo_rootx() + parent_widget.winfo_width()
        y = parent_widget.winfo_rooty()
        
        self.submenu_window = tk.Toplevel(self.window)
        self.submenu_window.overrideredirect(True)
        self.submenu_window.attributes("-topmost", True)
        self.submenu_window.geometry(f"+{x}+{y}")
        
        # 样式常量 (复用)
        BORDER_COLOR = "#FFD700"
        BG_COLOR = "#222222"
        FG_COLOR = "#FFFFFF"
        HOVER_BG = "#FFD700"
        HOVER_FG = "#000000"
        
        border = tk.Frame(self.submenu_window, bg=BORDER_COLOR, padx=2, pady=2)
        border.pack(fill="both", expand=True)
        content = tk.Frame(border, bg=BG_COLOR)
        content.pack(fill="both", expand=True)
        
        for item in items:
            cmd = item.get("command")
            label_text = f" {item['label']} "
            
            # 支持选中状态标记
            if item.get("checked"):
                label_text = " ✓" + label_text
            else:
                label_text = "   " + label_text # 占位
                
            lbl = tk.Label(
                content, 
                text=label_text, 
                fg=FG_COLOR, 
                bg=BG_COLOR,
                font=("微软雅黑", 10),
                anchor="w",
                padx=12,
                pady=8
            )
            lbl.pack(fill="x")
            
            def on_sub_enter(e, l=lbl):
                l.configure(bg=HOVER_BG, fg=HOVER_FG)
            
            def on_sub_leave(e, l=lbl):
                l.configure(bg=BG_COLOR, fg=FG_COLOR)
                
            def on_sub_click(e, c=cmd):
                self.hide() # 关闭所有菜单
                if c: c()
            
            lbl.bind("<Enter>", on_sub_enter)
            lbl.bind("<Leave>", on_sub_leave)
            lbl.bind("<Button-1>", on_sub_click)
            
    def _hide_submenu(self) -> None:
        if self.submenu_window:
            try:
                self.submenu_window.destroy()
            except Exception:
                pass
            self.submenu_window = None

    def _check_close(self, event: tk.Event) -> None:
        # 检查点击是否在主菜单或子菜单范围内
        x, y = event.x_root, event.y_root
        
        def is_in_window(win):
            if not win: return False
            wx, wy = win.winfo_rootx(), win.winfo_rooty()
            ww, wh = win.winfo_width(), win.winfo_height()
            return wx <= x <= wx + ww and wy <= y <= wy + wh

        if not is_in_window(self.window) and not is_in_window(self.submenu_window):
            self.hide()

    def hide(self) -> None:
        self._hide_submenu()
        if self.window:
            try:
                self.window.grab_release()
                self.window.destroy()
            except Exception:
                pass
            self.window = None


class FloatWindow:
    """桌宠悬浮窗：置顶、透明、可拖拽，支持右键菜单与点击互动
    依赖：
        - 优先使用 pywin32 设置层叠透明；缺失时降级为 Tkinter attributes
    """

    def __init__(
        self,
        root: tk.Tk,
        username: str,
        pet_frames_path: str,
        tracker: RuntimeTracker,
        data_manager: Optional[DataManager] = None,
        on_back_home: Optional[Callable[[], None]] = None,
        on_change_pet: Optional[Callable[[], None]] = None,
        on_switched_pet: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.root = root
        self.username = username
        self.frames_path = pet_frames_path
        self.tracker = tracker
        self.dm = data_manager
        self.on_back_home = on_back_home
        self.on_change_pet = on_change_pet
        self.on_switched_pet = on_switched_pet

        # 问候模式状态
        self.warm_greetings_enabled = False
        self._greeting_timer: Optional[str] = None
        self._greeting_win: Optional[tk.Toplevel] = None

        self.top = tk.Toplevel(self.root)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)
        # 降级透明背景（Windows 上可用）
        try:
            self.top.wm_attributes("-transparentcolor", "#00FEFE")
            bg = "#00FEFE"
        except Exception:
            self.top.attributes("-alpha", 0.98)
            bg = "#000000"
        self.top.configure(bg=bg)

        self.animator = PetAnimator(pet_frames_path, scale=5)
        
        self.canvas = tk.Canvas(self.top, width=self.animator.w, height=self.animator.h, highlightthickness=0, bg=bg)
        self.canvas.pack()

        # 设置初始位置为屏幕右下角
        try:
            screen_w = self.top.winfo_screenwidth()
            screen_h = self.top.winfo_screenheight()
            # 留出一定边距，避免紧贴任务栏
            margin_right = 50
            margin_bottom = 80
            
            init_x = screen_w - self.animator.w - margin_right
            init_y = screen_h - self.animator.h - margin_bottom
            
            # 确保坐标不小于0
            init_x = max(0, init_x)
            init_y = max(0, init_y)
            
            self.top.geometry(f"+{init_x}+{init_y}")
        except Exception:
            pass

        self._photo = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._win_start_x = 0
        self._win_start_y = 0
        self._is_dragging = False
        self._bind_events()
        self._setup_win32_layer()

        # 开始计时
        self.tracker.start(username, self._pet_name_from_path(pet_frames_path))
        # 驱动动画与刷新
        self._tick()

    def _pet_name_from_path(self, frames_path: str) -> str:
        """根据帧路径推断宠物名称（优先通过配置映射，其次用文件名）"""
        try:
            import os
            norm = os.path.normpath(frames_path).lower()
            # 优先通过配置反查名称
            if self.dm:
                pets_cfg = self.dm.get_pets()
                for name, cfg in pets_cfg.items():
                    p = os.path.normpath(cfg.get("frames", "")).lower()
                    if p == norm:
                        return name
            # 回退：使用文件名（兼容 Windows 路径分隔符）
            base = os.path.basename(norm)
            base_no_ext = base.split(".")[0]
            # 针对几款内置中文名做映射
            if "dog" in base_no_ext:
                return "像素小狗"
            if "cat" in base_no_ext:
                return "像素小猫"
            if "rabbit" in base_no_ext:
                return "像素兔子"
            if "dragon" in base_no_ext:
                # 这里可能是黄金像素龙或星河小龙，仍旧由配置映射更可靠
                return "黄金像素龙"
            return base_no_ext
        except Exception:
            return frames_path

    def _bind_events(self) -> None:
        """绑定鼠标事件与右键菜单"""
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        # self.canvas.bind("<Button-1>", lambda e: self.animator.interact_random())
        self.canvas.bind("<Button-3>", self._show_menu)

    def _update_menu(self) -> None:
        """动态更新菜单项，生成更换桌宠的子菜单"""
        # 获取已解锁宠物列表
        submenu_items = []
        if self.dm:
            try:
                user = self.dm.get_user(self.username) or {}
                unlocked = user.get("unlocked_pets", [])
                pets_cfg = self.dm.get_pets()
                
                # 当前宠物名称
                current_pet = self._pet_name_from_path(self.frames_path)
                
                for name in unlocked:
                    cfg = pets_cfg.get(name)
                    if not cfg: continue
                    
                    frames_path = cfg.get("frames", "")
                    # 检查是否是当前宠物（用于打钩）
                    # 这里对比 frames_path 可能更准确，或者对比名字
                    # _pet_name_from_path 返回的是中文名，而 unlocked 存的是 key
                    # 假设 unlocked 里的 key 对应 pets_cfg 的 key
                    
                    # 为了确保名称匹配正确，我们重新反推一下中文名，或者直接用 key
                    # 这里 _pet_name_from_path 逻辑有点硬编码，我们尽量用 key 显示
                    
                    is_current = (frames_path == self.frames_path)
                    
                    submenu_items.append({
                        "label": name,
                        "command": lambda n=name, p=frames_path: self._switch_pet(n, p),
                        "checked": is_current
                    })
            except Exception:
                pass
        
        # 如果没有获取到（比如没传 dm），回退到旧逻辑（虽然后面代码是 submenu）
        if not submenu_items:
             # 仅作为 fallback，实际应都有
             submenu_items.append({"label": "无可用宠物", "command": None})

        self.menu = PixelContextMenu(self.top, [
            {"label": "返回主页面", "command": self._back_home},
            {"label": "更换桌宠", "submenu": submenu_items},
            {"label": "投喂", "submenu": self._build_feed_submenu()},
            {"separator": True},
            {"label": "关闭悬浮窗", "command": self.close},
        ])

    def _switch_pet(self, name: str, frames_path: str) -> None:
        """原地切换桌宠"""
        if frames_path == self.frames_path:
            return
            
        # 1. 停止当前动画与计时
        # self.tracker.stop() # 不完全停止，只是换个名字继续记？
        # RuntimeTracker 的 start 会更新 current pet name
        
        # 2. 更新属性
        self.frames_path = frames_path
        
        # 3. 重置动画器
        self.animator = PetAnimator(frames_path, scale=5)
        
        # 4. 调整画布与窗口尺寸
        # 注意：如果尺寸变化很大，可能需要重新计算位置居中？
        # 这里简单起见，保持左上角位置不变，或者调整 geometry
        self.canvas.configure(width=self.animator.w, height=self.animator.h)
        
        # 5. 重启计时（切换归属）
        self.tracker.start(self.username, self._pet_name_from_path(frames_path))
        
        # 6. 强制刷新一帧
        self._tick_manual()

        # 7. 通知外部已切换
        if self.on_switched_pet:
            self.on_switched_pet(name)

    def _build_feed_submenu(self) -> list:
        """构建投喂子菜单"""
        items = []
        if self.dm:
            try:
                user = self.dm.get_user(self.username) or {}
                inv = dict(user.get("inventory", {}))
                for n, q in inv.items():
                    if int(q) > 0:
                        items.append({
                            "label": f"{n} x{int(q)}",
                            "command": (lambda name=n: self._feed_item(name))
                        })
            except Exception:
                pass
        if not items:
            items.append({"label": "粮仓为空", "command": None})
        return items

    def _feed_item(self, item_name: str) -> None:
        """投喂指定粮食并触发爱心动画"""
        if not self.dm:
            return
        ok = False
        try:
            ok = self.dm.consume_inventory_item(self.username, item_name, 1)
        except Exception:
            ok = False
        if ok:
            self._bubble_hearts(6)
        else:
            try:
                from tkinter import messagebox
                messagebox.showinfo("提示", "该粮食不足或不存在")
            except Exception:
                pass

    def _bubble_hearts(self, count: int = 5) -> None:
        """在桌宠上方显示像素爱心冒泡动画"""
        w = self.animator.w
        h = self.animator.h
        for _ in range(max(1, int(count))):
            x = random.randint(w // 4, (w * 3) // 4)
            y = random.randint(h // 3, (h * 2) // 3)
            ids = self._create_pixel_heart(x, y, scale=2)
            self._animate_hearts(ids, steps=24)

    def _create_pixel_heart(self, x: int, y: int, scale: int = 2) -> list:
        """在给定位置创建像素爱心并返回 Canvas 元素 ID 列表"""
        pixels = [
            (1,0),(2,0),(3,0),(4,0),(5,0),
            (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),
            (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
            (1,3),(2,3),(3,3),(4,3),(5,3),
            (2,4),(3,4),(4,4),
            (3,5)
        ]
        ids = []
        for px, py in pixels:
            rx0 = x + px * scale
            ry0 = y + py * scale
            rx1 = rx0 + scale
            ry1 = ry0 + scale
            ids.append(self.canvas.create_rectangle(rx0, ry0, rx1, ry1, fill="#FF4D6D", outline=""))
        return ids

    def _animate_hearts(self, ids: list, steps: int = 20) -> None:
        """以向上漂浮的方式动画显示像素爱心"""
        if not ids:
            return
        def step(i: int) -> None:
            if i >= steps:
                for cid in ids:
                    try:
                        self.canvas.delete(cid)
                    except Exception:
                        pass
                return
            dy = -2
            dx = random.choice([-1,0,1])
            for cid in ids:
                try:
                    self.canvas.move(cid, dx, dy)
                except Exception:
                    pass
            self.top.after(50, lambda: step(i+1))
        step(0)

    def _tick_manual(self) -> None:
        """手动刷新一帧（非递归，用于切换时立即更新）"""
        self.animator.next_frame()
        self._photo = self.animator.get_tk_image()
        self.canvas.configure(width=self.animator.w, height=self.animator.h)
        self.canvas.create_image(0, 0, image=self._photo, anchor="nw")

    def _setup_win32_layer(self) -> None:
        """通过 pywin32 设置层叠与置顶（若可用）"""
        if win32gui is None or win32con is None:
            return
        try:
            hwnd = self.top.winfo_id()
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
            # 使用近全透明的关键色（与 bg 一致），实现不规则窗口
            # 颜色格式：RGB，Alpha 忽略；此处选择青色 0x00FEFE
            # SetLayeredWindowAttributes 需要 COLORREF (0x00BBGGRR)
            # 对应 #00FEFE (R=0, G=254, B=254) -> 0xFEFE00
            win32gui.SetLayeredWindowAttributes(hwnd, 0xFEFE00, 255, win32con.LWA_COLORKEY)
        except Exception:
            # 失败则保持 Tkinter 属性，不影响功能
            pass

    def _on_press(self, event: tk.Event) -> None:
        """记录拖拽起点：保存初始屏幕坐标与窗口位置"""
        self._is_dragging = False
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._win_start_x = self.top.winfo_x()
        self._win_start_y = self.top.winfo_y()

    def _on_drag(self, event: tk.Event) -> None:
        """跟随鼠标移动窗口位置
        
        性能优化：使用屏幕绝对坐标差值 (Delta) 计算新位置，
        完全消除相对坐标偏移可能导致的漂移或抖动问题。
        """
        # 计算位移量
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        
        # 增加防抖阈值（3像素），区分点击与拖拽
        if not self._is_dragging:
            if abs(dx) > 3 or abs(dy) > 3:
                self._is_dragging = True
        
        if self._is_dragging:
            # 应用位移到初始窗口位置
            new_x = self._win_start_x + dx
            new_y = self._win_start_y + dy
            self.top.geometry(f"+{new_x}+{new_y}")

            # 同步移动问候气泡
            if self._greeting_win:
                try:
                    bw = self._greeting_win.winfo_width()
                    bh = self._greeting_win.winfo_height()
                    ww = self.top.winfo_width()
                    wh = self.top.winfo_height()
                    
                    bx = new_x + (ww - bw) // 2
                    by = new_y - bh - 10
                    
                    if bx < 0: bx = 0
                    if by < 0: by = new_y + wh + 10
                    
                    self._greeting_win.geometry(f"+{bx}+{by}")
                except Exception:
                    pass

    def _on_release(self, event: tk.Event) -> None:
        """释放拖拽：若未触发拖拽则视为点击互动"""
        if not self._is_dragging:
            self.animator.interact_random()
        self._is_dragging = False

    def _show_menu(self, event: tk.Event) -> None:
        """显示右键菜单"""
        self._update_menu()  # 每次显示前重新构建菜单，确保选中状态正确
        self.menu.show(event.x_root, event.y_root)

    def _back_home(self) -> None:
        """返回主页面：仅调用回调，不关闭悬浮窗"""
        if self.on_back_home:
            self.on_back_home()

    def _change_pet(self) -> None:
        """更换桌宠：关闭悬浮窗并调用回调（由主页处理具体选择）"""
        self.close()
        if self.on_change_pet:
            self.on_change_pet()

    def _tick(self) -> None:
        """定时刷新动画与画布显示"""
        self.animator.next_frame()
        self._photo = self.animator.get_tk_image()
        self.canvas.configure(width=self.animator.w, height=self.animator.h)
        self.canvas.create_image(0, 0, image=self._photo, anchor="nw")
        self.top.after(120, self._tick)

    def close(self) -> None:
        """关闭悬浮窗并停止计时"""
        self._cancel_greeting()
        self.tracker.stop()
        try:
            self.top.destroy()
        except Exception:
            pass

    def update_settings(self, settings: dict) -> None:
        """更新配置"""
        self.warm_greetings_enabled = settings.get("warm_greetings", False)
        if self.warm_greetings_enabled:
            # 如果没有正在运行的计时器，则启动
            if not self._greeting_timer:
                self._schedule_next_greeting()
        else:
            self._cancel_greeting()

    def _schedule_next_greeting(self) -> None:
        """安排下一次问候"""
        if self._greeting_timer:
            try:
                self.top.after_cancel(self._greeting_timer)
            except Exception:
                pass
            self._greeting_timer = None
            
        if not self.warm_greetings_enabled:
            return
            
        # 随机间隔 30~60秒 (演示用，实际可调长)
        delay = random.randint(30000, 60000)
        self._greeting_timer = self.top.after(delay, self._show_greeting)

    def _cancel_greeting(self) -> None:
        """取消问候计划与当前窗口"""
        if self._greeting_timer:
            try:
                self.top.after_cancel(self._greeting_timer)
            except Exception:
                pass
            self._greeting_timer = None
        if self._greeting_win:
            try:
                self._greeting_win.destroy()
            except Exception:
                pass
            self._greeting_win = None

    def _show_greeting(self) -> None:
        """显示问候气泡"""
        if not self.warm_greetings_enabled:
            return
            
        # 如果已有气泡，先关闭
        if self._greeting_win:
            try:
                self._greeting_win.destroy()
            except Exception:
                pass

        msgs = [
            "主人，记得喝水哦！",
            "坐久了，起来活动一下吧~",
            "今天心情怎么样？",
            "不论发生什么，我都在你身边。",
            "要注意保护眼睛哦！",
            "休息一下，眺望远方吧~",
            "工作/学习辛苦啦，加油！"
        ]
        msg = random.choice(msgs)

        # 创建气泡窗口
        try:
            win = tk.Toplevel(self.top)
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            
            # 样式
            bg = "#FFFFE0" # 浅黄
            fg = "#333"
            
            # 容器
            frame = tk.Frame(win, bg=bg, highlightbackground="#FFD700", highlightthickness=1)
            frame.pack(fill="both", expand=True)
            
            tk.Label(frame, text=msg, bg=bg, fg=fg, font=("微软雅黑", 10), padx=10, pady=10).pack()
            
            btn_frame = tk.Frame(frame, bg=bg)
            btn_frame.pack(fill="x", pady=(0, 5))
            
            # 交互按钮
            def on_reply():
                self._close_greeting()
                
            tk.Button(btn_frame, text="谢谢", command=on_reply, bg="#FFD700", relief="flat", font=("微软雅黑", 8), width=6).pack(side="left", padx=10)
            tk.Button(btn_frame, text="关闭", command=self._close_greeting, bg="#ddd", relief="flat", font=("微软雅黑", 8), width=6).pack(side="right", padx=10)
            
            # 计算位置（在宠物上方）
            win.update_idletasks()
            bw = win.winfo_reqwidth()
            bh = win.winfo_reqheight()
            
            wx = self.top.winfo_x()
            wy = self.top.winfo_y()
            ww = self.top.winfo_width()
            
            bx = wx + (ww - bw) // 2
            by = wy - bh - 10
            
            # 简单的边界检查
            screen_w = self.top.winfo_screenwidth()
            screen_h = self.top.winfo_screenheight()
            if bx < 0: bx = 0
            if by < 0: by = wy + self.top.winfo_height() + 10 # 如果上方不够，放下方
            
            win.geometry(f"{bw}x{bh}+{bx}+{by}")
            self._greeting_win = win
            
        except Exception:
            pass
        
    def _close_greeting(self) -> None:
        """关闭气泡并计划下一次"""
        if self._greeting_win:
            try:
                self._greeting_win.destroy()
            except Exception:
                pass
            self._greeting_win = None
        self._schedule_next_greeting()
