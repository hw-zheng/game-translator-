# Universal AI Galgame Translator 设计方案 (v2.0 优化版)

## 1. 概述 (Overview)

本方案旨在设计一款 **通用型 (Engine-Agnostic)** 的 Galgame 自动化汉化工具。
鉴于用户需求为“不受游戏引擎影响”且最终需要“打包输出”，本方案采用 **运行时注入 (Runtime Injection)** 与 **虚拟打包 (Virtual Packing)** 相结合的架构。

**v2.0 更新**: 针对注入式汉化常见的“排异反应”（编码冲突、内存溢出、文本碎片化），本方案引入 **Hybrid 模式 (Hook 替换 + Overlay 覆盖)** 以及 **文本防抖与清洗机制**。

## 2. 核心架构 (Core Architecture)

软件由四个核心模块组成，重点增强了稳定性和兼容性：

### 2.1 模块一：增强型文本钩子 (Robust Text Hooker)

复用 [Textractor](https://github.com/Artikash/Textractor) (C++) 技术，但增加了以下防御机制：

*   **文本防抖 (Debouncer)**:
    *   **问题**: 游戏逐字输出 (我..爱..你) 导致 Hook 抓取碎片。
    *   **解决**: 引入 `TextBuffer`，当接收到文本时，设置一个短计时器 (e.g., 50ms)。只有计时器结束且后续无新文本时，才视为一句完整话语提交给 AI。
*   **垃圾过滤 (Garbage Filter)**:
    *   **问题**: Hook 抓到系统日志或文件名。
    *   **解决**: 使用正则过滤。只处理包含假名/汉字且长度 > 2 的文本。忽略纯 ASCII 或纯数字行。

### 2.2 模块二：AI 翻译核心与文本清洗 (Sanitizer & AI Core)

*   **控制符保护 (Control Code Protection)**:
    *   **问题**: AI 可能会吃掉 `\n` 或 `%s`，导致游戏崩溃。
    *   **解决**: 在发送给 AI 前，将 `%s`, `[color]` 等替换为安全占位符 `[[VAR_0]]`。翻译后，严格检查并还原占位符。
*   **上下文感知 (Context Aware)**:
    *   维护对话历史队列，解决主语省略问题。
    *   引入 **术语表 (Glossary)** 强制一致性。

### 2.3 模块三：混合显示系统 (Hybrid Display System)

这是解决“渲染排异”的关键。Loader 提供两种显示模式，用户/开发者可配置：

*   **Mode A: 内存直接替换 (Native Injection)**
    *   **适用**: 支持 UTF-8/GBK 的现代引擎 (Unity, Kirikiri 2 Z+)。
    *   **原理**: 直接修改内存中的文本字符串。
    *   **风险**: Shift-JIS 老游戏会乱码或溢出。
*   **Mode B: 覆盖层显示 (Overlay Mode) - *推荐默认***
    *   **适用**: 所有游戏，特别是老旧引擎。
    *   **原理**:
        1. Hook 拦截到日文文本。
        2. **屏蔽** 原游戏文本绘制 (将其替换为空格或透明色)。
        3. 在游戏窗口上方创建一个透明的 DirectX/GDI 窗口。
        4. 在与原文本相同的位置（坐标追踪）绘制高质量的中文文本。
    *   **优势**: 彻底规避编码限制 (Shift-JIS) 和内存溢出风险。

### 2.4 模块四：打包发布器 (Distributor)

生成独立的 "汉化启动包"：
*   `GameLoader.exe`: 启动器，负责注入 DLL 和管理 Overlay 窗口。
*   `trans_db.sqlite`: 预先翻译好的文本库。
*   `config.ini`: 指定显示模式 (Mode A/B)。

## 3. 风险评估与缓解 (Risk Mitigation)

| 风险点 | 描述 | 解决方案 (v2.0) |
| :--- | :--- | :--- |
| **Hook 不稳定** | 抓取到碎片文本或垃圾信息。 | **Python 端防抖 (Debouncer)** + **正则过滤器**。 |
| **编码排异** | Shift-JIS 游戏无法显示 GBK 中文，或显示乱码。 | **Overlay 模式**: 不在游戏内存渲染，而是在覆盖层绘制。 |
| **内存溢出** | 中文文本长度 > 日文原分配内存，导致崩溃。 | **Overlay 模式**: 外部渲染，无内存限制。**Mode A** 下截断文本或Hook分配函数。 |
| **AI 幻觉/格式错误** | AI 丢失控制符 (`%s`) 或换行。 | **占位符机制**: 将特殊符号替换为 `[[VAR]]` 再发给 AI，翻后还原。 |
| **杀毒误报** | Hook 行为被视为病毒。 | 在发布页明确提示添加白名单；尝试申请代码签名；开源 Loader 代码。 |

## 4. 技术栈调整 (Tech Stack)

*   **Core Logic**: Python (现已实现部分).
*   **Hook**: C++ (Textractor).
*   **Overlay**: C# (WinForms/WPF 透明窗体) 或 C++ (ImGui). *Overlay 需要紧跟游戏窗口坐标。*

## 5. 总结

v2.0 方案不再执着于“完美的原生替换”，而是务实地提供 **Overlay 兜底方案**。这极大地提高了通用性和稳定性，解决了“注入式汉化”最头疼的编码和崩溃问题。
