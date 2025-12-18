import hashlib
import hmac

class LicenseManager:
    """许可证管理器：处理卡密生成与验证"""
    
    # 这里的盐值应该保密，但在本地程序中很难完全隐藏
    # 混淆一下，增加一点点逆向难度
    _SALT = b"Cber_Pet_2024_Super_Secret_Salt_Key_#9981"

    @staticmethod
    def generate_key(username: str, pet_id: str) -> str:
        """
        为指定用户和宠物生成解锁密钥（管理员使用）
        格式：XXXX-XXXX-XXXX
        """
        # 归一化输入
        data = f"{username.strip()}|{pet_id.strip()}".encode("utf-8")
        
        # 使用 HMAC-SHA256
        h = hmac.new(LicenseManager._SALT, data, hashlib.sha256)
        digest = h.hexdigest().upper()
        
        # 截取前12位作为密钥
        raw_key = digest[:12]
        
        # 格式化为 4-4-4
        return f"{raw_key[:4]}-{raw_key[4:8]}-{raw_key[8:]}"

    @staticmethod
    def verify_key(username: str, pet_id: str, key_input: str) -> bool:
        """验证用户输入的密钥是否正确"""
        if not key_input:
            return False
            
        # 生成正确密钥
        correct_key = LicenseManager.generate_key(username, pet_id)
        
        # 忽略大小写和横杠进行比较
        clean_input = key_input.strip().upper().replace("-", "")
        clean_correct = correct_key.replace("-", "")
        
        # 使用常量时间比较防止时序攻击（虽然本地应用不需要这么严谨，但在商业化代码中是好习惯）
        return hmac.compare_digest(clean_input, clean_correct)

    @staticmethod
    def generate_transfer_key(from_user: str, to_user: str, seconds: int) -> str:
        """生成充值/转账卡密，包含来源、目标与秒数的有签名载荷"""
        import base64, time
        payload = f"v1|{from_user.strip()}|{to_user.strip()}|{int(seconds)}|{int(time.time())}"
        p_b64 = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")
        sig = hmac.new(LicenseManager._SALT, p_b64.encode("utf-8"), hashlib.sha256).hexdigest().upper()
        return f"TR-{p_b64}-{sig[:12]}"

    @staticmethod
    def verify_transfer_key(expect_to_user: str, from_user: str, key_input: str):
        """验证转账卡密并解析载荷，返回 dict 或 None
        返回: {"from": str, "to": str, "seconds": int, "ts": int, "raw": str}
        """
        import base64
        if not key_input or not expect_to_user or not from_user:
            return None
        if not key_input.startswith("TR-"):
            return None
        try:
            _, p_b64, mac12 = key_input.split("-", 2)
        except ValueError:
            return None
        calc = hmac.new(LicenseManager._SALT, p_b64.encode("utf-8"), hashlib.sha256).hexdigest().upper()[:12]
        if not hmac.compare_digest(mac12.upper(), calc):
            return None
        # 解析载荷
        try:
            pad_len = (-len(p_b64)) % 4
            p_b64_padded = p_b64 + ("=" * pad_len)
            payload = base64.urlsafe_b64decode(p_b64_padded.encode("ascii")).decode("utf-8")
            parts = payload.split("|")
            if len(parts) != 5 or parts[0] != "v1":
                return None
            src, dst, secs, ts = parts[1], parts[2], int(parts[3]), int(parts[4])
            if dst.strip() != expect_to_user.strip():
                return None
            if src.strip() != from_user.strip():
                return None
            if secs <= 0:
                return None
            return {"from": src, "to": dst, "seconds": int(secs), "ts": int(ts), "raw": key_input}
        except Exception:
            return None
