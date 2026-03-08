# 🛡️ 网络安全深度知识库

> 最后更新: 2026-03-07
> 学习来源: Tavily API 自动搜索 + 用户指导

---

## 一、红队攻防技术

### 1.1 渗透测试流程 (PTES)
```
1. 信息收集 → 2. 漏洞扫描 → 3. 漏洞利用 → 4. 权限提升 → 5. 横向移动 → 6. 持久化 → 7. 清理痕迹
```

### 1.2 信息收集
- **被动收集**: WHOIS、搜索引擎、社交媒体、Shodan、Censys
- **主动扫描**: Nmap 端口扫描、Masscan 快速扫描、OneForAll 子域名挖掘
- **工具推荐**:
  - Nmap: 端口和服务识别
  - Maltego: 关系图谱分析
  - theHarvester: 邮箱和子域名收集
  - Gobuster: 目录和文件爆破

### 1.3 漏洞扫描与利用
- **Web漏洞**:
  - SQL注入 (SQLi)
  - 跨站脚本 (XSS)
  - CSRF 跨站请求伪造
  - 文件上传漏洞
  - SSRF 服务器端请求伪造
  - RCE 远程代码执行

- **工具**:
  - AWVS: 商业漏洞扫描
  - Acunetix: Web应用扫描
  - Burp Suite: Web安全测试
  - SQLMap: SQL注入利用
  - XSSer: XSS 测试框架

### 1.4 权限提升 (Privilege Escalation)
- **Windows**:
  - 内核漏洞利用 (CVE)
  - 服务配置错误
  - 不当的权限配置
  - DLL 劫持
  - 热补丁漏洞

- **Linux**:
  - SUID/GUID 滥用
  - Cron 任务提权
  - 内核漏洞
  - sudo 配置错误
  - 内存溢出漏洞

### 1.5 横向移动 (Lateral Movement)
- Pass-the-Hash (PtH)
- Pass-the-Ticket (Kerberos)
- RDP  hijacking
- WMI / PowerShell Remoting
- SMB/Relay 攻击

### 1.6 持久化 (Persistence)
- Windows: 注册表后门、计划任务、WMI 事件订阅、服务创建
- Linux: SSH 密钥、cron 后门、cronabe、rootkit

---

## 二、漏洞分析

### 2.1 常见漏洞分类 (OWASP Top 10)
1. Broken Access Control (访问控制失效)
2. Cryptographic Failures (加密失败)
3. Injection (注入攻击)
4. Insecure Design (不安全设计)
5. Security Misconfiguration (安全配置错误)
6. Vulnerable Components (漏洞组件)
7. Authentication Failures (认证失败)
8. Data Integrity Failures (数据完整性失效)
9. Logging Failures (日志记录失败)
10. SSRF (服务端请求伪造)

### 2.2 二进制漏洞
- 栈溢出 (Stack Overflow)
- 堆溢出 (Heap Overflow)
- 格式化字符串漏洞
- UAF (Use-After-Free)
- 整数溢出
- Race Condition (条件竞争)

### 2.3 漏洞赏金平台
- HackerOne
- Bugcrowd
- YesWeHack
- 补天
- 漏洞盒子

---

## 三、防御技术

### 3.1 网络防御
- **防火墙**: iptables、pf、硬件防火墙
- **入侵检测/防御**: Snort、Suricata、Zeek (Bro)
- **WAF (Web应用防火墙)**: ModSecurity、硬件WAF
- **DDoS 防护**: Cloudflare、Akamai、阿里云盾

### 3.2 主机安全
- **HIDS (主机入侵检测)**: OSSEC、Wazuh、AIDE
- **EDR (端点检测与响应)**: CrowdStrike、Cylance
- **基线核查**: Lynis、CIS-CAT

### 3.3 应用安全
- **代码审计**: Fortify、Checkmarx、SonarQube
- **SAST/DAST**: 静态/动态应用安全测试
- **依赖检查**: OWASP Dependency-Check、Snyk

### 3.4 身份与访问管理
- **多因素认证 (MFA)**: TOTP、硬件令牌
- **单点登录 (SSO)**: SAML、OAuth、OIDC
- **最小权限原则**: RBAC、ABAC

### 3.5 安全监控与响应
- **SIEM (安全信息和事件管理)**: Splunk、ELK Stack、QRadar
- **威胁情报**: MISP、TAXII
- **应急响应**: IR 流程、取证分析

---

## 四、密码学基础

### 4.1 对称加密
- AES (高级加密标准)
- DES/3DES (数据加密标准)
- ChaCha20
- RC4 (已废弃)

### 4.2 非对称加密
- RSA (大数分解)
- ECC (椭圆曲线密码学)
- DH (Diffie-Hellman 密钥交换)
- ElGamal

### 4.3 哈希函数
- SHA-256、SHA-3 系列
- BLAKE2/BLAKE3
- MD5 (已废弃)
- SHA-1 (已废弃)

### 4.4 现代密码学应用
- TLS/SSL 协议
- 端到端加密 (E2EE)
- 零知识证明 (ZKP)
- 同态加密
- 多方安全计算 (MPC)

---

## 五、安全工具

### 5.1 Kali Linux 工具集
```
信息收集:    Nmap, Masscan, Maltego, theHarvester
漏洞分析:    OpenVAS, Nikto, Lynis
Web应用:     Burp Suite, OWASP ZAP, SQLMap, XSSer
密码攻击:    John the Ripper, Hashcat, Hydra, Medusa
无线安全:    Aircrack-ng, Kismet
逆向工程:    Ghidra, IDA Pro, Radare2
```

### 5.2 安全平台
- ** VulnHub**: 靶机练习
- **HackTheBox**: 在线渗透测试实验室
- **TryHackMe**: 学习路径平台
- **PortSwigger Web Security Academy**: Web安全学习
- **PentesterLab**: Web渗透测试练习

### 5.3 自动化渗透
- AutoSploit
- RouterSploit
- Metasploit Framework
- Cobalt Strike (商业红队工具)

---

## 六、云安全

### 6.1 云平台安全
- **CSPM**: 云安全态势管理
- **CWPP**: 云工作负载保护
- **CASB**: 云访问安全代理

### 6.2 云安全工具
- AWS: GuardDuty, Security Hub, Inspector
- Azure: Azure Security Center, Sentinel
- GCP: Security Command Center

### 6.3 容器安全
- Docker/B Pod Security
- Falco (运行时安全)
- Trivy (漏洞扫描)
- Clair (容器镜像分析)

---

## 七、学习路线图

### 入门阶段 (3-6个月)
```
Week 1-4:   计算机基础 + Linux/Windows 操作
Week 5-8:   网络协议 (TCP/IP, HTTP, DNS, TLS)
Week 9-12:  编程能力 (Python/Bash/Golang)
Week 13-16: Web安全基础 (OWASP Top 10)
Week 17-20: 工具使用 (Burp, Nmap, SQLMap)
Week 21-24: 靶场练习 (VulnHub, HTB)
```

### 中级阶段 (6-12个月)
- 深入一种漏洞类型 (Web/二进制/移动)
- 学习逆向工程和漏洞挖掘
- 参与CTF比赛
- 考取证书 (OSCP, CEH)

### 高级阶段 (1-2年)
- 红队攻防实战
- 漏洞研究 (CVE)
- 安全开发 (SDL)
- 体系建设 (蓝队/红队/紫队)

---

## 八、资源推荐

### 📚 书籍
- 《Web应用安全权威指南》
- 《Metasploit渗透测试指南》
- 《灰帽黑客》
- 《内网安全攻防》
- 《逆向工程核心原理》

### 🎓 在线课程
- PortSwigger Web Security Academy (免费)
- Offensive Security (OSCP)
- SANS Institute
- Cybrary

### 🛠️ 实用工具
- **信息收集**: Nmap, Gobuster, crt.sh
- **Web测试**: Burp Suite, OWASP ZAP, SQLMap
- **密码破解**: Hashcat, John
- **逆向分析**: Ghidra, x64dbg
- **漏洞利用**: Metasploit

### 🌐 社区
- FreeBuf (国内)
- 安全客
- 先知社区
- 嘶吼
- Reddit: netsec, cybersecurity

---

## 九、实践平台

### 靶场环境
- **VulnHub**: 下载靶机本地练习
- **HackTheBox**: 在线实验室
- **TryHackMe**: 学习路径
- **PentesterLab**: 专项训练
- **DVWA**: Web安全练习

### CTF 平台
- CTFHub
- XCTF
- PicoCTF
- HackTheBox CTF
- Root Me

---

## 十、职业发展

### 岗位方向
1. **渗透测试工程师**: 模拟攻击测试
2. **安全研究员**: 漏洞挖掘与分析
3. **安全开发 (SecDevOps)**: 安全编码
4. **安全运维**: 安全监控与响应
5. **安全架构师**: 安全体系设计

### 认证证书
- **入门**: CEH, Security+
- **中级**: OSCP, OSCE, CISSP
- **高级**: OSCE3, OSEE, CISSP
- **云安全**: CCSK, CCSP

---

> ⚠️ **声明**: 本知识库仅供学习和防御研究使用，请勿用于非法渗透测试。
> 所有实践请在授权环境下进行，遵守《网络安全法》等相关法律法规。

---

*学习永无止境，安全任重道远。*