# CSI OpenBase for Python

这是 CSI OpenBase 的完整 Python 源码项目，包含抖音创作者授权、创作者中心表格导出、主页视频本地归档、用户手动触发的匿名化评论导出，以及本地 Web 界面。

正式仓库：[CSI-OpenBase/local-web](https://github.com/CSI-OpenBase/local-web)

SSH 克隆地址：`git@github.com:CSI-OpenBase/local-web.git`

Windows 和 macOS 桌面程序使用本项目提供同一套本地后端，不另行实现采集逻辑。平台主机分别维护在 [CSI-OpenBase/winform](https://github.com/CSI-OpenBase/winform) 和 [CSI-OpenBase/mac](https://github.com/CSI-OpenBase/mac)，三个仓库可分别克隆、构建和发布。

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

## Data model

- 一个工作目录对应一个创作者账号；桌面端由用户选择目录，源码版默认使用 `var/local`。
- 每次创作者中心导出保存到 `exports/<日期时间>/`，并生成包含状态、大小和 SHA-256 的 manifest。
- 主页发现批次位于 `works/discovery/`，逐视频档案位于 `works/videos/douyin/`；同步时记录主页可见的评论数。
- 评论只在用户手动操作后导出，按视频和批次保存匿名化 `.jsonl`。
- `openbase.sqlite3` 保存本地索引和任务状态；原始下载及不可变快照仍是数据源。
- 默认不下载视频 MP4，不保存观众昵称、用户 ID、头像、属地或创作者平台密码。

完整模型见 [`docs/data-model.md`](docs/data-model.md)，数据契约位于 [`admin_app/resources/`](admin_app/resources/)。

## Repository layout

```text
./
  admin_app/                 本地后台、采集、任务、分析和页面资源
  docs/                      架构与数据模型文档
  migrations/                兼容管理后台的数据库迁移
  scripts/                   启动、工作区、导入和分析命令
  tests/                     自动化测试与样本
  var/README.md              本地数据与备份说明
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
