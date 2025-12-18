import tkinter as tk
from typing import Dict

from core.data_manager import DataManager
from core.account import AccountManager
from core.runtime_tracker import RuntimeTracker

from ui.login_view import LoginView
from ui.register_view import RegisterView
from ui.recover_view import RecoverView
from ui.home_view import HomeView
from ui.mall_view import MallView
from ui.inventory_view import InventoryView
from ui.settings_view import SettingsView
from ui.account_view import AccountView
from ui.update_view import UpdateView


class AppController:
    """应用控制器：持有路由、共享服务与当前用户，负责页面切换"""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Trae 像素桌宠")
        self.root.geometry("800x600")
        self.root.configure(bg="#222")
        # 核心服务
        self.dm = DataManager()
        self.am = AccountManager(self.dm)
        self.tracker = RuntimeTracker(self.dm)
        # 状态
        self.current_user: str = ""
        self.float_window = None
        # 页面容器
        self.container = tk.Frame(self.root, bg="#222")
        self.container.pack(fill="both", expand=True)
        # 初始化路由
        self.views: Dict[str, tk.Frame] = {}
        self.current_view_name: str = ""
        self._init_views()
        self.show("login")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_views(self) -> None:
        """创建并注册所有页面视图"""
        self.views["login"] = LoginView(self.container, self, self.dm, self.am)
        self.views["register"] = RegisterView(self.container, self, self.dm, self.am)
        self.views["recover"] = RecoverView(self.container, self, self.dm, self.am)
        self.views["home"] = HomeView(self.container, self, self.dm, self.tracker)
        self.views["mall"] = MallView(self.container, self, self.dm)
        self.views["inventory"] = InventoryView(self.container, self, self.dm)
        self.views["settings"] = SettingsView(self.container, self, self.dm)
        self.views["account"] = AccountView(self.container, self, self.dm)
        self.views["update"] = UpdateView(self.container, self, self.dm, self.am)
        for v in self.views.values():
            v.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show(self, name: str) -> None:
        """切换显示到指定页面，并调用 on_show 钩子"""
        # 确保主窗口可见并置顶
        try:
            self.root.deiconify()
            self.root.lift()
        except Exception:
            pass

        # 如果有前一个页面，调用其 on_hide
        if self.current_view_name and self.current_view_name in self.views:
            prev_view = self.views[self.current_view_name]
            if hasattr(prev_view, "on_hide"):
                try:
                    prev_view.on_hide()
                except Exception:
                    pass

        view = self.views.get(name)
        if not view:
            return
            
        self.current_view_name = name
        view.lift()
        if hasattr(view, "on_show"):
            try:
                view.on_show()
            except Exception:
                pass

    def set_current_user(self, username: str) -> None:
        """设置当前登录用户"""
        self.current_user = username
        # 登录时应用用户配置
        user = self.dm.get_user(username)
        if user:
            settings = user.get("settings", {})
            self.apply_settings(settings)

    def apply_settings(self, settings: Dict) -> None:
        """应用全局配置"""
        if self.float_window:
            self.float_window.update_settings(settings)

    def logout(self) -> None:
        """退出登录：清理悬浮窗与用户状态"""
        # 1. 关闭悬浮窗
        if self.float_window:
            try:
                self.float_window.close()
            except Exception:
                pass
            self.float_window = None
        
        # 2. 停止计时器
        try:
            self.tracker.stop()
        except Exception:
            pass
            
        # 3. 清除当前用户并跳转
        self.current_user = ""
        self.show("login")

    def _on_close(self) -> None:
        """窗口关闭事件：停止计时与数据写线程"""
        try:
            self.tracker.stop()
        except Exception:
            pass
        try:
            self.dm.stop()
        except Exception:
            pass
        self.root.destroy()


def main() -> None:
    """应用入口：创建控制器并启动主循环"""
    # Windows 高 DPI 适配，防止坐标漂移与界面模糊
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
        
    app = AppController()
    app.root.mainloop()


if __name__ == "__main__":
    main()
