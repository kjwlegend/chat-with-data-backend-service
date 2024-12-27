from fastapi import UploadFile
import pandas as pd
from typing import Dict, Any, Optional, List
from pathlib import Path
from app.core.config import settings
import uuid
import json
import shutil
from datetime import datetime

class FileService:
    def __init__(self):
        self.base_dir = settings.UPLOAD_DIRECTORY
        
    async def process_csv(self, session_id: str, filename: str, df: pd.DataFrame) -> Dict[str, Any]:
        """处理上传的CSV文件"""
        try:
            # 创建会话目录
            session_dir = self.base_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件ID和目录
            file_id = str(uuid.uuid4())
            file_dir = session_dir / file_id
            file_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存文件元数据
            metadata = {
                "file_id": file_id,
                "session_id": session_id,
                "original_filename": filename,
                "created_at": datetime.now().isoformat(),
                "file_size": df.memory_usage(deep=True).sum(),
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": self._get_column_info(df)
            }
            
            # 保存元数据
            with open(file_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            # 保存数据
            df.to_parquet(file_dir / "data.parquet")
            
            # 创建分析结果目录
            (file_dir / "analysis_results").mkdir(exist_ok=True)
            
            return {
                "success": True,
                "file_id": file_id,
                "summary": self._generate_summary(df),
                "columns": metadata["columns"],
                "sample_data": df.head(5).to_dict(orient='records')
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_file_data(self, session_id: str, file_id: str) -> Optional[pd.DataFrame]:
        """获取文件数据"""
        try:
            file_path = self.base_dir / session_id / file_id / "data.parquet"
            if file_path.exists():
                return pd.read_parquet(file_path)
            return None
        except Exception:
            return None
    
    async def save_analysis_result(
        self,
        session_id: str,
        file_id: str,
        analysis_id: str,
        result: Dict[str, Any]
    ):
        """保存分析结果"""
        result_dir = self.base_dir / session_id / file_id / "analysis_results"
        result_dir.mkdir(parents=True, exist_ok=True)
        
        with open(result_dir / f"{analysis_id}.json", "w") as f:
            json.dump(result, f, indent=2)
    
    async def cleanup_old_sessions(self):
        """清理过期会话数据"""
        try:
            for session_dir in self.base_dir.iterdir():
                if not session_dir.is_dir():
                    continue
                    
                # 检查会话目录中最新的文件修改时间
                latest_modified = max(
                    f.stat().st_mtime 
                    for f in session_dir.rglob("*") 
                    if f.is_file()
                )
                
                # 如果超过过期时间，删除整个会话目录
                if (datetime.now().timestamp() - latest_modified) > settings.FILE_EXPIRE_DAYS * 86400:
                    shutil.rmtree(session_dir)
                    
        except Exception as e:
            print(f"清理会话数据时出错: {e}")
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """生成数据摘要"""
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "basic_stats": df.describe().to_dict(),
            "missing_values": df.isnull().sum().to_dict()
        }
    
    def _get_column_info(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """获取列信息"""
        return [
            {
                "name": col,
                "type": str(df[col].dtype),
                "null_count": df[col].isnull().sum(),
                "unique_count": df[col].nunique()
            }
            for col in df.columns
        ] 