# 飞书消息发送 - 关键教训

## 问题：open_id cross app 错误

**现象**：发送飞书消息时返回 `Request failed with status code 400`，错误信息为 `open_id cross app`

**原因**：飞书的 `open_id` 是跨应用不同的。同一个用户在不同的飞书应用下会有不同的 `open_id`。之前存储的目标用户 `ou_6cd03b0f9501b02d17cae1a573b690c5` 是另一个应用下的 ID，而不是当前 OpenClaw 飞书应用（`cli_a92ad6cebbb8dbde`）下的 ID。

**解决方法**：

1. 获取当前应用的 tenant_access_token：
```bash
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a92ad6cebbb8dbde","app_secret":"kuTm6eYxx3BsaewZG0dlAbrUWjIvCLdL"}'
```

2. 使用 token 获取当前应用下的用户列表：
```bash
curl -X GET "https://open.feishu.cn/open-apis/contact/v3/users?user_id_type=open_id&page_size=10" \
  -H "Authorization: Bearer <token>"
```

3. 使用正确获取到的 `open_id` 发送消息

## 当前应用下的用户信息

- 用户名：用户920372
- open_id：ou_1dd4a1b1f9f9b7df3c86b7be0135a9c4
- user_id：b32a7874

## 更新记录

- 2026-03-21：首次发现此问题并解决
