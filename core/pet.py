import random
from typing import List, Tuple

from PIL import Image, ImageTk

try:
    import pygame
except Exception as e:  # pragma: no cover
    pygame = None

from .assets_loader import AssetsLoader


class PetAnimator:
    """桌宠动画器：管理帧动画、交互动作与 Tkinter 图像转换
    使用：
        pa = PetAnimator(frames_path)
        img = pa.get_tk_image()  # 当前帧转 Tk Image
        pa.next_frame()          # 切换到下一帧
        pa.interact_random()     # 触发随机互动动作
    """

    def __init__(self, frames_path: str, scale: int = 4) -> None:
        if pygame is None:
            raise RuntimeError("未检测到 pygame，请先安装：pip install pygame")
        pygame.init()
        self.scale = scale
        self.loader = AssetsLoader()
        self.raw_w, self.raw_h, frames_rgba = self.loader.load_frames(frames_path)
        self.frames: List["pygame.Surface"] = self.loader.to_surfaces(frames_rgba)
        self._idx = 0
        self._state = "idle"
        # 互动叠加效果：短时改变某些像素颜色（如摇尾/吐舌）
        self._interact_ticks = 0

    @property
    def w(self) -> int:
        return self.raw_w * self.scale

    @property
    def h(self) -> int:
        return self.raw_h * self.scale

    def next_frame(self) -> None:
        """前进到下一帧，循环播放，支持轻微随机停顿模拟呼吸"""
        if not self.frames:
            return
        self._idx = (self._idx + 1) % len(self.frames)
        if self._interact_ticks > 0:
            self._apply_interact_overlay(self.frames[self._idx])
            self._interact_ticks -= 1

    def interact_random(self) -> None:
        """随机互动：摇尾、跳动、眨眼（以叠加像素效果实现）"""
        self._state = random.choice(["wag", "jump", "blink"])
        self._interact_ticks = random.randint(5, 12)

    def get_tk_image(self, outline_color: Tuple[int, int, int] = None) -> "ImageTk.PhotoImage":
        """将当前 Pygame Surface 转为 Tkinter 可用的 PhotoImage
        
        Args:
            outline_color: 可选 (R, G, B)，若提供则绘制像素轮廓
        """
        if not self.frames:
            img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
            return ImageTk.PhotoImage(img)
        surf = self.frames[self._idx]

        # 如果需要绘制轮廓
        if outline_color:
            # 创建 mask 并生成纯色图
            mask = pygame.mask.from_surface(surf)
            # 注意：setcolor 需要 (R, G, B, A)
            solid_surf = mask.to_surface(setcolor=(*outline_color, 255), unsetcolor=(0, 0, 0, 0))
            
            # 创建合成用的临时 Surface
            w, h = surf.get_size()
            temp_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            
            # 上下左右偏移绘制纯色底（模拟膨胀效果）
            temp_surf.blit(solid_surf, (-1, 0))
            temp_surf.blit(solid_surf, (1, 0))
            temp_surf.blit(solid_surf, (0, -1))
            temp_surf.blit(solid_surf, (0, 1))
            
            # 叠加原图
            temp_surf.blit(surf, (0, 0))
            surf = temp_surf

        raw_str = pygame.image.tostring(surf, "RGBA", False)
        img = Image.frombytes("RGBA", (self.raw_w, self.raw_h), raw_str)
        
        if self.scale != 1:
            img = img.resize((self.w, self.h), Image.NEAREST)
            
        return ImageTk.PhotoImage(img)

    def _apply_interact_overlay(self, surf: "pygame.Surface") -> None:
        """在当前帧上应用互动叠加（示例：随机若干像素加亮）"""
        w, h = self.raw_w, self.raw_h
        for _ in range(30):
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            r, g, b, a = surf.get_at((x, y))
            surf.set_at((x, y), (min(r + 10, 255), min(g + 10, 255), min(b + 10, 255), a))

