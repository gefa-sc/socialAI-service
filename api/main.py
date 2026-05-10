"""
SocialAI Service - 主应用入口
"""
import hashlib
import time
import os
from fastapi import FastAPI, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config import settings
from database import engine, Base
from routers import auth, contents, schedules, analytics, social_accounts, ai, dingtalk, wecom

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SocialAI Service API",
    description="AI驱动的社交媒体管理助手",
    version="1.0.0",
    redirect_slashes=False,
)

# 微信域名验证文件
@app.get("/MP_verify_4eqvvZHaC5df9Ana.txt")
async def wechat_verify_file():
    """微信域名验证文件"""
    return PlainTextResponse(content="4eqvvZHaC5df9Ana")

@app.get("/88e3cdc1664ea9c3f26b9ec1c6c940c3.txt")
async def wechat_verify_file2():
    """微信域名验证文件2"""
    return PlainTextResponse(content="8699186fc2480cff55eb81f081d384129bd34140")

# 静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 微信服务器验证Token
WECHAT_TOKEN = "wechat_token"

def verify_wechat_signature(token: str, signature: str, timestamp: str, nonce: str) -> bool:
    """验证微信签名"""
    tmp_list = sorted([token, timestamp, nonce])
    tmp_str = ''.join(tmp_list)
    tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    return tmp_str == signature

# 微信服务器验证接口 (用于配置URL时的验证)
@app.get("/api/accounts/callback/wechat")
async def wechat_verify(
    signature: str = Query(None),
    timestamp: str = Query(None),
    nonce: str = Query(None),
    echostr: str = Query(None)
):
    """微信服务器URL验证"""
    # 直接返回 echostr，忽略签名验证（测试号模式）
    return PlainTextResponse(content=echostr or "success")

# 微信回调简路径 (用于测试号配置)
@app.get("/callback")
@app.get("/callback/wechat")
async def wechat_callback_simple(echostr: str = Query(None)):
    """简化的微信回调路径"""
    return PlainTextResponse(content=echostr or "success")

# 微信消息接收接口 (POST)
@app.post("/api/accounts/callback/wechat")
async def wechat_message(request: Request):
    """接收微信消息推送"""
    body = await request.body()
    # 这里可以处理微信发来的消息
    # 目前先简单返回success
    return PlainTextResponse(content="success")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(contents.router, prefix="/api/contents", tags=["内容管理"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["发布调度"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["数据分析"])
app.include_router(social_accounts.router, prefix="/api/accounts", tags=["社交账户"])
app.include_router(ai.router, tags=["AI生成"])
app.include_router(dingtalk.router, tags=["钉钉"])
app.include_router(wecom.router, tags=["企业微信"])

@app.get("/")
async def root():
    return {"message": "SocialAI Service API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
