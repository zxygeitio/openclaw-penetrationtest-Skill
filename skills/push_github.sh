#!/bin/bash
# 推送到GitHub的脚本

# 说明：
# 1. 安装GitHub CLI: https://cli.github.com
# 2. 运行: gh auth login  (需要GitHub账号密码)
# 3. 运行此脚本

# 或者直接运行以下命令：

echo "=== 方式1: 使用Git ==="
echo "cd ~/.openclaw/workspace/skills/penetration-testing"
echo "git remote add origin https://github.com/zxygeitio/openclaw-penetrationtest-Skill.git"
echo "git push -u origin master"
echo ""
echo "=== 方式2: 下载zip文件 ==="
echo "zip文件已生成: ~/.openclaw/workspace/skills/penetration-testing.zip"
echo "请手动上传到GitHub"
