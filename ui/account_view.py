import tkinter as tk

from core.data_manager import DataManager
from core.runtime_tracker import RuntimeTracker
from core.license_manager import LicenseManager


class AccountView(tk.Frame):
    """账户视图：支持提现（生成卡密）与充值（校验卡密）"""

    def __init__(self, master: tk.Misc, controller, dm: DataManager) -> None:
        super().__init__(master, bg="#222")
        self.controller = controller
        self.dm = dm
        self._build_ui()

    def _build_ui(self) -> None:
        """构建账户页面控件"""
        head = tk.Frame(self, bg="#222")
        head.pack(fill="x", pady=8)
        tk.Label(head, text="账户：提现 / 充值", fg="#fff", bg="#222").pack(side="left", padx=12)
        tk.Button(head, text="返回主页", command=lambda: self.controller.show("home")).pack(side="right", padx=12)

        body = tk.Frame(self, bg="#222")
        body.pack(fill="both", expand=True, padx=12, pady=8)

        # 提现区域
        withdraw = tk.LabelFrame(body, text="提现（生成充值卡密）", fg="#fff", bg="#222")
        withdraw.pack(fill="x", pady=8)

        tk.Label(withdraw, text="目标用户名", fg="#ddd", bg="#222").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.to_user_var = tk.StringVar()
        tk.Entry(withdraw, textvariable=self.to_user_var).grid(row=0, column=1, padx=6, pady=4)

        tk.Label(withdraw, text="扣除时间（秒）", fg="#ddd", bg="#222").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.seconds_var = tk.StringVar(value="60")
        tk.Entry(withdraw, textvariable=self.seconds_var).grid(row=1, column=1, padx=6, pady=4)

        self.key_out_var = tk.StringVar(value="")
        tk.Button(withdraw, text="生成卡密", command=self._on_withdraw).grid(row=2, column=0, padx=6, pady=6)
        tk.Entry(withdraw, textvariable=self.key_out_var, width=48).grid(row=2, column=1, padx=6, pady=6)

        # 充值区域
        recharge = tk.LabelFrame(body, text="充值（使用卡密）", fg="#fff", bg="#222")
        recharge.pack(fill="x", pady=8)

        tk.Label(recharge, text="来源用户名", fg="#ddd", bg="#222").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.from_user_var = tk.StringVar()
        tk.Entry(recharge, textvariable=self.from_user_var).grid(row=0, column=1, padx=6, pady=4)

        tk.Label(recharge, text="充值卡密", fg="#ddd", bg="#222").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.key_in_var = tk.StringVar()
        tk.Entry(recharge, textvariable=self.key_in_var, width=48).grid(row=1, column=1, padx=6, pady=4)

        tk.Button(recharge, text="充值到账户", command=self._on_recharge).grid(row=2, column=0, padx=6, pady=6)
        self.msg_var = tk.StringVar(value="")
        tk.Label(recharge, textvariable=self.msg_var, fg="#ffb", bg="#222").grid(row=2, column=1, sticky="w", padx=6, pady=6)

    def on_show(self) -> None:
        """显示时清理状态并展示货币"""
        user = self.dm.get_user(self.controller.current_user) or {}
        total = int(user.get("total_run_time", 0))
        self.msg_var.set(f"当前货币：{RuntimeTracker.format_hms(total)}")

    def _on_withdraw(self) -> None:
        """提现：扣减本账户时间并生成卡密"""
        to_user = self.to_user_var.get().strip()
        secs_str = self.seconds_var.get().strip()
        try:
            secs = int(secs_str)
        except Exception:
            secs = 0
        if secs <= 0 or not to_user:
            self.key_out_var.set("")
            self.msg_var.set("请输入有效的目标用户与扣除秒数")
            return
        me = self.controller.current_user
        if not self.dm.deduct_total_run_time(me, secs):
            self.msg_var.set("扣除失败：余额不足或用户无效")
            return
        key = LicenseManager.generate_transfer_key(me, to_user, secs)
        self.key_out_var.set(key)
        self.msg_var.set("卡密已生成，请安全传递给对方")

    def _on_recharge(self) -> None:
        """充值：校验卡密并为当前账户增加时间"""
        src = self.from_user_var.get().strip()
        key = self.key_in_var.get().strip()
        dst = self.controller.current_user
        info = LicenseManager.verify_transfer_key(expect_to_user=dst, from_user=src, key_input=key)
        if not info:
            self.msg_var.set("卡密无效或不匹配")
            return
        if self.dm.is_transfer_key_used(dst, key):
            self.msg_var.set("该卡密已使用")
            return
        secs = int(info["seconds"])
        if not self.dm.credit_total_run_time(dst, secs):
            self.msg_var.set("充值失败：用户无效")
            return
        self.dm.mark_transfer_key_used(dst, key)
        total = int(self.dm.get_user(dst).get("total_run_time", 0))
        self.msg_var.set(f"充值成功：+{RuntimeTracker.format_hms(secs)}，当前：{RuntimeTracker.format_hms(total)}")

