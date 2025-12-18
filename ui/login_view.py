import json
import os
import tkinter as tk
from typing import Optional

from core.account import AccountManager
from core.data_manager import DataManager


class LoginView(tk.Frame):
    """登录页面：用户名/密码/记住密码，登录/注册/找回按钮"""

    def __init__(self, master: tk.Misc, controller, dm: DataManager, am: AccountManager) -> None:
        super().__init__(master, bg="#222")
        self.controller = controller
        self.dm = dm
        self.am = am
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar(value=True)
        self._build_ui()
        self._load_saved()

    def _build_ui(self) -> None:
        """构建登录界面控件"""
        tk.Label(self, text="登录", fg="#fff", bg="#222", font=("Consolas", 18)).pack(pady=12)
        form = tk.Frame(self, bg="#222")
        form.pack(pady=8)
        tk.Label(form, text="用户名", fg="#ddd", bg="#222").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.username_var).grid(row=0, column=1, padx=6, pady=4)
        tk.Label(form, text="密码", fg="#ddd", bg="#222").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=6, pady=4)
        tk.Checkbutton(form, text="记住密码", variable=self.remember_var, fg="#ddd", bg="#222").grid(row=2, column=1, sticky="w", padx=6, pady=4)

        btns = tk.Frame(self, bg="#222")
        btns.pack(pady=10)
        tk.Button(btns, text="登录", command=self._on_login).grid(row=0, column=0, padx=6)
        tk.Button(btns, text="注册", command=lambda: self.controller.show("register")).grid(row=0, column=1, padx=6)
        tk.Button(btns, text="找回密码", command=lambda: self.controller.show("recover")).grid(row=0, column=2, padx=6)
        tk.Button(btns, text="数据更新", command=lambda: self.controller.show("update")).grid(row=0, column=3, padx=6)
        self.msg = tk.Label(self, text="", fg="#ffb", bg="#222")
        self.msg.pack(pady=6)

    def _on_login(self) -> None:
        """处理登录逻辑，并根据记住密码选项保存配置"""
        ok, msg = self.am.login(self.username_var.get(), self.password_var.get())
        self.msg.configure(text=msg)
        if not ok:
            return
        if self.remember_var.get():
            self._save_creds(self.username_var.get(), self.password_var.get())
        self.controller.set_current_user(self.username_var.get())
        self.controller.show("home")

    def _save_creds(self, username: str, password: str) -> None:
        """保存登录凭据到 data/config.json（本地化用途）"""
        cfg_path = os.path.join("data", "config.json")
        os.makedirs("data", exist_ok=True)
        cfg = {"username": username, "password": password}
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def on_show(self) -> None:
        """页面显示时清理状态消息"""
        self.msg.configure(text="")

    def _load_saved(self) -> None:
        """尝试加载已保存的用户名与密码"""
        cfg_path = os.path.join("data", "config.json")
        if not os.path.exists(cfg_path):
            return
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.username_var.set(cfg.get("username", ""))
            self.password_var.set(cfg.get("password", ""))
        except Exception:
            pass

