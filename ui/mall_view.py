import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from typing import Dict, List, Optional

from core.data_manager import DataManager
from core.runtime_tracker import RuntimeTracker
from core.pet import PetAnimator
from core.license_manager import LicenseManager


class MallView(tk.Frame):
    """商城页面：展示未解锁宠物列表与购买逻辑"""

    def __init__(self, master: tk.Misc, controller, dm: DataManager) -> None:
        super().__init__(master, bg="#222")
        self.controller = controller
        self.dm = dm
        self.selected_pet: Optional[str] = None
        self.selected_food: Optional[str] = None
        self.mode: str = "pet"
        self.qty_var = tk.IntVar(value=1)
        self._photo_cache: Dict[str, tk.PhotoImage] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """构建商城界面控件"""
        head = tk.Frame(self, bg="#222")
        head.pack(fill="x", pady=8)
        self.time_label = tk.Label(head, text="货币：00:00:00", fg="#fff", bg="#222")
        self.time_label.pack(side="left", padx=12)
        tk.Button(head, text="返回主页", command=lambda: self.controller.show("home")).pack(side="right", padx=12)

        # 模式切换：宠物 / 粮食
        modebar = tk.Frame(self, bg="#222")
        modebar.pack(fill="x", padx=12)
        def set_mode(m: str) -> None:
            self.mode = m
            self.selected_pet = None
            self.selected_food = None
            self.btn_buy.configure(state="disabled", text="购买", command=self._on_buy)
            try:
                self.qty_label.pack_forget()
                self.spin_qty.pack_forget()
            except Exception:
                pass
            self._render_list()
            self.canvas.yview_moveto(0)
        tk.Button(modebar, text="宠物", command=lambda: set_mode("pet")).pack(side="left", padx=4)
        tk.Button(modebar, text="粮食", command=lambda: set_mode("food")).pack(side="left", padx=4)

        # 中间滚动容器
        mid = tk.Frame(self, bg="#222")
        mid.pack(fill="both", expand=True, padx=12, pady=8)

        # Canvas + Scrollbar 组合
        self.canvas = tk.Canvas(mid, bg="#222", highlightthickness=0)
        scrollbar = tk.Scrollbar(mid, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 将实际列表框置于 Canvas 内
        self.list_frame = tk.Frame(self.canvas, bg="#222")
        self._canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        # 绑定尺寸变化事件，保持滚动正确与宽度自适应
        self.list_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        foot = tk.Frame(self, bg="#222")
        foot.pack(fill="x", pady=8)
        self.btn_buy = tk.Button(foot, text="购买", command=self._on_buy, state="disabled")
        self.btn_buy.pack(side="left", padx=8)
        # 粮食数量选择控件（默认不显示，仅在选择粮食时显示）
        self.qty_label = tk.Label(foot, text="数量", fg="#ddd", bg="#222")
        self.spin_qty = tk.Spinbox(foot, from_=1, to=99, textvariable=self.qty_var, width=5)

    def on_show(self) -> None:
        """页面显示时刷新未解锁列表与货币显示"""
        # 绑定鼠标滚轮
        try:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        except Exception:
            pass
        user = self.dm.get_user(self.controller.current_user) or {}
        total = int(user.get("total_run_time", 0))
        self.time_label.configure(text=f"货币：{RuntimeTracker.format_hms(total)}")
        self._render_list()

    def on_hide(self) -> None:
        """页面隐藏时解绑事件"""
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass

    def _render_list(self) -> None:
        """渲染当前模式的商品列表（宠物或粮食）"""
        for w in list(self.list_frame.children.values()):
            try:
                w.destroy()
            except Exception:
                pass
        if self.mode == "pet":
            user = self.dm.get_user(self.controller.current_user) or {}
            unlocked = set(user.get("unlocked_pets", []))
            pets_cfg = self.dm.get_pets()
            locked = [name for name in pets_cfg.keys() if name not in unlocked]
            if not locked:
                tk.Label(self.list_frame, text="所有宠物已解锁", fg="#9f9", bg="#222").pack(pady=18)
                return
        else:
            foods_cfg = self.dm.get_foods()
            if not foods_cfg:
                tk.Label(self.list_frame, text="暂无粮食上架", fg="#f99", bg="#222").pack(pady=18)
                return

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

        items = []
        if self.mode == "pet":
            pets_cfg = self.dm.get_pets()
            user = self.dm.get_user(self.controller.current_user) or {}
            unlocked = set(user.get("unlocked_pets", []))
            items = [(name, pets_cfg[name]) for name in pets_cfg.keys() if name not in unlocked]
        else:
            foods_cfg = self.dm.get_foods()
            items = list(foods_cfg.items())

        for name, cfg in items:
            is_selected = (name == (self.selected_pet if self.mode == "pet" else self.selected_food))
            style = STYLE_SELECTED if is_selected else STYLE_NORMAL
            
            # 外层容器充当边框
            container = tk.Frame(
                self.list_frame, 
                bg=style["border_color"], 
                padx=style["border_width"], 
                pady=style["border_width"]
            )
            container.pack(fill="x", pady=6)
            
            # 内层内容容器
            fr = tk.Frame(container, bg="#333")
            fr.pack(fill="both", expand=True)
            
            # 预览
            frames_path = cfg.get("frames", "")
            try:
                preview = self._get_preview(name, frames_path)
                tk.Label(fr, image=preview, bg="#333").pack(side="left", padx=8, pady=6)
            except Exception:
                pass
            
            # 文本区域
            text_frame = tk.Frame(fr, bg="#333")
            text_frame.pack(side="left", fill="both", expand=True, padx=4)
            
            tk.Label(text_frame, text=name, fg="#fff", bg="#333", font=("微软雅黑", 12, "bold")).pack(anchor="w")

            if self.mode == "pet":
                if cfg.get("unlock_type") == "key":
                    price_text = "获取方式：卡密兑换 (联系管理员)"
                else:
                    price_text = f"价格：{RuntimeTracker.format_hms(int(cfg.get('price', 0)))}"
            else:
                price_text = f"单价：{RuntimeTracker.format_hms(int(cfg.get('price', 0)))}"

            tk.Label(text_frame, text=price_text, fg="#ccc", bg="#333").pack(anchor="w")
            tk.Label(text_frame, text=cfg.get("description", ""), fg="#bbb", bg="#333").pack(anchor="w")
            
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
                command=(lambda n=name: self._select_pet(n)) if self.mode == "pet" else (lambda n=name: self._select_food(n))
            )
            btn.pack(side="right", padx=12)

    def _select_pet(self, name: str) -> None:
        """选中或取消选中未解锁宠物"""
        if self.selected_pet == name:
            self.selected_pet = None
            self.btn_buy.configure(state="disabled", text="购买", command=self._on_buy)
        else:
            self.selected_pet = name
            self.selected_food = None
            self.btn_buy.configure(state="normal")
            
            pets_cfg = self.dm.get_pets()
            cfg = pets_cfg.get(name, {})
            if cfg.get("unlock_type") == "key":
                self.btn_buy.configure(text="激活 (卡密)", command=self._on_activate)
            else:
                self.btn_buy.configure(text="购买", command=self._on_buy)
        # 宠物模式下隐藏数量控件
        try:
            self.qty_label.pack_forget()
            self.spin_qty.pack_forget()
        except Exception:
            pass
        self._render_list()

    def _select_food(self, name: str) -> None:
        """选中或取消选中粮食"""
        if self.selected_food == name:
            self.selected_food = None
            self.btn_buy.configure(state="disabled", text="购买", command=self._on_buy)
            try:
                self.qty_label.pack_forget()
                self.spin_qty.pack_forget()
            except Exception:
                pass
        else:
            self.selected_food = name
            self.selected_pet = None
            self.btn_buy.configure(state="normal", text="购买", command=self._on_buy)
            # 粮食模式下，选中后显示数量控件
            try:
                self.qty_label.pack(side="left", padx=(16, 4))
                self.spin_qty.pack(side="left")
            except Exception:
                pass
        self._render_list()

    def _unlock_pet(self, pet_name: str) -> None:
        """通用解锁逻辑"""
        user = self.dm.get_user(self.controller.current_user) or {}
        unlocked: List[str] = list(user.get("unlocked_pets", []))
        if pet_name not in unlocked:
            unlocked.append(pet_name)
            
        pet_times: Dict[str, int] = dict(user.get("pet_run_time", {}))
        pet_times.setdefault(pet_name, 0)
        
        self.dm.enqueue_user_update(self.controller.current_user, {
            "unlocked_pets": unlocked,
            "pet_run_time": pet_times
        })

    def _on_activate(self) -> None:
        """卡密激活逻辑"""
        if not self.selected_pet:
            return
            
        username = self.controller.current_user
        
        # 提示用户
        prompt = f"当前用户：{username}\n\n请输入针对该用户和宠物【{self.selected_pet}】的激活密钥：\n(请联系管理员获取)"
        key = simpledialog.askstring("激活宠物", prompt, parent=self)
        
        if not key:
            return
            
        if LicenseManager.verify_key(username, self.selected_pet, key):
            self._unlock_pet(self.selected_pet)
            self._toast("激活成功！")
            self.selected_pet = None
            self.btn_buy.configure(state="disabled", text="购买", command=self._on_buy)
            self.on_show()
        else:
            messagebox.showerror("激活失败", "激活码无效或与当前用户/宠物不匹配")

    def _on_buy(self) -> None:
        """购买逻辑：根据当前模式购买宠物或粮食"""
        if self.mode == "pet":
            if not self.selected_pet:
                return
            user = self.dm.get_user(self.controller.current_user) or {}
            pets_cfg = self.dm.get_pets()
            price = int(pets_cfg.get(self.selected_pet, {}).get("price", 0))
            if int(user.get("total_run_time", 0)) < price:
                self._toast("运行时间不足，无法购买")
                return
            if not self.dm.deduct_total_run_time(self.controller.current_user, price):
                self._toast("扣减失败，请重试")
                return
            self._unlock_pet(self.selected_pet)
            self._toast("购买成功")
            self.on_show()
        else:
            if not self.selected_food:
                return
            qty = max(1, int(self.qty_var.get()))
            user = self.dm.get_user(self.controller.current_user) or {}
            foods_cfg = self.dm.get_foods()
            unit = int(foods_cfg.get(self.selected_food, {}).get("price", 0))
            total_price = unit * qty
            if int(user.get("total_run_time", 0)) < total_price:
                self._toast("运行时间不足，无法购买")
                return
            if not self.dm.deduct_total_run_time(self.controller.current_user, total_price):
                self._toast("扣减失败，请重试")
                return
            self.dm.add_inventory_item(self.controller.current_user, self.selected_food, qty)
            self._toast("购买成功，已入粮仓")
            # 重置选择
            self.selected_food = None
            self.qty_var.set(1)
            self.btn_buy.configure(state="disabled", text="购买", command=self._on_buy)
            try:
                self.qty_label.pack_forget()
                self.spin_qty.pack_forget()
            except Exception:
                pass
            self.on_show()

    def _toast(self, text: str) -> None:
        """轻提示"""
        try:
            messagebox.showinfo("提示", text)
        except Exception:
            pass

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
            if self.list_frame.winfo_height() > self.canvas.winfo_height():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass
