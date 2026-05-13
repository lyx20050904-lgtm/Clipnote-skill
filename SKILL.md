---
name: clipnote
description: 丢进去一个小红书链接，出来一篇带 AI 摘要和润色逐字稿的 Obsidian 笔记
---

# ClipNote - 视频摘录工具

将小红书视频内容摘录为 Obsidian 笔记的自动化管线。

运行 `python` 命令时始终使用 Skill 自带虚拟环境的 Python（macOS/Linux: `.venv/bin/python`，Windows: `.venv\Scripts\python.exe`）。

## 调用方式

用户输入 `/clipnote <url>` 时执行以下完整流程。

## 工作流程

> **静默执行规则：** 全程所有步骤的输出都对用户保持隐形。不要展示下载日志、进度条、模型加载信息、原始转录文本、润色过程或润色后的全文。每个步骤只需输出简短的状态（如"下载完成""转录完成"），最终只展示笔记路径和摘要预览。

### Step 1: 验证链接

确认链接是小红书有效链接（xhslink.com 或 xiaohongshu.com）。

### Step 2: 下载视频

```bash
python scripts/download.py "<url>" "<临时工作目录>"
```
（从 skill 目录运行，使用 skill 虚拟环境的 python）

成功时返回 JSON，包含 `title`, `author`, `video_path` 等字段。
失败时（exit code 1）提示用户链接无效或需要 Cookie。

### Step 3: 提取音频

```bash
python scripts/extract.py "<video_path>" "<工作目录>/audio.wav"
```

成功输出音频路径。失败则跳过转录，仅做 AI 总结（不含逐字稿）。

### Step 4: 转录

```bash
python scripts/transcribe.py "<audio_path>"
```

返回 JSON: `{"text": "..."}`。失败则跳过逐字稿。

### Step 5: LLM 润色 + 总结（静默执行）

你（Claude）直接对原始转录文本执行以下操作。**整个过程在后台静默完成，不要将润色后的全文展示给用户。**

**5a. 格式润色**（不改变原意）
- 添加中文标点（。，！？；：""等），不要替换原文用词
- 按语义切分段落（每个段落聚焦一个子话题）
- 删除 ASR 产生的连续填充词（如"嗯嗯嗯呃呃"），但保留语气词节奏

**5b. 语义润色**（最小改动原则）
- 只修改明显不通顺的语句，做最小幅度的调整
- 不改变原意、不补充原文没有的信息
- 拿不准的地方保留原文

**5c. 不确定性标注**
- 在你认为转写可能不准确的位置，用 `〔存疑：原因〕` 格式标注
- 常见的不确定信号：ASR 特有的同音错字、语义断裂、奇怪的专有名词

**5d. 生成摘要**
- 一段 3-5 行的中文内容摘要，概括视频核心观点

### Step 6: 写入笔记

```bash
python scripts/write_note.py '<json_data>'
```

其中 json_data 需要包含：
- `title` — 视频标题
- `author` — 博主名
- `url` — 原始链接
- `duration` — 时长（如果没有，写 "未知"）
- `summary` — AI 摘要
- `transcript` — **润色后**的转录全文（含 `〔存疑〕` 标记）
- `uncertain_sections` — 不确定内容列表（可选，每个元素含 `text` 和 `reason`）

**输出路径策略：**
1. 如果 `config.json` 中 `vault_path` 存在且有效，则写入 `<vault_path>/<output_dir>/`
2. 如果 vault 不存在，自动降级到 `~/Desktop/ClipNote/`
3. 笔记文件自动在文件名后追加（如果同名文件已存在则覆盖）

**作者签名：** 每篇笔记末尾自动附上个人品牌信息：

```
---
*created by Clipnote Ethan*
*Contact: lyx20050904@gmail.com*
```

### Step 7: 返回结果（简洁输出）

向用户展示（**不要展示润色后的全文，全程保持静默**）：
- **笔记已生成：** `<绝对路径>`（必须是完整绝对路径，方便用户直接访问）
- **摘要预览**（前 3-5 行，简洁呈现）
- 可选操作：`[补充]` `[追问]` `[再摘一条]`

## 降级策略

- 如果 Step 2 失败：告知用户，建议手动录屏
- 如果 Step 3/4 失败：跳过逐字稿，仅出 AI 摘要
- 每个步骤都不阻塞后续步骤

## 配置

`config.json` 位于 skill 根目录，包含：
- `vault_path`: Obsidian vault 根路径
- `output_dir`: 笔记存放子目录
- `sensevoice_model`: small | large
- `xhs_cookie`: 小红书 Cookie（可选，不设只能下载低清视频）
- `xhs_proxy`: HTTP 代理地址（可选，海外访问需配置，如 `http://127.0.0.1:7890`）
