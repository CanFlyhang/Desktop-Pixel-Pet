import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Optional, Tuple

class BackupManager:
    """备份管理器：负责用户数据的加密导出与解密导入
    采用“哈希算法加密”（自定义流加密 + HMAC 签名）以满足需求。
    """
    
    _SALT = b"TraePet_Backup_Salt_v1"
    _sk = b"TraePet_Secret_Key_For_Obfuscation"

    @staticmethod
    def _derive_key(iv: bytes) -> bytes:
        """根据 IV 派生会话密钥"""
        return hashlib.sha256(BackupManager._sk + iv + BackupManager._SALT).digest()

    @staticmethod
    def _xor_cipher(data: bytes, key: bytes) -> bytes:
        """简单的 XOR 流加密"""
        # 扩展密钥流以覆盖数据长度
        # 使用 key 的反复哈希作为密钥流生成器
        out = bytearray(len(data))
        stream_block = key
        block_idx = 0
        
        for i in range(len(data)):
            if i % 32 == 0:
                # 每 32 字节更新一次密钥流块
                stream_block = hashlib.sha256(stream_block + str(block_idx).encode()).digest()
                block_idx += 1
            out[i] = data[i] ^ stream_block[i % 32]
        return bytes(out)

    @staticmethod
    def export_data(user_data: Dict[str, Any]) -> str:
        """将用户数据序列化并加密导出为字符串"""
        # 1. 序列化
        json_bytes = json.dumps(user_data, ensure_ascii=False).encode("utf-8")
        
        # 2. 生成随机 IV
        iv = os.urandom(16)
        
        # 3. 派生密钥并加密
        key = BackupManager._derive_key(iv)
        ciphertext = BackupManager._xor_cipher(json_bytes, key)
        
        # 4. 计算 HMAC 签名 (对 IV + Ciphertext)
        sig_payload = iv + ciphertext
        sig = hmac.new(BackupManager._SALT, sig_payload, hashlib.sha256).hexdigest()
        
        # 5. 编码：Base64(IV + Ciphertext) + "|" + Sig
        # IV (16) + Ciphertext (N)
        payload_b64 = base64.urlsafe_b64encode(iv + ciphertext).decode("ascii")
        return f"{payload_b64}|{sig}"

    @staticmethod
    def import_data(file_content: str) -> Optional[Dict[str, Any]]:
        """解析并解密备份文件内容，返回用户数据字典"""
        try:
            parts = file_content.strip().split("|")
            if len(parts) != 2:
                return None
                
            payload_b64, sig_hex = parts[0], parts[1]
            
            # 1. 解码载荷
            raw_payload = base64.urlsafe_b64decode(payload_b64.encode("ascii"))
            if len(raw_payload) < 16:
                return None
                
            iv = raw_payload[:16]
            ciphertext = raw_payload[16:]
            
            # 2. 验证签名
            calc_sig = hmac.new(BackupManager._SALT, raw_payload, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(calc_sig.upper(), sig_hex.upper()):
                return None
                
            # 3. 解密
            key = BackupManager._derive_key(iv)
            json_bytes = BackupManager._xor_cipher(ciphertext, key)
            
            # 4. 反序列化
            return json.loads(json_bytes.decode("utf-8"))
            
        except Exception:
            return None
