# QMusicSign
JackHanQMusicSign` 是一个接收 QQ 音乐请求参数串、本地计算并返回 sign`的 HTTP 服务。逆向还原了 QQ 音乐前端的签名算法（基于 SHA1 摘要 + 异或混淆 + 自定义 base64 编码）支持 GET / POST 多种传参方式，可作为爬虫 / 自动化脚本的签名中间件，开箱即用。
