# 🌤️ 天气美食早报小程序 - 开发文档

> 文档版本：v1.0
> 创建日期：2026-03-14

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

### 2.1 系统架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                         微信小程序前端                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  首页     │  │  设置    │  │  历史    │  │  关于    │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │             │             │                │
│       └─────────────┴─────────────┴─────────────┘                │
│                              │                                   │
│                    ┌──────────▼──────────┐                      │
│                    │    小程序宿主环境     │                      │
│                    │  (微信App内运行)      │                      │
│                    └──────────┬──────────┘                      │
└───────────────────────────────┼───────────────────────────────────┘
                                │ HTTPS API
┌───────────────────────────────▼───────────────────────────────────┐
│                         后端服务 (K8s 部署)                         │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                     Node.js API Server                       │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────┐  │  │
│  │  │ 天气接口   │  │ 美食推荐  │  │ 用户管理  │  │ 推送服务│  │  │
│  │  └───────────┘  └───────────┘  └───────────┘  └─────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│              ┌───────────────┼───────────────┐                    │
│              ▼               ▼               ▼                    │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│    │   wttr.in    │  │  美食数据    │  │  微信订阅    │           │
│    │   天气API    │  │  本地存储    │  │  消息推送    │           │
│    └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | 原生小程序 | WXML + WXSS + JavaScript |
| 后端 | Node.js + Express | 轻量级 API 服务 |
| 天气数据 | wttr.in / 和风天气 | 免费/付费 API |
| 部署 | Docker + K8s | 现有集群 |
| 消息推送 | 微信订阅消息 | 需要模板 ID |

### 2.3 接口设计

#### 2.3.1 天气接口

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

#### 2.3.2 美食推荐接口

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

#### 2.3.3 订阅接口

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

#### 3.2.3 创建项目

```bash
# 安装微信开发者工具
# 下载地址: https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

# 初始化项目
mkdir weather-food-miniapp
cd weather-food-miniapp
npm init -y
```

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
├── Dockerfile
├── docker-compose.yml
└── package.json
```

#### 3.3.2 核心代码示例

**app.js**
```javascript
const express = require('express');
const cors = require('cors');
const weatherRouter = require('./routes/weather');
const foodRouter = require('./routes/food');
const userRouter = require('./routes/user');

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api/weather', weatherRouter);
app.use('/api/food', foodRouter);
app.use('/api/user', userRouter);

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

**weatherService.js**
```javascript
const axios = require('axios');

async function getWeather(city) {
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

**foodService.js**
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
  // 根据天气关键词匹配
  let category = '多云';
  if (weather.includes('雨')) category = '雨天';
  else if (weather.includes('晴')) category = '晴天';
  else if (weather.includes('阴')) category = '阴天';
  
  return foodDatabase[category] || foodDatabase['多云'];
}

module.exports = { getRecommendations };
```

#### 3.3.3 Docker 部署

**Dockerfile**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 3000

CMD ["node", "src/app.js"]
```

**K8s Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-food-api
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: weather-food-api
  template:
    metadata:
      labels:
        app: weather-food-api
    spec:
      containers:
      - name: api
        image: weather-food-api:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: production
        resources:
          limits:
            memory: "256Mi"
            cpu: "250m"
          requests:
            memory: "128Mi"
            cpu: "100m"
---
apiVersion: v1
kind: Service
metadata:
  name: weather-food-api
spec:
  selector:
    app: weather-food-api
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
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
│   └── history/           # 历史页
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

#### 3.4.2 核心页面

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
const API_BASE = 'https://your-api-domain.com/api';

Page({
  data: {
    weather: {},
    foods: [],
    isSubscribed: false,
    city: '成都'
  },

  onLoad() {
    this.loadData();
  },

  async loadData() {
    const city = wx.getStorageSync('city') || '成都';
    this.setData({ city });
    
    wx.showLoading({ title: '加载中...' });
    
    try {
      const [weatherRes, foodRes] = await Promise.all([
        wx.request({ url: `${API_BASE}/weather?city=${city}` }),
        wx.request({ url: `${API_BASE}/food/recommend?city=${city}` })
      ]);
      
      this.setData({
        weather: weatherRes.data.data,
        foods: foodRes.data.data.recommendations
      });
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  },

  async subscribe() {
    const that = this;
    
    // 请求订阅消息权限
    wx.requestSubscribeMessage({
      tmplIds: ['YOUR_TEMPLATE_ID'],
      success(res) {
        if (res['YOUR_TEMPLATE_ID'] === 'accept') {
          // 发送到后端保存订阅状态
          wx.request({
            url: `${API_BASE}/subscribe`,
            method: 'POST',
            data: {
              openId: '获取用户openId',
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

### 3.5 阶段四：推送接入（1-2天）

#### 3.5.1 订阅消息模板

在微信公众平台创建模板：

```
{{date.DATA}}
{{weather.DATA}}
{{food1.DATA}}
{{food2.DATA}}
{{food3.DATA}}
```

#### 3.5.2 推送服务

**pushService.js**
```javascript
const axios = require('axios');

async function sendDailyPush(users) {
  const accessToken = await getAccessToken();
  
  for (const user of users) {
    const weather = await getWeather(user.city);
    const foods = getRecommendations(weather.condition);
    
    const message = {
      touser: user.openId,
      template_id: 'YOUR_TEMPLATE_ID',
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
      'https://api.weixin.qq.com/cgi-bin/message/subscribe/send',
      message,
      { params: { access_token: accessToken } }
    );
  }
}

async function getAccessToken() {
  const appId = process.env.WEIXIN_APPID;
  const secret = process.env.WEIXIN_SECRET;
  
  const res = await axios.get(
    `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${appId}&secret=${secret}`
  );
  
  return res.data.access_token;
}
```

#### 3.5.3 定时任务

```javascript
// cron job - 每天早上8点执行
cron.schedule('0 8 * * *', async () => {
  const users = await getSubscribedUsers();
  await sendDailyPush(users);
});
```

---

### 3.6 阶段五：测试上线（3-5天）

#### 3.6.1 测试清单

| 测试项 | 内容 |
|--------|------|
| 功能测试 | 天气显示、美食推荐、订阅、推送 |
| 兼容性测试 | iOS/Android 不同版本 |
| 网络测试 | 弱网、离线等场景 |
| 性能测试 | 页面加载时间、接口响应 |

#### 3.6.2 提交审核

1. 在微信开发者工具点击「上传」
2. 填写版本号和备注
3. 在公众平台提交审核
4. 等待审核（通常1-3天）

#### 3.6.3 发布

审核通过后，在公众平台点击「发布」

---

## 四、数据字典

### 4.1 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| openId | string | 微信openId |
| city | string | 订阅城市 |
| subscribeTime | string | 订阅时间 |
| notifyTime | string | 推送时间 |

### 4.2 美食库

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| name | string | 美食名称 |
| reason | string | 推荐理由 |
| tags | json | 标签数组 |
| weatherTypes | json | 适用天气 |

---

## 五、注意事项

### 5.1 接口限制

- wttr.in 免费有频率限制，生产环境建议用和风天气 API
- 微信订阅消息有每月推送次数限制

### 5.2 安全

- 不要在前端暴露 AppSecret
- 所有接口使用 HTTPS
- 验证用户身份

### 5.3 费用

| 项目 | 费用 |
|------|------|
| 微信小程序认证 | 免费（个人） |
| 服务器 | 现有 K8s 集群 |
| 天气 API | 免费版够用 |
| 域名备案 | 如需国内访问 |

---

## 六、后续迭代

- [ ] 美食地图（附近推荐商家）
- [ ] 社交分享
- [ ] 会员功能
- [ ] AI 智能推荐

---

*文档结束*
