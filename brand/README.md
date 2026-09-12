# CSI OpenBase 品牌标识

这套标识把 OpenBase 定义为一套可靠、开放、以本地数据主权为先的创作者数据底座。

## 核心图形

图形由三部分组成：

- 右侧开口的外框同时表达 `Open` 与 CSI 家族中的字母 `C`；
- 两条不等长的数据记录表达采集、归档与可追溯快照；
- 更长的底边表达稳定的 `Base`，也让小尺寸图标保持清晰重心。

图形不绑定抖音或任何单一平台，也不使用数据库圆柱、AI 大脑、机器人等通用符号。

## 标准资产

| 文件 | 用途 |
| --- | --- |
| `svg/csi-openbase-lockup-horizontal.svg` | 默认横版主标，优先使用 |
| `svg/csi-openbase-lockup-stacked.svg` | 窄版、封面或居中版式 |
| `svg/csi-openbase-wordmark.svg` | 空间不适合放图形时使用 |
| `svg/csi-openbase-mark.svg` | 头像、应用内紧凑位置 |
| `svg/csi-openbase-mark-micro.svg` | 16 至 32 像素的小尺寸位置 |
| `svg/csi-openbase-favicon.svg` | 浏览器标签页专用的高对比底色版 |
| `svg/csi-openbase-lockup-horizontal-reversed.svg` | 深色背景 |
| `svg/csi-openbase-lockup-horizontal-mono.svg` | 单色印刷、雕刻或受限场景 |
| `svg/csi-openbase-app-icon.svg` | macOS 与通用应用图标母版 |
| `svg/csi-openbase-app-icon-windows.svg` | 带透明圆角安全区的 Windows 母版 |
| `png/csi-openbase-social-preview-1280x640.png` | GitHub 与社交分享预览 |
| `preview/csi-openbase-logo-system.png` | 全套标识总览 |

所有字标均已转换为矢量轮廓，不依赖用户设备上的字体。

## 颜色

| 名称 | 色值 | 用途 |
| --- | --- | --- |
| OpenBase Ink | `#1B2320` | 主体、字标、应用图标底色 |
| Open Teal | `#087F77` | 浅色背景上的数据记录与 CSI 标识 |
| Signal Teal | `#43B8AA` | 深色背景上的高对比强调 |
| Archive Mist | `#E4F4F1` | 品牌辅助底色 |
| White | `#FFFFFF` | 反白主体 |

默认浅色组合只使用 Ink 与 Open Teal；深色组合使用 White 与 Signal Teal。不要把现有界面的洋红色加入标志，以免形成对单一内容平台的视觉依赖。

## 留白与最小尺寸

以外框厚度为一个单位 `x`。标志四周至少保留 `1x` 留白，不放文字、边框或其他图形。

- 标志图形：屏幕最小 `16px`，小于 `32px` 时使用 micro 版；印刷最小 `6mm`。
- 横版主标：屏幕最小宽度 `200px`；印刷最小宽度 `38mm`。
- 竖版主标：屏幕最小宽度 `120px`。

## 使用规则

- 产品正式名称写作 `CSI OpenBase`；正文中可简称 `OpenBase`。
- 浅色底使用标准彩色版，深色底使用 reversed 版，单色工艺使用 mono 版。
- 应用图标应使用专用母版，不要把透明标志直接放进任意颜色方块。
- 不拉伸、旋转、描边、加阴影、加渐变或改变图形内部比例。
- 不交换 Ink 与 Teal 的角色，也不要单独使用两条数据记录作为标志。

## 资产维护

`svg/` 是唯一矢量母版；`png/`、ICO 与 macOS iconset 都由母版生成。修改母版后应重新导出全部位图，并在 `16px`、`32px`、浅色和深色背景上逐一检查。

这些资产随所在仓库的 `LICENSE` 与 `NOTICE` 一并分发。

## 产品接入位置

- Web：`admin_app/static/brand/`
- Windows：`CSI.OpenBase.Desktop/Assets/CSI.OpenBase.ico`
- macOS：`Packaging/AppIcon.iconset/`，构建时生成 `CSI-OpenBase.icns`
