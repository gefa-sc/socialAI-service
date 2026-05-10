"""
SocialAI Service - 定时发布任务
"""
import os
import sys
import logging
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery import Celery
from celery_config import REDIS_URL
from database import SessionLocal
from models.models import Schedule, Content, SocialAccount
import httpx

# 创建 Celery 应用
celery_app = Celery("publish", broker=REDIS_URL, backend=REDIS_URL)

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.publish.check_pending_schedules")
def check_pending_schedules():
    """
    检查并执行待发布的调度任务
    每分钟执行一次
    """
    logger.info("🔍 检查待发布任务...")
    
    db = SessionLocal()
    try:
        # 查找所有已到期的待发布任务
        pending_schedules = db.query(Schedule).filter(
            Schedule.status == "pending",
            Schedule.scheduled_at <= datetime.utcnow()
        ).all()
        
        logger.info(f"📋 发现 {len(pending_schedules)} 个待发布任务")
        
        for schedule in pending_schedules:
            # 标记为执行中
            schedule.status = "running"
            db.commit()
            
            # 执行发布
            result = execute_publish(schedule, db)
            
            if result["success"]:
                schedule.status = "published"
                schedule.published_at = datetime.utcnow()
                schedule.platform_post_id = result.get("post_id")
                schedule.error_message = None
                logger.info(f"✅ 发布成功: {schedule.id}")
            else:
                schedule.status = "failed"
                schedule.error_message = result.get("error")
                logger.error(f"❌ 发布失败: {schedule.id} - {result.get('error')}")
            
            db.commit()
        
        return {"success": True, "processed": len(pending_schedules)}
    
    except Exception as e:
        logger.error(f"❌ 检查待发布任务出错: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="tasks.publish.execute_publish")
def execute_publish_task(schedule_id: str):
    """
    执行单个发布任务（可手动触发）
    """
    logger.info(f"📤 执行发布任务: {schedule_id}")
    
    db = SessionLocal()
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if not schedule:
            return {"success": False, "error": "调度不存在"}
        
        if schedule.status != "pending":
            return {"success": False, "error": f"当前状态不允许发布: {schedule.status}"}
        
        # 标记为执行中
        schedule.status = "running"
        db.commit()
        
        # 执行发布
        result = execute_publish(schedule, db)
        
        if result["success"]:
            schedule.status = "published"
            schedule.published_at = datetime.utcnow()
            schedule.platform_post_id = result.get("post_id")
            schedule.error_message = None
            logger.info(f"✅ 发布成功: {schedule_id}")
        else:
            schedule.status = "failed"
            schedule.error_message = result.get("error")
            logger.error(f"❌ 发布失败: {schedule_id}")
        
        db.commit()
        return result
    
    except Exception as e:
        logger.error(f"❌ 执行发布任务出错: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()


def execute_publish(schedule: Schedule, db) -> dict:
    """
    执行发布操作
    
    返回: (success: bool, result: dict)
    """
    # 获取内容和账户
    content = db.query(Content).filter(
        Content.id == schedule.content_id
    ).first()
    
    account = db.query(SocialAccount).filter(
        SocialAccount.id == schedule.social_account_id
    ).first()
    
    if not content or not account:
        return {"success": False, "error": "内容或账户不存在"}
    
    try:
        # 根据平台调用不同的发布API
        if account.platform == "wechat":
            post_id = _publish_to_wechat(account, content)
        elif account.platform == "linkedin":
            post_id = _publish_to_linkedin(account, content)
        else:
            return {"success": False, "error": f"不支持的平台: {account.platform}"}
        
        return {"success": True, "post_id": post_id}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def _publish_to_wechat(account: SocialAccount, content: Content) -> str:
    """
    发布到微信公众号
    """
    # 调用微信群发API
    url = "https://api.weixin.qq.com/cgi-bin/message/mass/sendall"
    params = {"access_token": account.access_token}
    
    data = {
        "filter": {"is_to_all": True},
        "text": {"content": content.body},
        "msgtype": "text"
    }
    
    response = httpx.post(url, params=params, json=data, timeout=30)
    result = response.json()
    
    if "errcode" in result and result["errcode"] != 0:
        raise Exception(f"微信API错误: {result.get('errmsg', result['errcode'])}")
    
    return f"wechat_msg_{result.get('msg_id', 'unknown')}"


def _publish_to_linkedin(account: SocialAccount, content: Content) -> str:
    """
    发布到 LinkedIn
    """
    # LinkedIn API 调用
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {account.access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    data = {
        "author": f"urn:li:person:{account.account_name}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content.body},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    response = httpx.post(url, headers=headers, json=data, timeout=30)
    
    if response.status_code not in [200, 201]:
        raise Exception(f"LinkedIn API错误: {response.text}")
    
    result = response.json()
    return result.get("id", "linkedin_post_unknown")


@celery_app.task(name="tasks.publish.retry_failed")
def retry_failed_schedules(max_retries: int = 3):
    """
    重试失败的发布任务
    """
    logger.info("🔄 重试失败的任务...")
    
    db = SessionLocal()
    try:
        # 查找失败的任务（重试次数小于最大重试次数）
        failed_schedules = db.query(Schedule).filter(
            Schedule.status == "failed",
            Schedule.retry_count < max_retries
        ).all()
        
        logger.info(f"📋 发现 {len(failed_schedules)} 个失败任务需要重试")
        
        for schedule in failed_schedules:
            schedule.status = "pending"
            schedule.retry_count = (schedule.retry_count or 0) + 1
            db.commit()
            
            # 立即触发执行
            execute_publish_task.delay(str(schedule.id))
        
        return {"success": True, "retried": len(failed_schedules)}
    
    except Exception as e:
        logger.error(f"❌ 重试失败: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()


# 添加重试次数字段支持
def init_db():
    """初始化数据库（如果需要）"""
    from sqlalchemy import text
    db = SessionLocal()
    try:
        # 检查 retry_count 列是否存在
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'schedules' AND column_name = 'retry_count'"))
        if not result.fetchone():
            # 添加列
            db.execute(text("ALTER TABLE schedules ADD COLUMN retry_count INTEGER DEFAULT 0"))
            db.commit()
            logger.info("✅ 添加 retry_count 字段成功")
    except Exception as e:
        logger.warning(f"数据库初始化: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # 初始化数据库
    init_db()
    
    # 启动 Celery worker
    celery_app.start()
