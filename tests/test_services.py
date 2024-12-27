import asyncio
from app.services.context_service import ContextService
import uuid

async def test_redis_connection():
    try:
        context_service = ContextService()
        session_id = str(uuid.uuid4())
        
        # 测试创建会话
        session = await context_service.create_session(session_id)
        print("创建会话成功:", session)
        
        # 测试获取会话
        context = await context_service.get_context(session_id)
        print("获取会话成功:", context)
        
        # 测试获取活动会话
        active_sessions = await context_service.get_active_sessions()
        print("活动会话列表:", active_sessions)
        
        return True
    except Exception as e:
        print("测试失败:", str(e))
        return False

if __name__ == "__main__":
    success = asyncio.run(test_redis_connection())
    print("测试结果:", "成功" if success else "失败") 