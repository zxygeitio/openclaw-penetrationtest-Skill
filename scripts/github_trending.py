#!/usr/bin/env python3
"""
获取GitHub每日飙升榜前10项目并推送到飞书
"""
import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import re

# 飞书配置
FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET')
FEISHU_RECEIVER_ID = os.environ.get('FEISHU_RECEIVER_ID')

def get_github_trending():
    """获取GitHub今日飙升榜"""
    url = "https://github.com/trending?since=daily"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        repos = []
        
        # 查找仓库条目
        articles = soup.find_all('article', class_='border-bottom')
        for article in articles[:10]:
            try:
                # 获取仓库名
                h2 = article.find('h2')
                if not h2:
                    continue
                repo_link = h2.find('a')
                if not repo_link:
                    continue
                    
                href = repo_link.get('href', '')
                if not href.startswith('/'):
                    continue
                repo_name = href.strip('/')
                full_name = f"https://github.com/{repo_name}"
                
                # 获取描述
                p = article.find('p')
                description = p.get_text(strip=True) if p else "暂无描述"
                
                # 获取语言
                lang_span = article.find('span', itemprop='programmingLanguage')
                language = lang_span.get_text(strip=True) if lang_span else "Unknown"
                
                # 获取今日星星数
                stars_div = article.find('div', class_='f6')
                stars_today = "0"
                if stars_div:
                    text = stars_div.get_text(strip=True)
                    if 'today' in text.lower():
                        match = re.search(r'([\d,\.]+)', text)
                        if match:
                            stars_today = match.group(1)
                
                repos.append({
                    'name': repo_name,
                    'url': full_name,
                    'description': description[:100],
                    'language': language,
                    'stars_today': stars_today
                })
            except Exception as e:
                continue
        
        return repos
    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
        return []

def get_feishu_access_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if data.get('code') == 0:
        return data.get('tenant_access_token')
    return None

def send_to_feishu(repos, access_token):
    """发送消息到飞书"""
    if not repos:
        return False
    
    message_lines = ["📊 **GitHub 今日飙升榜 Top 10**\n"]
    for i, repo in enumerate(repos, 1):
        message_lines.append(
            f"{i}. **{repo['name']}**\n"
            f"   📌 语言: {repo['language']} | ⭐ 今日: {repo['stars_today']}\n"
            f"   📝 {repo['description']}\n"
            f"   🔗 {repo['url']}\n"
        )
    
    message_lines.append("\n---\n🤖 由 OpenClaw 自动推送")
    message_content = "\n".join(message_lines)
    
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    params = {"receive_id_type": "open_id"}
    payload = {
        "receive_id": FEISHU_RECEIVER_ID,
        "msg_type": "text",
        "content": json.dumps({"text": message_content})
    }
    
    response = requests.post(url, params=params, headers=headers, json=payload)
    result = response.json()
    if result.get('code') == 0:
        print(f"Successfully sent {len(repos)} repositories")
        return True
    else:
        print(f"Error sending: {result}")
        return False

def main():
    print("=" * 50)
    print("GitHub Trending Bot")
    print("=" * 50)
    
    repos = get_github_trending()
    print(f"Found {len(repos)} repositories")
    
    if repos:
        token = get_feishu_access_token()
        if token:
            send_to_feishu(repos, token)
        else:
            print("Failed to get Feishu token")
            sys.exit(1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
