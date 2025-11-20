# New Evaluation Metrics Guide

## Overview

Three new evaluation metrics have been added to provide comprehensive assessment of LLM performance:

1. **Prompt Understanding (Natural-Language Intent Accuracy)**
2. **Requirement Coverage**
3. **Error Recovery Ability**

## 1. Prompt Understanding (Natural-Language Intent Accuracy)

### Purpose
Evaluates whether the model correctly understands the user's natural language question.

### Evaluation Criteria

#### 1.1 Column Extraction (40% weight)
- **Checks**: Whether correct column names are extracted from the question
- **Method**: 
  - Identifies columns mentioned in the question
  - Extracts columns used in the generated code
  - Compares and scores based on match rate
- **Score**: 0.0 - 0.4

#### 1.2 Natural Language Parsing (30% weight)
- **Checks**: Whether natural language descriptions are correctly parsed
- **Patterns Evaluated**:
  - `top N` / `largest N` → `.nlargest()`, `.head()`, `.sort_values(ascending=False)`
  - `bottom N` / `smallest N` → `.nsmallest()`, `.tail()`, `.sort_values(ascending=True)`
  - Filtering keywords → `df[...]`, `.query()`, `.loc[]`
- **Score**: 0.0 - 0.3

#### 1.3 Statistical Understanding (30% weight)
- **Checks**: Whether statistical requirements are correctly understood
- **Operations Evaluated**:
  - Mean/Average → `.mean()`
  - Sum/Total → `.sum()`
  - Maximum → `.max()`, `.nlargest()`
  - Minimum → `.min()`, `.nsmallest()`
  - Count → `.count()`, `.size()`, `len()`
  - Group by → `.groupby()`, `.pivot_table()`
- **Score**: 0.0 - 0.3

### Output Format
```json
{
  "prompt_understanding": {
    "understanding_score": 0.85,
    "details": {
      "column_extraction_score": 0.4,
      "nl_parsing_score": 0.25,
      "statistical_understanding_score": 0.2,
      "extracted_columns": ["age", "salary"],
      "mentioned_columns": ["age", "salary"],
      "statistical_operations": ["mean", "groupby"]
    }
  }
}
```

## 2. Requirement Coverage

### Purpose
Evaluates whether the generated code includes all requirements from the prompt, detecting if the model "cut corners" or missed requirements.

### Evaluation Criteria

#### 2.1 Filter Conditions Coverage (30% weight)
- **Checks**: Multiple filter conditions (are all conditions included?)
- **Method**: 
  - Counts filter keywords in question (`and`, `or`, `where`, `filter`, `greater than`, etc.)
  - Counts filter operations in code
  - Compares to detect missing conditions
- **Score**: 0.0 - 0.3

#### 2.2 Groupby Columns Coverage (30% weight)
- **Checks**: Multiple groupby columns (are all columns included?)
- **Method**:
  - Extracts columns mentioned in "group by X, Y, Z" patterns
  - Compares with columns in `.groupby()` operation
  - Detects missing columns
- **Score**: 0.0 - 0.3

#### 2.3 Sorting Coverage (20% weight)
- **Checks**: Sorting requirements (is sorting included if mentioned?)
- **Keywords**: `sort`, `order`, `ascending`, `descending`, `top`, `bottom`, `largest`, `smallest`
- **Code Patterns**: `.sort_values()`, `.sort_index()`, `.nlargest()`, `.nsmallest()`
- **Score**: 0.0 - 0.2

#### 2.4 Join Conditions Coverage (20% weight)
- **Checks**: Join/merge conditions (are all join conditions included?)
- **Keywords**: `join`, `merge`, `combine`, `match`
- **Code Patterns**: `.merge()`, `.join()`, `.concat()`
- **Score**: 0.0 - 0.2

### Output Format
```json
{
  "requirement_coverage": {
    "coverage_score": 0.9,
    "details": {
      "filter_conditions_coverage": 1.0,
      "groupby_columns_coverage": 1.0,
      "sorting_coverage": 1.0,
      "join_conditions_coverage": 0.5,
      "missing_requirements": ["Join/merge operation missing"]
    }
  }
}
```

## 3. Error Recovery Ability

### Purpose
Evaluates the model's ability to recover from execution errors by fixing the code.

### Evaluation Criteria

#### 3.1 Recovery Attempts Count
- **Tracks**: Number of recovery attempts made when code execution fails
- **Maximum**: 2 attempts (configurable)

#### 3.2 Recovery Success Rate (50% weight)
- **Calculates**: Percentage of successful recoveries
- **Formula**: `successful_recoveries / total_attempts`
- **Score**: 0.0 - 1.0

#### 3.3 Error Fix Quality (30% weight)
- **Evaluates**: Whether the root cause is addressed
- **Scoring**:
  - Successful recovery: 1.0
  - Error type changed (progress): 0.5
  - Same error type (no progress): 0.1
- **Score**: 0.0 - 1.0

#### 3.4 Attempts Made (20% weight)
- **Rewards**: Making recovery attempts (even if unsuccessful)
- **Formula**: `min(attempts / 3.0, 1.0)`
- **Score**: 0.0 - 1.0

### Error Classification
Errors are classified into categories for comparison:
- `column_error`: KeyError, column-related errors
- `syntax_error`: Syntax errors, invalid syntax
- `type_error`: Type errors, dtype errors
- `index_error`: Index errors, out of range
- `attribute_error`: Attribute errors, has no attribute
- `value_error`: Value errors
- `other_error`: Other types of errors

### Recovery Process
1. When code execution fails, the system automatically attempts recovery
2. A recovery prompt is generated with:
   - Original error message
   - Original question
   - Original code
3. The model generates fixed code
4. Fixed code is executed and evaluated
5. Process repeats up to `max_recovery_attempts` times

### Output Format
```json
{
  "error_recovery": {
    "has_error": true,
    "error_message": "KeyError: 'age'",
    "recovery_attempts_count": 2,
    "recovery_success": true,
    "recovery_success_rate": 0.5,
    "error_fix_quality": 0.75,
    "recovery_score": 0.65,
    "recovery_details": [
      {
        "attempt_number": 1,
        "success": false,
        "error": "KeyError: 'age'",
        "fix_quality": 0.1
      },
      {
        "attempt_number": 2,
        "success": true,
        "error": null,
        "fix_quality": 1.0
      }
    ]
  }
}
```

## Overall Score Calculation

The overall score now includes all six metrics:

```python
overall_score = (
    correctness_score * 0.25 +      # 25%
    quality_score * 0.20 +          # 20%
    performance_score * 0.15 +      # 15%
    understanding_score * 0.15 +    # 15% (NEW)
    coverage_score * 0.15 +         # 15% (NEW)
    recovery_score * 0.10           # 10% (NEW)
)
```

## Metrics Summary

The `metrics_summary.json` file now includes:

```json
{
  "summary": {
    "average_understanding_score": 0.85,
    "average_coverage_score": 0.90,
    "average_recovery_score": 0.65,
    "errors_encountered": 10,
    "total_recovery_attempts": 15,
    "successful_recoveries": 8,
    "recovery_success_rate": 0.80
  }
}
```

## Usage

These metrics are automatically calculated for every code generation and execution. They are stored in:
- `chat_history/{session_id}/metrics.json` - Individual metric entries
- `chat_history/{session_id}/metrics_summary.json` - Aggregated statistics

## Benefits

1. **Prompt Understanding**: Helps identify if models correctly interpret user intent
2. **Requirement Coverage**: Detects incomplete implementations and "corner-cutting"
3. **Error Recovery**: Evaluates model's ability to learn from mistakes and self-correct

These metrics provide a more comprehensive evaluation of LLM performance beyond just code correctness and quality.



