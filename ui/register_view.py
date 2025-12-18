import tkinter as tk

from core.account import AccountManager
from core.data_manager import DataManager


class RegisterView(tk.Frame):
    """注册页面：用户名/密码/确认/密保问题及答案"""

    def __init__(self, master: tk.Misc, controller, dm: DataManager, am: AccountManager) -> None:
        super().__init__(master, bg="#222")
        self.controller = controller
        self.dm = dm
        self.am = am
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_var = tk.StringVar()
        self.question_var = tk.StringVar(value="你的生日？")
        self.answer_var = tk.StringVar()
        self._build_ui()

    def _build_ui(self) -> None:
        """构建注册界面控件"""
        tk.Label(self, text="注册", fg="#fff", bg="#222", font=("Consolas", 18)).pack(pady=12)
        form = tk.Frame(self, bg="#222")
        form.pack(pady=8)
        tk.Label(form, text="用户名", fg="#ddd", bg="#222").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.username_var).grid(row=0, column=1, padx=6, pady=4)
        tk.Label(form, text="密码", fg="#ddd", bg="#222").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=6, pady=4)
        tk.Label(form, text="确认密码", fg="#ddd", bg="#222").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.confirm_var, show="*").grid(row=2, column=1, padx=6, pady=4)
        tk.Label(form, text="密保问题", fg="#ddd", bg="#222").grid(row=3, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.question_var).grid(row=3, column=1, padx=6, pady=4)
        tk.Label(form, text="密保答案", fg="#ddd", bg="#222").grid(row=4, column=0, sticky="e", padx=6, pady=4)
        tk.Entry(form, textvariable=self.answer_var).grid(row=4, column=1, padx=6, pady=4)

        btns = tk.Frame(self, bg="#222")
        btns.pack(pady=10)
        tk.Button(btns, text="提交注册", command=self._on_submit).grid(row=0, column=0, padx=6)
        tk.Button(btns, text="返回登录", command=lambda: self.controller.show("login")).grid(row=0, column=1, padx=6)
        self.msg = tk.Label(self, text="", fg="#ffb", bg="#222")
        self.msg.pack(pady=6)

    def _on_submit(self) -> None:
        """处理注册逻辑，成功后返回登录页面"""
        ok, msg = self.am.register_user(
            self.username_var.get(),
            self.password_var.get(),
            self.confirm_var.get(),
            self.question_var.get(),
            self.answer_var.get(),
        )
        self.msg.configure(text=msg)
        if ok:
            self.controller.show("login")

