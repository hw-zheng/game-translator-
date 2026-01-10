# 用户手册 (User Guide)

欢迎使用 **Universal Galgame AI Translator (UGT)**。这是一个通用的 Galgame AI 翻译工具，通过 Textractor 获取游戏文本，利用 AI (GPT, Claude, DeepSeek 等) 进行实时翻译，并在游戏上层以字幕形式显示。

## 目录
1. [准备工作](#1-准备工作)
2. [安装与配置](#2-安装与配置)
3. [如何启动](#3-如何启动)
4. [游戏连接指南 (Hook 设置)](#4-游戏连接指南-hook-设置)
5. [常见问题](#5-常见问题)

---

## 1. 准备工作

在使用本软件之前，请确保你已经准备好了以下组件：

1.  **本软件核心文件**: 即你当前所在的这个文件夹。
2.  **Textractor**: 一款通用的 Galgame 文本提取工具。
    *   **重要**: 本软件**不包含** Textractor，你需要自行下载。
    *   推荐版本: 5.2.0 或更高版本 (x86/x64 均可，推荐 x64)。
3.  **Python 环境** (仅开发模式需要): 如果你是直接运行源码，需要 Python 3.10+。如果是使用打包好的 `.exe`，则不需要。
4.  **API Key**: 你需要一个支持 OpenAI 格式的 API Key (例如 OpenAI, DeepSeek, OpenRouter 等)。

---

## 2. 安装与配置

### 2.1 放置 Textractor

为了让启动器能自动管理 Textractor，**必须**按照以下结构放置文件：

1.  找到本项目文件夹中的 `UniversalGalTrans/tools/` 目录 (发布版可能是 `tools/`)。
2.  在里面新建一个名为 `Textractor` 的文件夹。
3.  将你下载并解压的 Textractor 所有文件放入该文件夹。
    *   **正确路径示例**:
        *   `.../UniversalGalTrans/tools/Textractor/Textractor.exe`
        *   或者 `.../UniversalGalTrans/tools/Textractor/x64/Textractor.exe`

### 2.2 配置 API Key

首次运行时，软件通常会弹出一个向导。如果需要手动配置：

1.  打开 `UniversalGalTrans/core/config.py` (源码版) 或 `config.ini` (发布版)。
2.  找到 `API_KEY` 和 `BASE_URL` 字段。
3.  填入你的服务商信息。
    *   例如使用 DeepSeek: `BASE_URL="https://api.deepseek.com/v1"`, `MODEL="deepseek-chat"`.

---

## 3. 如何启动

### 方式一：源码运行 (开发人员)
1.  确保已安装依赖: `pip install -r UniversalGalTrans/requirements.txt`
2.  运行启动器:
    ```bash
    python UniversalGalTrans/launcher.py
    ```

### 方式二：发布版运行
1.  直接双击根目录下的 `Start.bat` 或 `UniversalGalTrans.exe`。

**启动成功标志**:
*   会弹出一个**黑色的透明长条窗口** (这是字幕栏)。
*   会自动启动 Textractor 窗口。
*   控制台显示 `Listening on http://localhost:5000`。

---

## 4. 游戏连接指南 (Hook 设置)

这是最关键的一步。本软件本身只是一个“翻译器 + 显示器”，它依赖 **Textractor** 来从游戏内存中“偷”出文本。

### 步骤 1: 启动器自动注入插件
当你通过本软件的 `launcher.py` 或 `Start.bat` 启动时，它会**自动检测** Textractor 目录，并强制安装一个名为 `ugt_hook.lua` 的插件到 Textractor 的扩展目录中。
*   你可以在控制台日志中看到: `UGT_Textractor: Installing extension to ...`。
*   这个插件负责把 Textractor 抓到的日文发送给翻译器。

### 步骤 2: 在 Textractor 中附加游戏
1.  保持本软件运行。
2.  打开你要玩的 Galgame。
3.  切换到自动弹出的 **Textractor** 窗口。
4.  点击左上角的 **"Attach to Game"**。
5.  在列表中选择游戏的进程 (通常是 `Game.exe` 或游戏名)，点击 OK。

### 步骤 3: 选择正确的文本钩子 (Hook)
1.  在游戏中点击鼠标，推进剧情，让游戏显示几句日文对话。
2.  观察 Textractor 的主窗口下拉框 (Console 区域上方)。
3.  Textractor 会自动搜索多个内存地址（称为 Hooks）。你需要**下拉选择**那个显示了**正确、干净的日文文本**的 Hook。
    *   *提示*: 这里的“正确”是指：不仅包含刚才那句话，而且当你继续玩游戏时，它能持续更新。
4.  **重要**: 确保该 Hook 的文本能够正常输出。

### 步骤 4: 验证翻译
一旦你在 Textractor 中选对了 Hook：
1.  Textractor 界面会显示日文。
2.  `ugt_hook.lua` 插件会自动拦截这段文本，并发回给本软件。
3.  你应该能看到本软件的**黑色字幕条**上出现“正在翻译...”或直接显示中文结果。

### 常见 Hook 问题
*   **乱码?** 尝试在 Textractor 中选择其他 Hook (如 `H-Code` 或其他地址)。
*   **重复字符 (我我我爱爱爱你)?** 这是游戏引擎特性。本软件内置了“防抖动”功能，会自动处理大部分重复，但如果 Textractor 输出太碎，可能需要手动寻找更好的 Hook。
*   **没有翻译?**
    *   检查控制台是否有报错。
    *   检查 Textractor 扩展是否启用 (默认是启用的)。
    *   确保 Textractor 里确实有日文流出。

---

## 5. 常见问题 (FAQ)

**Q: 为什么字幕条是黑的？**
A: 字幕条默认是半透明黑色背景。当有翻译结果时，文字会显示在上面。你可以拖动它改变位置。

**Q: 报错 `Connection Refused`?**
A: 确保服务器 (port 5000) 已启动。通常 `launcher.py` 会自动启动它。

**Q: 支持哪些 API?**
A: 理论上支持所有兼容 OpenAI 格式的 API。推荐使用 GPT-3.5/4 或 DeepSeek (性价比高)。
