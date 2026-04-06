# Zettelkasten — AI 驱动的 Obsidian 笔记整理工具

[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blue)](https://docs.anthropic.com/en/docs/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**用 AI 自动整理你的 Obsidian 知识库。** 把文件丢进收件箱，AI 自动拆分为原子笔记、构建双向链接、维护 MOC（内容地图）导航 — 基于 Claude Code 插件。

> 零依赖。不需要 Python、不需要脚本 — 纯 Claude Code skills + agents 实现。

[English](README.md)

## 痛点

你收藏文章、记录灵感、保存代码片段 — 然后它们就堆在文件夹里，**没有链接、逐渐遗忘**。手动整理笔记无法规模化，你的"第二大脑"始终是死的。

## 解决方案

这个插件把你的 Obsidian 仓库变成一个自组织的知识库：

- **原子化** — 每条笔记只包含一个概念，多主题文件自动拆分
- **改写** — 清晰的文字表述，保留所有原始信息
- **链接** — 每条笔记通过上下文 wikilink 连接到已有知识，偏好跨领域关联
- **导航** — 当某个标签积累 ≥3 条笔记时，自动生成 MOC（内容地图）

## 快速开始

### 1. 安装插件

```bash
# 在 Claude Code 中执行
/plugins install github:henrywen98/zettelkasten
```

### 2. 初始化仓库

```bash
cd /path/to/your/obsidian/vault
mkdir -p 0_inbox 1_zettel 2_maps 3_output 4_assets
git init  # 推荐，用于版本安全
```

### 3. 处理第一批笔记

把任意文件（笔记、网页剪藏、文章导出）放入 `0_inbox/`，然后：

```bash
cd /path/to/your/vault
claude
```

```
> /zet-ingest
```

完成。原子笔记出现在 `1_zettel/` 中，按年月组织，互相链接，MOC 导航在 `2_maps/`。

## 功能

### `/zet-ingest` — 收件箱 → 知识库

核心工作流。扫描 `0_inbox/`，分批派发 AI agent 处理（每批 ~10 个文件），然后更新 MOC 并 git 提交。

每个文件经历：**读取 → 分类 → 原子化 → 改写 → 元数据 → 建链接 → 写入**

```
0_inbox/每周学习笔记.md              →  1_zettel/2026-04/ssh-key-authentication.md
  (SSH + Python装饰器 + Docker)         1_zettel/2026-04/python-decorator-patterns.md
                                        1_zettel/2026-04/docker-compose-networking.md
```

- 多主题文件自动拆分为独立的原子笔记
- 每条笔记至少链接到 1 条已有笔记（强制连接）
- 保持原始语言（中文写的笔记保持中文）
- 处理后删除源文件 — 收件箱保持清洁

### `/zet-query` — 向知识库提问

用自然语言查询你积累的知识。AI 通过 MOC 和笔记链接导航，阅读相关笔记，生成带 `[[wikilink]]` 引用的综合回答。

```
> /zet-query 我关于认证方面知道什么？
```

输出保存到 `3_output/`，附完整来源引用。

### `/zet-lint` — 仓库健康检查

结构完整性扫描：

- 指向不存在笔记的断链
- 没有入站或出站链接的孤立笔记
- 不完整的元数据（缺少必填字段）
- MOC 覆盖空白 — 未被分类的笔记
- 过时的 MOC 计数

可自动修复常见问题。

## 仓库结构

```
Vault/
├── 0_inbox/        在此放入素材（处理后删除）
├── 1_zettel/       永久笔记 — 原子化、已链接、按年月组织
│   └── YYYY-MM/    如 2026-04/
├── 2_maps/         内容地图 — 自动维护的主题导航
├── 3_output/       查询结果、健康检查报告
└── 4_assets/       图片和附件
```

## 笔记格式

每条永久笔记遵循统一的 YAML frontmatter 结构：

```yaml
---
id: "202604061430"
title: "SSH 密钥认证原理"
created: 2026-04-06
processed: 2026-04-06
source: web-clip          # original | web-clip | import
tags: [ssh, security, devops]
summary: "SSH 密钥认证的工作原理 — 密钥生成、交换和验证流程"
---

# SSH 密钥认证原理

[笔记正文...]

## Links
- Related to [[tls-handshake-protocol]]: 都使用非对称加密进行初始认证
- See [[server-hardening-checklist]]: SSH 密钥认证是服务器加固的关键步骤
```

## 工作原理

```
/zet-ingest
    │
    ▼
zet-ingest (skill)          ← 编排器：扫描、分批、派发、MOC、提交
    │
    ├── zet-worker (agent)  ← 第 1 批：读取 → 原子化 → 改写 → 链接 → 写入
    ├── zet-worker (agent)  ← 第 2 批：可链接到第 1 批的笔记
    └── ...                 ← 顺序处理，每批提交后再开始下一批
```

| 组件 | 职责 |
|------|------|
| **zet-ingest** | 编排器 — 扫描收件箱、分批文件、派发 worker、更新 MOC、git 提交 |
| **zet-worker** | 文件处理器 — 读取、原子化、改写、链接、写入。每批 ~10 个文件 |
| **zet-query** | 知识问答 — 通过 MOC + 全文搜索回答问题 |
| **zet-lint** | 健康检查 — 发现结构问题，提供自动修复 |

批次顺序执行 — 每批提交后再开始下一批。后续批次能发现并链接到之前创建的笔记，逐步提高链接质量。你可以在批次之间随时中断，已完成的工作不会丢失。

## 系统要求

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)（CLI、桌面应用或 IDE 扩展）
- Obsidian 仓库（或任何 Markdown 文件夹）
- 仓库内初始化 Git（推荐）

## 模型推荐

| 模型 | 适用场景 |
|------|----------|
| **Sonnet** | 日常处理 — 速度快、可靠、链接质量好 |
| **Opus** | 高价值内容 — 原子化判断和跨领域链接质量最佳 |

## 相关概念

- [Zettelkasten 方法](https://zettelkasten.de/introduction/) — 本插件背后的笔记方法论
- [原子笔记](https://notes.andymatuschak.org/Evergreen_notes_should_be_atomic) — Andy Matuschak 论为何每条笔记只写一个概念
- [内容地图 MOC](https://www.linkingyourthinking.com/) — Nick Milo 的 MOC 概念，用于导航链接笔记
- [打造第二大脑](https://www.buildingasecondbrain.com/) — Tiago Forte 的 PARA 方法，组织数字知识

## 灵感来源

受 [Andrej Karpathy](https://karpathy.ai/) 关于用 AI 构建个人知识库的理念启发 — 让机器处理整理工作，你专注于思考。

## 联系方式

问题、建议或反馈？请联系 **henrywen98@gmail.com**

## 许可证

MIT
