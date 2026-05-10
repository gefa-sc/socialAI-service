"""
SocialAI Service - AI生成路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field
from typing import Optional, List
import httpx
from config import settings
from database import get_db
from models.models import User
from routers.auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/ai", tags=["AI生成"])

# ==================== 请求模型 ====================

class GenerateContentRequest(BaseModel):
    """内容生成请求"""
    prompt: str = Field(..., description="生成提示词", min_length=1, max_length=2000)
    content_type: str = Field(default="article", description="内容类型: article/post/caption/hashtag")
    platform: Optional[str] = Field(default="wechat", description="目标平台: wechat/linkedin")
    tone: Optional[str] = Field(default="professional", description="语气: professional/friendly/humorous")
    length: Optional[str] = Field(default="medium", description="长度: short/medium/long")
    
class OptimizeContentRequest(BaseModel):
    """内容优化请求"""
    content: str = Field(..., description="原始内容")
    instruction: str = Field(..., description="优化指令: 改进/缩短/扩写/改写")

class TranslateContentRequest(BaseModel):
    """翻译请求"""
    content: str = Field(..., description="待翻译内容")
    target_lang: str = Field(..., description="目标语言: en/zh/ja/ko")

# ==================== 提示词模板 ====================

CONTENT_TEMPLATES = {
    "article": {
        "system": "你是一个专业的公众号编辑，擅长撰写高质量的文章。",
        "template": "请生成一篇关于{prompt}的文章，要求：\n1. 主题明确，观点清晰\n2. 内容详实，有理有据\n3. 长度适中，结构清晰\n4. 语气：{tone}"
    },
    "post": {
        "system": "你是一个社交媒体运营专家，擅长撰写吸引人的社交媒体帖子。",
        "template": "请为{prompt}生成一条社交媒体帖子，要求：\n1. 简洁有力，吸引眼球\n2. 适合在{platform}平台发布\n3. 带适当的话题标签\n4. 长度：{length}"
    },
    "caption": {
        "system": "你是一个文案专家，擅长撰写各种场景的文案。",
        "template": "请为{prompt}生成一个吸引人的文案/配文，要求：\n1. 简洁精炼\n2. 有感染力\n3. 适合社交媒体传播"
    },
    "hashtag": {
        "system": "你是一个社交媒体运营专家，擅长生成话题标签。",
        "template": "请为{prompt}生成相关的话题标签，要求：\n1. 热门且相关\n2. 数量适中（5-10个）\n3. 中英文混合"
    }
}

# ==================== MiniMax API调用 ====================

async def call_minimax(prompt: str, system_prompt: str = "", model: str = None) -> str:
    """调用MiniMax API"""
    if not settings.MINIMAX_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MiniMax API密钥未配置"
        )
    
    url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    headers = {
        "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    model = model or settings.MINIMAX_MODEL or "MiniMax-M2.5"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"MiniMax API错误: {response.text}"
                )
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="AI生成失败，请稍后重试"
                )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI生成超时，请稍后重试"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI生成失败: {str(e)}"
        )

# ==================== 路由 ====================

@router.post("/generate", summary="AI内容生成")
async def generate_content(
    request: GenerateContentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI内容生成接口
    
    - **prompt**: 生成提示词
    - **content_type**: 内容类型 (article/post/caption/hashtag)
    - **platform**: 目标平台
    - **tone**: 语气风格
    - **length**: 长度
    """
    template = CONTENT_TEMPLATES.get(request.content_type, CONTENT_TEMPLATES["article"])
    
    # 构建提示词
    prompt = template["template"].format(
        prompt=request.prompt,
        platform=request.platform,
        tone=request.tone,
        length=request.length
    )
    
    # 调用AI生成
    content = await call_minimax(prompt, template["system"])
    
    return {
        "success": True,
        "content": content,
        "content_type": request.content_type,
        "platform": request.platform,
        "prompt": request.prompt
    }

@router.post("/optimize", summary="内容优化")
async def optimize_content(
    request: OptimizeContentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    内容优化接口
    
    - **content**: 原始内容
    - **instruction**: 优化指令
    """
    prompt = f"请根据以下指令优化内容：\n\n指令：{request.instruction}\n\n原始内容：\n{request.content}"
    
    system_prompt = "你是一个专业的文案编辑，擅长优化和改写内容。"
    
    result = await call_minimax(prompt, system_prompt)
    
    return {
        "success": True,
        "original": request.content,
        "optimized": result,
        "instruction": request.instruction
    }

@router.post("/translate", summary="内容翻译")
async def translate_content(
    request: TranslateContentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    内容翻译接口
    
    - **content**: 待翻译内容
    - **target_lang**: 目标语言 (en/zh/ja/ko)
    """
    lang_map = {
        "en": "英语",
        "zh": "中文",
        "ja": "日语",
        "ko": "韩语"
    }
    
    target = lang_map.get(request.target_lang, "中文")
    
    prompt = f"请将以下内容翻译成{target}：\n\n{request.content}"
    
    system_prompt = "你是一个专业的翻译专家，擅长中英日韩等多种语言的翻译。"
    
    result = await call_minimax(prompt, system_prompt)
    
    return {
        "success": True,
        "original": request.content,
        "translated": result,
        "target_lang": request.target_lang
    }

@router.get("/templates", summary="获取提示词模板")
async def get_templates():
    """获取可用的提示词模板"""
    return {
        "templates": [
            {
                "id": key,
                "name": value["system"].split("，")[0],
                "description": value["template"][:50] + "..."
            }
            for key, value in CONTENT_TEMPLATES.items()
        ]
    }

@router.get("/models", summary="获取可用模型")
async def get_models():
    """获取可用的AI模型"""
    return {
        "models": [
            {"id": "MiniMax-M2.5", "name": "MiniMax M2.5", "provider": "MiniMax"},
            {"id": "MiniMax-M2.1", "name": "MiniMax M2.1", "provider": "MiniMax"}
        ],
        "current": settings.MINIMAX_MODEL
    }

@router.post("/chat", summary="AI对话")
async def chat(
    message: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user)
):
    """
    AI对话接口
    
    - **message**: 用户消息
    """
    prompt = message
    system_prompt = "你是SocialAI助手，一个专业、友好的AI助手，擅长回答各种问题。"
    
    result = await call_minimax(prompt, system_prompt)
    
    return {
        "success": True,
        "reply": result,
        "message": message
    }
