# AI Agent - CSV数据分析系统

基于Aurite框架的智能CSV数据分析系统，支持自然语言查询、安全代码执行和智能结果展示。

## 功能特性

1. **CSV上传和预览**
   - 上传CSV文件并自动预览
   - 显示数据形状、列信息和示例数据

2. **自然语言查询**
   - 使用OpenAI GPT-4将自然语言问题转换为Pandas代码
   - 智能理解数据结构和查询意图

3. **安全代码执行**
   - 在受控环境中执行生成的代码
   - 支持只读操作，确保数据安全

4. **智能输出**
   - 自动识别结果类型（数字/表格/图表）
   - 支持matplotlib和seaborn可视化
   - 美观的结果展示界面

5. **历史记录和可追溯性**
   - 记录每次查询的问题、代码、结果和CSV哈希
   - 支持回溯查看历史记录

## 环境变量配置

创建 `.env` 文件并设置以下环境变量：

```env
# OpenAI API Key
OPENAI_API_KEY=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

# Smithery API Configuration
SMITHERY_API_KEY=30a5c47c-fdc7-4c7a-bc30-d1b99b1c89f9
SMITHERY_PROFILE_ID=enchanting-finch-Fj3QCf

# Flask Secret Key (change in production)
SECRET_KEY=your-secret-key-here
```

## 安装和运行

1. **安装依赖**：
```bash
pip install -r requirements.txt
```

2. **设置环境变量**：
创建 `.env` 文件并填入上述环境变量

3. **运行应用**：
```bash
python frontend.py
```

4. **访问应用**：
浏览器会自动打开 `http://127.0.0.1:5000`

## 项目结构

```
ISE547project/
├── frontend.py          # Flask后端应用
├── aurite_project.py    # Aurite项目配置
├── config.py            # 配置文件
├── requirements.txt     # Python依赖
├── .env                 # 环境变量（需创建）
├── templates/
│   └── index.html      # 主HTML模板
├── static/
│   ├── css/
│   │   └── style.css   # 样式文件
│   └── js/
│       └── app.js      # 前端JavaScript
├── uploads/            # 上传文件存储目录
├── chat_history/       # 聊天历史存储目录
└── data/               # 数据存储目录
```

## API端点

- `GET /` - 主页面
- `POST /api/new-chat` - 创建新聊天会话
- `GET /api/chat-sessions` - 获取所有聊天会话
- `GET /api/chat/<session_id>` - 获取特定会话的消息
- `POST /api/upload` - 上传CSV文件并预览
- `POST /api/message` - 发送消息并获取AI响应
- `GET /api/history/<session_id>` - 获取会话历史记录

## 使用示例

1. **上传CSV文件**：点击左侧的"+"按钮上传CSV文件
2. **查看预览**：上传后自动显示数据预览
3. **提问**：在输入框中输入自然语言问题，例如：
   - "显示前10行数据"
   - "计算平均年龄"
   - "绘制年龄分布直方图"
   - "按类别分组统计"
4. **查看结果**：系统会自动生成代码、执行并展示结果

## 技术栈

- **后端**: Flask, Python
- **AI**: OpenAI GPT-4
- **数据处理**: Pandas, NumPy
- **可视化**: Matplotlib, Seaborn, Plotly
- **框架**: Aurite MCP
- **安全执行**: Smithery (可选)

## 注意事项

- 当前版本使用内存存储聊天会话，重启服务器后数据会丢失
- 代码执行在本地环境中进行，确保代码安全性
- 文件上传限制为16MB，仅支持CSV格式
- 生成的代码仅支持只读操作，不会修改原始数据

## 后续开发

1. 使用数据库持久化聊天历史
2. 集成Smithery API进行远程沙箱执行
3. 支持更多文件格式（Excel, JSON等）
4. 添加代码编辑和调试功能
5. 实现结果导出功能
