from pydantic import BaseModel
from typing import Optional, Dict, List, Any

class ChatRequest(BaseModel):
    query: str
    session_id: str
    data_context: Optional[Dict[str, Any]] = None

class DataAnalysisResult(BaseModel):
    processed_data: Dict[str, Any]  # 处理后的数据
    data_type: str  # 数据类型，如 'table', 'series', 'aggregation' 等
    suggested_viz_type: Optional[str] = None  # 建议的可视化类型

class ChatResponse(BaseModel):
    answer: str  # LLM 的分析结论
    data_results: Optional[DataAnalysisResult] = None  # 处理后的数据
    code_snippet: Optional[str] = None  # 使用的 pandas 代码
    suggestions: List[str] = []  # 后续分析建议
    error: Optional[str] = None

class UploadResponse(BaseModel):
    success: bool
    file_id: str
    summary: Dict[str, Any]  # 数据基本统计信息
    columns: List[Dict[str, str]]  # 列名和数据类型
    sample_data: List[Dict[str, Any]]
    error: Optional[str] = None 