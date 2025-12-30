# 🐾 Desktop Pixel Pet（桌面像素宠物）

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)

Desktop Pixel Pet（桌面像素宠物）是一个 **轻量、可扩展、以像素动画驱动的桌面陪伴应用**。  
它会在你的电脑桌面角落展示一只（或多只）可爱的像素宠物，让它待机、走动、互动，陪你一起工作与学习 ✨

---

## 📸 项目预览

<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/4ae36b74-598c-4066-9204-869db0b82dff" /><img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/358db5b0-29bf-4bdf-b53c-0fa7eae5e337" />



<!-- TODO: 添加项目截图 -->
<!--
![宠物待机](docs/images/idle.png)
![宠物行走](docs/images/walk.gif)
![宠物商城](docs/images/shop.png)
-->

---

## ✨ 项目特性

- 🐶 **桌面像素宠物**
  - 宠物常驻桌面，不干扰正常操作
  - 支持待机、行走、互动等动画状态

- 🛒 **宠物商城与解锁机制**
  - 以 **运行时间作为货币**
  - 可购买 / 解锁新的宠物与粮食

- 💾 **本地数据存储 & 迁移**
  - 支持数据导入 / 导出
  - 方便在不同设备间迁移账号与进度

- 🎨 **像素资源驱动**
  - 宠物基于像素帧数据（Frame-based）
  - 易于社区创作新角色、新动画

- 🧩 **清晰可扩展的架构**
  - 适合作为：
    - 桌面小工具示例
    - GUI 项目实践
    - 像素动画资源管理项目

---

## 🧱 技术栈

- 🐍 **Python**
- 🖼️ GUI：Tkinter / PyQt / 其他（按实际填写）
- 📦 数据存储：本地文件（JSON / SQLite 等）
- 🎞️ 像素动画：帧数据驱动

---
# Desktop-Pixel-Pet
Desktop Pixel Pet（桌面像素宠物）是一个轻量、可扩展的桌面陪伴应用：在你的电脑桌面上展示可爱的像素宠物，让它在屏幕角落里待机、走动、互动，陪你工作与学习。项目内置宠物商城与解锁机制，支持使用运行时间作为货币购买/激活宠物与粮食，并提供本地数据导入/导出能力，方便在不同设备间迁移账号与进度。整体架构清晰，宠物资源以像素帧数据驱动，便于社区创作与扩展更多角色与动画，适合作为桌面小工具、像素动画资源管理与 GUI 项目实践的开源范例。

## 简介
- 使用 Python 3.8+、Tkinter、Pygame、pywin32 构建的本地像素桌宠养成小游戏
- 全程离线，用户与宠物数据存储于 `data/*.json`
- 运行时间为唯一“货币”，可在商城解锁更多桌宠；桌宠支持悬浮窗展示与互动

## 依赖安装（Windows）
```bash
pip install pygame pillow pywin32
```
Tkinter 为 Python 自带库，无需安装。

## 启动方式
```bash
python main.py
```
首次运行将自动创建 `data/users.json` 与 `data/pets.json` 等模板。

## 功能概览
- 账号系统：注册/登录/密码找回（密保问题）
- 数据存储：JSON 文件本地化，异步写入，原子落盘
- 主页：显示用户名与总运行时间，网格展示已解锁宠物
- 悬浮窗：置顶透明、可拖拽、右键菜单（返回/更换/关闭）、点击互动（随机动作）
- 商城：展示未解锁宠物，价格为运行时间；购买后扣减总时间并解锁

## 文件结构
```
core/
  account.py          # 注册/登录/找回
  data_manager.py     # JSON 缓存与异步写
  runtime_tracker.py  # 每秒累计时间
  assets_loader.py    # 像素矩阵 → Pygame Surface
  pet.py              # 动画与互动
  float_window.py     # 悬浮窗（pywin32 优先）
ui/
  login_view.py
  register_view.py
  recover_view.py
  home_view.py
  mall_view.py
assets/
  pets/
    pixel_dog.json / pixel_cat.json / pixel_rabbit.json
data/
  users.json
  pets.json
main.py
README.md
```

---

## 🛠 开发文档（面向开发者）

### 开发环境与依赖
- Python 3.8+（推荐 3.10/3.11）
- Windows 优先支持透明悬浮窗（pywin32），macOS/Linux 自动降级为 Tkinter 顶层窗
- 依赖安装（Windows）：

```bash
pip install pygame pillow pywin32
```

- 资源说明：
  - 像素宠物帧数据：`assets/pets/*.json`
  - 本地数据：`data/*.json`（用户、宠物配置等）
  - 音频文件：项目根目录放置 `manbo.mp3`（疲劳提示）与 `where.mp3`（无脸提示）

### 快速开始（开发模式）
- 运行主程序：

```bash
python main.py
```

- 首次运行会自动生成数据模板（如 `data/users.json`、`data/pets.json`）
- 进入主页后可打开“悬浮窗”，进行右键菜单操作（返回/更换/投喂/关闭）

### 核心模块与职责
- core/pet.py：宠物动画与互动入口，负责帧轮换、随机互动动作
- core/float_window.py：悬浮窗载体，负责置顶、透明、拖拽、右键菜单、问候气泡与视觉/音频提示
- core/fatigue_detector.py：疲劳检测状态机（示例），输出三种状态
  - NORMAL：绿色轮廓常亮
  - FATIGUE：红色轮廓闪烁、循环播放疲劳音频
  - NO_FACE：黄色轮廓闪烁、循环播放无脸提示音频
- core/data_manager.py：用户与宠物数据的读写与缓存、异步落盘
- core/runtime_tracker.py：记录用户运行时长（商城货币）
- ui/*：登录/注册/找回/主页/商城等 Tkinter 视图

### 疲劳检测与音频/视觉提示
- 视觉提示（在悬浮窗中绘制宠物外沿轮廓）：
  - FATIGUE：红色闪烁（0.5 秒节奏）
  - NORMAL：绿色常亮
  - NO_FACE：黄色闪烁（0.5 秒节奏）
- 音频提示（通过 pygame.mixer）：
  - FATIGUE：播放 `manbo.mp3`，循环
  - NO_FACE：播放 `where.mp3`，循环
  - NORMAL：统一停止所有音频
- 状态切换时会主动停止上一段音频，避免重叠；初始化失败会自动禁用音频并打印错误信息
- 关键实现参考：
  - 轮廓颜色与闪烁节奏：[float_window.py:_tick](core/float_window.py#L648-L659)
  - 状态化音频控制（切换/停止）：[float_window.py:_tick](core/float_window.py#L599-L647)
  - 初始化音频路径与状态字段：[float_window.py:__init__](core/float_window.py#L225-L236)

### 悬浮窗与交互
- 置顶透明、可拖拽，右键菜单支持：
  - 返回主页、更换桌宠（子菜单打钩显示当前）、投喂、关闭悬浮窗
- 点击宠物（非拖拽）会触发随机互动动作
- 问候气泡（可选）：定时在宠物上方显示提醒语句，可关闭或移动时同步位置

### 数据与配置
- 用户数据：`data/users.json`
  - 字段示例：用户名、密码哈希、已解锁宠物、库存等
- 宠物配置：`data/pets.json`
  - 指定帧资源路径、显示名称、商城价格等
- 安全与本地化：
  - 本地纯离线，不进行网络通信
  - 密码以 SHA256 存储；“记住密码”仅用于本机开发演示（`data/config.json`）

### 资源与扩展
- 新增宠物：在 `assets/pets/` 添加对应 JSON 帧数据，并在 `data/pets.json` 注册
- 自定义动画：遵循帧驱动模型，确保像素矩阵与尺寸一致
- 音效：将对应 mp3 文件放在项目根目录，并在 `float_window.py` 中配置路径

### 调试与排错
- 悬浮窗透明失败：检查是否已安装 `pywin32`；失败会自动降级为 Tkinter 顶层窗体
- 音频无法播放：
  - 确认 `pygame.mixer` 初始化成功（控制台报错会提示）
  - 确认 `manbo.mp3` / `where.mp3` 路径与文件存在
  - 切换状态时应能自动停止上一段音频
- 资源预览为空：示例帧为占位素材，需替换 `assets/pets/*.json` 为实际像素资源
- 数据异常退出：写入采用异步与原子落盘；损坏时可清理 `*.tmp` 并重启

### 跨平台说明
- Windows：优先 pywin32 设置层叠透明与置顶，体验更佳
- macOS/Linux：使用 Tkinter 顶层窗，功能可用但透明与层叠效果不同

### 贡献指南（简版）
- 提交前请自测基本流程（登录→主页→悬浮窗→商城→投喂）
- 代码风格保持与现有模块一致，命名清晰、函数职责单一
- 资源与配置变更请同步更新 `data/pets.json` 或相关文档说明

### 🧭 版本迭代历史
- v1.0（第一代）
  - 基础桌宠：悬浮窗置顶透明、可拖拽、右键菜单
  - 像素帧驱动动画与随机互动
  - 商城与解锁：以运行时间作为货币
  - 本地数据：`data/users.json`、`data/pets.json`；密码以 SHA256 存储
  - 文件结构与资源目录规范化
- v2.0（第二代，当前版本）
  - 疲劳检测可视与音频反馈：
    - FATIGUE：红色轮廓闪烁（0.5s 节奏）、循环播放 `manbo.mp3`
    - NO_FACE：黄色轮廓闪烁（0.5s 节奏）、循环播放 `where.mp3`
    - NORMAL：绿色常亮并停止音频
    - 状态化音频切换，避免重叠播放，失败自动禁用并打印错误
  - 右键菜单增强：更换桌宠子菜单打钩显示当前、投喂子菜单展示库存
  - 问候气泡：定时提醒，移动悬浮窗时同步位置
  - 投喂爱心动画：投喂成功在宠物上方冒泡显示
  - 悬浮窗默认定位优化：屏幕右下角并留出边距
  - 开发者文档完善：环境、模块职责、调试与排错、跨平台说明
  - 稳定性优化：拖拽防抖、异常保护、pywin32 失败降级到 Tkinter

## 👥 项目贡献者

感谢所有为本项目贡献过代码的小伙伴 ❤️

[![Contributors](https://contrib.rocks/image?repo=CanFlyhang/desktop-pixel-pet)](https://github.com/CanFlyhang/desktop-pixel-pet/graphs/contributors)

## 关于商业化的思考与设计（作者说明）

Desktop Pixel Pet 是一个面向开源社区的桌面像素宠物项目：核心体验尽量保持开放、透明、可扩展；同时也预留了**可持续的商业化路径**，用以支持长期维护、内容创作与生态建设。

### 为什么需要商业化
开源项目的长期发展往往需要稳定投入，包括但不限于：
- 新宠物与动画资源的持续制作
- 交互玩法与性能优化的迭代
- 用户反馈处理、兼容性适配与 Bug 修复
- 服务器/分发/运营等基础成本（如未来引入更多在线能力）

因此，本项目选择在不影响核心可用性的前提下，提供一种“**可选的付费解锁机制**”，让愿意支持项目的用户获得更多内容，同时反哺开发。

### 商城与卡密兑换：可选、克制、可持续
项目内置商城体系，并预留了“**卡密兑换/激活**”入口，用于解锁特定像素宠物（或特殊内容）。该机制遵循以下原则：
- **默认不强制付费**：基础体验与开源部分不设门槛
- **内容型付费**：更多以新宠物/皮肤/特殊动画等内容扩展为主
- **最小化侵入**：不引入干扰式广告，不影响使用体验

### 针对二手倒卖的设计：绑定用户名的兑换密钥
为了避免常见的“卡密被转卖/重复使用/二手倒卖”问题，本项目采用“**按用户名生成兑换密钥**”的思路：

- 兑换密钥由系统根据 `用户名 + 宠物标识 + 盐值` 等信息生成
- 采用哈希/签名类算法使密钥**不可逆**、难以伪造
- 校验时同样基于当前用户名与宠物标识进行验证，确保“**一人一密**”

这样带来的效果是：
- 同一串密钥无法给其他用户名使用，降低二手转售价值
- 即使密钥被泄露，也难以大规模复用
- 商业化更偏向“支持作者获得内容”而非“投机套利”

### 开源与商业的边界
我希望这个项目在开源社区里保持清晰边界：
- **核心框架与基础能力**继续开源，方便学习与二次开发
- **可商业化内容**（例如部分宠物资源、特殊动画、增值包）可以作为可选扩展
- 在不违背开源精神的前提下，建立一个对作者与用户都更健康的长期模式
如果你喜欢这个项目，欢迎 Star、提 Issue、贡献宠物资源或 PR；你的支持会直接推动 Desktop Pixel Pet 变得更好。

## 常见问题
- 无法创建悬浮透明窗：确保已安装 `pywin32`；若缺失将自动降级为 Tkinter 顶层窗体。
- 资源预览为空：使用了占位帧，实际像素素材可替换 `assets/pets/*.json`。
- 进程意外退出：数据写入采用原子落盘与异步队列，尽量避免损坏；如损坏可删除 `*.tmp` 并重启。

## 本地化与安全
- 密码以 SHA256 存储于本地 `users.json`；“记住密码”将明文写入 `data/config.json`（仅用于本机开发与演示）。
- 项目不进行任何网络通信。

## 版权与扩展
- 可自由扩展更多像素宠物与动画帧、增加音效等。
