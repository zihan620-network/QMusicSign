# JackHanQMusicSign

QQ 音乐（`cgi-bin/musicu.fcg`）接口 **sign 参数** 的纯算生成服务。

输入请求参数串（`o(t.data)` 的原始字符串），返回该请求所需的 `sign`。
纯算法本地计算，无任何依赖浏览器环境。

---

## 算法说明

对请求参数串 `param_str` 做如下处理：

1. **SHA1**：`hex_hash = SHA1(param_str)`，取大写 40 位十六进制。
2. **sign_head**：按下标 `[23, 14, 6, 36, 16, 40, 7, 19]` 取字符（越界忽略，共 7 位）。
3. **sign_mid**：
   - 按字节异或：`bytes[i] = (hex[2i] 十六进制值 * 16 + hex[2i+1] 十六进制值) ^ xorlist[i]`
   - `xorlist = [89, 39, 179, 150, 218, 82, 58, 252, 177, 52, 186, 123, 120, 64, 242, 133, 143, 161, 121, 179]`
   - 用自定义字符表 `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789`（62 位，非标准 base64）编码；下标 ≥ 62 时跳过该字符（对应 JS 的 `undefined`）。
4. **sign_tail**：按下标 `[16, 1, 32, 12, 19, 27, 8, 5]` 取字符（共 8 位）。
5. **拼接**：`sign = ("zzc" + sign_head + sign_mid + sign_tail).lower()`

**验证示例**：

```
param_str = {"comm":{"cv":4747474,...},"req_4":{...}}
SHA1  = DD69685AD37B71DB3E870E35FB14EFE3CC465405
sign  = zzc5d553a7he7bzakpsyeps7rog1qdzkpnlby3dc774d8
```

运行方式
### 运行 exe

不会用别用

## 接口使用

接口地址：`GET|POST /sign`

| 参数 | 位置 | 说明 |
| --- | --- | --- |
| `data` | body / query / JSON | 请求参数串（`o(t.data)` 原始字符串），必填 |
| `params` / `m` | 同上 | `data` 的别名 |
| `raw` | query（`1/true/yes`）或 Header `X-Raw: 1` | 为真时直接返回纯文本 sign |

支持四种传参方式：

```bash
# 1. 直接 POST 原始 JSON 字符串（推荐，Content-Type: text/plain）
curl -X POST http://127.0.0.1:5000/sign \
     -H "Content-Type: text/plain" \
     --data '{"comm":{...},"req_1":{...}}'

# 2. JSON 包裹 data 字段（Content-Type: application/json）
curl -X POST http://127.0.0.1:5000/sign \
     -H "Content-Type: application/json" \
     -d '{"data":"{\"comm\":{...},\"req_1\":{...}}"}'

# 3. 查询参数（需 URL 编码）
curl "http://127.0.0.1:5000/sign?data=%7B%22comm%22..."

# 4. 直接返回纯文本 sign
curl "http://127.0.0.1:5000/sign?data=...&raw=true"
```

---

## 响应格式

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
{"code": 1, "error": "缺少参数 data，请提供请求参数串", "msg": "JackHanQMusicSign"}
```

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 1 | 缺少参数 data |
| 2 | 请求体读取失败 |
| 3 | sign 计算失败 |

> 响应为 UTF-8，中文不做 unicode 转义（`JSON_AS_ASCII=False`）。

---

## 注意事项

- `data` 必须是 QQ 音乐实际发送的**原始字符串**，键顺序不能改变，否则 sign 不一致。
- 服务默认仅监听 `127.0.0.1`，如需局域网/公网访问请加 `--host 0.0.0.0`。
- 本工具仅用于学习与接口研究，使用者需自行承担后果。