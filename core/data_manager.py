import json
import os
import threading
import time
from typing import Any, Dict, Optional


class DataManager:
    """数据管理器：负责 JSON 数据的读写、缓存与异步落盘
    属性：
        data_dir: 数据目录路径
        users_path: 用户数据文件路径
        pets_path: 宠物配置文件路径
        users_cache: 内存中的用户数据缓存（dict）
        pets_cache: 内存中的宠物配置缓存（dict）
        _lock: 全局锁，保护缓存并发访问
        _stop: 写线程停止标志
        _writer_thread: 写入守护线程，每秒合并并落盘
        _pending_user_updates: 待写入的用户字段更新（按用户名聚合）
    方法：
        ensure_ready(): 确保目录与文件存在并加载缓存
        get_user(username): 获取用户数据（不存在返回 None）
        upsert_user(username, user_obj): 插入或更新完整用户对象并立即落盘
        enqueue_user_update(username, patch): 入队字段更新，异步合并写入
        deduct_total_run_time(username, seconds): 扣减总运行时间（防负），异步写入
        get_pets(): 获取宠物配置字典
        flush_now(): 立即将待更新内容落盘到 users.json
        stop(): 停止写线程（程序退出时调用）
    异常：
        文件读写异常将在内部捕获并重试，必要时回退为空结构。
    """

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        self.users_path = os.path.join(self.data_dir, "users.json")
        self.pets_path = os.path.join(self.data_dir, "pets.json")
        self.foods_path = os.path.join(self.data_dir, "foods.json")
        self.users_cache: Dict[str, Dict[str, Any]] = {}
        self.pets_cache: Dict[str, Dict[str, Any]] = {}
        self.foods_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._pending_user_updates: Dict[str, Dict[str, Any]] = {}
        self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.ensure_ready()
        self._writer_thread.start()

    def ensure_ready(self) -> None:
        """初始化数据目录与文件，加载 users 与 pets 到缓存"""
        os.makedirs(self.data_dir, exist_ok=True)
        # 初始化空的 users.json
        if not os.path.exists(self.users_path):
            self._safe_write_json(self.users_path, {})
        # 初始化 pets.json（若缺失则创建最小模板）
        if not os.path.exists(self.pets_path):
            self._safe_write_json(self.pets_path, {
                "像素小狗": {
                    "price": 0,
                    "description": "初始桌宠，可爱的像素小狗",
                    "pixel_size": "32x32",
                    "frames": "assets/pets/pixel_dog.json"
                }
            })
        # 初始化 foods.json（若缺失则创建最小模板）
        if not os.path.exists(self.foods_path):
            self._safe_write_json(self.foods_path, {
                "胡萝卜": {
                    "price": 120,
                    "description": "基础粮食：脆甜胡萝卜",
                    "frames": "assets/pets/pixel_food_carrot.json"
                }
            })
        self.users_cache = self._safe_read_json(self.users_path, {})
        self.pets_cache = self._safe_read_json(self.pets_path, {})
        self.foods_cache = self._safe_read_json(self.foods_path, {})
        # 规范化历史数据中的 pet_run_time 键名
        self._normalize_pet_run_time_keys()

    def _safe_read_json(self, path: str, default: Any) -> Any:
        """安全读取 JSON 文件并返回，失败时返回 default"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _safe_write_json(self, path: str, data: Any) -> bool:
        """安全写入 JSON 文件（原子落盘）；成功返回 True"""
        try:
            tmp_path = path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
            return True
        except Exception:
            return False

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """获取指定用户名的数据对象，不存在返回 None"""
        with self._lock:
            return self.users_cache.get(username)

    def get_pets(self) -> Dict[str, Dict[str, Any]]:
        """获取宠物配置字典（只读副本）"""
        with self._lock:
            return dict(self.pets_cache)

    def get_foods(self) -> Dict[str, Dict[str, Any]]:
        """获取粮食配置字典（只读副本）"""
        with self._lock:
            return dict(self.foods_cache)

    def _normalize_pet_run_time_keys(self) -> None:
        """规范化用户 pet_run_time 的键名，避免出现文件路径作为键"""
        try:
            import os
            # 构建路径到宠物名的映射（含无扩展名对照）
            path_to_name: Dict[str, str] = {}
            base_to_name: Dict[str, str] = {}
            for name, cfg in self.pets_cache.items():
                p = os.path.normpath(str(cfg.get("frames", ""))).lower()
                if p:
                    path_to_name[p] = name
                    base = os.path.basename(p)
                    base_no_ext = base.split(".")[0]
                    base_to_name[base_no_ext] = name

            # 遍历用户，修正 pet_run_time 的键
            for uname, user in list(self.users_cache.items()):
                prt = dict(user.get("pet_run_time", {}))
                changed = False
                new_prt: Dict[str, int] = {}
                for k, v in prt.items():
                    kk = str(k)
                    norm_k = os.path.normpath(kk).lower()
                    target_name = None
                    if norm_k in path_to_name:
                        target_name = path_to_name[norm_k]
                    else:
                        # 尝试补扩展名或用 basename 映射
                        if not kk.endswith(".json") and (norm_k + ".json") in path_to_name:
                            target_name = path_to_name[norm_k + ".json"]
                        else:
                            base_no_ext = os.path.basename(norm_k).split(".")[0]
                            target_name = base_to_name.get(base_no_ext)

                    if target_name:
                        new_prt[target_name] = int(new_prt.get(target_name, 0)) + int(v)
                        if target_name != kk:
                            changed = True
                    else:
                        new_prt[kk] = int(v)
                if changed:
                    user["pet_run_time"] = new_prt
        except Exception:
            # 忽略规范化异常，避免影响主流程
            pass

    def upsert_user(self, username: str, user_obj: Dict[str, Any]) -> bool:
        """插入或更新完整用户对象，并立即落盘到 users.json"""
        with self._lock:
            self.users_cache[username] = user_obj
            return self._safe_write_json(self.users_path, self.users_cache)

    def enqueue_user_update(self, username: str, patch: Dict[str, Any]) -> None:
        """将用户字段更新入队（异步写入），同一用户多次更新自动合并"""
        with self._lock:
            cached = self._pending_user_updates.get(username, {})
            cached.update(patch)
            self._pending_user_updates[username] = cached

    def deduct_total_run_time(self, username: str, seconds: int) -> bool:
        """扣减总运行时间（防止小于 0），入队并立即返回是否成功"""
        with self._lock:
            user = self.users_cache.get(username)
            if not user:
                return False
            current = int(user.get("total_run_time", 0))
            if current < seconds:
                return False
            new_val = current - seconds
            user["total_run_time"] = new_val
            # 入队持久化
            self.enqueue_user_update(username, {"total_run_time": new_val})
            return True

    def credit_total_run_time(self, username: str, seconds: int) -> bool:
        """增加总运行时间（秒），入队并立即返回是否成功"""
        with self._lock:
            if seconds <= 0:
                return False
            user = self.users_cache.get(username)
            if not user:
                return False
            current = int(user.get("total_run_time", 0))
            new_val = current + int(seconds)
            user["total_run_time"] = new_val
            self.enqueue_user_update(username, {"total_run_time": new_val})
            return True

    def flush_now(self) -> None:
        """立即合并待更新并落盘到 users.json（用于关键路径如注册）"""
        with self._lock:
            if not self._pending_user_updates:
                return
            for username, patch in self._pending_user_updates.items():
                base = self.users_cache.get(username, {})
                base.update(patch)
                self.users_cache[username] = base
            self._pending_user_updates.clear()
            self._safe_write_json(self.users_path, self.users_cache)

    def add_inventory_item(self, username: str, item_name: str, qty: int) -> None:
        """增加用户粮仓中某项的数量"""
        with self._lock:
            user = self.users_cache.get(username)
            if not user:
                return
            inv = dict(user.get("inventory", {}))
            inv[item_name] = int(inv.get(item_name, 0)) + int(qty)
            user["inventory"] = inv
            self.enqueue_user_update(username, {"inventory": inv})

    def consume_inventory_item(self, username: str, item_name: str, qty: int) -> bool:
        """消耗用户粮仓中指定物品数量，成功返回 True"""
        with self._lock:
            user = self.users_cache.get(username)
            if not user:
                return False
            inv = dict(user.get("inventory", {}))
            cur = int(inv.get(item_name, 0))
            need = int(qty)
            if cur < need or need <= 0:
                return False
            new_val = cur - need
            if new_val <= 0:
                inv.pop(item_name, None)
            else:
                inv[item_name] = new_val
            user["inventory"] = inv
            self.enqueue_user_update(username, {"inventory": inv})
            return True

    def stop(self) -> None:
        """停止写线程并进行最后一次落盘"""
        self._stop.set()
        try:
            self._writer_thread.join(timeout=2.0)
        except RuntimeError:
            pass
        self.flush_now()

    def is_transfer_key_used(self, username: str, key: str) -> bool:
        """检查指定用户是否已使用某充值/转账卡密"""
        with self._lock:
            user = self.users_cache.get(username) or {}
            used = set(user.get("used_transfer_keys", []))
            return key in used

    def mark_transfer_key_used(self, username: str, key: str) -> None:
        """标记指定用户已使用某充值/转账卡密"""
        with self._lock:
            user = self.users_cache.get(username)
            if not user:
                return
            used = set(user.get("used_transfer_keys", []))
            used.add(key)
            user["used_transfer_keys"] = list(used)
            self.enqueue_user_update(username, {"used_transfer_keys": list(used)})

    def _writer_loop(self) -> None:
        """守护线程：每秒合并入队更新并原子写入 users.json"""
        while not self._stop.is_set():
            time.sleep(1.0)
            try:
                self.flush_now()
            except Exception:
                # 忽略异常，下一轮继续尝试
                pass
