# AI Daily Digest + GitHub Trending Skill

每日汇总：GitHub 热门飙升榜 + AI 领域重要新闻，发送到飞书。

## 触发方式

手动调用或集成到定时任务：
```
使用 sessions_spawn 调用此 skill
```

## 功能

1. **GitHub 热门飙升榜** - 抓取今日星标增长最快的项目
2. **AI 新闻摘要** - 汇总 AI 领域重要新闻和进展
3. **飞书推送** - 格式化后发送到飞书用户

## 配置

无需额外配置。使用 OpenClaw 的主模型 API 配置。

## 输出格式

发送到飞书，包含：
- 📊 GitHub Trending（今日飙升榜 Top 5）
- 🤖 AI News（每日重要新闻摘要）
- ⏰ 发布时间

## 依赖

- `web_search` - 搜索 GitHub 趋势和 AI 新闻
- `message` - 发送到飞书
