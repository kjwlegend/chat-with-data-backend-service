import pandas as pd
from typing import Union, Dict, Any

def process_dataframe(df: pd.DataFrame, operation: Dict[str, Any]) -> Union[pd.DataFrame, Dict[str, Any]]:
    """
    根据LLM的指令处理DataFrame
    
    operation 示例:
    {
        "type": "aggregation",
        "method": "groupby",
        "columns": ["category"],
        "agg_func": "mean",
        "target_columns": ["sales"]
    }
    """
    try:
        op_type = operation['type']
        
        if op_type == "aggregation":
            result = df.groupby(operation['columns'])[operation['target_columns']]\
                      .agg(operation['agg_func'])
            return result.reset_index()
            
        elif op_type == "filter":
            query = operation['query']
            return df.query(query)
            
        elif op_type == "sort":
            return df.sort_values(
                by=operation['columns'],
                ascending=operation.get('ascending', True)
            )
            
        elif op_type == "statistical":
            if operation['method'] == 'correlation':
                return df[operation['columns']].corr().to_dict()
            elif operation['method'] == 'describe':
                return df[operation['columns']].describe().to_dict()
                
        return df
        
    except Exception as e:
        raise ValueError(f"数据处理错误: {str(e)}") 