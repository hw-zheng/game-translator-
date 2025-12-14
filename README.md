# 通用 Galgame AI 翻译器 (Universal Galgame AI Translator)

本项目是一个**引擎无关**的 Galgame 自动化翻译工具核心。基于 [设计文档 (AI_Galgame_Translator_Design.md)](AI_Galgame_Translator_Design.md) 开发，旨在利用 AI (LLM) 为任意 Galgame 提供实时的、高质量的中文本地化体验。

## 核心特性 (Features)

*   **引擎无关 (Engine Agnostic)**: 不依赖特定游戏的解包工具。通过内存钩子 (Hooking) 获取文本，理论上支持所有 Windows 平台的 Galgame。
*   **AI 驱动 (AI Powered)**: 兼容 OpenAI 格式接口。支持 GPT-4, Claude 3, DeepSeek 以及本地 LLM (Ollama 等)。
*   **智能上下文 (Smart Context)**: 自动维护对话历史，帮助 AI 理解代词（如“他”、“它”）的指代对象。
*   **本地缓存 (Caching)**: 使用 SQLite 数据库存储已翻译文本。二周目游玩零延迟、零消耗。
*   **术语表支持 (Glossary)**: 支持自定义 `glossary.txt`，确保角色名和专有名词翻译一致。
*   **覆盖层显示 (Overlay UI)**: 采用独立的透明字幕窗口显示翻译，彻底避免修改游戏内存导致的乱码和崩溃风险。

## 项目结构 (Project Structure)

```
UniversalGalTrans/
├── core/
│   ├── bridge_server.py    # 桥接服务器 (接收 Hook 文本)
│   ├── overlay_ui.py       # 字幕显示窗口 (Tkinter)
│   ├── llm_client.py       # AI API 客户端
│   ├── database.py         # SQLite 缓存存储
│   ├── text_processor.py   # 文本处理 (防抖、过滤、上下文)
│   └── config.py           # 配置管理
├── launcher.py             # 统一启动器
└── requirements.txt        # 依赖列表
scripts/
└── build_release.py        # 打包脚本
AI_Galgame_Translator_Design.md # 架构设计文档
HOOK_INTEGRATION.md             # Textractor 对接指南
```

## 快速开始 (Quick Start)

### 方式一：生成发布包 (推荐)

最简单的使用方式是生成一个独立的“绿色版”文件夹。

1.  **运行构建脚本**:
    ```bash
    python scripts/build_release.py
    ```
    这将生成 `dist/` 目录。

2.  **配置与运行**:
    *   进入 `dist/` 目录。
    *   修改 `config.ini`，填入您的 API Key。
    *   双击 `Start.bat` 启动。
    *   此时会显示一个黑色透明的字幕条，并启动后台翻译服务。

### 方式二：源码运行 (开发模式)

1.  **安装依赖**:
    ```bash
    pip install -r UniversalGalTrans/requirements.txt
    ```

2.  **配置**:
    您可以直接修改 `UniversalGalTrans/core/config.py` 中的默认值，或者创建一个 `config.ini` 文件在项目根目录。

3.  **启动**:
    ```bash
    python UniversalGalTrans/launcher.py
    ```

## 如何连接游戏？

本项目作为“翻译后端”和“显示前端”，需要配合 **Textractor** (或其他 Hook 工具) 来抓取游戏文本。

详细步骤请参阅 [对接指南 (HOOK_INTEGRATION.md)](HOOK_INTEGRATION.md)。

简单来说：
1. 下载并安装 Textractor。
2. 将 `HOOK_INTEGRATION.md` 中提供的 Lua 脚本放入 Textractor 的 `extensions` 文件夹。
3. 启动本软件 (`Start.bat`)。
4. 使用 Textractor 附加到游戏进程。
5. 游戏文本将自动流向本软件并显示在字幕条上。
