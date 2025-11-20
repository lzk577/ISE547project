# Metrics Organization Guide

## 指标存储结构

现在所有评估指标都按照会话窗口进行组织，每个会话的所有指标都保存在该会话的文件夹中。

## 目录结构

```
chat_history/
├── {session_id_1}/
│   ├── session.json          # 会话数据（消息、历史等）
│   ├── metrics.json          # 该会话的所有评估指标（数组）
│   └── metrics_summary.json  # 该会话的指标汇总统计
├── {session_id_2}/
│   ├── session.json
│   ├── metrics.json
│   └── metrics_summary.json
└── ...
```

## 文件说明

### 1. `metrics.json`
包含该会话的所有评估指标记录，是一个数组格式：

```json
[
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
      "performance_score": 0.9
    },
    "overall_score": 0.92
  },
  {
    "timestamp": "2024-01-15T10:35:00",
    "model": "llama-3.3-70b",
    ...
  }
]
```

### 2. `metrics_summary.json`
包含该会话的汇总统计信息：

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
    "models_used": ["gpt-4", "llama-3.3-70b"],
    "total_questions": 5,
    "successful_executions": 4
  }
}
```

## 功能特点

1. **按会话组织**：每个会话的所有指标都保存在自己的文件夹中
2. **自动追加**：每次新的评估都会追加到 `metrics.json` 数组中
3. **自动汇总**：每次保存指标时自动更新 `metrics_summary.json`
4. **删除同步**：删除会话时，所有相关文件（包括指标）都会被删除

## 使用场景

### 查看某个会话的所有指标
```python
import json

session_id = "your-session-id"
with open(f"chat_history/{session_id}/metrics.json", 'r') as f:
    metrics = json.load(f)
    
# 查看所有指标
for metric in metrics:
    print(f"Question: {metric['question']}")
    print(f"Model: {metric['model']}")
    print(f"Overall Score: {metric['overall_score']}")
    print("---")
```

### 查看会话汇总统计
```python
import json

session_id = "your-session-id"
with open(f"chat_history/{session_id}/metrics_summary.json", 'r') as f:
    summary = json.load(f)
    
print(f"Total Questions: {summary['summary']['total_questions']}")
print(f"Average Score: {summary['summary']['average_overall_score']}")
print(f"Models Used: {summary['summary']['models_used']}")
```

### 比较不同模型的性能
```python
import json
from collections import defaultdict

session_id = "your-session-id"
with open(f"chat_history/{session_id}/metrics.json", 'r') as f:
    metrics = json.load(f)

# 按模型分组统计
model_stats = defaultdict(list)
for metric in metrics:
    model = metric['model']
    model_stats[model].append(metric['overall_score'])

# 计算每个模型的平均分
for model, scores in model_stats.items():
    avg_score = sum(scores) / len(scores)
    print(f"{model}: {avg_score:.2f} (n={len(scores)})")
```

## 优势

1. **组织清晰**：每个会话的指标独立存储，便于管理
2. **易于分析**：可以轻松分析单个会话的表现
3. **完整记录**：保留所有历史指标，支持回溯分析
4. **自动维护**：汇总统计自动更新，无需手动计算

## 注意事项

- 指标文件会随着会话使用而增长，建议定期清理不需要的会话
- 删除会话时会同时删除所有相关指标文件
- 指标计算在后台进行，不会影响用户体验




