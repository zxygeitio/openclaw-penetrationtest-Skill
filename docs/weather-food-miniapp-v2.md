# 🌤️ 天气美食早报小程序 - 开发文档

> 文档版本：v2.0
> 创建日期：2026-03-14
> 部署方式：云服务器 (ECS/VPS)

---

## 一、项目概述

### 1.1 产品定位

一款基于天气的美食推荐小程序，为用户提供每日天气信息和美食推荐服务。

### 1.2 核心功能

| 功能 | 描述 |
|------|------|
| 实时天气 | 显示当前温度、湿度、风力、天气状况 |
| 3日预报 | 展示未来3天的天气走势 |
| 美食推荐 | 根据天气智能推荐适合的美食 |
| 每日推送 | 订阅后每天8点收到早报 |
| 城市切换 | 支持多城市切换 |

### 1.3 目标用户

- 美食爱好者
- 日常需要天气参考的用户
- 喜欢早餐获取正能量的人群

---

## 二、技术架构

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         微信小程序前端                           │
│                    (微信App内运行)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS API
┌────────────────────────────▼────────────────────────────────────┐
│                      云服务器 (ECS/VPS)                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Nginx (反向代理)                       │    │
│  │                      端口 80/443                         │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐    │
│  │              Node.js API 服务 (PM2)                      │    │
│  │                  端口 3000                                │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐    │
│  │              数据存储 (SQLite/文件)                      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | 原生小程序 | WXML + WXSS + JavaScript |
| 后端 | Node.js + Express | 轻量级 API 服务 |
| 进程管理 | PM2 | Node.js 进程管理 |
| Web服务器 | Nginx | 反向代理 + 静态文件 |
| 天气数据 | wttr.in / 和风天气 | 免费/付费 API |
| 消息推送 | 微信订阅消息 | 需要模板 ID |
| 数据库 | SQLite | 轻量级，无需额外部署 |

### 2.3 接口设计

#### 天气接口

```
GET /api/weather?city=成都

Response:
{
  "code": 0,
  "data": {
    "city": "成都",
    "temp": 10,
    "feelsLike": 9,
    "humidity": 82,
    "wind": "↙8km/h",
    "condition": "小雨",
    "conditionCode": "🌦",
    "forecast": [
      {"date": "明天", "tempMax": 15, "tempMin": 8, "condition": "多云"},
      {"date": "后天", "tempMax": 18, "tempMin": 10, "condition": "晴"}
    ]
  }
}
```

#### 美食推荐接口

```
GET /api/food/recommend?city=成都&weather=小雨

Response:
{
  "code": 0,
  "data": {
    "weather": "小雨",
    "recommendations": [
      {
        "name": "火锅",
        "reason": "阴雨天和火锅最配！",
        "tags": ["麻辣", "暖身", "聚会"]
      },
      {
        "name": "羊肉汤",
        "reason": "暖身驱寒首选",
        "tags": ["滋补", "清淡"]
      },
      {
        "name": "冒菜",
        "reason": "麻辣鲜香",
        "tags": ["麻辣", "快捷"]
      }
    ]
  }
}
```

#### 订阅接口

```
POST /api/subscribe
Body: { "openId": "xxx", "city": "成都", "time": "8:00" }

Response: { "code": 0, "message": "订阅成功" }
```

---

## 三、开发流程

### 3.1 流程总览

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 阶段一   │───▶│ 阶段二   │───▶│ 阶段三   │───▶│ 阶段四   │───▶│ 阶段五   │
│ 准备阶段 │    │ 后端开发 │    │ 前端开发 │    │ 推送接入 │    │ 测试上线 │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
   1-2天          2-3天          2-3天          1-2天          3-5天
```

---

### 3.2 阶段一：准备阶段（1-2天）

#### 3.2.1 注册微信小程序

1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 选择「小程序」注册
3. 完成个人认证（需要身份证 + 手机号）
4. 获取 AppID

#### 3.2.2 开通服务

| 服务 | 位置 | 用途 |
|------|------|------|
| 订阅消息 | 功能 -> 订阅消息 | 每日推送早报 |
| 获取用户位置 | 开发 -> 开发设置 | 天气定位 |

#### 3.2.3 购买云服务器

推荐配置：

| 配置项 | 推荐选择 |
|--------|----------|
| 运营商 | 阿里云 / 腾讯云 / 华为云 |
| 规格 | 1核1G / 1核2G |
| 系统 | Ubuntu 22.04 LTS / CentOS 8 |
| 带宽 | 3-5Mbps |
| 存储 | 40GB SSD |

> 💰 费用：约 30-50元/月

#### 3.2.4 域名准备

1. 购买域名（可选，测试阶段可用 IP）
2. 完成域名备案（国内服务器需要）
3. 配置 SSL 证书（可选，推荐 Let's Encrypt 免费）

---

### 3.3 阶段二：后端开发（2-3天）

#### 3.3.1 项目结构

```
backend/
├── src/
│   ├── config/
│   │   └── index.js          # 配置文件
│   ├── controllers/
│   │   ├── weather.js        # 天气控制器
│   │   ├── food.js           # 美食控制器
│   │   └── user.js           # 用户控制器
│   ├── services/
│   │   ├── weatherService.js # 天气服务
│   │   ├── foodService.js    # 美食推荐服务
│   │   └── pushService.js    # 推送服务
│   ├── routes/
│   │   └── index.js          # 路由
│   ├── utils/
│   │   └── http.js           # HTTP 工具
│   └── app.js                # 入口文件
├── data/
│   └── database.sqlite       # SQLite 数据库
├── ecosystem.config.js      # PM2 配置
├── package.json
└── .env                     # 环境变量
```

#### 3.3.2 核心代码

**package.json**
```json
{
  "name": "weather-food-api",
  "version": "1.0.0",
  "main": "src/app.js",
  "scripts": {
    "start": "node src/app.js",
    "dev": "nodemon src/app.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "axios": "^1.6.0",
    "better-sqlite3": "^9.2.2",
    "node-cron": "^3.0.3",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

**src/app.js**
```javascript
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const weatherRouter = require('./routes/weather');
const foodRouter = require('./routes/food');
const userRouter = require('./routes/user');
const { initDatabase } = require('./services/database');

const app = express();

// 初始化数据库
initDatabase();

app.use(cors());
app.use(express.json());

// 路由
app.use('/api/weather', weatherRouter);
app.use('/api/food', foodRouter);
app.use('/api/user', userRouter);

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

**src/services/weatherService.js**
```javascript
const axios = require('axios');

async function getWeather(city) {
  try {
    const url = `wttr.in/${encodeURIComponent(city)}?lang=zh&format=j1`;
    const response = await axios.get(url);
    const data = response.data;
    
    return {
      city: data.nearest_area[0].areaName[0].value,
      temp: parseInt(data.current_condition[0].temp_C[0]),
      feelsLike: parseInt(data.current_condition[0].FeelsLikeC[0]),
      humidity: parseInt(data.current_condition[0].humidity[0]),
      wind: data.current_condition[0].windspeedKmph[0] + 'km/h',
      condition: data.current_condition[0].weatherDesc[0].value,
      conditionCode: getWeatherCode(data.current_condition[0].weatherCode[0])
    };
  } catch (error) {
    console.error('Weather API error:', error.message);
    return null;
  }
}

function getWeatherCode(code) {
  const map = {
    '113': '☀️', '116': '⛅', '119': '☁️', '122': '☁️',
    '176': '🌧️', '179': '🌧️', '182': '🌧️', '200': '⛈️',
    '227': '🌨️', '230': '❄️', '263': '🌧️', '266': '🌧️'
  };
  return map[code] || '🌤️';
}

module.exports = { getWeather };
```

**src/services/foodService.js**
```javascript
const foodDatabase = {
  '晴天': [
    { name: '凉面', reason: '清爽解暑', tags: ['清淡', '快捷'] },
    { name: '冰粉', reason: '清凉甜品', tags: ['甜品', '解暑'] },
    { name: '串串香', reason: '边吃边逛', tags: ['麻辣', '聚会'] }
  ],
  '雨天': [
    { name: '火锅', reason: '雨天和火锅最配！', tags: ['麻辣', '暖身'] },
    { name: '羊肉汤', reason: '暖身驱寒', tags: ['滋补', '清淡'] },
    { name: '冒菜', reason: '麻辣鲜香', tags: ['麻辣', '快捷'] }
  ],
  '阴天': [
    { name: '火锅', reason: '阴天吃火锅暖暖的', tags: ['麻辣', '暖身'] },
    { name: '川菜', reason: '经典美味', tags: ['麻辣', '下饭'] },
    { name: '抄手', reason: '皮薄馅大', tags: ['快捷', '鲜美'] }
  ],
  '多云': [
    { name: '川菜', reason: '百吃不厌', tags: ['麻辣', '经典'] },
    { name: '烧烤', reason: '聚会首选', tags: ['烤', '聚会'] },
    { name: '面条', reason: '简单实惠', tags: ['快捷', '饱腹'] }
  ]
};

function getRecommendations(weather) {
  let category = '多云';
  if (!weather) return foodDatabase['多云'];
  
  if (weather.includes('雨')) category = '雨天';
  else if (weather.includes('晴')) category = '晴天';
  else if (weather.includes('阴')) category = '阴天';
  
  return foodDatabase[category] || foodDatabase['多云'];
}

module.exports = { getRecommendations };
```

**src/services/database.js**
```javascript
const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '../data/database.sqlite');
const db = new Database(dbPath);

function initDatabase() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      openId TEXT UNIQUE,
      city TEXT DEFAULT '成都',
      subscribeTime TEXT,
      notifyTime TEXT DEFAULT '8:00',
      createdAt TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `);
  console.log('Database initialized');
}

function addUser(openId, city, notifyTime) {
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO users (openId, city, subscribeTime, notifyTime)
    VALUES (?, ?, ?, ?)
  `);
  return stmt.run(openId, city, new Date().toISOString(), notifyTime);
}

function getSubscribedUsers() {
  const stmt = db.prepare('SELECT * FROM users');
  return stmt.all();
}

module.exports = { initDatabase, addUser, getSubscribedUsers };
```

**ecosystem.config.js (PM2配置)**
```javascript
module.exports = {
  apps: [{
    name: 'weather-food-api',
    script: 'src/app.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '200M',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
};
```

**src/services/pushService.js (推送服务)**
```javascript
const axios = require('axios');
const { getWeather } = require('./weatherService');
const { getRecommendations } = require('./foodService');

const WEIXIN_APPID = process.env.WEIXIN_APPID;
const WEIXIN_SECRET = process.env.WEIXIN_SECRET;
const TEMPLATE_ID = process.env.TEMPLATE_ID;

async function getAccessToken() {
  const res = await axios.get(
    `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${WEIXIN_APPID}&secret=${WEIXIN_SECRET}`
  );
  return res.data.access_token;
}

async function sendDailyPush(users) {
  const accessToken = await getAccessToken();
  
  for (const user of users) {
    try {
      const weather = await getWeather(user.city);
      if (!weather) continue;
      
      const foods = getRecommendations(weather.condition);
      
      const message = {
        touser: user.openId,
        template_id: TEMPLATE_ID,
        data: {
          date: {
            value: new Date().toLocaleDateString('zh-CN', { 
              weekday: 'long', 
              month: 'long', 
              day: 'numeric' 
            })
          },
          weather: {
            value: `${weather.city} ${weather.condition} ${weather.temp}°C`
          },
          food1: {
            value: `${foods[0].name} - ${foods[0].reason}`
          },
          food2: {
            value: `${foods[1].name} - ${foods[1].reason}`
          },
          food3: {
            value: `${foods[2].name} - ${foods[2].reason}`
          }
        }
      };
      
      await axios.post(
        `https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token=${accessToken}`,
        message
      );
      
      console.log(`Push sent to ${user.openId}`);
    } catch (error) {
      console.error('Push error:', error.message);
    }
  }
}

module.exports = { sendDailyPush };
```

#### 3.3.3 本地测试

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/weather-food-backend.git
cd weather-food-backend

# 2. 安装依赖
npm install

# 3. 创建环境变量文件
cp .env.example .env
# 编辑 .env 填入配置

# 4. 启动开发服务器
npm run dev

# 5. 测试接口
curl http://localhost:3000/api/weather?city=成都
curl http://localhost:3000/api/food/recommend?weather=晴天
```

---

### 3.4 阶段三：前端开发（2-3天）

#### 3.4.1 目录结构

```
miniprogram/
├── app.js                 # 小程序入口
├── app.json               # 全局配置
├── app.wxss               # 全局样式
├── pages/
│   ├── index/             # 首页
│   │   ├── index.js
│   │   ├── index.json
│   │   ├── index.wxml
│   │   └── index.wxss
│   ├── settings/          # 设置页
│   │   ├── settings.js
│   │   ├── settings.json
│   │   ├── settings.wxml
│   │   └── settings.wxss
│   └── history/          # 历史页
│       ├── history.js
│       ├── history.json
│       ├── history.wxml
│       └── history.wxss
├── components/
│   ├── weather-card/
│   └── food-card/
├── utils/
│   ├── api.js             # API 封装
│   └── util.js            # 工具函数
└── images/                # 图片资源
```

#### 3.4.2 核心页面代码

**app.json**
```json
{
  "pages": [
    "pages/index/index",
    "pages/settings/settings",
    "pages/history/history"
  ],
  "window": {
    "navigationBarBackgroundColor": "#ffffff",
    "navigationBarTitleText": "天气美食",
    "navigationBarTextStyle": "black",
    "backgroundColor": "#f5f5f5"
  },
  "tabBar": {
    "color": "#666666",
    "selectedColor": "#1890ff",
    "backgroundColor": "#ffffff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "images/home.png",
        "selectedIconPath": "images/home-active.png"
      },
      {
        "pagePath": "pages/settings/settings",
        "text": "设置",
        "iconPath": "images/settings.png",
        "selectedIconPath": "images/settings-active.png"
      }
    ]
  }
}
```

**pages/index/index.wxml**
```html
<view class="container">
  <!-- 天气卡片 -->
  <view class="weather-card">
    <view class="location">{{weather.city}}</view>
    <view class="temp">{{weather.temp}}°</view>
    <view class="condition">{{weather.condition}}</view>
    <view class="details">
      <text>体感 {{weather.feelsLike}}°</text>
      <text>湿度 {{weather.humidity}}%</text>
      <text>风力 {{weather.wind}}</text>
    </view>
  </view>

  <!-- 美食推荐 -->
  <view class="section-title">🍜 今日美食推荐</view>
  <view class="food-list">
    <view class="food-card" wx:for="{{foods}}" wx:key="index">
      <view class="food-name">{{item.name}}</view>
      <view class="food-reason">{{item.reason}}</view>
      <view class="food-tags">
        <text wx:for="{{item.tags}}" wx:for-item="tag" wx:key="tag" class="tag">
          {{tag}}
        </text>
      </view>
    </view>
  </view>

  <!-- 订阅按钮 -->
  <button class="subscribe-btn" bindtap="subscribe">
    {{isSubscribed ? '已订阅每日早报' : '订阅每日早报'}}
  </button>
</view>
```

**pages/index/index.wxss**
```css
.container {
  padding: 20rpx;
  background: #f5f5f5;
  min-height: 100vh;
}

.weather-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20rpx;
  padding: 40rpx;
  color: #fff;
  text-align: center;
  margin-bottom: 30rpx;
}

.location {
  font-size: 32rpx;
  margin-bottom: 10rpx;
}

.temp {
  font-size: 80rpx;
  font-weight: bold;
}

.condition {
  font-size: 28rpx;
  margin: 10rpx 0;
}

.details {
  display: flex;
  justify-content: space-around;
  font-size: 24rpx;
  opacity: 0.9;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  margin: 30rpx 0 20rpx;
}

.food-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.food-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
}

.food-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.food-reason {
  font-size: 26rpx;
  color: #666;
  margin: 10rpx 0;
}

.food-tags {
  display: flex;
  gap: 10rpx;
}

.tag {
  background: #f0f0f0;
  color: #666;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
}

.subscribe-btn {
  margin-top: 40rpx;
  background: #1890ff;
  color: #fff;
  border-radius: 50rpx;
}
```

**pages/index/index.js**
```javascript
const app = getApp();
// 配置你的云服务器API地址
const API_BASE = 'https://your-domain.com/api';

Page({
  data: {
    weather: {},
    foods: [],
    isSubscribed: false,
    city: '成都'
  },

  onLoad() {
    const city = wx.getStorageSync('city') || '成都';
    this.setData({ city });
    this.loadData();
  },

  async loadData() {
    wx.showLoading({ title: '加载中...' });
    
    try {
      const [weatherRes, foodRes] = await Promise.all([
        wx.request({ url: `${API_BASE}/weather?city=${this.data.city}` }),
        wx.request({ url: `${API_BASE}/food/recommend?city=${this.data.city}` })
      ]);
      
      if (weatherRes.data.code === 0 && foodRes.data.code === 0) {
        this.setData({
          weather: weatherRes.data.data,
          foods: foodRes.data.data.recommendations
        });
      }
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  },

  async subscribe() {
    const that = this;
    
    // 获取用户 OpenID (需要通过wx.login获取code，再去后端换取)
    const loginRes = await wx.login();
    const openIdRes = await wx.request({
      url: `${API_BASE}/user/login`,
      method: 'POST',
      data: { code: loginRes.code }
    });
    
    const openId = openIdRes.data.data.openId;
    
    // 请求订阅消息权限
    wx.requestSubscribeMessage({
      tmplIds: ['YOUR_TEMPLATE_ID'],
      success(res) {
        if (res['YOUR_TEMPLATE_ID'] === 'accept') {
          // 保存订阅状态到后端
          wx.request({
            url: `${API_BASE}/user/subscribe`,
            method: 'POST',
            data: {
              openId: openId,
              city: that.data.city,
              time: '8:00'
            },
            success() {
              that.setData({ isSubscribed: true });
              wx.showToast({ title: '订阅成功！', icon: 'success' });
            }
          });
        }
      }
    });
  },

  onPullDownRefresh() {
    this.loadData().then(() => {
      wx.stopPullDownRefresh();
    });
  }
});
```

---

### 3.5 阶段四：服务器部署（1-2天）

#### 3.5.1 服务器初始化

```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 更新系统
apt update && apt upgrade -y

# 3. 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 4. 安装 Nginx
apt install -y nginx

# 5. 安装 PM2
npm install -g pm2

# 6. 安装 Git
apt install -y git
```

#### 3.5.2 部署后端服务

```bash
# 1. 创建项目目录
mkdir -p /var/www/weather-food-api
cd /var/www/weather-food-api

# 2. 克隆项目（或上传代码）
git clone https://github.com/your-repo/weather-food-backend.git .

# 3. 安装依赖
npm install --production

# 4. 创建环境变量文件
cp .env.example .env
nano .env

# 填写以下内容：
# WEIXIN_APPID=你的小程序AppID
# WEIXIN_SECRET=你的小程序AppSecret
# TEMPLATE_ID=你的消息模板ID
# PORT=3000

# 5. 创建数据目录
mkdir -p data

# 6. 使用 PM2 启动服务
pm2 start ecosystem.config.js

# 7. 设置开机自启
pm2 startup
pm2 save
```

#### 3.5.3 配置 Nginx 反向代理

```bash
# 创建 Nginx 配置
nano /etc/nginx/sites-available/weather-food-api
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 或使用服务器IP

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# 启用配置
ln -s /etc/nginx/sites-available/weather-food-api /etc/nginx/sites-enabled/

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx
```

#### 3.5.4 配置定时推送任务

```bash
# 创建定时推送脚本
nano /var/www/weather-food-api/scripts/daily-push.js
```

```javascript
const { sendDailyPush } = require('./src/services/pushService');
const { getSubscribedUsers } = require('./src/services/database');

async function main() {
  console.log('Starting daily push...');
  const users = getSubscribedUsers();
  console.log(`Found ${users.length} subscribers`);
  
  await sendDailyPush(users);
  console.log('Daily push completed');
  
  process.exit(0);
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
```

```bash
# 添加 crontab 任务
crontab -e

# 添加以下行（每天早上8点执行）
0 8 * * * cd /var/www/weather-food-api && node scripts/daily-push.js >> /var/log/daily-push.log 2>&1
```

#### 3.5.5 配置 HTTPS（推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
apt install -y certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com

# 设置自动续期
certbot renew --dry-run
```

---

### 3.6 阶段五：小程序配置与上线（2-3天）

#### 3.6.1 配置请求合法域名

在微信公众平台：
1. 开发 → 开发管理 → 开发设置
2. 服务器域名 → 修改
3. 添加 request 合法域名：
   - `https://your-domain.com`

#### 3.6.2 创建订阅消息模板

1. 功能 → 订阅消息
2. 添加模板：
```
{{date.DATA}}
{{weather.DATA}}
{{food1.DATA}}
{{food2.DATA}}
{{food3.DATA}}
```
3. 获取模板 ID，填入后端 .env 配置

#### 3.6.3 提交审核

1. 在微信开发者工具点击「上传」
2. 填写版本号（如 1.0.0）和备注
3. 在公众平台提交审核
4. 等待审核（通常1-3天）

#### 3.6.4 发布

审核通过后，在公众平台点击「发布」

---

## 四、运维清单

### 4.1 常用命令

```bash
# 查看服务状态
pm2 status

# 查看日志
pm2 logs weather-food-api

# 重启服务
pm2 restart weather-food-api

# 查看 Nginx 状态
systemctl status nginx

# 查看定时任务日志
tail -f /var/log/daily-push.log
```

### 4.2 监控

```bash
# 安装 Node.js 监控工具
pm2 install pm2-logrotate

# 配置自动重启（内存超限）
pm2 update
```

### 4.3 备份

```bash
# 备份数据库
cp /var/www/weather-food-api/data/database.sqlite /backup/db-$(date +%Y%m%d).sqlite
```

---

## 五、费用估算

| 项目 | 费用 | 备注 |
|------|------|------|
| 云服务器 (1核1G) | 30-50元/月 | 阿里云/腾讯云 |
| 域名 | 30-50元/年 | 可选 |
| 备案 | 免费 | 国内服务器需要 |
| 微信小程序认证 | 免费 | 个人认证 |
| SSL证书 | 免费 | Let's Encrypt |
| **总计** | **约 50-100元/月** | |

---

## 六、注意事项

### 6.1 接口限制

- wttr.in 免费有频率限制，生产环境建议用和风天气 API
- 微信订阅消息有每月推送次数限制

### 6.2 安全建议

- 不要在前端暴露 AppSecret
- 所有接口使用 HTTPS
- 验证用户身份
- 定期更新系统补丁

### 6.3 性能优化

- 使用 PM2 集群模式提升并发
- 启用 Nginx 缓存
- 考虑使用 CDN 加速

---

## 七、后续迭代

- [ ] 美食地图（附近推荐商家）
- [ ] 社交分享
- [ ] 会员功能
- [ ] AI 智能推荐
- [ ] 多语言支持

---

*文档结束*
