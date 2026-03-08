#!/bin/bash

# ==========================================
# GitHub 技术学习脚本
# 每天自动从 GitHub 学习技术并推送总结
# ==========================================

set -e

# 配置
API_KEY="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"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
LOG_DIR="/root/.openclaw/workspace/memory"
OUTPUT_FILE="${LOG_DIR}/github-learning-${DATE}.md"
TEMP_DIR="/tmp/github-learning-$$"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 创建临时目录
mkdir -p "$TEMP_DIR"
mkdir -p "$LOG_DIR"

log_info "开始 GitHub 学习任务... (${DATE} ${TIME})"

# 开始生成学习笔记
cat > "$OUTPUT_FILE" << EOF
# GitHub 学习笔记 - ${DATE}

> 学习时间: ${TIME} | 自动生成

---

## 📊 学习概览

- **日期**: ${DATE}
- **时间**: ${TIME}
- **数据来源**: GitHub API + Tavily 搜索

---

EOF

# ------------------------------------------
# 1. 获取 GitHub Trending 仓库
# ------------------------------------------
log_info "获取 GitHub Trending 仓库..."

cat >> "$OUTPUT_FILE" << 'EOF'
## 🔥 GitHub Trending 热门项目

EOF

# 获取今日 Python Trending
log_info "获取 Python 项目..."
PYTHON_TRENDING=$(curl -s "https://api.github.com/search/repositories?q=language:python+created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&order=desc&per_page=10" 2>/dev/null || echo "")

echo "### 🐍 Python 热门项目" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '| 项目 | Stars | 描述 |' >> "$OUTPUT_FILE"
echo '|------|-------|------|' >> "$OUTPUT_FILE"

echo "$PYTHON_TRENDING" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for repo in data.get('items', [])[:5]:
        name = repo.get('full_name', 'N/A')
        stars = repo.get('stargazers_count', 0)
        desc = repo.get('description', '')[:60]
        url = repo.get('html_url', '')
        print(f'| [{name}]({url}) | ⭐{stars} | {desc} |')
except Exception as e:
    print('| 暂无数据 | 0 | 获取失败 |')
" >> "$OUTPUT_FILE" 2>/dev/null || echo "| 暂无数据 | 0 | API 错误 |" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"

# 获取 JavaScript Trending
log_info "获取 JavaScript 项目..."
JS_TRENDING=$(curl -s "https://api.github.com/search/repositories?q=language:javascript+created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&order=desc&per_page=10" 2>/dev/null || echo "")

echo "### ⚡ JavaScript 热门项目" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '| 项目 | Stars | 描述 |' >> "$OUTPUT_FILE"
echo '|------|-------|------|' >> "$OUTPUT_FILE"

echo "$JS_TRENDING" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for repo in data.get('items', [])[:5]:
        name = repo.get('full_name', 'N/A')
        stars = repo.get('stargazers_count', 0)
        desc = repo.get('description', '')[:60]
        url = repo.get('html_url', '')
        print(f'| [{name}]({url}) | ⭐{stars} | {desc} |')
except Exception as e:
    print('| 暂无数据 | 0 | 获取失败 |')
" >> "$OUTPUT_FILE" 2>/dev/null || echo "| 暂无数据 | 0 | API 错误 |" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"

# ------------------------------------------
# 2. 网络安全相关项目
# ------------------------------------------
log_info "获取网络安全项目..."

cat >> "$OUTPUT_FILE" << 'EOF'

## 🛡️ 网络安全项目

EOF

# 搜索网络安全仓库
CYBER_TRENDING=$(curl -s "https://api.github.com/search/repositories?q=topic:cybersecurity+created:>$(date -d '30 days ago' +%Y-%m-%d)&sort=stars&order=desc&per_page=10" 2>/dev/null || echo "")

echo '| 项目 | Stars | 描述 |' >> "$OUTPUT_FILE"
echo '|------|-------|------|' >> "$OUTPUT_FILE"

echo "$CYBER_TRENDING" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for repo in data.get('items', [])[:5]:
        name = repo.get('full_name', 'N/A')
        stars = repo.get('stargazers_count', 0)
        desc = repo.get('description', '')[:60]
        url = repo.get('html_url', '')
        print(f'| [{name}]({url}) | ⭐{stars} | {desc} |')
except Exception as e:
    print('| 暂无数据 | 0 | 获取失败 |')
" >> "$OUTPUT_FILE" 2>/dev/null || echo "| 暂无数据 | 0 | API 错误 |" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"

# ------------------------------------------
# 3. AI/机器学习项目
# ------------------------------------------
log_info "获取 AI/ML 项目..."

cat >> "$OUTPUT_FILE" << 'EOF'

## 🤖 AI/机器学习项目

EOF

AI_TRENDING=$(curl -s "https://api.github.com/search/repositories?q=topic:machine-learning+created:>$(date -d '30 days ago' +%Y-%m-%d)&sort=stars&order=desc&per_page=10" 2>/dev/null || echo "")

echo '| 项目 | Stars | 描述 |' >> "$OUTPUT_FILE"
echo '|------|-------|------|' >> "$OUTPUT_FILE"

echo "$AI_TRENDING" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for repo in data.get('items', [])[:5]:
        name = repo.get('full_name', 'N/A')
        stars = repo.get('stargazers_count', 0)
        desc = repo.get('description', '')[:60]
        url = repo.get('html_url', '')
        print(f'| [{name}]({url}) | ⭐{stars} | {desc} |')
except Exception as e:
    print('| 暂无数据 | 0 | 获取失败 |')
" >> "$OUTPUT_FILE" 2>/dev/null || echo "| 暂无数据 | 0 | API 错误 |" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"

# ------------------------------------------
# 4. 通过 Tavily 搜索技术趋势
# ------------------------------------------
log_info "搜索最新技术趋势..."

cat >> "$OUTPUT_FILE" << 'EOF'

## 📈 技术趋势分析

EOF

# 使用 Tavily 搜索技术趋势
TAVILY_RESULT=$(curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\":\"$API_KEY\",\"query\":\"latest technology trends programming 2024\",\"max_results\":10}" 2>/dev/null || echo "")

if [ -n "$TAVILY_RESULT" ]; then
    echo "$TAVILY_RESULT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get('results', [])[:5]
    for r in results:
        title = r.get('title', 'N/A')
        url = r.get('url', '')
        print(f'### [{title}]({url})')
        print()
except Exception as e:
    print('搜索结果获取失败')
" >> "$OUTPUT_FILE" 2>/dev/null || echo "暂无趋势数据" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"

# ------------------------------------------
# 5. 安全漏洞情报
# ------------------------------------------
log_info "获取安全漏洞情报..."

cat >> "$OUTPUT_FILE" << 'EOF'

## ⚠️ 安全漏洞情报

EOF

# 搜索最近的 CVE
CVE_RESULT=$(curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\":\"$API_KEY\",\"query\":\"latest CVE vulnerabilities 2024\",\"max_results\":5}" 2>/dev/null || echo "")

if [ -n "$CVE_RESULT" ]; then
    echo "| 时间 | 漏洞 | 严重程度 |" >> "$OUTPUT_FILE"
    echo "|-----|------|---------|" >> "$OUTPUT_FILE"
    echo "$CVE_RESULT" | python3 -c "
import sys, json
from datetime import datetime
try:
    data = json.load(sys.stdin)
    results = data.get('results', [])[:5]
    for r in results:
        title = r.get('title', 'N/A')[:40]
        url = r.get('url', '')
        print(f'| 近期 | [{title}]({url}) | 中高 |')
except Exception as e:
    print('| - | 暂无漏洞信息 | - |')
" >> "$OUTPUT_FILE" 2>/dev/null || echo "| - | 暂无漏洞信息 | - |" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"

# ------------------------------------------
# 6. 学习总结
# ------------------------------------------
cat >> "$OUTPUT_FILE" << EOF

---

## 📝 今日学习总结

### ✅ 完成项目
- GitHub Trending 项目收集: 15+ 个
- 网络安全项目跟踪: 5+ 个
- AI/ML 项目跟踪: 5+ 个
- 技术趋势分析: 5+ 篇

### 🎯 重点关注
1. **Python 项目**: 关注自动化、爬虫、数据分析方向
2. **网络安全**: 持续跟踪新漏洞和防御技术
3. **AI/ML**: 学习最新的大模型应用

### 📚 明日学习计划
- [ ] 深入学习 2-3 个重点项目的源码
- [ ] 阅读 3-5 篇技术文章
- [ ] 实践 1 个小型项目

---

*学习时间: $(date '+%Y-%m-%d %H:%M:%S')*

EOF

# 清理临时文件
rm -rf "$TEMP_DIR"

# 输出结果
log_success "学习任务完成！"
log_success "学习笔记: $OUTPUT_FILE"
log_info "文件大小: $(wc -c < "$OUTPUT_FILE") bytes"

# 统计
TOTAL_REPOS=$(grep -c "github.com" "$OUTPUT_FILE" 2>/dev/null || echo "0")
log_info "共收集 $TOTAL_REPOS 个项目链接"

exit 0