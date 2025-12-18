import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

class SettingsView(tk.Frame):
    """设置页面：管理应用配置与偏好"""

    def __init__(self, master: tk.Misc, controller, dm) -> None:
        super().__init__(master, bg="#222")
        self.controller = controller
        self.dm = dm
        self._build_ui()

    def _build_ui(self) -> None:
        """构建设置页布局"""
        # 标题栏
        head = tk.Frame(self, bg="#222")
        head.pack(fill="x", pady=20)
        tk.Label(head, text="设置", fg="#fff", bg="#222", font=("微软雅黑", 16, "bold")).pack()

        # 内容区域
        content = tk.Frame(self, bg="#222")
        content.pack(fill="both", expand=True, padx=40, pady=20)

        # 嘘寒问暖模式开关
        self.var_warm_greetings = tk.BooleanVar(value=False)
        
        # 自定义样式的复选框容器
        chk_frame = tk.Frame(content, bg="#333", padx=15, pady=15)
        chk_frame.pack(fill="x", pady=10)
        
        chk = tk.Checkbutton(
            chk_frame,
            text="开启嘘寒问暖模式",
            variable=self.var_warm_greetings,
            bg="#333",
            fg="#fff",
            selectcolor="#444",
            activebackground="#333",
            activeforeground="#fff",
            font=("微软雅黑", 12),
            command=self._on_setting_change
        )
        chk.pack(side="left")
        
        tk.Label(
            chk_frame, 
            text="（开启后，桌宠会不时向您发送问候）", 
            fg="#aaa", 
            bg="#333",
            font=("微软雅黑", 10)
        ).pack(side="left", padx=10)

        # 底部按钮
        foot = tk.Frame(self, bg="#222")
        foot.pack(fill="x", pady=20, side="bottom")
        
        btn_back = tk.Button(
            foot, 
            text="返回主页", 
            command=lambda: self.controller.show("home"),
            bg="#555",
            fg="#fff",
            relief="flat",
            font=("微软雅黑", 10),
            width=15
        )
        btn_back.pack(pady=10)

    def on_show(self) -> None:
        """显示时加载当前配置"""
        username = self.controller.current_user
        if not username:
            return
            
        user = self.dm.get_user(username) or {}
        settings = user.get("settings", {})
        
        # 加载各项配置
        self.var_warm_greetings.set(settings.get("warm_greetings", False))

    def _on_setting_change(self) -> None:
        """配置变更时立即保存并生效"""
        username = self.controller.current_user
        if not username:
            return
            
        new_settings = {
            "warm_greetings": self.var_warm_greetings.get()
        }
        
        # 1. 更新数据库
        # 注意：这里需要合并更新，避免覆盖其他潜在设置
        # 但目前 DataManager.enqueue_user_update 支持 patch
        # 为了简单起见，我们直接获取 full user 对象更新 settings 字段
        
        user = self.dm.get_user(username) or {}
        # 确保 settings 也是合并更新
        current_settings = user.get("settings", {})
        current_settings.update(new_settings)
        user["settings"] = current_settings
        
        self.dm.upsert_user(username, user)
        
        # 2. 通知控制器应用新配置
        self.controller.apply_settings(current_settings)
