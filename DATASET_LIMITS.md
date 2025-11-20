# Dataset Limits and Restrictions

## 当前代码中的数据集限制

### 1. **文件大小限制**
- **限制**: **16 MB** (16,777,216 字节)
- **位置**: `frontend.py` 第 33 行
- **代码**: `app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024`
- **说明**: Flask 会自动拒绝超过此大小的文件上传

### 2. **文件格式限制**
- **限制**: 仅支持 **CSV 格式**
- **位置**: `frontend.py` 第 189 行
- **代码**: `if not file.filename.endswith('.csv')`
- **说明**: 其他格式（Excel, JSON等）会被拒绝

### 3. **行数和列数限制**
- **当前**: **无明确限制**
- **说明**: 
  - 代码中没有对行数或列数的硬性限制
  - 实际限制取决于：
    - 系统内存
    - Pandas 处理能力
    - 代码执行时间

### 4. **前端显示限制**
- **表格显示**: 最多显示 **100 行**
- **位置**: `static/js/app.js` 第 290 行
- **代码**: `result.data.slice(0, 100)`
- **说明**: 超过100行的结果会显示提示信息

### 5. **预览数据限制**
- **预览行数**: 显示前 **5 行**
- **位置**: `frontend.py` 第 214 行
- **代码**: `df.head(5)`

## 实际限制因素

### 内存限制
- 取决于系统可用内存
- Pandas 加载 CSV 到内存
- 大文件可能导致内存不足

### 执行时间限制
- 无硬性超时限制
- 但用户可能等待超时
- 建议：大文件处理时间可能较长

### 代码生成限制
- LLM 生成的代码长度受 `max_tokens=1000` 限制
- 位置：`frontend.py` 第 293 行

## 建议的限制值

根据实际使用场景，建议设置以下限制：

### 推荐配置

```python
# 文件大小
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB (可根据需要调整)

# 行数限制（可选）
MAX_ROWS = 1_000_000  # 100万行

# 列数限制（可选）
MAX_COLUMNS = 1000  # 1000列

# 执行超时（可选）
EXECUTION_TIMEOUT = 60  # 60秒
```

## 如何修改限制

### 修改文件大小限制

在 `frontend.py` 中修改：

```python
# 当前: 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 修改为 50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# 修改为 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# 无限制（不推荐）
app.config['MAX_CONTENT_LENGTH'] = None
```

### 添加行数/列数检查

在 `upload_file()` 函数中添加：

```python
# 读取CSV后检查
df = pd.read_csv(io.BytesIO(file_content))

# 检查行数
MAX_ROWS = 1_000_000
if len(df) > MAX_ROWS:
    return jsonify({
        'error': f'Dataset too large. Maximum {MAX_ROWS:,} rows allowed. Your file has {len(df):,} rows.'
    }), 400

# 检查列数
MAX_COLUMNS = 1000
if len(df.columns) > MAX_COLUMNS:
    return jsonify({
        'error': f'Too many columns. Maximum {MAX_COLUMNS} columns allowed. Your file has {len(df.columns)} columns.'
    }), 400
```

### 添加执行超时

在 `execute_code_safely()` 函数中添加：

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timeout")

# 设置60秒超时
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)  # 60秒

try:
    exec(code, exec_globals, exec_locals)
finally:
    signal.alarm(0)  # 取消超时
```

## 当前限制总结

| 限制类型 | 当前值 | 位置 | 可修改 |
|---------|--------|------|--------|
| **文件大小** | 16 MB | `frontend.py:33` | ✅ 是 |
| **文件格式** | CSV only | `frontend.py:189` | ✅ 是 |
| **行数** | 无限制 | - | ✅ 可添加 |
| **列数** | 无限制 | - | ✅ 可添加 |
| **执行超时** | 无限制 | - | ✅ 可添加 |
| **显示行数** | 100 行 | `app.js:290` | ✅ 是 |
| **预览行数** | 5 行 | `frontend.py:214` | ✅ 是 |
| **代码长度** | 1000 tokens | `frontend.py:293` | ✅ 是 |

## 性能考虑

### 大文件处理建议

1. **文件大小 > 50MB**: 考虑使用数据采样或分块处理
2. **行数 > 100万**: 可能需要优化代码生成策略
3. **列数 > 100**: 可能影响代码生成质量

### 内存使用估算

- **CSV 文件大小**: X MB
- **加载到内存**: 约 2-3X MB (Pandas 开销)
- **处理过程**: 可能再增加 1-2X MB
- **总内存需求**: 约 4-5X MB

例如：
- 16MB CSV → 约 64-80MB 内存
- 50MB CSV → 约 200-250MB 内存

## 建议

根据你的使用场景，可以考虑：

1. **增加文件大小限制**到 50MB 或 100MB
2. **添加行数/列数检查**，提前拒绝过大的数据集
3. **添加执行超时**，避免长时间等待
4. **优化大文件处理**，使用数据采样或分块

需要我帮你修改这些限制吗？




