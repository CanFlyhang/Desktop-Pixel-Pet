import os
import tkinter as tk
from typing import Dict, List, Optional

from core.data_manager import DataManager
from core.runtime_tracker import RuntimeTracker
from core.pet import PetAnimator
from core.float_window import FloatWindow


class HomeView(tk.Frame):
    """主页：显示用户名与总运行时间，展示已解锁宠物网格与操作按钮"""

    def __init__(self, master: tk.Misc, controller, dm: DataManager, tracker: RuntimeTracker) -> None:
        super().__init__(master, bg="#222")
        self.controller = controller
        self.dm = dm
        self.tracker = tracker
        self.selected_pet: Optional[str] = None
        self._grid_items: List[tk.Frame] = []
        self._photo_cache: Dict[str, tk.PhotoImage] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """构建主页布局"""
        head = tk.Frame(self, bg="#222")
        head.pack(fill="x", pady=8)
        self.user_label = tk.Label(head, text="用户：-", fg="#fff", bg="#222")
        self.user_label.pack(side="left", padx=12)
        self.time_label = tk.Label(head, text="总时间：00:00:00", fg="#fff", bg="#222")
        self.time_label.pack(side="right", padx=12)

        # 中间滚动区域容器
        mid_container = tk.Frame(self, bg="#222")
        mid_container.pack(fill="both", expand=True, padx=12, pady=8)

        # 创建 Canvas 和 Scrollbar
        self.canvas = tk.Canvas(mid_container, bg="#222", highlightthickness=0)
        scrollbar = tk.Scrollbar(mid_container, orient="vertical", command=self.canvas.yview)
        
        # 放置 Scrollbar 和 Canvas
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # 关联 Canvas 和 Scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # 创建内容网格 Frame (放在 Canvas 中)
        self.grid = tk.Frame(self.canvas, bg="#222")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid, anchor="nw")

        # 绑定事件以更新滚动区域
        self.grid.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        foot = tk.Frame(self, bg="#222")
        foot.pack(fill="x", pady=8)
        self.btn_float = tk.Button(foot, text="选择为悬浮窗", command=self._start_float, state="disabled")
        self.btn_float.pack(side="left", padx=8)
        tk.Button(foot, text="进入商城", command=lambda: self.controller.show("mall")).pack(side="left", padx=8)
        tk.Button(foot, text="粮仓", command=lambda: self.controller.show("inventory")).pack(side="left", padx=8)
        tk.Button(foot, text="账户", command=lambda: self.controller.show("account")).pack(side="left", padx=8)
        tk.Button(foot, text="设置", command=lambda: self.controller.show("settings")).pack(side="left", padx=8)
        tk.Button(foot, text="退出登录", command=self.controller.logout).pack(side="right", padx=8)

    def _on_frame_configure(self, event) -> None:
        """当网格内容变化时，更新 Canvas 滚动范围"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        """当 Canvas 大小变化时，调整网格宽度以匹配"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        """鼠标滚轮滚动"""
        # 只有当内容超出可视区域时才滚动
        if self.grid.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_show(self) -> None:
        """页面显示时刷新数据与网格"""
        # 绑定鼠标滚轮
        try:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        except Exception:
            pass

        username = self.controller.current_user
        self.user_label.configure(text=f"用户：{username}")
        user = self.dm.get_user(username)
        total = int(user.get("total_run_time", 0)) if user else 0
        self.time_label.configure(text=f"总时间：{RuntimeTracker.format_hms(total)}")
        self._render_grid()
        # 订阅计时器以更新时间显示
        self.tracker.subscribe(lambda t, _: self.time_label.configure(text=f"总时间：{RuntimeTracker.format_hms(t)}"))

    def on_hide(self) -> None:
        """页面隐藏时解绑事件"""
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass

    def _render_grid(self) -> None:
        """渲染已解锁宠物网格"""
        for it in self._grid_items:
            try:
                it.destroy()
            except Exception:
                pass
        self._grid_items.clear()

        username = self.controller.current_user
        user = self.dm.get_user(username) or {}
        unlocked = user.get("unlocked_pets", [])
        pet_times: Dict[str, int] = user.get("pet_run_time", {})
        pets_cfg = self.dm.get_pets()
        names = list(unlocked)
        cols = 3
        
        # 定义选中与未选中的样式常量
        STYLE_SELECTED = {
            "border_color": "#FFD700",  # 金色边框
            "border_width": 3,
            "btn_text": "取消选中",
            "btn_bg": "#FFD700",
            "btn_fg": "#000000",
            "btn_state": "normal"
        }
        STYLE_NORMAL = {
            "border_color": "#444444",  # 深灰边框
            "border_width": 1,
            "btn_text": "选中",
            "btn_bg": "#555555",
            "btn_fg": "#ffffff",
            "btn_state": "normal"
        }

        for i, name in enumerate(names):
            is_selected = (name == self.selected_pet)
            style = STYLE_SELECTED if is_selected else STYLE_NORMAL
            
            # 外层容器充当边框
            container = tk.Frame(
                self.grid, 
                bg=style["border_color"], 
                padx=style["border_width"], 
                pady=style["border_width"]
            )
            container.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="nsew")
            self._grid_items.append(container)
            
            # 内层内容容器
            fr = tk.Frame(container, bg="#333")
            fr.pack(fill="both", expand=True)
            
            # 预览图
            frames_path = pets_cfg.get(name, {}).get("frames", "")
            try:
                preview = self._get_preview(name, frames_path)
                tk.Label(fr, image=preview, bg="#333").pack(pady=8)
            except Exception:
                tk.Label(fr, text="[预览失败]", fg="#f99", bg="#333").pack(pady=8)
            
            # 文本信息
            tk.Label(fr, text=name, fg="#fff", bg="#333", font=("微软雅黑", 10, "bold")).pack()
            tk.Label(fr, text=f"累计：{RuntimeTracker.format_hms(int(pet_times.get(name, 0)))}", fg="#ccc", bg="#333", font=("Arial", 9)).pack(pady=(0, 4))
            
            # 选择按钮
            btn = tk.Button(
                fr, 
                text=style["btn_text"], 
                bg=style["btn_bg"], 
                fg=style["btn_fg"],
                activebackground=style["btn_bg"],
                activeforeground=style["btn_fg"],
                state=style["btn_state"],
                relief="flat",
                command=lambda n=name: self._select_pet(n)
            )
            btn.pack(pady=8, ipadx=10)

        # 扩展网格权重
        for c in range(cols):
            self.grid.grid_columnconfigure(c, weight=1)

    def _get_preview(self, name: str, frames_path: str) -> tk.PhotoImage:
        """生成或取缓存的预览 PhotoImage"""
        if name in self._photo_cache:
            return self._photo_cache[name]
        pa = PetAnimator(frames_path, scale=3)
        img = pa.get_tk_image()
        self._photo_cache[name] = img
        return img

    def _select_pet(self, name: str) -> None:
        """选中或取消选中指定宠物"""
        if self.selected_pet == name:
            self.selected_pet = None
            self.btn_float.configure(state="disabled")
        else:
            self.selected_pet = name
            self.btn_float.configure(state="normal")
        self._render_grid()

    def set_selection(self, name: str) -> None:
        """强制选中指定宠物（用于外部同步）"""
        self.selected_pet = name
        self.btn_float.configure(state="normal")
        self._render_grid()

    def _start_float(self) -> None:
        """以所选桌宠启动悬浮窗"""
        if not self.selected_pet:
            return
            
        pets_cfg = self.dm.get_pets()
        frames_path = pets_cfg.get(self.selected_pet, {}).get("frames", "")
        
        # 如果已存在悬浮窗
        if self.controller.float_window:
            # 检查窗口是否存活
            is_alive = False
            try:
                if self.controller.float_window.top.winfo_exists():
                    is_alive = True
            except Exception:
                pass

            if is_alive:
                # 若是同一个宠物，则仅置顶提示，不重新创建（避免位置重置）
                current_path = getattr(self.controller.float_window, "frames_path", "")
                if os.path.normpath(current_path) == os.path.normpath(frames_path):
                    try:
                        self.controller.float_window.top.lift()
                    except Exception:
                        pass
                    return

                try:
                    self.controller.float_window.close()
                except Exception:
                    pass
            # 如果窗口已销毁但对象还在，直接创建新的覆盖之
        
        try:
            self.controller.float_window = FloatWindow(
                root=self.controller.root,
                username=self.controller.current_user,
                pet_frames_path=frames_path,
                tracker=self.tracker,
                data_manager=self.dm,
                on_back_home=lambda: self.controller.show("home"),
                on_change_pet=lambda: self.controller.show("home"),
                on_switched_pet=self.set_selection,
            )
            
            # 立即应用用户配置
            user = self.dm.get_user(self.controller.current_user)
            if user:
                self.controller.apply_settings(user.get("settings", {}))
                
        except Exception as e:
            try:
                from tkinter import messagebox
                messagebox.showerror("错误", f"无法启动悬浮窗：{e}")
            except Exception:
                pass
