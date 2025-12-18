import threading
import time
from typing import Callable, List, Optional

from .data_manager import DataManager


class RuntimeTracker:
    """运行时间跟踪器：负责每秒累计总时间与当前宠物时间，并异步持久化
    使用：
        rt = RuntimeTracker(dm)
        rt.start(username, pet_name)
        rt.stop()
        rt.subscribe(callback)  # 每次 tick 回调更新 UI
    """

    def __init__(self, data_manager: DataManager) -> None:
        self.dm = data_manager
        self._username: Optional[str] = None
        self._pet_name: Optional[str] = None
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[int, int], None]] = []

    def subscribe(self, fn: Callable[[int, int], None]) -> None:
        """订阅 tick 事件，参数为（总时间秒，宠物时间秒）"""
        self._callbacks.append(fn)

    def start(self, username: str, pet_name: str) -> None:
        """开始计时：设置当前用户与宠物，并启动守护线程"""
        self._username = username
        self._pet_name = pet_name
        self._stop.clear()
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """停止计时线程"""
        self._stop.set()
        try:
            if self._thread:
                self._thread.join(timeout=2.0)
        except RuntimeError:
            pass

    def _loop(self) -> None:
        """每秒递增总时间与当前宠物时间，并通知 UI"""
        while not self._stop.is_set():
            time.sleep(1.0)
            if not (self._username and self._pet_name):
                continue
            user = self.dm.get_user(self._username)
            if not user:
                continue
            total = int(user.get("total_run_time", 0)) + 1
            pet_times = dict(user.get("pet_run_time", {}))
            pet_times[self._pet_name] = int(pet_times.get(self._pet_name, 0)) + 1
            # 更新内存并异步持久化
            user["total_run_time"] = total
            user["pet_run_time"] = pet_times
            self.dm.enqueue_user_update(self._username, {
                "total_run_time": total,
                "pet_run_time": pet_times
            })
            for cb in self._callbacks:
                try:
                    cb(total, pet_times.get(self._pet_name, 0))
                except Exception:
                    # 忽略回调异常，保证主流程
                    pass

    @staticmethod
    def format_hms(seconds: int) -> str:
        """将秒数格式化为 时:分:秒 字符串"""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

