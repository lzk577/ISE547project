# 🎯 Chat with Your Data

*A natural-language-powered CSV analysis platform*

A smart and secure system that allows you to upload CSV files, ask natural-language questions, automatically generate Pandas code, execute it safely, and display results through tables, summaries, and charts.

Supports multiple LLMs including **GPT-4**, **Llama 3.3 70B**, **Gemini 2.0 Flash**, and **Qwen 2.5 72B**.

---

## 🚀 Features

### 📂 **CSV Upload & Preview**

* Upload CSV files from the UI
* Auto-preview data shape, columns, and sample rows

### 💬 **Natural-Language Query**

* Convert natural language into safe Pandas code
* Intelligent understanding of schema & query intent
* Support for GPT-4, Llama 3.3, Gemini 2.0, Qwen 2.5 via OpenAI & OpenRouter APIs

### 🔒 **Secure Code Execution**

* Sandboxed, read-only execution environment
* Protects data from modification and prevents unsafe operations

### 📊 **Intelligent Output Rendering**

* Automatically identifies output type:

  * Numbers
  * DataFrames
  * Matplotlib/Seaborn charts
* Clean, responsive display

### 📝 **History & Traceability**

* Each query logs:

  * The question
  * Generated code
  * Execution results
  * CSV file hash
  * Evaluation metrics
* Organized per session in `chat_history/{session_id}/`

### 📈 **Evaluation Metrics**

* Automatic evaluation of:

  * Code correctness
  * Code quality
  * Execution performance
  * Prompt understanding & coverage
  * Error recovery
* Saved per session

---

## ⚙ Environment Variables

Create a `.env` file:

```env
# OpenAI API Key (GPT-4)
OPENAI_API_KEY=your-openai-api-key-here

# OpenRouter API Key (Llama, Gemini, Qwen)
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Flask session key
SECRET_KEY=your-secret-key-here
```

> ⚠️ Do **NOT** commit `.env` to GitHub.
> `.gitignore` already excludes it.

---

## 📦 Installation & Running

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Set environment variables

Create your `.env` file and fill in the keys above.

### 3️⃣ Run the application

```bash
python frontend.py
```

### 4️⃣ Open in browser

```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
ISE547project/
├── frontend.py                    # Flask backend application
├── evaluation_metrics.py          # Evaluation metrics logic
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore configuration
├── .env (create this manually)    # Environment variables
│
├── templates/
│   └── index.html                 # Main HTML template
│
├── static/
│   ├── css/
│   │   └── style.css              # Application stylesheet
│   └── js/
│       └── app.js                 # Frontend logic
│
├── llm_providers/
│   ├── __init__.py
│   ├── openai_provider.py         # GPT-4 API provider
│   └── openrouter_provider.py     # Llama/Gemini/Qwen provider
│
├── uploads/                       # Storage for uploaded CSV files
└── chat_history/                  # Per-session directories
    └── {session_id}/
        ├── chat_history.json
        ├── metrics.json
        └── metrics_summary.json
```

---

## 📡 API Endpoints

| Method | Endpoint                 | Description                 |
| ------ | ------------------------ | --------------------------- |
| GET    | `/`                      | Main UI                     |
| POST   | `/api/new-chat`          | Create a new chat session   |
| GET    | `/api/chat-sessions`     | List all sessions           |
| GET    | `/api/chat/<session_id>` | Load a session              |
| DELETE | `/api/chat/<session_id>` | Delete a session            |
| POST   | `/api/upload`            | Upload + preview CSV        |
| POST   | `/api/message`           | Send question → AI response |

---

## 💡 Usage Examples

* “Show the first 10 rows”
* “Calculate average age”
* “Plot histogram of age distribution”
* “Group by category and compute mean values”
* “Show correlation heatmap”

Each query:

* Generates safe Pandas code
* Executes it in a sandbox
* Renders results
* Logs metrics automatically

---

## 🧰 Technology Stack

**Backend:** Flask (Python)
**LLMs:** GPT-4, Llama 3.3, Gemini 2.0, Qwen 2.5
**Processing:** Pandas, NumPy
**Visualization:** Matplotlib, Seaborn
**Frontend:** HTML / CSS / JavaScript
**APIs:** OpenAI, OpenRouter

---

## ⚠ Notes

* Chat sessions stored under `chat_history/`
* Only CSV format supported (max 16MB)
* All code execution is read-only
* Generated code never modifies original data

---

## 🔮 Future Development

* Database persistence for history
* Support Excel, JSON, Parquet
* Code editor with re-run option
* Export charts/tables
* Metrics dashboard visualization
