# -*- coding: utf-8 -*-
import hashlib
import json as _json
import logging
import sys

from flask import Flask, request, Response

APP_NAME = "JackHanQMusicSign"
# 签名核心参数
XORLIST = [89, 39, 179, 150, 218, 82, 58, 252, 177, 52, 186, 123, 120, 64, 242, 133, 143, 161, 121, 179]  # 异或表
BASE64CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'  # 自定义 62 位编码表
HEXMAP = {c: i for i, c in enumerate('0123456789ABCDEF')}
HEAD_IDX = [23, 14, 6, 36, 16, 40, 7, 19]  # 头部取位下标
TAIL_IDX = [16, 1, 32, 12, 19, 27, 8, 5]  # 尾部取位下标


def qq_sign(param_str, encoding='utf-8'):
    hex_hash = hashlib.sha1(param_str.encode(encoding)).hexdigest().upper()
    sign_head = ''.join(hex_hash[i] if i < len(hex_hash) else '' for i in HEAD_IDX)
    bytes_list = [
        (HEXMAP[hex_hash[2 * i]] * 16 + HEXMAP[hex_hash[2 * i + 1]]) ^ XORLIST[i]
        for i in range(20)
    ]

    # 自定义 base64 编码；下标越界(62/63)对应 JS 的 undefined，返回空串跳过
    def b64c(idx):
        return BASE64CHARS[idx] if 0 <= idx < len(BASE64CHARS) else ''

    sign_mid = ''
    i = 0
    while i < 20:
        a = b64c(bytes_list[i] >> 2)
        b = b64c(((bytes_list[i] & 3) << 4) | (bytes_list[i + 1] >> 4))
        if i + 2 == 20:
            e = b64c((bytes_list[i + 1] & 15) << 2)
            sign_mid += a + b + e
        else:
            c = b64c(((bytes_list[i + 1] & 15) << 2) | (bytes_list[i + 2] >> 6))
            d = b64c(bytes_list[i + 2] & 63)
            sign_mid += a + b + c + d
        i += 3
    sign_tail = ''.join(hex_hash[i] if i < len(hex_hash) else '' for i in TAIL_IDX)
    return ('zzc' + sign_head + sign_mid + sign_tail).lower()


def read_params():
    import json as _json
    raw = request.get_data(as_text=True).strip()
    if raw:
        if request.is_json:
            try:
                payload = _json.loads(raw)
                if isinstance(payload, dict):
                    for k in ("data", "params", "m"):
                        if k in payload:
                            return str(payload[k])
            except Exception:
                pass
        return raw
    for k in ("data", "params", "m"):
        if request.args.get(k):
            return request.args.get(k)
    return ""


def resp(code=0, **kw):
    r = {"code": code}
    r["msg"] = kw.pop("msg", APP_NAME)
    r.update(kw)
    return r


def jd(data, status=200):
    body = _json.dumps(data, ensure_ascii=False, sort_keys=False)
    return Response(body, status=status, mimetype="application/json; charset=utf-8")


app = Flask(__name__)
app.logger.setLevel(logging.WARNING)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False


@app.route("/", methods=["GET"])
def index():
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>JackHanQMusicSign</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei","PingFang SC",sans-serif;min-height:100vh;overflow:hidden;color:#fff;background:radial-gradient(circle at 50% 45%,#172554 0%,transparent 42%),linear-gradient(160deg,#050816 0%,#0f172a 48%,#050816 100%)}
.bg{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;border-radius:50%;filter:blur(100px);opacity:.5}
.orb1{width:520px;height:520px;top:-160px;left:-120px;background:radial-gradient(circle,#22d3ee,#3b82f6 55%,transparent 72%);animation:float1 14s ease-in-out infinite}
.orb2{width:460px;height:460px;right:-100px;bottom:-140px;background:radial-gradient(circle,#8b5cf6,#ec4899 60%,transparent 75%);animation:float2 18s ease-in-out infinite reverse}
.orb3{width:300px;height:300px;top:45%;left:62%;opacity:.35;background:radial-gradient(circle,#06b6d4,#3b82f6,transparent 75%);animation:float3 20s ease-in-out infinite}
@keyframes float1{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(50px,-35px) scale(1.1)}}
@keyframes float2{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-45px,30px) scale(1.08)}}
@keyframes float3{0%,100%{transform:translate(0,0)}50%{transform:translate(-30px,-35px)}}
.wrap{position:relative;z-index:1;width:100%;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:30px}
.hero{width:100%;text-align:center;display:flex;flex-direction:column;align-items:center;animation:heroIn 1.2s cubic-bezier(.2,.8,.2,1) both}
@keyframes heroIn{from{opacity:0;transform:translateY(24px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}
.badge{display:inline-flex;align-items:center;gap:9px;padding:8px 17px;margin-bottom:28px;border-radius:999px;font-size:12px;letter-spacing:3px;color:#cffafe;border:1px solid rgba(103,232,249,.35);background:rgba(34,211,238,.07);box-shadow:0 0 30px rgba(34,211,238,.08),inset 0 1px 0 rgba(255,255,255,.08);backdrop-filter:blur(12px)}
.dot{width:8px;height:8px;border-radius:50%;background:#22d3ee;box-shadow:0 0 8px #22d3ee,0 0 20px #22d3ee;animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.75)}}
h1{margin:0;font-size:clamp(48px,9vw,128px);font-weight:900;line-height:.95;letter-spacing:-4px;background:linear-gradient(90deg,#22d3ee,#3b82f6,#8b5cf6,#ec4899,#f43f5e,#f59e0b,#22d3ee);background-size:400% auto;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:gradientMove 8s linear infinite,titleGlow 3s ease-in-out infinite alternate;user-select:none}
@keyframes gradientMove{0%{background-position:0 50%}100%{background-position:400% 50%}}
@keyframes titleGlow{0%{filter:drop-shadow(0 0 12px rgba(34,211,238,.15)) drop-shadow(0 0 30px rgba(59,130,246,.08))}100%{filter:drop-shadow(0 0 22px rgba(34,211,238,.35)) drop-shadow(0 0 55px rgba(139,92,246,.2))}}
.sub{margin-top:30px;font-size:clamp(14px,2vw,18px);line-height:1.8;color:#94a3b8;letter-spacing:2px}
.sub span{color:#e2e8f0}
.line{width:180px;height:2px;margin-top:32px;border-radius:999px;background:linear-gradient(90deg,transparent,#22d3ee,#8b5cf6,#ec4899,transparent);background-size:200% 100%;animation:lineMove 4s linear infinite}
@keyframes lineMove{0%{background-position:200% 0}100%{background-position:-200% 0}}
.foot{position:absolute;left:0;right:0;bottom:30px;text-align:center;font-size:11px;letter-spacing:3px;color:rgba(148,163,184,.45)}
@media(max-width:600px){.wrap{padding:20px}h1{font-size:clamp(42px,13vw,72px);letter-spacing:-2px;line-height:1}.badge{margin-bottom:24px;letter-spacing:2px}.sub{margin-top:24px;padding:0 15px;letter-spacing:1px}.line{margin-top:26px;width:140px}.orb1{width:360px;height:360px}.orb2{width:330px;height:330px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important}}
</style>
</head>
<body>
<div class="bg"><div class="orb orb1"></div><div class="orb orb2"></div><div class="orb orb3"></div></div>
<main class="wrap">
<section class="hero">
<div class="badge"><span class="dot"></span>QQMUSIC SIGN</div>
<h1>JackHanQMusicSign</h1>
<p class="sub"><span>让音乐，拥有属于自己的色彩。</span><br>Your sound. Your signature.</p>
<div class="line"></div>
</section>
<div class="foot">JackHanQMusicSign</div>
</main>
</body>
</html>
"""
    return html


@app.route("/sign", methods=["GET", "POST"])
def sign():
    try:
        data_str = read_params().strip()
    except Exception:
        return jd(resp(2, error="body 读取失败"), 400)
    if not data_str:
        return jd(resp(1, error="缺少参数 data，请提供请求参数串"), 400)
    try:
        sign_val = qq_sign(data_str)
    except Exception as e:
        return jd(resp(3, error="sign 计算失败: " + str(e)), 500)
    if request.args.get("raw") in ("1", "true", "yes") or request.headers.get("X-Raw") == "1":
        return Response(sign_val, mimetype="text/plain")
    return jd(resp(0, sign=sign_val, length=len(sign_val)))


if __name__ == "__main__":
    port = 5000
    if "--port" in sys.argv:
        try:
            port = int(sys.argv[sys.argv.index("--port") + 1])
        except (ValueError, IndexError):
            pass
    host = "127.0.0.1"
    if "--host" in sys.argv:
        host = sys.argv[sys.argv.index("--host") + 1]
    print("%s 服务已启动: http://%s:%d/sign" % (APP_NAME, host, port))
    print("示例: curl -X POST http://%s:%d/sign -H 'Content-Type: text/plain' --data '你的参数字符串'" % (host, port))
    from waitress import serve
    serve(app, host=host, port=port)