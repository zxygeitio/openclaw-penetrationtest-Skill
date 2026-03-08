#!/bin/bash
# GitHub 记忆同步脚本
set -e
REPO="zxygeitio/openClaw-config"
BRANCH="main"
MEMORY_DIR="/root/.openclaw/workspace/memory"
TOKEN="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"
WORK_DIR="/tmp/memory-sync-$$"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"
git clone "https://$TOKEN@github.com/$REPO.git" . --quiet 2>/dev/null || (git init && git remote add origin "https://$TOKEN@github.com/$REPO.git")
git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH"
cp -r "$MEMORY_DIR" ./memory
[ -f "/root/.openclaw/workspace/MEMORY.md" ] && cp /root/.openclaw/workspace/MEMORY.md .
git config user.email "bot@openclaw.local" 2>/dev/null
git config user.name "OpenClaw Bot" 2>/dev/null
git add -A
git commit -m "Memory sync $(date '+%Y-%m-%d %H:%M')" --quiet 2>/dev/null || echo "无新更改"
git push origin "$BRANCH" --quiet 2>/dev/null && echo "✅ 同步成功" || echo "⚠️ 推送失败"
rm -rf "$WORK_DIR"
