# Universal AI Galgame Translator 设计方案

## 1. 概述 (Overview)

本方案旨在设计一款 **通用型 (Engine-Agnostic)** 的 Galgame 自动化汉化工具。
鉴于用户需求为“不受游戏引擎影响”且最终需要“打包输出”，本方案采用 **运行时注入 (Runtime Injection)** 与 **虚拟打包 (Virtual Packing)** 相结合的架构。

传统的“解包-翻译-封包”模式严重依赖于特定引擎（如 Artemis, Kirikiri, Ren'Py）的文件格式，无法做到通用。
本方案的核心在于：**不修改原始游戏资源文件，而是通过外挂加载器 (Loader) 在内存中动态替换文本。**

## 2. 核心架构 (Core Architecture)

软件由三个主要部分组成：

1.  **通用文本钩子 (Universal Text Hooker)**: 负责从内存中提取和注入文本。
2.  **AI 翻译/管理核心 (Translation Core)**: 负责与 AI API 通信及文本管理。
3.  **打包发布器 (Distributor)**: 将“钩子+翻译数据库+启动器”打包，形成“汉化版”游戏。

### 2.1 模块一：通用文本钩子 (基于 Textractor)

为了实现“对所有 Galgame 都能使用”，必须复用成熟的开源钩子技术。

*   **技术选型**: [Textractor](https://github.com/Artikash/Textractor) (C++)
*   **原理**:
    *   自动搜索游戏进程中的文本输出函数（如 `TextOutA`, `TextOutW`, `GDI+`, 或引擎特定的打印函数）。
    *   **Hook (拦截)**: 拦截这些函数的调用。
    *   **提取**: 获取原始日语文本。
    *   **替换 (Injection)**: 在文本绘制到屏幕之前，将其替换为缓存中的中文文本。
*   **优势**: 支持 x86/x64，支持绝大多数引擎（Artemis, Siglus, Kirikiri 等）。

### 2.2 模块二：AI 翻译与 API 管理

此模块负责“在线汉化”和 API 对接。

*   **API 接口层**:
    *   **通用性**: 设计标准的 HTTP 适配器，允许用户输入任意 OpenAI 兼容的接口地址 (Base URL) 和 Key。
    *   **支持模型**: GPT-4, Claude 3, DeepSeek, 甚至本地 Ollama。
*   **上下文感知 (Context Aware)**:
    *   维护一个“对话历史队列”，将前 5-10 句文本连同当前文本发送给 AI，以解决主语省略问题。
    *   **术语表 (Glossary)**: 允许用户导入 `names.txt` (角色名) 和 `terms.txt` (专有名词)，在 Prompt 中强制 AI 遵守。
*   **流式处理**: 采用异步并发请求，提高翻译速度。

### 2.3 模块三：打包输出 (Virtual Packing)

用户希望“打包输出”，但在通用架构下，我们不生成修改后的 `.pfs` 或 `.xp3`。
我们生成一个 **"汉化启动包"**。

*   **输出内容**:
    *   `GameLoader.exe`: 一个轻量级启动器。
    *   `hook_core.dll`: 修改版的 Textractor 核心，专注于“读取本地翻译DB并替换”。
    *   `trans_db.json` / `.sqlite`: 存储已翻译的文本（Hash Map: 日文 -> 中文）。
    *   `font_sub.dll` (可选): 用于解决某些旧引擎不支持 GBK/UTF-8 汉字显示的问题（动态修改字体编码）。

*   **用户体验**: 玩家双击 `GameLoader.exe`，游戏启动，且自动显示为中文。对玩家而言，这等同于一个“汉化硬盘版”。

## 3. 工作流程 (Workflow)

### 阶段一：开发者/汉化者使用 (制作汉化包)

1.  **挂载**: 启动本软件，选择目标游戏 EXE。
2.  **Hook**: 软件自动寻找最佳 Hook 点（类似 Textractor 的自动搜索）。
3.  **遍历/游玩**:
    *   **自动模式**: 开发者快速快进游戏，软件实时抓取文本并发送给 AI 翻译，结果存入数据库。
    *   **批量模式 (高级)**: 如果能提取纯文本 (利用 Textractor 的 `TextHooker` 导出功能)，可批量上传翻译后再导回。
4.  **校对**: 在软件界面中查看“日文 vs AI 中文”，可手动修正。
5.  **导出**: 点击“生成汉化包”，软件生成 `GameLoader.exe` 和 `data.db` 到游戏目录。

### 阶段二：最终玩家使用 (游玩)

1.  玩家下载“汉化补丁包”（包含 Loader 和 DB）。
2.  解压到游戏目录。
3.  运行 `GameLoader.exe`。
4.  游戏启动，Loader 注入 Hook，拦截日语，显示中文。

## 4. 技术栈推荐 (Tech Stack)

*   **Hook Core**: C++ (Visual Studio), 复用 Textractor 源码。
*   **GUI/Manager**: Electron (TypeScript) 或 C# (WPF)。Electron 更容易实现现代 UI 和 API 交互。
*   **Database**: SQLite (存储海量文本和翻译索引)。

## 5. 开源项目参考 (References)

*   **Textractor** (Artikash): 核心 Hook 技术的基石。
*   **LunaTranslator** (HIllya51): 参考其 UI 设计和 API 聚合方式。
*   **MQA (Muv-Luv QA)**: 参考其“数据库驱动的文本替换”逻辑。
*   **XUnity.AutoTranslator**: 参考其“运行时自动翻译与替换”的架构模式。

## 6. 总结

该方案满足了用户的所有核心需求：
1.  **通用性**: 基于 Hook 技术，不依赖特定文件解包器。
2.  **API 自定义**: 独立的 API 适配层。
3.  **打包输出**: 生成独立的 Loader 发布包，无需修改原游戏文件，风险更低，兼容性更强。
