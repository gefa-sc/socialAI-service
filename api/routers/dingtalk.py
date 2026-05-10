"""
钉钉消息推送模块

功能：
- 群机器人Webhook发送消息（无需OAuth，最快接入）
- 企业应用推送消息给指定用户

接入文档：https://open.dingtalk.com/
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import requests
import os

router = APIRouter(prefix="/api/v1/dingtalk", tags=["钉钉"])


# ============== 数据模型 ==============

class DingTalkRobotMessage(BaseModel):
    """钉钉群机器人消息"""
    webhook: str  # 群机器人Webhook地址
    content: str
    msgtype: str = "text"


class DingTalkRobotCardMessage(BaseModel):
    """钉钉卡片消息"""
    webhook: str
    title: str
    content: str
    btn_orientation: str = "0"  # 按钮排列方向: 0-竖直 1-水平


class DingTalkAppMessage(BaseModel):
    """企业应用推送消息给用户"""
    user_ids: List[str]  # 用户UserID列表
    content: str
    agent_id: Optional[str] = None  # 企业应用ID


# ============== 群机器人接口 ==============

@router.post("/robot/send")
async def send_robot_message(msg: DingTalkRobotMessage):
    """
    使用群机器人发送消息
    
    这是最简单的接入方式，只需：
    1. 在钉钉群设置中添加群机器人
    2. 获取Webhook地址
    3. 调用此接口发送消息
    """
    url = msg.webhook
    
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


@router.post("/robot/send_card")
async def send_robot_card_message(msg: DingTalkRobotCardMessage):
    """
    发送卡片消息（富文本格式）
    
    支持更丰富的消息展示格式
    """
    url = msg.webhook
    
    # 使用Markdown格式的卡片消息
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": msg.title,
            "text": msg.content
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            return {"status": "success", "message": "卡片消息发送成功"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"发送失败: {result.get('errmsg', '未知错误')}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@router.post("/robot/send_link")
async def send_robot_link_message(
    webhook: str,
    title: str,
    text: str,
    message_url: str,
    pic_url: Optional[str] = None
):
    """
    发送链接消息
    
    参数:
    - webhook: 群机器人Webhook地址
    - title: 链接标题
    - text: 链接文本
    - message_url: 跳转URL
    - pic_url: 图片URL（可选）
    """
    payload = {
        "msgtype": "link",
        "link": {
            "title": title,
            "text": text,
            "messageUrl": message_url,
            "picUrl": pic_url or ""
        }
    }
    
    try:
        response = requests.post(webhook, json=payload, timeout=10)
        result = response.json()
        
        if result.get("errcode") == 0:
            return {"status": "success", "message": "链接消息发送成功"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"发送失败: {result.get('errmsg', '未知错误')}"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


# ============== 企业应用接口 ==============

async def get_dingtalk_token() -> str:
    """获取钉钉access_token"""
    app_key = os.getenv("DINGTALK_APP_KEY")
    app_secret = os.getenv("DINGTALK_APP_SECRET")
    
    if not app_key or not app_secret:
        raise HTTPException(
            status_code=500,
            detail="钉钉应用配置未完成，请设置 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET"
        )
    
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    
    data = {
        "appKey": app_key,
        "appSecret": app_secret
    }
    
    response = requests.post(url, json=data, timeout=10)
    result = response.json()
    
    if "accessToken" in result:
        return result["accessToken"]
    else:
        raise HTTPException(
            status_code=500,
            detail=f"获取access_token失败: {result}"
        )


@router.post("/app/send")
async def send_app_message(msg: DingTalkAppMessage):
    """
    通过企业应用发送消息给用户
    
    需要提前配置：
    1. 在钉钉开放平台创建企业内部应用
    2. 开通"消息通知"权限
    3. 设置应用可用范围
    """
    access_token = await get_dingtalk_token()
    
    agent_id = msg.agent_id or os.getenv("DINGTALK_AGENT_ID")
    if not agent_id:
        raise HTTPException(
            status_code=500,
            detail="未配置 DINGTALK_AGENT_ID"
        )
    
    # 发送工作通知
    url = f"https://api.dingtalk.com/v1.0/robot/oToMessages/batchSend?agentId={agent_id}"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {
        "userIds": msg.user_ids,
        "msg": {
            "msgtype": "text",
            "text": {"content": msg.content}
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        
        return result
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@router.get("/app/users")
async def get_app_users():
    """
    获取应用可用范围内的用户列表
    """
    access_token = await get_dingtalk_token()
    
    url = "https://api.dingtalk.com/v1.0/contact/users?offset=0&size=100"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


# ============== 辅助接口 ==============

@router.get("/health")
async def health_check():
    """检查钉钉配置是否完整"""
    app_key = os.getenv("DINGTALK_APP_KEY")
    app_secret = os.getenv("DINGTALK_APP_SECRET")
    agent_id = os.getenv("DINGTALK_AGENT_ID")
    
    return {
        "configured": bool(app_key and app_secret and agent_id),
        "app_key": bool(app_key),
        "app_secret": bool(app_secret),
        "agent_id": bool(agent_id)
    }
