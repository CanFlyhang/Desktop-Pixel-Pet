import tkinter as tk
from typing import Dict

from core.data_manager import DataManager
from core.pet import PetAnimator


class InventoryView(tk.Frame):
    """粮仓页面：展示用户所购买的粮食库存"""

    def __init__(self, master: tk.Misc, controller, dm: DataManager) -> None:
        super().__init__(master, bg="#222")
        self.controller = controller
        self.dm = dm
        self._photo_cache: Dict[str, tk.PhotoImage] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """构建粮仓界面控件"""
        head = tk.Frame(self, bg="#222")
        head.pack(fill="x", pady=8)
        tk.Label(head, text="粮仓", fg="#fff", bg="#222").pack(side="left", padx=12)
        tk.Button(head, text="返回主页", command=lambda: self.controller.show("home")).pack(side="right", padx=12)

        mid = tk.Frame(self, bg="#222")
        mid.pack(fill="both", expand=True, padx=12, pady=8)
        self.canvas = tk.Canvas(mid, bg="#222", highlightthickness=0)
        scrollbar = tk.Scrollbar(mid, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.grid = tk.Frame(self.canvas, bg="#222")
        self._canvas_window = self.canvas.create_window((0, 0), window=self.grid, anchor="nw")
        self.grid.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def on_show(self) -> None:
        """页面显示时渲染库存并绑定滚轮"""
        try:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        except Exception:
            pass
        self._render_grid()

    def on_hide(self) -> None:
        """页面隐藏时解绑滚轮"""
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass

    def _render_grid(self) -> None:
        """渲染粮仓物品网格"""
        for w in list(self.grid.children.values()):
            try:
                w.destroy()
            except Exception:
                pass
        user = self.dm.get_user(self.controller.current_user) or {}
        inv: Dict[str, int] = dict(user.get("inventory", {}))
        foods = self.dm.get_foods()

        if not inv:
            tk.Label(self.grid, text="粮仓为空，去商城购买吧", fg="#ccc", bg="#222").pack(pady=18)
            return

        names = list(inv.keys())
        cols = 3
        for i, name in enumerate(names):
            qty = int(inv.get(name, 0))
            cfg = foods.get(name, {})
            container = tk.Frame(self.grid, bg="#444", padx=1, pady=1)
            container.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="nsew")
            fr = tk.Frame(container, bg="#333")
            fr.pack(fill="both", expand=True)

            frames_path = cfg.get("frames", "")
            try:
                preview = self._get_preview(name, frames_path)
                tk.Label(fr, image=preview, bg="#333").pack(pady=8)
            except Exception:
                tk.Label(fr, text="[预览]", fg="#999", bg="#333").pack(pady=8)

            tk.Label(fr, text=name, fg="#fff", bg="#333", font=("微软雅黑", 10, "bold")).pack()
            tk.Label(fr, text=f"数量：{qty}", fg="#ccc", bg="#333").pack(pady=(0, 6))

        for c in range(cols):
            self.grid.grid_columnconfigure(c, weight=1)

    def _get_preview(self, name: str, frames_path: str) -> tk.PhotoImage:
        """生成或取缓存的预览 PhotoImage"""
        if name in self._photo_cache:
            return self._photo_cache[name]
        pa = PetAnimator(frames_path)
        img = pa.get_tk_image()
        self._photo_cache[name] = img
        return img

    def _on_frame_configure(self, event) -> None:
        """根据内容尺寸更新 Canvas 的滚动区域"""
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception:
            pass

    def _on_canvas_configure(self, event) -> None:
        """保持 Canvas 内窗口宽度与可视宽度一致"""
        try:
            self.canvas.itemconfig(self._canvas_window, width=event.width)
        except Exception:
            pass

    def _on_mousewheel(self, event) -> None:
        """鼠标滚轮滚动列表"""
        try:
            if self.grid.winfo_height() > self.canvas.winfo_height():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

