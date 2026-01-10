# Universal Galgame AI Translator

> [!IMPORTANT]
> **详细使用教程请阅读: [用户手册 (User Guide)](UserGuide.md)**

本项目是一个通用的 Galgame 自动化 AI 翻译工具。它通过 "Overlay" (覆盖层) 的方式在游戏上方显示字幕，彻底解决了传统注入式汉化可能导致的乱码、崩溃和兼容性问题。

## 核心原理

1.  **Textractor (Hook)**: 从游戏内存提取日文文本。
2.  **Server (Core)**: 接收文本，进行清洗、防抖，并调用 AI (LLM) 进行翻译。
3.  **Overlay (UI)**: 在游戏窗口上方创建一个透明窗口显示中文翻译。

## 快速上手 (Quick Start)

### 1. 依赖准备
*   将 **Textractor** 放入 `UniversalGalTrans/tools/Textractor` 目录。
*   配置 API Key (支持 OpenAI / DeepSeek 等)。

### 2. 启动
直接运行启动器，它会自动管理所有组件：

```bash
# 开发模式
python UniversalGalTrans/launcher.py
```

或者直接运行发布包中的 `Start.bat`。

### 3. 连接游戏
1.  启动器会自动打开 Textractor。
2.  在 Textractor 中点击 "Attach to Game" 选择游戏进程。
3.  在 Textractor 下拉框中找到正确的文本流。
4.  翻译会自动出现在屏幕上方的字幕条中。

---

*更多高级配置与故障排除，请参阅 [UserGuide.md](UserGuide.md).*
