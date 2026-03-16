#!/bin/bash
# 每日天气+美食早报脚本

CITY="成都"
USER_ID="ou_1dd4a1b1f9f9b7df3c86b7be0135a9c4"

# 获取天气
WEATHER=$(curl -s "wttr.in/${CITY}?lang=zh&format=%l:+%c+%t+(体感%f)+湿度%h+%w风")
FORECAST=$(curl -s "wttr.in/${CITY}?lang=zh&format=v2")

# 解析天气状况
if echo "$WEATHER" | grep -q "雨"; then
    WEATHER_TYPE="雨天"
elif echo "$WEATHER" | grep -q "雪"; then
    WEATHER_TYPE="雪天"
elif echo "$WEATHER" | grep -q "晴"; then
    WEATHER_TYPE="晴天"
elif echo "$WEATHER" | grep -q "多云"; then
    WEATHER_TYPE="多云"
elif echo "$WEATHER" | grep -q "阴"; then
    WEATHER_TYPE="阴天"
else
    WEATHER_TYPE="多变"
fi

# 根据天气推荐美食
case "$WEATHER_TYPE" in
    "雨天"|"雪天"|"阴天")
        FOOD="🍲 今日美食推荐：
• 火锅 - 阴雨天和火锅最配！
• 羊肉汤 - 暖身驱寒
• 冒菜 - 麻辣鲜香"
        ;;
    "晴天")
        FOOD="🍜 今日美食推荐：
• 凉面 - 清爽解暑
• 冰粉 - 清凉甜品
• 串串香 - 边吃边逛"
        ;;
    "多云")
        FOOD="🥢 今日美食推荐：
• 川菜 - 经典美味
• 烧烤 - 聚会首选
• 抄手 - 皮薄馅大"
        ;;
    *)
        FOOD="🍴 今日美食推荐：
• 川菜 - 百吃不厌
• 盖浇饭 - 快捷美味
• 面条 - 简单实惠"
        ;;
esac

# 发送飞书消息
MESSAGE="☀️ **早安！成都今日天气** ☀️

$WEATHER

$FOOD

---
早报自动生成 | 每天8:00推送"

# 从 OpenClaw 配置获取飞书 app credentials
APP_ID="cli_a92ad6cebbb8dbde"
APP_SECRET="kuTm6eYxx3BsaewZG0dlAbrUWjIvCLdL"

# 获取 tenant_access_token
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
    -H "Content-Type: application/json" \
    -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}")

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Failed to get token: $TOKEN_RESPONSE"
    exit 1
fi

# 发送消息
curl -s -X POST "https://open.feishu.cn/open-apis/message/v4/send/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{
        \"receive_id\": \"$USER_ID\",
        \"msg_type\": \"text\",
        \"content\": {\"text\": \"$MESSAGE\"}
    }"
