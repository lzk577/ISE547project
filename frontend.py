'''
python frontend.py

'''

from flask import Flask, render_template, request, jsonify, session
import os
import json
from datetime import datetime
import uuid
import webbrowser
import threading
import time
import hashlib
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import requests
import base64
import io

# Load environment variables
load_dotenv()

# Check if .env file exists
if not os.path.exists('.env'):
    print("Warning: .env file does not exist! Please run setup_env.bat to create .env file.")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('chat_history', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('evaluation_results', exist_ok=True)

# Initialize LLM providers
from llm_providers.openrouter_provider import OpenRouterProvider
from llm_providers.openai_provider import OpenAIProvider
from evaluation_metrics import calculate_evaluation_metrics, save_evaluation_metrics

# Initialize OpenAI provider for GPT-4
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not set. GPT-4 will not be available.")
    openai_provider = None
else:
    openai_provider = OpenAIProvider(api_key=OPENAI_API_KEY)
    print("✓ OpenAI API client initialized successfully")

# Initialize OpenRouter provider for other models
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not set. OpenRouter models will not be available.")
    openrouter_provider = None
else:
    openrouter_provider = OpenRouterProvider(api_key=OPENROUTER_API_KEY)
    print("✓ OpenRouter API client initialized successfully")

# Available models configuration
# GPT-4 uses OpenAI API directly, others use OpenRouter
AVAILABLE_MODELS = {
    "gpt-4": {
        "provider": "openai",
        "model_id": "gpt-4"
    },
    "llama-3.3-70b": {
        "provider": "openrouter",
        "model_id": "meta-llama/llama-3.3-70b-instruct"
    },
    "gemini-2.0": {
        "provider": "openrouter",
        "model_id": "google/gemini-2.0-flash-lite-001"
    },
    "qwen-2.5-72b": {
        "provider": "openrouter",
        "model_id": "qwen/qwen-2.5-72b-instruct"
    }
}

# Smithery configuration
SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')
SMITHERY_PROFILE_ID = os.getenv('SMITHERY_PROFILE_ID')
SMITHERY_API_URL = 'https://api.smithery.ai/v1'

# Dictionary to store chat sessions (should use database in production)
chat_sessions = {}

# Global variable: prevent duplicate browser opening
_browser_opened = False

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/api/new-chat', methods=['POST'])
def new_chat():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    chat_sessions[session_id] = {
        'id': session_id,
        'title': 'New Chat',
        'created_at': datetime.now().isoformat(),
        'messages': [],
        'csv_file': None,
        'csv_hash': None,
        'history': []
    }
    save_chat_session(session_id)
    return jsonify({'session_id': session_id, 'title': 'New Chat'})

@app.route('/api/chat-sessions', methods=['GET'])
def get_chat_sessions():
    """Get all chat sessions list"""
    sessions = list(chat_sessions.values())
    sessions.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(sessions)

@app.route('/api/chat/<session_id>', methods=['GET'])
def get_chat(session_id):
    """Get message history for a specific session"""
    if session_id in chat_sessions:
        return jsonify(chat_sessions[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/api/chat/<session_id>', methods=['POST'])
def update_chat_title(session_id):
    """Update chat session title"""
    data = request.json
    if session_id in chat_sessions:
        chat_sessions[session_id]['title'] = data.get('title', 'New Chat')
        save_chat_session(session_id)
        return jsonify({'success': True})
    return jsonify({'error': 'Session not found'}), 404

@app.route('/api/chat/<session_id>', methods=['DELETE'])
def delete_chat(session_id):
    """Delete chat session and associated files"""
    import shutil
    
    try:
        # Delete session from memory
        if session_id in chat_sessions:
            csv_file = chat_sessions[session_id].get('csv_file')
            
            # Delete CSV file
            if csv_file and os.path.exists(csv_file):
                try:
                    os.remove(csv_file)
                    print(f"Deleted CSV file: {csv_file}")
                except Exception as e:
                    print(f"Error deleting CSV file {csv_file}: {e}")
            
            # Delete session data
            del chat_sessions[session_id]
        
        # Delete history directory (includes session.json, metrics.json, and metrics_summary.json)
        session_dir = os.path.join('chat_history', session_id)
        if os.path.exists(session_dir):
            try:
                shutil.rmtree(session_dir)
                print(f"Deleted session directory: {session_dir} (including all metrics)")
            except Exception as e:
                print(f"Error deleting session directory {session_dir}: {e}")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error deleting session {session_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and preview CSV data"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file type
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    try:
        # Read CSV file
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Save file
        session_id = session.get('session_id', str(uuid.uuid4()))
        filename = f"{session_id}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read CSV for preview
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Get data preview information
        preview_data = {
            'shape': {'rows': len(df), 'columns': len(df.columns)},
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'sample_data': df.head(5).to_dict('records'),
            'null_counts': df.isnull().sum().to_dict(),
            'file_hash': file_hash
        }
        
        # Update session file information
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                'id': session_id,
                'title': 'New Chat',
                'created_at': datetime.now().isoformat(),
                'messages': [],
                'csv_file': None,
                'csv_hash': None,
                'history': []
            }
        
        chat_sessions[session_id]['csv_file'] = filepath
        chat_sessions[session_id]['csv_hash'] = file_hash
        
        # Save session to file
        save_chat_session(session_id)
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'filepath': filepath,
            'preview': preview_data
        })
    except Exception as e:
        return jsonify({'error': f'Error processing CSV: {str(e)}'}), 400

def generate_pandas_code(question, csv_info, model="gpt-4"):
    """Generate Pandas code using appropriate provider based on model"""
    columns = csv_info.get('columns', [])
    dtypes = csv_info.get('dtypes', {})
    
    # Get model configuration
    model_config = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["gpt-4"])
    provider_type = model_config["provider"]
    model_id = model_config["model_id"]
    
    system_prompt = """You are a data analysis assistant. Convert natural language questions into safe, read-only Pandas code.

Rules:
1. Only use read-only operations (no file writes, no network calls, no system commands)
2. Use the variable 'df' for the DataFrame
3. IMPORTANT: Always assign the final result to a variable named 'result' or create a figure named 'fig'
4. For aggregations, calculations, or data filtering, assign to 'result'
5. For visualizations, create a matplotlib figure and assign to 'fig'
6. Return only valid Python/Pandas code, no explanations or markdown
7. Import necessary libraries (matplotlib.pyplot as plt, seaborn as sns if needed)

Available columns: {columns}
Column types: {dtypes}

Examples:
- For calculations: result = df['column'].mean()
- For filtering: result = df[df['column'] > 10]
- For visualizations: 
  import matplotlib.pyplot as plt
  fig, ax = plt.subplots()
  ax.plot(df['x'], df['y'])
  fig = plt.gcf()

Return ONLY the Python code, nothing else.""".format(
        columns=', '.join(columns),
        dtypes=json.dumps(dtypes)
    )
    
    try:
        # Select provider based on model
        if provider_type == "openai":
            if not openai_provider:
                raise Exception("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file.")
            code = openai_provider.generate_code(
                system_prompt=system_prompt,
                user_prompt=question,
                model=model_id,
                temperature=0.3,
                max_tokens=1000
            )
        elif provider_type == "openrouter":
            if not openrouter_provider:
                raise Exception("OpenRouter API key not configured. Please set OPENROUTER_API_KEY in .env file.")
            code = openrouter_provider.generate_code(
                system_prompt=system_prompt,
                user_prompt=question,
                model=model_id,
                temperature=0.3,
                max_tokens=1000
            )
        else:
            raise Exception(f"Unknown provider type: {provider_type}")
        
        # Remove code block markers
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
        return code.strip()
    except Exception as e:
        raise Exception(f"Error generating code: {str(e)}")

def execute_code_safely(code, csv_filepath):
    """Safely execute code in a controlled environment"""
    execution_time = None
    try:
        # Read CSV file
        df = pd.read_csv(csv_filepath)
        
        # Prepare execution environment
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        exec_globals = {
            'pd': pd,
            'np': np,
            'df': df,
            'json': json,
            'plt': plt,
            'sns': sns,
            'result': None,
            'fig': None
        }
        
        # Execute code
        exec_result = {}
        exec_locals = {}
        
        # Execute code and capture output with timing
        try:
            start_time = time.time()
            exec(code, exec_globals, exec_locals)
            execution_time = time.time() - start_time
            
            # Check result type
            result = None
            
            # Check for chart first
            if 'fig' in exec_locals and exec_locals['fig'] is not None:
                # Chart result
                fig = exec_locals['fig']
                # Convert chart to base64
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
                plt.close(fig)  # Close chart to free memory
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                exec_result = {
                    'type': 'chart',
                    'data': f'data:image/png;base64,{img_base64}'
                }
                return exec_result
            
            # Check result variable
            if 'result' in exec_locals and exec_locals['result'] is not None:
                result = exec_locals['result']
            else:
                # Try to get last expression result
                result = exec_locals.get('_', None)
                if result is None:
                    exec_result = {
                        'type': 'text',
                        'data': 'Code executed successfully, but no result returned. Please ensure the code has an explicit return value or assigns to the result variable.'
                    }
                    return exec_result
            
            # Determine result type
            if isinstance(result, (int, float, np.number)):
                exec_result = {
                    'type': 'number',
                    'data': float(result)
                }
            elif isinstance(result, pd.DataFrame):
                exec_result = {
                    'type': 'table',
                    'data': result.to_dict('records'),
                    'columns': result.columns.tolist()
                }
            elif isinstance(result, pd.Series):
                exec_result = {
                    'type': 'table',
                    'data': result.to_dict(),
                    'columns': ['Index', 'Value']
                }
            else:
                exec_result = {
                    'type': 'text',
                    'data': str(result)
                }
            
            # Add execution time to result
            if execution_time is not None:
                exec_result['execution_time'] = execution_time
            
            return exec_result
        except Exception as e:
            error_result = {
                'type': 'error',
                'data': f'Execution error: {str(e)}'
            }
            if execution_time is not None:
                error_result['execution_time'] = execution_time
            return error_result
    except Exception as e:
        return {
            'type': 'error',
            'data': f'Error: {str(e)}'
        }

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """Get list of available models"""
    models = [
        {"id": "gpt-4", "name": "GPT-4", "provider": "OpenAI"},
        {"id": "llama-3.3-70b", "name": "Llama 3.3 70B", "provider": "Meta"},
        {"id": "gemini-2.0", "name": "Gemini 2.0 Flash", "provider": "Google"},
        {"id": "qwen-2.5-72b", "name": "Qwen 2.5 72B", "provider": "Alibaba"}
    ]
    return jsonify(models)

@app.route('/api/message', methods=['POST'])
def send_message():
    """Process user message and return AI response"""
    data = request.json
    question = data.get('question', '')
    session_id = session.get('session_id')
    
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    # Initialize session if it doesn't exist
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            'id': session_id,
            'title': question[:30] if question else 'New Chat',
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'csv_file': None,
            'csv_hash': None,
            'history': []
        }
    
    # Ensure all required keys exist (backward compatibility)
    if 'history' not in chat_sessions[session_id]:
        chat_sessions[session_id]['history'] = []
    if 'csv_file' not in chat_sessions[session_id]:
        chat_sessions[session_id]['csv_file'] = None
    if 'csv_hash' not in chat_sessions[session_id]:
        chat_sessions[session_id]['csv_hash'] = None
    
    # Check if CSV file exists
    csv_file = chat_sessions[session_id].get('csv_file')
    if not csv_file:
        return jsonify({
            'success': False,
            'error': 'Please upload a CSV file first'
        }), 400
    
    # Add user message
    user_message = {
        'id': str(uuid.uuid4()),
        'type': 'user',
        'content': question,
        'timestamp': datetime.now().isoformat()
    }
    chat_sessions[session_id]['messages'].append(user_message)
    
    # Update session title (if it's the first message)
    if len(chat_sessions[session_id]['messages']) == 1 and question:
        chat_sessions[session_id]['title'] = question[:30]
    
    # Initialize variables for metrics calculation
    generated_code = ""
    execution_result = {'type': 'error', 'data': 'Code generation failed'}
    execution_time = None
    recovery_attempts = []
    selected_model = data.get('model', 'gpt-4')
    
    try:
        # Get CSV information
        df = pd.read_csv(csv_file)
        csv_info = {
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict()
        }
        
        # Generate Pandas code
        generated_code = generate_pandas_code(question, csv_info, model=selected_model)
        
        # Execute code and measure execution time
        execution_result = execute_code_safely(generated_code, csv_file)
        execution_time = execution_result.get('execution_time')
        
        # Track recovery attempts if execution failed
        max_recovery_attempts = 2  # Maximum number of recovery attempts
        
        # If execution failed, attempt to recover
        if execution_result.get('type') == 'error' and max_recovery_attempts > 0:
            error_message = execution_result.get('data', '')
            for attempt_num in range(max_recovery_attempts):
                try:
                    # Generate recovery prompt
                    recovery_prompt = f"""The previous code failed with error: {error_message}

Original question: {question}
Original code:
```python
{generated_code}
```

Please fix the code to resolve the error. Return only the corrected Python code."""
                    
                    # Generate fixed code
                    fixed_code = generate_pandas_code(recovery_prompt, csv_info, model=selected_model)
                    
                    # Execute fixed code
                    fixed_result = execute_code_safely(fixed_code, csv_file)
                    fixed_execution_time = fixed_result.get('execution_time')
                    
                    # Record recovery attempt
                    recovery_attempt = {
                        'attempt_number': attempt_num + 1,
                        'code': fixed_code,
                        'error': fixed_result.get('data') if fixed_result.get('type') == 'error' else None,
                        'success': fixed_result.get('type') != 'error',
                        'execution_time': fixed_execution_time
                    }
                    recovery_attempts.append(recovery_attempt)
                    
                    # If recovery successful, use the fixed code and result
                    if recovery_attempt['success']:
                        generated_code = fixed_code
                        execution_result = fixed_result
                        execution_time = fixed_execution_time
                        break
                except Exception as e:
                    # Recovery attempt failed
                    recovery_attempts.append({
                        'attempt_number': attempt_num + 1,
                        'code': None,
                        'error': f'Recovery attempt failed: {str(e)}',
                        'success': False,
                        'execution_time': None
                    })
        
        # Calculate evaluation metrics (runs in background, doesn't block response)
        try:
            print(f"[METRICS] Starting metrics calculation for session {session_id}")
            print(f"[METRICS] Question: {question[:50]}...")
            print(f"[METRICS] Model: {selected_model}")
            print(f"[METRICS] Execution result type: {execution_result.get('type')}")
            
            metrics = calculate_evaluation_metrics(
                question=question,
                generated_code=generated_code,
                execution_result=execution_result,
                csv_file=csv_file,
                model=selected_model,
                execution_time=execution_time,
                recovery_attempts=recovery_attempts
            )
            
            print(f"[METRICS] Metrics calculated successfully. Overall score: {metrics.get('overall_score', 'N/A')}")
            
            # Save metrics to file in session directory (background operation)
            session_dir = os.path.join('chat_history', session_id)
            print(f"[METRICS] Saving metrics to {session_dir}")
            save_evaluation_metrics(session_id, metrics, session_dir=session_dir)
            print(f"[METRICS] Metrics saved successfully for session {session_id}")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[METRICS ERROR] Error calculating/saving metrics: {e}")
            print(f"[METRICS ERROR] Traceback: {error_trace}")
            # Don't fail the request if metrics calculation fails
        
        # Record history (ensure history key exists)
        if 'history' not in chat_sessions[session_id]:
            chat_sessions[session_id]['history'] = []
        
        history_entry = {
            'id': str(uuid.uuid4()),
            'question': question,
            'code': generated_code,
            'result': execution_result,
            'csv_hash': chat_sessions[session_id].get('csv_hash'),
            'timestamp': datetime.now().isoformat()
        }
        chat_sessions[session_id]['history'].append(history_entry)
        
        # Build AI response
        if execution_result['type'] == 'error':
            ai_content = f"Error executing code:\n\n{execution_result['data']}\n\nGenerated code:\n```python\n{generated_code}\n```"
        else:
            ai_content = {
                'code': generated_code,
                'result': execution_result
            }
        
        ai_message = {
            'id': str(uuid.uuid4()),
            'type': 'assistant',
            'content': ai_content,
            'timestamp': datetime.now().isoformat()
        }
        chat_sessions[session_id]['messages'].append(ai_message)
        
        # Save session to file
        save_chat_session(session_id)
        
        return jsonify({
            'success': True,
            'user_message': user_message,
            'ai_message': ai_message
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in send_message: {error_trace}")
        
        # Update execution_result to reflect the error
        execution_result = {
            'type': 'error',
            'data': f'Error processing request: {str(e)}'
        }
        
        # Still try to calculate metrics even if there was an error
        try:
            print(f"[METRICS] Attempting to save metrics after error for session {session_id}")
            metrics = calculate_evaluation_metrics(
                question=question,
                generated_code=generated_code if generated_code else "",
                execution_result=execution_result,
                csv_file=csv_file if csv_file else "",
                model=selected_model,
                execution_time=execution_time,
                recovery_attempts=recovery_attempts
            )
            session_dir = os.path.join('chat_history', session_id)
            save_evaluation_metrics(session_id, metrics, session_dir=session_dir)
            print(f"[METRICS] Metrics saved after error for session {session_id}")
        except Exception as metrics_error:
            print(f"[METRICS ERROR] Failed to save metrics after error: {metrics_error}")
        
        # Ensure history key exists
        if 'history' not in chat_sessions[session_id]:
            chat_sessions[session_id]['history'] = []
        
        error_message = {
            'id': str(uuid.uuid4()),
            'type': 'assistant',
            'content': f'Error processing request: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }
        chat_sessions[session_id]['messages'].append(error_message)
        
        # Save session to file
        save_chat_session(session_id)
        
        return jsonify({
            'success': False,
            'user_message': user_message,
            'ai_message': error_message,
            'error': str(e)
        }), 500

def open_browser():
    """Open browser after server starts (only once)"""
    global _browser_opened
    if not _browser_opened:
        time.sleep(1.5)
        webbrowser.open('http://127.0.0.1:5000')
        _browser_opened = True

def save_chat_session(session_id):
    """Save chat session to file"""
    if session_id not in chat_sessions:
        return
    
    try:
        session_dir = os.path.join('chat_history', session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        session_file = os.path.join(session_dir, 'session.json')
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(chat_sessions[session_id], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving session {session_id}: {e}")

def load_chat_sessions_from_disk():
    """Load chat sessions from disk"""
    global chat_sessions
    if not os.path.exists('chat_history'):
        return
    
    for session_id in os.listdir('chat_history'):
        session_dir = os.path.join('chat_history', session_id)
        if os.path.isdir(session_dir):
            session_file = os.path.join(session_dir, 'session.json')
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    # Ensure all required keys exist
                    if 'history' not in session_data:
                        session_data['history'] = []
                    if 'csv_file' not in session_data:
                        session_data['csv_file'] = None
                    if 'csv_hash' not in session_data:
                        session_data['csv_hash'] = None
                    chat_sessions[session_id] = session_data
                except Exception as e:
                    print(f"Error loading session {session_id}: {e}")

@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get history records for a session"""
    if session_id in chat_sessions:
        return jsonify(chat_sessions[session_id].get('history', []))
    return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    # Load saved chat sessions
    load_chat_sessions_from_disk()
    print(f"Loaded {len(chat_sessions)} chat sessions from disk")
    
    # Only open browser in main process (avoid duplicate opening on Flask reload)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=True, port=5000, use_reloader=True)

