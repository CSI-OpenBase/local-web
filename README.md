# CSI OpenBase for Python

<p align="center">
  <img src="brand/svg/csi-openbase-lockup-horizontal.svg" alt="CSI OpenBase" width="420">
</p>

这是 CSI OpenBase 的完整 Python 源码项目，包含抖音创作者授权、创作者中心表格导出、主页视频本地归档与分组、用户手动触发的匿名化评论导出，以及本地 Web 界面。

品牌母版、配色与使用规范见 [`brand/`](brand/README.md)。

正式仓库：[CSI-OpenBase/local-web](https://github.com/CSI-OpenBase/local-web)

SSH 克隆地址：`git@github.com:CSI-OpenBase/local-web.git`

本项目是共享 Python 后端的规范上游。Windows 程序可从源码、wheel 或冻结后端接入；macOS 仓库为独立构建保存一份受控的 `python-web/` 源码快照，并在其中的 `UPSTREAM.md` 记录同步提交。平台主机分别维护在 [CSI-OpenBase/winform](https://github.com/CSI-OpenBase/winform) 和 [CSI-OpenBase/mac](https://github.com/CSI-OpenBase/mac)，三个仓库可分别克隆、构建和发布；共享后端变更需要显式同步并分别验证。

## Requirements

- Python 3.12+
- Chromium 支持的 Windows、macOS 或 Linux 环境

## Install and run

在本目录执行：

```powershell
python -m pip install -e ".[test]"
python -m playwright install chromium
csi-openbase
```

也可以直接运行：

```powershell
python scripts/run_openbase.py
```

程序默认监听 <http://127.0.0.1:8000/>。源码运行时数据默认保存在本项目的 `var/`；从 wheel 安装后，数据默认保存在当前用户的平台应用数据目录（Windows 为 `%LOCALAPPDATA%\CSI OpenBase`，macOS 为 `~/Library/Application Support/CSI OpenBase`，Linux 遵循 XDG data 目录）。通过 `CSI_OPENBASE_HOME` 指定归档工作目录，通过 `CSI_OPENBASE_SESSION_HOME` 指定浏览器登录态目录。

旧的多工作区管理入口仍可通过 `csi-openbase-dashboard` 或 `python scripts/run_dashboard.py` 启动，供既有源码部署继续使用。当前后台没有公网多用户认证，不应直接暴露到公网。

## Version

根目录 `VERSION` 是应用、Python 包和发布版本号的唯一来源。版本格式为 `x.x.xx`，从 `0.0.10` 开始；末段从 `10` 递增到 `99`，之后将次版本加一并把末段重置为 `10`，例如 `1.1.99` 的下一版本是 `1.2.10`。

查看下一版本但不修改文件：

```powershell
python scripts/bump_version.py
```

确认发布后写入下一版本：

```powershell
python scripts/bump_version.py --apply
```

## Data model

- 一个工作目录对应一个创作者账号；桌面端由用户选择目录，源码版默认使用 `var/local`。
- 页面时间、任务时间、导出清单以及按日期时间生成的目录统一使用北京时间（UTC+08:00）；数据库和规范化数据字段继续使用 UTC，读取时再转换显示。
- 每次创作者中心导出保存到 `exports/<日期时间>/`，并生成包含状态、大小和 SHA-256 的 manifest。
- 作品发现批次位于 `works/discovery/`，逐视频档案位于 `works/videos/douyin/`；“同步作品档案”从已授权的抖音创作者中心内容管理页读取完整作品列表，“查看视频档案”进入独立详情页，将视频、标题和描述作为三个独立字段，并分页列出发布时间、分组、五项可见指标、档案时间和采集来源。首页“发布时间”按北京时间显示作品发布时间，“评论数”显示平台最后一次返回的总数及相对上一次的数量变化。
- 视频档案页可以把全部已同步作品导出为 XLSX。视频 ID、标题和发布时间固定必选；用户可以选择是否包含描述、视频链接、分组、五项指标、档案时间、观测时间和采集来源。
- 作品档案同步会识别作品所属的抖音栏目并创建同名平台分组；用户也可以创建、重命名和删除本地分组，批量加入或移出作品。平台栏目与用户分组彼此独立。
- “获取最新评论”只更新评论总数和变化量，不下载评论内容。“导出评论”完成结构校验后，只把相对本地评论索引新增或发生变化的匿名评论写入交付文件；“完整重新同步”输出本次可访问的完整快照。
- 根评论与回复分页完整、回复声明匹配且关系有效时，采集按当前可访问范围完成；抖音显示总数更高时保留“可能存在已删除、审核隐藏或暂不可见评论”的提示，不将汇总数差异单独视为采集失败。
- 任务记录位于独立的 `/tasks` 页面，首页只保留常用采集操作、视频档案和数据管理；任务运行状态仍通过 `/api/state` 实时更新。带视频 ID 的任务可直接跳转到对应作品所在的档案分页。
- 每个评论批次都保留完整快照、增量或完整交付文件和 `manifest.json`；逐视频 `comments/comments.jsonl` 保存跨批次合并的最新状态。首次增量导出会把全部可访问评论作为基线；新增或更新的回复会附带独立校验所需的父评论和根评论上下文，平台当前不可见的历史评论不会自动从本地索引删除。
- 评论正文采集按“人类平均速度的 130%”运行：打开评论页后等待约 2.31 秒；每次展开后等待 500ms 渲染，再按基础 1 秒加每条新评论约 269ms 阅读，最高 5 秒；滚动后保留 1 秒扫读时间。程序仍保持“点击、阅读、点击、阅读”，达到严格完整性条件后立即结束；大量回复的默认保护上限为 600 秒。
- 顶部“设置”可指定评论导出目录；设置后，每个成功或部分完成批次的交付文件会额外复制到 `<设置目录>/<视频ID>/<日期时间>/`。增量模式复制新增与变更记录，完整同步模式复制完整快照。
- `openbase.sqlite3` 保存本地索引和任务状态；原始下载及不可变快照仍是数据源。
- 页面可按范围清空本地数据，具体边界见 [清空本地数据](#清空本地数据)。
- 默认不下载视频 MP4，不保存观众昵称、用户 ID、头像、属地或创作者平台密码。

完整模型见 [`docs/data-model.md`](docs/data-model.md)，数据契约位于 [`admin_app/resources/`](admin_app/resources/)。

## Connect works to CSI

OpenBase can export a privacy-minimal XLSX work archive containing exactly the
Douyin video ID, title, and Beijing publish time:

```powershell
csi-openbase-export-links
```

The command writes `作品档案-<timestamp>.xlsx` under the configured `exports/`
directory. Upload that file from CSI's **数据连接** page. CSI first
previews unique matches inside the currently selected creator account and only
stores links after explicit confirmation. The workbook never contains browser
sessions, platform credentials, creator login identity, or viewer identity.

## 清空本地数据

在本地页面底部的“数据管理”区域点击“清空数据”，确认当前工作目录后选择清理范围：

| 清理范围 | 删除内容 | 保留内容 |
| --- | --- | --- |
| 平台导出的原始数据 | `exports/` 中已下载的表格、对应导出任务记录及最近导出状态 | 视频档案、评论数据、账号索引和浏览器登录授权 |
| 用户评论数据 | 各视频内部 `comments/` 目录、评论导出任务记录、已导出评论数及最近导出时间 | 视频档案、平台最后一次返回的评论总数和变化量、评论导出目录设置、指定目录中的用户副本、原始表格和浏览器登录授权 |
| 全部数据 | `exports/`、`works/` 及 SQLite 中的账号、视频、分组和任务索引 | 工作目录本身、评论导出目录设置及其中的用户副本、根目录中的其他文件与目录、SQLite 文件及表结构、运行日志和浏览器登录授权 |

清空操作无法撤销，需要在对话框中明确确认；存在等待中或运行中的任务时不能执行。清空“全部数据”后，本地账号索引会被移除，下一次采集前需要重新校验创作者账号，但已保存的浏览器登录授权不会被主动删除。

`exports/` 和 `works/` 是 CSI OpenBase 托管目录，清空对应范围会删除其中全部内容。设置的评论导出目录是用户管理的输出位置，清空数据不会删除其中的副本；程序也不允许把它设置到 `exports/`、`works/` 或浏览器授权目录内。需要长期保留的数据应先备份到托管目录之外。检测到符号链接、Windows 目录联接点、文件系统挂载点，或清理范围与浏览器授权目录重叠时，程序会拒绝清空；中断的清理操作会在下次启动时根据事务状态自动恢复或继续完成。

## Repository layout

```text
./
  admin_app/                 本地后台、采集、任务、分析和页面资源
  docs/                      架构与数据模型文档
  migrations/                兼容管理后台的数据库迁移
  scripts/                   启动、工作区、导入和分析命令
  tests/                     自动化测试与样本
  var/README.md              本地数据与备份说明
  VERSION                    应用、Python 包和发布版本号
  pyproject.toml             包、依赖、命令入口和测试配置
```

`var/`、`workspace-data/`、浏览器会话以及导出的表格均由 Git 忽略。Git 忽略不是加密，公开源码包或问题报告不应包含这些数据。

如果从旧仓库路径迁移，工作数据会继续保留；源码版默认会话目录包含工作目录绝对路径的哈希，因此目录改名后可能需要重新进行一次创作者授权。也可以将 `CSI_OPENBASE_SESSION_HOME` 显式指向原会话目录。

## Verify

```powershell
python -m pytest
python -m compileall -q admin_app scripts
python -m pip wheel . --no-deps --wheel-dir dist
```

## License

CSI OpenBase is licensed under the Apache License 2.0.

This license applies only to the code and documentation contained
in this repository.

CSI proprietary scoring models, weights, industry benchmarks,
commercial report logic, CSI Core components and services provided
through aicsi.cn are not included in this repository and are not
licensed under Apache-2.0.
