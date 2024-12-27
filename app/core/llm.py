from typing import Dict, Any, Optional
import openai
from app.core.config import settings
import json
import pandas as pd

class LLMManager:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL  # 例如 "gpt-4" 或 "gpt-3.5-turbo"
        
    def _generate_system_prompt(self, context: Dict[str, Any]) -> str:
        """生成系统提示，包含数据上下文和分析要求"""
        df = context.get('data')
        if df is not None and isinstance(df, pd.DataFrame):
            data_info = {
                "columns": list(df.columns),
                "shape": df.shape,
                "dtypes": df.dtypes.astype(str).to_dict(),
                "sample": df.head(3).to_dict(orient='records')
            }
        else:
            data_info = {}

        return f"""你是一个数据分析助手。请根据用户的问题，生成相应的数据处理方案。
数据信息: {json.dumps(data_info, ensure_ascii=False)}

你需要返回以下格式的 JSON 响应:
{{
    "answer": "对分析结果的解释",
    "data_operation": {{
        "type": "操作类型(aggregation/filter/sort/statistical)",
        "method": "具体方法",
        "columns": ["涉及的列"],
        "additional_params": {{}}
    }},
    "data_type": "返回数据类型(table/series/aggregation)",
    "suggested_viz_type": "建议的可视化类型",
    "code_snippet": "使用的pandas代码",
    "suggestions": ["后续分析建议"]
}}"""

    async def analyze(
        self,
        query: str,
        context: Dict[str, Any],
        data_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分析用户查询并生成数据处理方案
        """
        try:
            system_prompt = self._generate_system_prompt(context)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # 如果有历史上下文，添加到消息中
            if data_context and 'history' in data_context:
                messages.extend(data_context['history'])

            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=0.2,  # 降低随机性，保持输出的一致性
                max_tokens=2000
            )

            # 解析 LLM 响应
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # 如果无法解析为JSON，返回原始回答
                return {
                    "answer": response.choices[0].message.content,
                    "suggestions": ["无法生成结构化的数据处理方案"]
                }

        except Exception as e:
            return {
                "answer": f"分析过程中出现错误: {str(e)}",
                "error": str(e)
            }

    def _validate_operation(self, operation: Dict[str, Any]) -> bool:
        """验证操作指令的合法性"""
        required_fields = {
            "aggregation": ["method", "columns", "target_columns"],
            "filter": ["query"],
            "sort": ["columns"],
            "statistical": ["method", "columns"]
        }
        
        op_type = operation.get("type")
        if op_type not in required_fields:
            return False
            
        return all(field in operation for field in required_fields[op_type]) 