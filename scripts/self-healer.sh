#!/bin/bash
# OpenClaw Self-Healer - 定时任务和工具异常自动修复脚本
# 运行频率: 每小时检查一次

LOG_FILE="/var/log/openclaw_self_healer_$(date +%Y%m%d).log"
EMAIL_TO="admin@example.com"  # 可替换为实际邮箱

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 1. 检查定时任务健康状态
check_cron_health() {
    log "=== 检查定时任务健康状态 ==="
    
    # 检查 cron 服务是否运行
    if ! pgrep -x "crond" > /dev/null; then
        log "⚠️ 检测到 cron 服务未运行，尝试重启..."
        /etc/init.d/crond restart 2>/dev/null || systemctl restart crond 2>/dev/null || service crond restart 2>/dev/null
        if pgrep -x "crond" > /dev/null; then
            log "✅ cron 服务已重启成功"
        else
            log "❌ 无法重启 cron 服务，发送告警"
            return 1
        fi
    else
        log "✓ cron 服务运行正常"
    fi
    
    # 检查关键定时任务是否存在
    CRON_TASK="/www/server/cron/3ab48c27ec99cb9787749c362afae517"
    if [ ! -f "$CRON_TASK" ]; then
        log "⚠️ 关键定时任务脚本不存在，尝试重建..."
        recreate_cron_task
    else
        log "✓ 定时任务脚本存在"
    fi
}

# 2. 重建定时任务脚本
recreate_cron_task() {
    log "重建定时任务脚本..."
    
    cat > "$CRON_TASK" << 'SCRIPT'
#!/bin/bash
# AI Daily Digest + GitHub Trending Daily Push via OpenClaw CLI
# Runs at 12:00 Beijing Time (UTC 04:00)
LOG_FILE="/var/log/ai_daily_digest_$(date +%Y%m%d).log"
echo "=== AI Daily Digest + GitHub Trending Push: $(date) ===" > "$LOG_FILE"
cd /root/.openclaw/workspace
echo "Spawning sub-agent for AI Daily Digest + GitHub trending..." >> "$LOG_FILE"

su - root -c "cd /root/.openclaw/workspace && node -e '
const { sessions_spawn, web_search, message } = require(\"/root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/node_tools.js\");
(async () => {
  try {
    console.log(\"Starting AI Daily Digest + GitHub trending fetch...\");
    const today = new Date().toISOString().split(\"T\")[0];
    const [githubResult, aiNewsResult] = await Promise.all([
      web_search({ query: \"GitHub trending \" + today + \" most stars today rising repositories\", count: 10 }),
      web_search({ query: \"AI artificial intelligence news \" + today + \" important updates\", count: 10 })
    ]);
    const githubItems = (githubResult || []).slice(0, 5).map((item, i) => (i + 1) + \". **\" + (item.title || \"Unknown\") + \"**\\n ⭐ \" + (item.description || \"No description\") + \"\\n 🔗 \" + (item.url || \"#\")).join(\"\\n\\n\");
    const aiNewsItems = (aiNewsResult || []).slice(0, 5).map((item, i) => (i + 1) + \". \" + (item.title || \"No title\") + \"\\n 📰 \" + (item.description || \"\") + \"\\n 🔗 \" + (item.url || \"\")).join(\"\\n\\n\");
    const digestMessage = \"📊 **\" + today + \" 每日技术摘要**\\n\\n---\\n\\n### 🔥 GitHub 热门飙升榜 (今日)\\n\\n\" + (githubItems || \"暂无数据\") + \"\\n\\n---\\n\\n### 🤖 AI 领域重要新闻\\n\\n\" + (aiNewsItems || \"暂无新闻\") + \"\\n\\n---\\n\\n⏰ 生成时间: \" + new Date().toLocaleString(\"zh-CN\");
    await message({ action: \"send\", message: digestMessage });
    console.log(\"Push completed successfully\");
  } catch (err) {
    console.error(\"Push failed:\", err.message);
  }
})();
'" >> $LOG_FILE 2>&1
echo "=== Completed: $(date) ===" >> "$LOG_FILE"
SCRIPT
    
    chmod +x "$CRON_TASK"
    log "✓ 定时任务脚本已重建"
}

# 3. 检查 OpenClaw 服务健康状态
check_openclaw_health() {
    log "=== 检查 OpenClaw 服务健康状态 ==="
    
    # 检查 OpenClaw 进程
    if ! pgrep -f "openclaw" > /dev/null; then
        log "⚠️ OpenClaw 进程未检测到，尝试启动..."
        cd /root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw && nohup node openclaw.js > /var/log/openclaw.log 2>&1 &
        sleep 3
        if pgrep -f "openclaw" > /dev/null; then
            log "✅ OpenClaw 服务已重启"
        else
            log "❌ 无法启动 OpenClaw 服务"
            return 1
        fi
    else
        log "✓ OpenClaw 进程运行正常"
    fi
    
    # 检查关键配置文件
    for file in "/root/.openclaw/workspace/AGENTS.md" "/root/.openclaw/workspace/SOUL.md" "/root/.openclaw/workspace/MEMORY.md"; do
        if [ ! -f "$file" ]; then
            log "⚠️ 关键配置文件缺失: $file"
        else
            log "✓ 配置文件存在: $file"
        fi
    done
}

# 4. 检查磁盘空间和资源
check_resources() {
    log "=== 检查系统资源 ==="
    
    # 检查磁盘空间
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        log "⚠️ 磁盘空间不足: ${DISK_USAGE}%"
        # 清理日志文件
        find /var/log -name "*.log" -mtime +7 -delete 2>/dev/null
        log "已清理7天前的日志文件"
    else
        log "✓ 磁盘空间充足: ${DISK_USAGE}%"
    fi
    
    # 检查内存
    MEM_FREE=$(free | grep Mem | awk '{print $4/$2 * 100}')
    log "✓ 可用内存: ${MEM_FREE}%"
}

# 5. 检查网络连接
check_network() {
    log "=== 检查网络连接 ==="
    
    # 测试 GitHub 连接
    if ! curl -s --connect-timeout 5 https://github.com > /dev/null; then
        log "⚠️ GitHub 连接失败，尝试切换代理..."
        export HTTPS_PROXY="${HTTPS_PROXY:-http://proxy:7890}"
        if curl -s --connect-timeout 5 https://github.com > /dev/null; then
            log "✅ 代理连接成功"
        else
            log "❌ 网络连接异常，请检查代理设置"
        fi
    else
        log "✓ GitHub 连接正常"
    fi
}

# 6. 检查上次运行状态
check_last_run() {
    log "=== 检查上次定时任务运行状态 ==="
    
    LAST_LOG="/www/server/cron/3ab48c27ec99cb9787749c362afae517.log"
    if [ -f "$LAST_LOG" ]; then
        LAST_RUN=$(tail -5 "$LAST_LOG" | head -1)
        log "上次运行: $LAST_RUN"
        
        # 检查是否24小时内未运行
        LAST_RUN_TIME=$(stat -c %Y "$LAST_LOG" 2>/dev/null || echo 0)
        NOW_TIME=$(date +%s)
        DIFF=$((NOW_TIME - LAST_RUN_TIME))
        
        if [ $DIFF -gt 86400 ]; then
            log "⚠️ 定时任务超过24小时未运行，尝试手动触发..."
            /www/server/cron/3ab48c27ec99cb9787749c362afae517 >> "$LAST_LOG" 2>&1 &
        else
            log "✓ 定时任务运行正常"
        fi
    else
        log "⚠️ 未找到上次运行日志"
    fi
}

# 主流程
main() {
    echo "========================================" >> "$LOG_FILE"
    log "开始自动健康检查和修复..."
    
    check_cron_health
    check_openclaw_health
    check_resources
    check_network
    check_last_run
    
    log "自动修复检查完成"
    echo "========================================" >> "$LOG_FILE"
}

# 如果作为独立脚本运行
if [ "$1" = "--daemon" ]; then
    while true; do
        main
        sleep 3600  # 每小时检查一次
    done
else
    main
fi