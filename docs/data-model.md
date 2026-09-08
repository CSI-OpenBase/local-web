# 数据模型

CSI OpenBase 使用工作区外壳和四类不可变业务快照。JSON Schema 位于 `admin_app/resources/`，MySQL 表定义位于 `mysql-schema.sql`。

## 工作区

`workspace.json` 只保存非敏感配置：工作区 slug、展示名、平台、可选主页 URL 和数据库名。MySQL 密码、Cookie 和浏览器会话不进入该文件。

## 账号画像

`account/profile-snapshots.jsonl` 保存账号在某个观测时间的聚合计数：粉丝、关注、获赞和作品数。相同平台和观测时间只能有一个快照。

## 受众画像

`account/audience-snapshots.jsonl` 将创作者中心展示的聚合分布规范化为 `dimension / segment / share`。例如年龄、性别或活跃时间段。这里只保存群体比例，不保存任何观众账号标识。

## 作品表现

`works/work-snapshots.jsonl` 保存作品在某个观测时间的播放、互动、留存、主页访问和涨粉数据。系统识别官方作品 ID、视频 ID、`item_id` 与 `aweme_id` 等常见表头；仅在导出文件缺少稳定 ID 时，才使用标题与发布时间生成合成 ID。同一作品多次导入会保留时间序列。

## 评论

`comments/comments.jsonl` 保存每条评论的最新状态，`comments/batches/` 保存历史采集批次。评论仅区分观众和创作者角色，不保存昵称、用户 ID、头像或属地。MySQL 同时保留最新态和不可变快照。

评论采集目标位于 `comments/collection-targets.json`。后台既可导入这份完整 manifest，也接受以下简化 JSON；直接作品 URL 中的数字 ID 会自动提取，未分组作品归入“全部作品”：

```json
{
  "videos": [
    {
      "video_url": "https://www.douyin.com/video/1234567890123456789",
      "title": "作品标题"
    }
  ]
}
```

目标导入采用完整清单替换语义。服务端补齐合集、集号、计数和时间戳，严格校验后与 `collection-progress.json` 原子更新；仍在新清单中的视频保留原采集状态，移除目标不会删除已有评论。
已有工作区的 `scope_id` 不允许通过 Web 上传改变；数据库同步也会清理同一平台上被新清单取代的旧 scope 状态。

## 分析输出

`reports/` 保存账号基础分析和评论分析。基础分析目前包括作品分布、互动率、主页访问率、涨粉转化、评论问题需求和数据覆盖提示。所有比率都能由本地快照直接复算，不应解释为平台因果关系或收益承诺。
