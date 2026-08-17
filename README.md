<div align="center">

# OpenQMusicSign

**QQ 音乐 sign 参数·纯算生成服务**

纯算法本地生成 `cgi-bin/musicu.fcg` 请求签名 `sign`，SHA1 → 分段取值 → 异或混淆 → 自定义编码，零浏览器依赖、零外部算法。

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)
![Waitress](https://img.shields.io/badge/Waitress-WSGI-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

</div>
# QMusicSign
JackHanQMusicSign` 是一个接收 QQ 音乐请求参数串、本地计算并返回 sign`的 HTTP 服务。逆向还原了 QQ 音乐前端的签名算法（基于 SHA1 摘要 + 异或混淆 + 自定义 base64 编码）支持 GET / POST 多种传参方式，可作为爬虫 / 自动化脚本的签名中间件，开箱即用。

## 📖 项目简介

`JackHanQMusicSign` 是一个接收 QQ 音乐请求参数串、本地计算并返回 `sign` 的 HTTP 服务。

逆向还原了 QQ 音乐前端的签名算法（基于 SHA1 摘要 + 异或混淆 + 自定义 base64 编码），
支持 GET / POST 多种传参方式，可作为爬虫 / 自动化脚本的签名中间件，开箱即用。

<div align="center">
     <img src="https://github.com/zihan620-network/xiaohan/blob/main/qmusicsign.png">
</div>

## ✨ 功能特性

- 🧮 **纯算实现**：完整还原混淆算法，无环境校验，结果稳定一致
- 🔐 **签名原理**：SHA1 摘要 + 62 位自定义字符表编码 + 异或混淆，固定 `zzc` 前缀
- 🌐 **HTTP API**：GET / POST 通用接口，支持 JSON / 原始字符串 / 查询参数
- 🚀 **WSGI 生产服务**：基于 [waitress](https://github.com/Pylons/waitress)，非 Flask 开发服务器
- 🖥️ 桌面一键启动（Windows）

## 🧠 算法原理

给定请求参数串 `param_str`：

```
1. hex_hash = SHA1(param_str) 转大写 40 位十六进制
2. head = 按下标 [23,14,6,36,16,40,7,19] 取字符（越界忽略）
3. bytes[i] = (hex[2i]*16 + hex[2i+1]) ^ xorlist[i]      // 逐字节异或
4. mid  = 每 3 字节编码为 4 字符（末组 3 字符）             // 自定义 base64
5. tail = 按下标 [16,1,32,12,19,27,8,5] 取字符
6. sign = ("zzc" + head + mid + tail).lower()
```

> 自定义字符表：`ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789`（62 位，非标准 base64）


## 🚀 快速开始

### 方式一：源码运行

```bash
# 安装依赖
pip install flask waitress

# 启动服务（默认 127.0.0.1:5000）
python JackHanQMusicSign.py

# 自定义端口 / 允许局域网访问
python JackHanQMusicSign.py --port 8000 --host 0.0.0.0
```

### 方式二：运行 exe（Windows）

```bash
dist\JackHanQMusicSign.exe
```

打开 `http://127.0.0.1:5000/` 可查看项目介绍页。

## 🔌 接口文档

`GET | POST /sign`

### 请求参数

| 参数 | 位置 | 说明 |
| --- | --- | --- |
| `data` / `params` / `m` | body / query / JSON | 请求参数串（原始字符串），必填 |
| `raw` | query `1/true/yes` 或 Header `X-Raw: 1` | 返回纯文本 sign |

### 调用示例

```bash
# 1. POST 原始 JSON 字符串（推荐）
curl -X POST http://127.0.0.1:5000/sign \
     -H "Content-Type: text/plain" \
     --data '{"comm":{...},"req_1":{...}}'

# 2. JSON 包裹 data 字段
curl -X POST http://127.0.0.1:5000/sign \
     -H "Content-Type: application/json" \
     -d '{"data":"{\"comm\":{...},\"req_1\":{...}}"}'

# 3. GET 查询参数（URL 编码）
curl "http://127.0.0.1:5000/sign?data=%7B%22comm%22..."

# 4. 直接返回纯文本 sign
curl "http://127.0.0.1:5000/sign?data=...&raw=true"
```

### 响应格式

成功（HTTP 200）：

```json
{
  "code": 0,
  "msg": "JackHanQMusicSign",
  "sign": "zzc4ffb910rbvz8amvgisvdmmjbr469qzye9e26001c",
  "length": 43
}
```

失败（HTTP 400 / 500）：

```json
{"code": 1, "msg": "JackHanQMusicSign", "error": "缺少参数 data，请提供请求参数串"}
```

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 1 | 缺少参数 data |
| 2 | 请求体读取失败 |
| 3 | sign 计算失败 |

## ⚠️ 注意事项

- `data` 必须是 QQ 音乐实际发送的**原始字符串**，键顺序不能改变，否则 sign 不一致
- 服务默认仅监听 `127.0.0.1`，公网部署请加 `--host 0.0.0.0` 并自行做好鉴权
- 本工具仅用于学习与技术研究，请遵守相关法律法规与平台条款
