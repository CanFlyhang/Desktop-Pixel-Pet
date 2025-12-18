import tkinter as tk

from core.account import AccountManager
from core.data_manager import DataManager


class RecoverView(tk.Frame):
    """找回密码页面：用户名/密保问题展示/答案/新密码与确认"""

    def __init__(self, master: tk.Misc, controller, dm: DataManager, am: AccountManager) -> None:
        super().__init__(master, bg="#222")
        self.controller = controller
        self.dm = dm
        self.am = am
        self.username_var = tk.StringVar()
        self.question_var = tk.StringVar(value="")
        self.answer_var = tk.StringVar()
        self.new_pwd_var = tk.StringVar()
        self.confirm_var = tk.StringVar()
        self._build_ui()

    def _build_ui(self) -> None:
        """构建找回密码界面控件"""
        tk.Label(self, text="找回密码", fg="#fff", bg="#222", font=("Consolas", 18)).pack(pady=12)
        form = tk.Frame(self, bg="#222")
        form.pack(pady=8)
        tk.Label(form, text="用户名", fg="#ddd", bg="#222").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.username_var).grid(row=0, column=1, padx=6, pady=4)
        tk.Button(form, text="加载密保问题", command=self._load_question).grid(row=0, column=2, padx=6, pady=4)

        tk.Label(form, text="密保问题", fg="#ddd", bg="#222").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        tk.Label(form, textvariable=self.question_var, fg="#ddd", bg="#222").grid(row=1, column=1, sticky="w", padx=6, pady=4)
        tk.Label(form, text="密保答案", fg="#ddd", bg="#222").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.answer_var).grid(row=2, column=1, padx=6, pady=4)
        tk.Label(form, text="新密码", fg="#ddd", bg="#222").grid(row=3, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.new_pwd_var, show="*").grid(row=3, column=1, padx=6, pady=4)
        tk.Label(form, text="确认新密码", fg="#ddd", bg="#222").grid(row=4, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.confirm_var, show="*").grid(row=4, column=1, padx=6, pady=4)

        btns = tk.Frame(self, bg="#222")
        btns.pack(pady=10)
        tk.Button(btns, text="重置密码", command=self._on_reset).grid(row=0, column=0, padx=6)
        tk.Button(btns, text="返回登录", command=lambda: self.controller.show("login")).grid(row=0, column=1, padx=6)
        self.msg = tk.Label(self, text="", fg="#ffb", bg="#222")
        self.msg.pack(pady=6)

    def _load_question(self) -> None:
        """加载并展示密保问题"""
        q = self.am.get_security_question(self.username_var.get())
        self.question_var.set(q or "用户不存在")

    def _on_reset(self) -> None:
        """处理找回密码逻辑"""
        ok, msg = self.am.recover_password(
            self.username_var.get(),
            self.answer_var.get(),
            self.new_pwd_var.get(),
            self.confirm_var.get(),
        )
        self.msg.configure(text=msg)
        if ok:
            self.controller.show("login")

