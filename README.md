<h1 align="center">ClipNote</h1>

<p align="center">
  <b>小红书视频 → 逐字稿 + AI 摘要 → Obsidian 笔记</b><br>
  <i>一个 Claude Code Skill。丢进去一个链接，出来一篇永久保存的笔记。</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-violet" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/ASR-SenseVoice-brightgreen" alt="ASR">
</p>

---

## 这是什么？

收藏夹里的干货视频，99% 不会再打开第二次。

ClipNote 让你刷到好东西时直接保存——**下载 → ASR 转写 → AI 润色+摘要 → 写入 Obsidian**，全程静默完成。以后搜关键词就能找到，不用重看视频。

## 系统要求

- macOS / Linux / Windows
- **Python 3.10 ~ 3.12**（Python 3.13+ 部分科学计算包可能缺少 wheel）
- [Claude Code](https://claude.ai/code)（终端版）
- ffmpeg：`brew install ffmpeg`（macOS）或从 [ffmpeg.org](https://ffmpeg.org/) 下载（Windows）

## 快速开始

### 安装（给 Claude 的一句话指令）

直接把下面这句话发给你的 Claude Code agent，它会自动完成所有安装：

```
Clone https://github.com/ethanl-dev/Clipnote-skill.git into ~/.claude/skills/clipnote.skill, then run the setup script (scripts/setup.sh on macOS/Linux, scripts/setup.ps1 on Windows), then create a config.json from config.example.json and prompt me for the values.
```

### 手动安装

**macOS / Linux：**

```bash
# 克隆到 Claude Code skills 目录（只有这样 /clipnote 才能被识别）
git clone https://github.com/ethanl-dev/Clipnote-skill.git ~/.claude/skills/clipnote.skill
cd ~/.claude/skills/clipnote.skill
bash scripts/setup.sh
```

**Windows（PowerShell）：**

```powershell
# 克隆到 Claude Code skills 目录
git clone https://github.com/ethanl-dev/Clipnote-skill.git $env:USERPROFILE\.claude\skills\clipnote.skill
cd $env:USERPROFILE\.claude\skills\clipnote.skill
.\scripts\setup.ps1
```

### 触发方式

在 Claude Code 中，两种方式触发：

**手动调用：**
```
/clipnote http://xhslink.com/xxxxx
```

**自动检测：** 直接把小红书链接粘贴到对话中，ClipNote 会自动识别并开始处理。不需要记住任何命令。

## 功能

| 能力 | 说明 |
|------|------|
| **一键摘录** | 小红书分享链接 → 完整笔记，无需任何手动操作 |
| **高精度转录** | SenseVoice Small 本地 CPU 运行，不上传音频 |
| **AI 润色摘要** | Claude 清洗语义、标注转写疑点、生成 3-5 行摘要 |
| **智能降级** | 任一步骤失败不影响后续，最大化产出 |
| **Obsidian 原生** | 自动写入 vault，带 frontmatter 标签 |
| **优雅降级** | 无 Obsidian 则输出到 `~/Desktop/ClipNote/` |

## 配置

```json
{
  "vault_path": "/Users/yourname/obsidian-vaults/main",
  "output_dir": "ClipNote",
  "sensevoice_model": "small",
  "xhs_cookie": "",
  "xhs_proxy": ""
}
```

| 字段 | 说明 |
|------|------|
| `vault_path` | Obsidian vault 路径 |
| `output_dir` | 笔记存放子目录 |
| `xhs_proxy` | 代理地址，如 `http://127.0.0.1:7890`（海外用户必填） |
| `xhs_cookie` | 小红书 Cookie（可选，填了能下载高清） |

## 产出示例

```markdown
---
date: 2026-05-11
source: 小红书
tags: [clipnote, 待整理]
---

# 视频标题

## AI 摘要
...

## 逐字稿
润色后的完整转录

---
*created by Clipnote Ethan*
```

## 隐私

ASR 在本地 CPU 执行，音频不上传云端。仅润色文本经 Claude API 处理。

## 参考

- [XHS-Downloader](https://github.com/JoeanAmier/XHS-Downloader) — 小红书数据解析思路参考
- [SenseVoice](https://github.com/FunAudioLLM/SenseVoice) — 高精度语音识别模型
- [funasr](https://github.com/modelscope/FunASR) — SenseVoice 推理框架

## 许可

MIT

---

<p align="center">
  <i>Clip Smart. Note Better.</i><br>
  <a href="https://github.com/lyx20050904-lgtm">@lyx20050904-lgtm</a>
</p>
