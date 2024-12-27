from typing import List
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # 应用配置
    PROJECT_NAME: str = "CSV数据分析助手"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "基于LLM的CSV数据分析工具"
    API_V1_STR: str = "/api/v1"
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # OpenAI配置
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["csv"]
    UPLOAD_DIRECTORY: Path = Path("./uploads")
    
    # 缓存配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    CACHE_TTL: int = 3600
    
    # 会话管理配置
    MAX_CONVERSATION_HISTORY: int = 50  # 每个会话保留的最大对话数
    SESSION_EXPIRE_DAYS: int = 7    # 会话过期时间（天）
    MAX_ACTIVE_SESSIONS: int = 100  # 最大活动会话数
    
    # 文件管理配置
    MAX_FILES_PER_SESSION: int = 5  # 每个会话最大文件数
    FILE_EXPIRE_DAYS: int = 7      # 文件保留时间（天）
    CLEANUP_INTERVAL: int = 3600   # 清理间隔（秒）
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "ALLOWED_ORIGINS":
                if raw_val.startswith("[") and raw_val.endswith("]"):
                    return eval(raw_val)
                return [x.strip() for x in raw_val.split(",")]
            elif field_name == "UPLOAD_DIRECTORY":
                return Path(raw_val)
            return raw_val

settings = Settings()

# 确保上传目录存在
settings.UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True) 