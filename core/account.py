import hashlib
from typing import Dict, Tuple, Optional

from .data_manager import DataManager


class AccountManager:
    """账号管理器：提供注册、登录、密码找回功能
    方法返回统一的 (success, message) 元组，message 为中文提示。
    """

    def __init__(self, data_manager: DataManager) -> None:
        self.dm = data_manager

    def _hash_password(self, password: str) -> str:
        """生成密码的 sha256 哈希字符串"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(
        self,
        username: str,
        password: str,
        confirm_password: str,
        security_question: str,
        security_answer: str,
    ) -> Tuple[bool, str]:
        """注册新用户，校验用户名唯一、密码一致、密保非空，成功后写入 users.json"""
        username = (username or "").strip()
        if not username:
            return False, "用户名不能为空"
        if self.dm.get_user(username) is not None:
            return False, "用户名已存在"
        if not password or not confirm_password or password != confirm_password:
            return False, "密码与确认密码不一致"
        if not security_question or not security_answer:
            return False, "密保问题与答案不能为空"

        user_obj: Dict[str, object] = {
            "password": self._hash_password(password),
            "security_question": security_question,
            "security_answer": security_answer,
            "unlocked_pets": ["像素小狗"],
            "total_run_time": 0,
            "pet_run_time": {"像素小狗": 0},
        }
        ok = self.dm.upsert_user(username, user_obj)
        if not ok:
            return False, "写入用户数据失败，请重试"
        return True, "注册成功，默认获得像素小狗桌宠"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """登录：匹配用户名与密码哈希"""
        user = self.dm.get_user((username or "").strip())
        if not user:
            return False, "用户不存在"
        if user.get("password") != self._hash_password(password or ""):
            return False, "密码错误"
        return True, "登录成功"

    def get_security_question(self, username: str) -> Optional[str]:
        """根据用户名返回对应的密保问题，不存在返回 None"""
        user = self.dm.get_user((username or "").strip())
        if not user:
            return None
        return str(user.get("security_question", ""))

    def recover_password(
        self,
        username: str,
        security_answer: str,
        new_password: str,
        confirm_password: str,
    ) -> Tuple[bool, str]:
        """找回密码：校验密保答案与新密码一致性，成功后更新 users.json"""
        username = (username or "").strip()
        user = self.dm.get_user(username)
        if not user:
            return False, "用户不存在"
        if (security_answer or "") != str(user.get("security_answer", "")):
            return False, "密保答案不正确"
        if not new_password or new_password != (confirm_password or ""):
            return False, "新密码与确认新密码不一致"
        user["password"] = self._hash_password(new_password)
        ok = self.dm.upsert_user(username, user)
        if not ok:
            return False, "更新密码失败，请重试"
        return True, "密码已重置，请使用新密码登录"

