/**
 * AI Daily Digest + GitHub Trending Handler
 * 每日汇总：GitHub 热门飙升榜 + AI 领域重要新闻
 */

const { web_search, message, sessions_spawn } = require('/root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/node_tools.js');

(async () => {
  const today = new Date().toISOString().split('T')[0];
  
  console.log(`🚀 开始生成 ${today} 的每日摘要...`);
  
  // 并行获取 GitHub Trending 和 AI 新闻
  const [githubResult, aiNewsResult] = await Promise.all([
    web_search({
      query: `GitHub trending ${today} most stars today rising repositories`,
      count: 10
    }),
    web_search({
      query: `AI artificial intelligence news ${today} important updates`,
      count: 10
    })
  ]);
  
  console.log(`✅ GitHub 搜索结果: ${githubResult.length} 条`);
  console.log(`✅ AI 新闻搜索结果: ${aiNewsResult.length} 条`);
  
  // 解析 GitHub Trending Top 5
  const githubItems = (githubResult || []).slice(0, 5).map((item, i) => {
    return `${i + 1}. **${item.title || 'Unknown'}**\n   ⭐ ${item.description || 'No description'}\n   🔗 ${item.url || '#'}`;
  }).join('\n\n');
  
  // 解析 AI 新闻 Top 5
  const aiNewsItems = (aiNewsResult || []).slice(0, 5).map((item, i) => {
    return `${i + 1}. ${item.title || 'No title'}\n   📰 ${item.description || ''}\n   🔗 ${item.url || ''}`;
  }).join('\n\n');
  
  // 构建消息
  const digestMessage = `📊 **${today} 每日技术摘要**\n\n` +
    `---` +
    `\n\n` +
    `### 🔥 GitHub 热门飙升榜 (今日)` +
    `\n\n${githubItems || '暂无数据'}\n\n` +
    `---` +
    `\n\n` +
    `### 🤖 AI 领域重要新闻` +
    `\n\n${aiNewsItems || '暂无新闻'}\n\n` +
    `---` +
    `\n\n` +
    `⏰ 生成时间: ${new Date().toLocaleString('zh-CN')}`;
  
  console.log('📤 准备发送到飞书...');
  
  // 发送到飞书（通过 message 工具）
  await message({
    action: 'send',
    message: digestMessage
  });
  
  console.log(`✅ 每日摘要推送完成！`);
})();
