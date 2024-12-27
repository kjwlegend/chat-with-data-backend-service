from fastapi import APIRouter, HTTPException
from redis.asyncio import Redis
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        # 检查 Redis 连接
        redis = Redis.from_url(settings.REDIS_URL)
        await redis.ping()
        
        return {
            "status": "healthy",
            "services": {
                "api": "up",
                "redis": "up"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        ) 