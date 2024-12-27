from typing import Dict, Any, Optional
import pandas as pd
from app.core.llm import LLMManager
from app.utils.data_processor import process_dataframe

class ChatService:
    def __init__(self):
        self.llm_manager = LLMManager()
    
    async def process_query(
        self,
        query: str,
        context: Dict[str, Any],
        data_context: Optional[Dict[str, Any]] = None
    ):
        try:
            # 获取数据处理指令
            llm_response = await self.llm_manager.analyze(
                query=query,
                context=context,
                data_context=data_context
            )
            
            # 执行数据处理
            if 'data_operation' in llm_response:
                df = context['data']  # 假设context中的data是DataFrame
                processed_result = process_dataframe(
                    df,
                    llm_response['data_operation']
                )
                
                return {
                    "answer": llm_response['answer'],
                    "data_results": {
                        "processed_data": processed_result.to_dict(orient='records') 
                            if isinstance(processed_result, pd.DataFrame) 
                            else processed_result,
                        "data_type": llm_response.get('data_type', 'table'),
                        "suggested_viz_type": llm_response.get('suggested_viz_type')
                    },
                    "code_snippet": llm_response.get('code_snippet'),
                    "suggestions": llm_response.get('suggestions', [])
                }
            else:
                return {
                    "answer": llm_response['answer'],
                    "suggestions": llm_response.get('suggestions', [])
                }
                
        except Exception as e:
            return {"error": str(e)} 