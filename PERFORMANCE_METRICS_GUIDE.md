# Performance Metrics Guide

## 新增性能指标

现在评估指标包含以下性能相关指标：

### 1. **运行时间 (Execution Time)**
- **测量方式**: 实际代码执行时间（秒和毫秒）
- **位置**: `performance.execution_time_seconds` 和 `performance.execution_time_ms`
- **评分标准**:
  - < 0.1秒: 优秀 (0.3分)
  - < 1.0秒: 良好 (0.25分)
  - < 5.0秒: 一般 (0.15分)
  - ≥ 5.0秒: 较差 (0.05分)

### 2. **时间复杂度 (Time Complexity)**
- **分析方式**: 通过代码静态分析，检测循环、嵌套结构和Pandas操作
- **位置**: `performance.time_complexity`
- **复杂度等级**:
  - `O(1)`: 常数时间 (1.0分)
  - `O(log n)`: 对数时间 (0.9分)
  - `O(n)`: 线性时间 (0.7分)
  - `O(n log n)`: 线性对数时间 (0.5分)
  - `O(n²)`: 平方时间 (0.3分)
  - `O(n³)`: 立方时间 (0.1分)

**检测规则**:
- 检测 `for` 循环、`while` 循环
- 检测 Pandas 的 `apply()`, `iterrows()`, `itertuples()`
- 检测 Pandas 操作复杂度：
  - `O(1)`: `head()`, `tail()`, `iloc[]`, `loc[]`
  - `O(n)`: `mean()`, `sum()`, `groupby()`, `sort_values()`
  - `O(n log n)`: `sort_values()`, `sort_index()`
  - `O(n²)`: `merge()`, `join()`, `concat()`

### 3. **空间复杂度 (Space Complexity)**
- **分析方式**: 检测代码中创建新数据结构的操作
- **位置**: `performance.space_complexity`
- **复杂度等级**:
  - `O(1)`: 常数空间 (1.0分)
  - `O(n)`: 线性空间 (0.6分)
  - `O(n²)`: 平方空间 (0.2分)

**检测规则**:
- `O(1)`: 只读取数据，不创建新结构
- `O(n)`: 创建新DataFrame副本、过滤结果
- `O(n²)`: 合并、连接操作

**内存估算**:
- 基于CSV文件大小和空间复杂度估算内存使用
- `estimated_memory_mb`: 估算的内存使用量（MB）

## 指标结构

### 完整指标示例

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "model": "gpt-4",
  "question": "Calculate the mean of column 'price'",
  "csv_file": "uploads/...",
  "code_correctness": {
    "syntax_valid": true,
    "execution_success": true,
    "correctness_score": 1.0
  },
  "code_quality": {
    "has_imports": true,
    "readability_score": 8,
    "quality_score": 0.85
  },
  "performance": {
    "code_length": 45,
    "line_count": 3,
    "execution_time_seconds": 0.023,
    "execution_time_ms": 23.0,
    "time_complexity": {
      "notation": "O(n)",
      "score": 0.7,
      "nested_loops": 0,
      "estimated_operations": 1
    },
    "space_complexity": {
      "notation": "O(1)",
      "score": 1.0,
      "estimated_memory_mb": 2.5
    },
    "performance_score": 0.89
  },
  "overall_score": 0.92
}
```

### 汇总统计示例

```json
{
  "session_id": "...",
  "total_entries": 5,
  "last_updated": "2024-01-15T10:40:00",
  "summary": {
    "average_overall_score": 0.88,
    "average_correctness_score": 0.95,
    "average_quality_score": 0.82,
    "average_performance_score": 0.87,
    "average_execution_time_seconds": 0.15,
    "average_execution_time_ms": 150.0,
    "models_used": ["gpt-4", "llama-3.3-70b"],
    "total_questions": 5,
    "successful_executions": 4,
    "time_complexity_distribution": {
      "O(1)": 1,
      "O(n)": 3,
      "O(n²)": 1
    },
    "space_complexity_distribution": {
      "O(1)": 2,
      "O(n)": 3
    }
  }
}
```

## 性能评分权重

性能指标 (`performance_score`) 的计算权重：

- **执行时间**: 30%
- **时间复杂度**: 30%
- **空间复杂度**: 20%
- **代码长度**: 10%
- **执行成功**: 10%

## 使用示例

### 查看某个会话的性能指标

```python
import json

session_id = "your-session-id"
with open(f"chat_history/{session_id}/metrics.json", 'r') as f:
    metrics = json.load(f)

for metric in metrics:
    perf = metric.get('performance', {})
    print(f"Question: {metric['question']}")
    print(f"Execution Time: {perf.get('execution_time_ms', 'N/A')} ms")
    print(f"Time Complexity: {perf.get('time_complexity', {}).get('notation', 'N/A')}")
    print(f"Space Complexity: {perf.get('space_complexity', {}).get('notation', 'N/A')}")
    print("---")
```

### 分析不同模型的性能

```python
import json
from collections import defaultdict

session_id = "your-session-id"
with open(f"chat_history/{session_id}/metrics.json", 'r') as f:
    metrics = json.load(f)

model_performance = defaultdict(lambda: {
    'times': [],
    'time_complexities': [],
    'space_complexities': []
})

for metric in metrics:
    model = metric['model']
    perf = metric.get('performance', {})
    
    if perf.get('execution_time_seconds'):
        model_performance[model]['times'].append(perf['execution_time_seconds'])
    model_performance[model]['time_complexities'].append(
        perf.get('time_complexity', {}).get('notation', 'O(1)')
    )
    model_performance[model]['space_complexities'].append(
        perf.get('space_complexity', {}).get('notation', 'O(1)')
    )

for model, data in model_performance.items():
    avg_time = sum(data['times']) / len(data['times']) if data['times'] else 0
    print(f"{model}:")
    print(f"  Average Time: {avg_time*1000:.2f} ms")
    print(f"  Time Complexity: {max(set(data['time_complexities']), key=data['time_complexities'].count)}")
    print(f"  Space Complexity: {max(set(data['space_complexities']), key=data['space_complexities'].count)}")
```

## 注意事项

1. **运行时间测量**: 实际测量代码执行时间，包括所有操作
2. **复杂度分析**: 基于静态代码分析，是估算值，可能与实际有差异
3. **内存估算**: 基于文件大小和复杂度估算，仅供参考
4. **性能评分**: 综合考虑多个因素，分数越高表示性能越好

## 指标文件位置

所有指标保存在：
- `chat_history/{session_id}/metrics.json` - 详细指标
- `chat_history/{session_id}/metrics_summary.json` - 汇总统计




