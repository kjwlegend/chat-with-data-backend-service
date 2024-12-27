from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.context_service import ContextService
from typing import Optional

router = APIRouter()

@router.post("/analyze", response_model=ChatResponse)
async def analyze_data(
    request: ChatRequest,
    chat_service: ChatService = Depends(),
    context_service: ContextService = Depends()
):
    """
    分析数据并返回结果
    """
    try:
        # 获取会话上下文
        context = await context_service.get_context(request.session_id)
        if not context:
            raise HTTPException(
                status_code=400,
                detail="未找到有效的会话数据，请先上传CSV文件"
            )
        
        # 处理分析请求
        response = await chat_service.process_query(
            query=request.query,
            context=context,
            data_context=request.data_context
        )
        
        # 更新会话上下文
        await context_service.update_context(
            session_id=request.session_id,
            new_context={
                "last_query": request.query,
                "last_response": response
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理分析请求时出错: {str(e)}"
        )

@router.get("/context/{session_id}")
async def get_session_context(
    session_id: str,
    context_service: ContextService = Depends()
):
    """
    获取会话上下文信息
    """
    context = await context_service.get_context(session_id)
    if not context:
        raise HTTPException(
            status_code=404,
            detail="未找到会话上下文"
        )
    return context 