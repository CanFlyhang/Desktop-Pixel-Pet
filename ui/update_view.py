import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

from core.data_manager import DataManager
from core.account import AccountManager
from core.backup_manager import BackupManager

class UpdateView(tk.Frame):
    """数据更新页面：提供用户数据的加密导出与导入功能"""

    def __init__(self, master: tk.Misc, controller, dm: DataManager, am: AccountManager) -> None:
        super().__init__(master, bg="#222")
        self.controller = controller
        self.dm = dm
        self.am = am
        
        self.exp_username_var = tk.StringVar()
        self.exp_password_var = tk.StringVar()
        
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self, text="数据更新 (备份/恢复)", fg="#fff", bg="#222", font=("Consolas", 18)).pack(pady=20)

        # === 导出区域 ===
        exp_frame = tk.LabelFrame(self, text="导出数据 (备份)", fg="#ddd", bg="#222", font=("Consolas", 12))
        exp_frame.pack(pady=10, padx=20, fill="x")
        
        f1 = tk.Frame(exp_frame, bg="#222")
        f1.pack(pady=10)
        
        tk.Label(f1, text="用户名:", fg="#ddd", bg="#222").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(f1, textvariable=self.exp_username_var).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(f1, text="密码:", fg="#ddd", bg="#222").grid(row=0, column=2, padx=5, pady=5)
        tk.Entry(f1, textvariable=self.exp_password_var, show="*").grid(row=0, column=3, padx=5, pady=5)
        
        tk.Button(f1, text="验证并导出", command=self._on_export).grid(row=0, column=4, padx=10)
        
        tk.Label(exp_frame, text="* 将加密导出包括时间货币、宠物、粮仓等所有数据", fg="#888", bg="#222", font=("Arial", 9)).pack(pady=5)

        # === 导入区域 ===
        imp_frame = tk.LabelFrame(self, text="导入数据 (恢复)", fg="#ddd", bg="#222", font=("Consolas", 12))
        imp_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Button(imp_frame, text="选择加密文件并导入", command=self._on_import, font=("Consolas", 11), height=2).pack(pady=20)
        tk.Label(imp_frame, text="* 导入将覆盖本地同名账户的现有数据", fg="#888", bg="#222", font=("Arial", 9)).pack(pady=5)

        # === 底部 ===
        self.msg_label = tk.Label(self, text="", fg="#ffb", bg="#222")
        self.msg_label.pack(pady=10)
        
        tk.Button(self, text="返回登录", command=lambda: self.controller.show("login")).pack(pady=10)

    def on_show(self) -> None:
        self.msg_label.config(text="")
        # 尝试预填当前输入框（如果在登录页填过）
        login_view = self.controller.views.get("login")
        if login_view:
            if login_view.username_var.get():
                self.exp_username_var.set(login_view.username_var.get())
            if login_view.password_var.get():
                self.exp_password_var.set(login_view.password_var.get())

    def _on_export(self) -> None:
        username = self.exp_username_var.get().strip()
        password = self.exp_password_var.get().strip()
        
        if not username or not password:
            self.msg_label.config(text="请输入用户名和密码以验证身份")
            return
            
        # 验证身份
        user = self.dm.get_user(username)
        if not user:
            self.msg_label.config(text="用户不存在")
            return
            
        # 验证密码 (借用 AccountManager 的哈希逻辑，但它是私有的 _hash_password)
        # 既然 AccountManager 在 ui/login_view.py 里被使用，我可以调用它的 login 方法来验证？
        # 或者直接在 UpdateView 里调用 am.login(username, password)
        ok, msg = self.am.login(username, password)
        if not ok:
            self.msg_label.config(text=f"验证失败: {msg}")
            return
            
        # 身份验证通过，准备导出
        # 弹出保存对话框
        filepath = filedialog.asksaveasfilename(
            defaultextension=".dat",
            filetypes=[("加密数据文件", "*.dat"), ("所有文件", "*.*")],
            title="导出数据",
            initialfile=f"{username}_backup.dat"
        )
        
        if not filepath:
            return
            
        try:
            # 生成加密内容
            # 必须注入 username，因为 data_manager 中的用户对象不包含 key 本身
            export_payload = dict(user)
            export_payload["username"] = username
            encrypted_data = BackupManager.export_data(export_payload)
            
            # 写入文件
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(encrypted_data)
                
            self.msg_label.config(text=f"导出成功！已保存至 {os.path.basename(filepath)}")
            messagebox.showinfo("成功", "数据已加密导出！")
            
        except Exception as e:
            self.msg_label.config(text=f"导出失败: {str(e)}")
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def _on_import(self) -> None:
        filepath = filedialog.askopenfilename(
            filetypes=[("加密数据文件", "*.dat"), ("所有文件", "*.*")],
            title="选择要导入的数据文件"
        )
        
        if not filepath:
            return
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            # 解析并解密
            user_data = BackupManager.import_data(content)
            
            if not user_data or not isinstance(user_data, dict):
                self.msg_label.config(text="文件无效或校验失败（可能被篡改）")
                messagebox.showerror("错误", "无法解析文件：格式错误或签名验证失败。")
                return
                
            username = user_data.get("username")
            if not username:
                # 兼容旧版本备份或缺失用户名的情况：尝试从输入框获取
                fallback_user = self.exp_username_var.get().strip()
                if fallback_user:
                    if messagebox.askyesno("提示", f"备份数据中未包含用户名。\n是否将其恢复到用户 [{fallback_user}]？"):
                        username = fallback_user
                        user_data["username"] = username
                    else:
                        self.msg_label.config(text="操作取消")
                        return
                else:
                    self.msg_label.config(text="数据缺失用户名，请先在上方输入框填写目标用户名")
                    messagebox.showwarning("提示", "该备份文件未包含用户名信息。\n请先在上方“导出数据”区域的【用户名】框中输入目标账户名，再点击导入。")
                    return
                
            # 确认覆盖
            if messagebox.askyesno("确认导入", f"即将恢复用户 [{username}] 的数据。\n这将覆盖本地该用户的现有进度。\n是否继续？"):
                # 更新数据
                if self.dm.upsert_user(username, user_data):
                    self.msg_label.config(text=f"导入成功！用户 [{username}] 数据已更新")
                    messagebox.showinfo("成功", "数据导入成功！")
                    # 自动填入用户名
                    self.exp_username_var.set(username)
                else:
                    self.msg_label.config(text="写入数据库失败")
                    
        except Exception as e:
            self.msg_label.config(text=f"导入失败: {str(e)}")
            messagebox.showerror("错误", f"导入失败: {str(e)}")
