"""
企业微信消息推送模块

功能：
- 群机器人Webhook发送消息
- 企业应用推送消息给指定用户

接入文档：https://open.work.weixin.qq.com/
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import requests
import os

router = APIRouter(prefix="/api/v1/wecom", tags=["企业微信"])


# ============== 数据模型 ==============

class WeComRobotMessage(BaseModel):
    """企业微信群机器人消息"""
    webhook_key: str  # 群机器人Webhook Key
    content: str
    msgtype: str = "text"


class WeComRobotMarkdownMessage(BaseModel):
    """企业微信Markdown消息"""
    webhook_key: str
    content: str  # Markdown内容


class WeComAppMessage(BaseModel):
    """企业应用推送消息"""
    user_ids: List[str]  # 用户UserID列表
    content: str
    agent_id: Optional[str] = None  # 应用ID


# ============== 内部函数 ==============

async def get_wecom_token() -> str:
    """获取企业微信access_token"""
    corp_id = os.getenv("WECOM_CORP_ID")
    corp_secret = os.getenv("WECOM_CORP_SECRET")
    
    if not corp_id or not corp_secret:
        raise HTTPException(
            status_code=500,
            detail="企业微信配置未完成，请设置 WECOM_CORP_ID 和 WECOM_CORP_SECRET"
        )
    
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    params = {
        "corpid": corp_id,
        "corpsecret": corp_secret
    }
    
    response = requests.get(url, params=params, timeout=10)
    result = response.json()
    
    if result.get("errcode") == 0:
        return result["access_token"]
    else:
        raise HTTPException(
            status_code=500,
            detail=f"获取access_token失败: {result.get('errmsg', '未知错误')}"
        )


# ============== 群机器人接口 ==============

@router.post("/robot/send")
async def send_robot_message(msg: WeComRobotMessage):
    """
    使用企业微信群机器人发送消息
    
    接入方式：
    1. 在企业微信群中添加群机器人
    2. 获取Webhook地址中的key参数
    3. 调用此接口发送消息
    """
    webhook_key = msg.webhook_key
    
    # 获取access_token
    access_token = await get_wecom_token()
    
    # 发送消息
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    
    payload = {
        "msgtype": msg.msgtype,
        msg.msgtype: {
            "content": msg.content
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            return {"status": "success", "message": "消息发送成功"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"发送失败: {result.get('errmsg', '未知错误')}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@router.post("/robot/send_markdown")
async def send_robot_markdown(msg: WeComRobotMarkdownMessage):
    """
    发送Markdown格式消息
    
    支持的Markdown语法：
    - 标题：# 标题内容
    - 加粗：**加粗内容**
    - 斜体：*斜体内容*
    - 换行：\\n
    - 链接：[文字](URL)
    - 引用：> 引用内容
    """
    access_token = await get_wecom_token()
    
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={msg.webhook_key}"
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": msg.content
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            return {"status": "success", "message": "Markdown消息发送成功"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"发送失败: {result.get('errmsg', '未知错误')}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@router.post("/robot/send_news")
async def send_robot_news(
    webhook_key: str,
    articles: List[dict]
):
    """
    发送图文消息
    
    参数articles示例:
    [
        {
            "title": "文章标题",
            "description": "文章描述",
            "url": "https://example.com",
            "picurl": "https://example.com/image.jpg"
        }
    ]
    """
    access_token = await get_wecom_token()
    
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    
    payload = {
        "msgtype": "news",
        "news": {
            "articles": articles
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            return {"status": "success", "message": "图文消息发送成功"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"发送失败: {result.get('errmsg', '未知错误')}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


# ============== 企业应用接口 ==============

@router.post("/app/send")
async def send_app_message(msg: WeComAppMessage):
    """
    通过企业微信应用发送消息给用户
    
    需要提前配置：
    1. 在企业微信管理后台创建企业内部应用
    2. 获取应用的AgentId和Secret
    3. 设置应用的可发送成员
    """
    access_token = await get_wecom_token()
    
    agent_id = msg.agent_id or os.getenv("WECOM_AGENT_ID")
    if not agent_id:
        raise HTTPException(
            status_code=500,
            detail="未配置 WECOM_AGENT_ID"
        )
    
    # 发送应用消息
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send"
    params = {
        "access_token": access_token,
        "agentid": agent_id
    }
    
    payload = {
        "touser": "|".join(msg.user_ids),
        "msgtype": "text",
        "text": {
            "content": msg.content
        }
    }
    
    try:
        response = requests.post(url, params=params, json=payload, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            invalid_user_ids = result.get("invaliduser", "").split("|") if result.get("invaliduser") else []
            return {
                "status": "success", 
                "message": "消息发送成功",
                "invalid_users": invalid_user_ids
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"发送失败: {result.get('errmsg', '未知错误')}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@router.get("/app/users")
async def get_app_users():
    """
    获取应用可见的成员列表
    """
    access_token = await get_wecom_token()
    agent_id = os.getenv("WECOM_AGENT_ID")
    
    if not agent_id:
        raise HTTPException(
            status_code=500,
            detail="未配置 WECOM_AGENT_ID"
        )
    
    url = f"https://qyapi.weixin.qq.com/cgi-bin/user/list"
    params = {
        "access_token": access_token,
        "department_id": 1,
        "fetch_child": 1,
        "status": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


# ============== 辅助接口 ==============

@router.get("/health")
async def health_check():
    """检查企业微信配置是否完整"""
    corp_id = os.getenv("WECOM_CORP_ID")
    corp_secret = os.getenv("WECOM_CORP_SECRET")
    agent_id = os.getenv("WECOM_AGENT_ID")
    
    return {
        "configured": bool(corp_id and corp_secret and agent_id),
        "corp_id": bool(corp_id),
        "corp_secret": bool(corp_secret),
        "agent_id": bool(agent_id)
    }


@router.post("/robot/test")
async def test_robot(webhook_key: str, content: str = "测试消息"):
    """
    测试群机器人是否可用
    """
    access_token = await get_wecom_token()
    
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    
    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        return {
            "webhook_key": webhook_key,
            "result": result,
            "success": result.get("errcode") == 0
        }
    except requests.exceptions.RequestException as e:
        return {
            "webhook_key": webhook_key,
            "error": str(e),
            "success": False
        }
