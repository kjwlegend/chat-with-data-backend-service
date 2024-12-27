from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.file_service import FileService
from app.services.context_service import ContextService
from app.schemas.response import UploadResponse
from app.core.config import settings
import pandas as pd
import uuid

router = APIRouter()

@router.post("/csv/{session_id}", response_model=UploadResponse)
async def upload_csv(
    session_id: str,
    file: UploadFile = File(...),
    file_service: FileService = Depends(),
    context_service: ContextService = Depends()
):
    """上传CSV文件到指定会话"""
    # 验证文件类型
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="只支持CSV文件"
        )
    
    # 验证文件大小
    file_size = 0
    content = b''
    while chunk := await file.read(8192):
        content += chunk
        file_size += len(chunk)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE/1024/1024}MB)"
            )
    
    try:
        # 读取CSV数据
        df = pd.read_csv(pd.io.common.BytesIO(content))
        
        # 处理文件
        result = await file_service.process_csv(
            session_id=session_id,
            filename=file.filename,
            df=df
        )
        
        if result["success"]:
            # 添加文件到会话
            await context_service.add_file_to_session(session_id, result)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理CSV文件时出错: {str(e)}"
        ) 