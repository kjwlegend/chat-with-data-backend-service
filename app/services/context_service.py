from typing import Dict, Any, Optional, List
import json
from app.core.config import settings
from redis.asyncio import Redis
from datetime import datetime

class ContextService:
    def __init__(self):
        self.redis = Redis(host=settings.REDIS_URL)
    
    async def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话上下文"""
        context = await self.redis.get(f"context:{session_id}")
        return json.loads(context) if context else None
    
    async def create_session(self, session_id: str) -> Dict[str, Any]:
        """创建新的会话"""
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "files": [],  # 关联的文件列表
            "conversation_history": [],
            "analysis_results": []
        }
        
        await self.redis.set(
            f"context:{session_id}",
            json.dumps(session_data),
            ex=settings.SESSION_EXPIRE_DAYS * 86400
        )
        return session_data
    
    async def add_file_to_session(self, session_id: str, file_info: Dict[str, Any]):
        """添加文件到会话"""
        context = await self.get_context(session_id)
        if not context:
            raise ValueError("Session not found")
        
        # 检查文件数量限制
        if len(context["files"]) >= settings.MAX_FILES_PER_SESSION:
            raise ValueError(f"每个会话最多支持 {settings.MAX_FILES_PER_SESSION} 个文件")
        
        # 添加文件信息
        context["files"].append({
            "file_id": file_info["file_id"],
            "filename": file_info["original_filename"],
            "added_at": datetime.now().isoformat()
        })
        
        await self.update_context(session_id, context)
    
    async def add_conversation(
        self,
        session_id: str,
        query: str,
        response: Dict[str, Any],
        file_id: Optional[str] = None
    ):
        """添加对话记录"""
        context = await self.get_context(session_id)
        if not context:
            raise ValueError("Session not found")
        
        # 添加对话记录
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "file_id": file_id
        }
        
        context["conversation_history"].append(conversation)
        
        # 限制对话历史长度
        if len(context["conversation_history"]) > settings.MAX_CONVERSATION_HISTORY:
            context["conversation_history"] = context["conversation_history"][-settings.MAX_CONVERSATION_HISTORY:]
        
        # 更新最后活动时间
        context["last_active"] = datetime.now().isoformat()
        
        await self.update_context(session_id, context)
    
    async def get_file_conversations(self, session_id: str, file_id: str) -> List[Dict[str, Any]]:
        """获取特定文件的对话历史"""
        context = await self.get_context(session_id)
        if not context:
            return []
        
        return [
            conv for conv in context["conversation_history"]
            if conv.get("file_id") == file_id
        ]
    
    async def update_context(self, session_id: str, context: Dict[str, Any]):
        """更新会话上下文"""
        await self.redis.set(
            f"context:{session_id}",
            json.dumps(context),
            ex=settings.SESSION_EXPIRE_DAYS * 86400
        )
    
    async def cleanup_inactive_sessions(self):
        """清理不活跃的会话"""
        active_sessions = await self.get_active_sessions()
        for session_id in active_sessions:
            context = await self.get_context(session_id)
            if not context:
                continue
                
            last_active = datetime.fromisoformat(context["last_active"])
            if (datetime.now() - last_active).days >= settings.SESSION_EXPIRE_DAYS:
                await self.redis.delete(f"context:{session_id}")
    
    async def get_active_sessions(self) -> List[str]:
        """获取所有活动会话"""
        keys = await self.redis.keys("context:*")
        return [key.split(":")[1] for key in keys] 