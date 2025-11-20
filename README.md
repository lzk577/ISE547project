# Chat with Your Data

A smart CSV data analysis system that supports natural language queries, secure code execution, and intelligent result display. Supports multiple LLMs including GPT-4, Llama 3.3 70B, Gemini 2.0 Flash, and Qwen 2.5 72B.

## Features

1. **CSV Upload and Preview**
   - Upload CSV files and automatically preview
   - Display data shape, column information, and sample data

2. **Natural Language Query**
   - Convert natural language questions to Pandas code using multiple LLMs
   - Intelligently understand data structure and query intent
   - Support for GPT-4 (OpenAI API), Llama 3.3 70B, Gemini 2.0 Flash, and Qwen 2.5 72B (OpenRouter API)

3. **Secure Code Execution**
   - Execute generated code in a controlled environment
   - Support read-only operations to ensure data security

4. **Intelligent Output**
   - Automatically identify result types (numbers/tables/charts)
   - Support matplotlib and seaborn visualization
   - Beautiful result display interface

5. **History and Traceability**
   - Record each query's question, code, result, and CSV hash
   - Support backtracking to view history
   - Session-based organization of chat history and evaluation metrics

6. **Evaluation Metrics**
   - Automatic calculation of code correctness, code quality, and performance metrics
   - Prompt understanding, requirement coverage, and error recovery analysis
   - Metrics stored per session in `chat_history/{session_id}/`

## Environment Variables

Create a `.env` file and set the following environment variables:

```env
# OpenAI API Key for GPT-4
OPENAI_API_KEY=your-openai-api-key-here

# OpenRouter API Key for other models (Llama, Gemini, Qwen)
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Flask Secret Key (change in production)
SECRET_KEY=your-secret-key-here
```

**Note**: Do not commit your `.env` file to version control. The `.gitignore` file already excludes it.

## Installation and Running

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set environment variables**:
   Create a `.env` file and fill in the environment variables above

3. **Run the application**:
```bash
python frontend.py
```

4. **Access the application**:
   The browser will automatically open `http://127.0.0.1:5000`

## Project Structure

```
ISE547project/
├── frontend.py              # Flask backend application
├── evaluation_metrics.py    # Evaluation metrics calculation
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore rules
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css       # Style file
│   └── js/
│       └── app.js          # Frontend JavaScript
├── llm_providers/
│   ├── __init__.py
│   ├── openai_provider.py  # OpenAI API provider (for GPT-4)
│   └── openrouter_provider.py  # OpenRouter API provider (for other models)
├── uploads/                # Uploaded file storage directory
└── chat_history/           # Chat history storage directory
    └── {session_id}/       # Per-session directories
        ├── chat_history.json
        ├── metrics.json
        └── metrics_summary.json
```

## API Endpoints

- `GET /` - Main page
- `POST /api/new-chat` - Create new chat session
- `GET /api/chat-sessions` - Get all chat sessions
- `GET /api/chat/<session_id>` - Get messages for a specific session
- `DELETE /api/chat/<session_id>` - Delete a chat session and associated files
- `POST /api/upload` - Upload CSV file and preview
- `POST /api/message` - Send message and get AI response

## Usage Examples

1. **Upload CSV file**: Click the "+" button on the left to upload a CSV file
2. **View preview**: Data preview will be displayed automatically after upload
3. **Select model**: Choose from GPT-4, Llama 3.3 70B, Gemini 2.0 Flash, or Qwen 2.5 72B
4. **Ask questions**: Enter natural language questions in the input box, for example:
   - "Show the first 10 rows of data"
   - "Calculate the average age"
   - "Draw a histogram of age distribution"
   - "Group statistics by category"
5. **View results**: The system will automatically generate code, execute it, and display results
6. **View metrics**: Evaluation metrics are automatically calculated and saved in the session directory

## Technology Stack

- **Backend**: Flask, Python
- **AI**: OpenAI GPT-4, Llama 3.3 70B, Gemini 2.0 Flash, Qwen 2.5 72B
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **API Integration**: OpenAI API, OpenRouter API

## Notes

- Chat sessions are stored in the `chat_history/` directory
- Evaluation metrics are automatically calculated and stored per session
- Code execution is performed in a local environment, ensuring code security
- File upload limit is 16MB, CSV format only
- Generated code supports read-only operations and will not modify original data

## Future Development

1. Database persistence for chat history
2. Support for more file formats (Excel, JSON, etc.)
3. Code editing and debugging features
4. Result export functionality
5. Enhanced evaluation metrics visualization
