# LLM Integration Guide & Evaluation Metrics

## Part 1: Technical Requirements for Supporting Different LLMs

### Current Architecture Analysis

The current implementation directly uses OpenAI's SDK:
- **Location**: `frontend.py` → `generate_pandas_code()` function
- **API Call**: `openai_client.chat.completions.create()`
- **Model**: Hardcoded as "gpt-4"
- **Dependencies**: `openai==1.12.0`

### Required Technical Support

#### 1. **Abstraction Layer (LLM Provider Interface)**

Create a unified interface to abstract different LLM providers:

```python
# llm_providers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def generate_code(self, system_prompt: str, user_prompt: str, 
                     temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """Generate code from prompts"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name being used"""
        pass
    
    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost"""
        pass
```

#### 2. **Provider Implementations**

**2.1 OpenAI Provider (Current)**
```python
# llm_providers/openai_provider.py
from openai import OpenAI
from llm_providers.base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_code(self, system_prompt: str, user_prompt: str, 
                     temperature: float = 0.3, max_tokens: int = 1000) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
```

**2.2 Anthropic Claude Provider**
```python
# llm_providers/anthropic_provider.py
import anthropic
from llm_providers.base import LLMProvider

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_code(self, system_prompt: str, user_prompt: str, 
                     temperature: float = 0.3, max_tokens: int = 1000) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text.strip()
```

**2.3 Google Gemini Provider**
```python
# llm_providers/gemini_provider.py
import google.generativeai as genai
from llm_providers.base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
    
    def generate_code(self, system_prompt: str, user_prompt: str, 
                     temperature: float = 0.3, max_tokens: int = 1000) -> str:
        prompt = f"{system_prompt}\n\n{user_prompt}"
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )
        return response.text.strip()
```

**2.4 Local/Open Source Models (via Ollama/LM Studio)**
```python
# llm_providers/local_provider.py
import requests
from llm_providers.base import LLMProvider

class LocalProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "llama2"):
        self.base_url = base_url
        self.model = model
    
    def generate_code(self, system_prompt: str, user_prompt: str, 
                     temperature: float = 0.3, max_tokens: int = 1000) -> str:
        prompt = f"{system_prompt}\n\n{user_prompt}"
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
        )
        return response.json()["response"].strip()
```

**2.5 OpenAI-Compatible API (for other providers)**
```python
# llm_providers/openai_compatible_provider.py
from openai import OpenAI
from llm_providers.base import LLMProvider

class OpenAICompatibleProvider(LLMProvider):
    """For providers with OpenAI-compatible APIs (e.g., Together AI, Groq)"""
    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
    
    def generate_code(self, system_prompt: str, user_prompt: str, 
                     temperature: float = 0.3, max_tokens: int = 1000) -> str:
        # Same as OpenAI provider
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
```

#### 3. **Provider Factory Pattern**

```python
# llm_providers/factory.py
from llm_providers.openai_provider import OpenAIProvider
from llm_providers.anthropic_provider import AnthropicProvider
from llm_providers.gemini_provider import GeminiProvider
from llm_providers.local_provider import LocalProvider
from llm_providers.openai_compatible_provider import OpenAICompatibleProvider
from llm_providers.base import LLMProvider
import os

class LLMProviderFactory:
    @staticmethod
    def create_provider(provider_type: str = None) -> LLMProvider:
        """Create LLM provider based on configuration"""
        provider_type = provider_type or os.getenv('LLM_PROVIDER', 'openai')
        
        if provider_type.lower() == 'openai':
            return OpenAIProvider(
                api_key=os.getenv('OPENAI_API_KEY'),
                model=os.getenv('OPENAI_MODEL', 'gpt-4')
            )
        elif provider_type.lower() == 'anthropic':
            return AnthropicProvider(
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                model=os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
            )
        elif provider_type.lower() == 'gemini':
            return GeminiProvider(
                api_key=os.getenv('GEMINI_API_KEY'),
                model=os.getenv('GEMINI_MODEL', 'gemini-pro')
            )
        elif provider_type.lower() == 'local':
            return LocalProvider(
                base_url=os.getenv('LOCAL_LLM_URL', 'http://localhost:11434'),
                model=os.getenv('LOCAL_LLM_MODEL', 'llama2')
            )
        elif provider_type.lower() == 'openai-compatible':
            return OpenAICompatibleProvider(
                base_url=os.getenv('COMPATIBLE_API_URL'),
                api_key=os.getenv('COMPATIBLE_API_KEY'),
                model=os.getenv('COMPATIBLE_MODEL')
            )
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
```

#### 4. **Configuration Management**

Update `.env` file structure:
```env
# LLM Provider Selection
LLM_PROVIDER=openai  # Options: openai, anthropic, gemini, local, openai-compatible

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229

# Google Gemini Configuration
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-pro

# Local LLM Configuration
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama2

# OpenAI-Compatible API Configuration
COMPATIBLE_API_URL=https://api.together.xyz/v1
COMPATIBLE_API_KEY=...
COMPATIBLE_MODEL=meta-llama/Llama-2-70b-chat-hf
```

#### 5. **Required Dependencies**

Update `requirements.txt`:
```txt
# Existing dependencies
Flask==3.0.0
Werkzeug==3.0.1
pandas==2.2.0
numpy==1.26.3
matplotlib==3.8.2
seaborn==0.13.0
plotly==5.18.0
requests==2.31.0
python-dotenv==1.0.0

# LLM Provider SDKs
openai==1.12.0
anthropic==0.18.1
google-generativeai==0.3.2

# Optional: LangChain for advanced orchestration
# langchain==0.1.0
# langchain-openai==0.0.2
# langchain-anthropic==0.1.0
```

#### 6. **Code Refactoring**

Update `frontend.py`:
```python
from llm_providers.factory import LLMProviderFactory

# Initialize LLM provider
llm_provider = LLMProviderFactory.create_provider()

def generate_pandas_code(question, csv_info):
    """Generate Pandas code using configured LLM provider"""
    columns = csv_info.get('columns', [])
    dtypes = csv_info.get('dtypes', {})
    
    system_prompt = """..."""  # Same as before
    
    try:
        code = llm_provider.generate_code(
            system_prompt=system_prompt,
            user_prompt=question,
            temperature=0.3,
            max_tokens=1000
        )
        # Remove code block markers (same as before)
        return clean_code(code)
    except Exception as e:
        raise Exception(f"Error generating code: {str(e)}")
```

### Technical Challenges & Solutions

#### Challenge 1: **API Format Differences**
- **Solution**: Abstract interface with provider-specific implementations
- **Impact**: Each provider handles its own API format

#### Challenge 2: **Response Format Variations**
- **Solution**: Standardize response parsing in base class
- **Impact**: Handle different response structures (OpenAI vs Anthropic vs Gemini)

#### Challenge 3: **Rate Limiting & Error Handling**
- **Solution**: Implement retry logic and exponential backoff
- **Impact**: Handle API rate limits gracefully

#### Challenge 4: **Cost Tracking**
- **Solution**: Token counting and cost estimation per provider
- **Impact**: Track usage and costs across different providers

#### Challenge 5: **Model Capabilities**
- **Solution**: Provider-specific prompt engineering
- **Impact**: Optimize prompts for each model's strengths

---

## Part 2: Evaluation Metrics for LLM Agents

### 1. **Code Correctness Metrics**

#### 1.1 Syntax Correctness
- **Metric**: Percentage of generated code that is syntactically valid
- **Measurement**: Parse code with `ast.parse()` before execution
- **Target**: >95%

#### 1.2 Execution Success Rate
- **Metric**: Percentage of code that executes without errors
- **Measurement**: Run code in sandbox and check for exceptions
- **Target**: >80%

#### 1.3 Semantic Correctness
- **Metric**: Does the code produce the expected result?
- **Measurement**: Compare output with ground truth or expected output
- **Target**: >70% (subjective, requires manual evaluation)

### 2. **Code Quality Metrics**

#### 2.1 Code Completeness
- **Metric**: Does the code fully address the user's question?
- **Measurement**: Manual review or automated checks for required operations
- **Target**: >85%

#### 2.2 Code Efficiency
- **Metric**: Execution time and memory usage
- **Measurement**: Profile code execution
- **Target**: Within acceptable limits (context-dependent)

#### 2.3 Code Readability
- **Metric**: Code structure, naming conventions, comments
- **Measurement**: Static analysis tools (pylint, flake8)
- **Target**: Score >7/10

### 3. **Performance Metrics**

#### 3.1 Response Time (Latency)
- **Metric**: Time from question to final result
- **Components**:
  - LLM API call time
  - Code execution time
  - Total end-to-end time
- **Target**: 
  - LLM call: <5 seconds
  - Code execution: <10 seconds
  - Total: <15 seconds

#### 3.2 Throughput
- **Metric**: Requests processed per minute
- **Measurement**: Load testing
- **Target**: >10 requests/minute (depends on infrastructure)

#### 3.3 Token Usage
- **Metric**: Input and output tokens per request
- **Measurement**: Track token counts from API responses
- **Target**: Minimize while maintaining quality

### 4. **Cost Metrics**

#### 4.1 Cost per Request
- **Metric**: API cost per user question
- **Calculation**: `(input_tokens × input_price + output_tokens × output_price)`
- **Target**: Minimize while maintaining quality

#### 4.2 Cost Efficiency
- **Metric**: Cost per successful execution
- **Calculation**: `total_cost / successful_executions`
- **Target**: Optimize for best quality/cost ratio

### 5. **Reliability Metrics**

#### 5.1 Error Rate
- **Metric**: Percentage of requests that fail
- **Categories**:
  - LLM API errors
  - Code generation errors
  - Code execution errors
- **Target**: <10% total error rate

#### 5.2 Retry Success Rate
- **Metric**: Percentage of failed requests that succeed on retry
- **Measurement**: Track retry attempts and outcomes
- **Target**: >50%

### 6. **Safety & Security Metrics**

#### 6.1 Code Safety Score
- **Metric**: Percentage of generated code that passes safety checks
- **Checks**:
  - No file system writes
  - No network calls
  - No system commands
  - No dangerous operations
- **Target**: 100% (critical)

#### 6.2 Prompt Injection Resistance
- **Metric**: Ability to resist malicious prompts
- **Measurement**: Test with adversarial prompts
- **Target**: >90% resistance

### 7. **User Experience Metrics**

#### 7.1 Question Understanding Accuracy
- **Metric**: Does the agent understand the user's intent?
- **Measurement**: Manual evaluation or user feedback
- **Target**: >85%

#### 7.2 Result Relevance
- **Metric**: Is the result relevant to the question?
- **Measurement**: Manual evaluation or automated checks
- **Target**: >80%

#### 7.3 User Satisfaction
- **Metric**: User ratings or feedback scores
- **Measurement**: Post-interaction surveys
- **Target**: >4/5 stars

### 8. **Comparative Metrics (Multi-LLM Evaluation)**

#### 8.1 Head-to-Head Comparison
- **Metric**: Side-by-side comparison of outputs
- **Measurement**: Run same questions on different LLMs
- **Output**: Win rate, tie rate, loss rate

#### 8.2 Best Model Selection
- **Metric**: Which model performs best overall?
- **Factors**:
  - Code correctness
  - Response time
  - Cost
  - Reliability
- **Method**: Weighted scoring system

### Evaluation Framework Implementation

```python
# evaluation/evaluator.py
import time
import ast
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class EvaluationResult:
    """Results from evaluating a single LLM response"""
    question: str
    generated_code: str
    execution_result: Dict
    syntax_valid: bool
    execution_success: bool
    execution_time: float
    llm_api_time: float
    total_time: float
    token_count: Dict[str, int]
    cost: float
    safety_score: float
    correctness_score: Optional[float] = None

class LLMEvaluator:
    def __init__(self, llm_provider, code_executor):
        self.llm_provider = llm_provider
        self.code_executor = code_executor
    
    def evaluate(self, question: str, csv_info: Dict, 
                 expected_result: Optional[Dict] = None) -> EvaluationResult:
        """Evaluate LLM performance on a single question"""
        
        # Measure LLM API time
        start_time = time.time()
        code = self.llm_provider.generate_code(...)
        llm_api_time = time.time() - start_time
        
        # Check syntax
        syntax_valid = self._check_syntax(code)
        
        # Execute code
        exec_start = time.time()
        execution_result = self.code_executor.execute(code)
        execution_time = time.time() - exec_start
        
        # Calculate metrics
        token_count = self.llm_provider.get_token_count(...)
        cost = self.llm_provider.estimate_cost(...)
        safety_score = self._check_safety(code)
        correctness_score = self._check_correctness(
            execution_result, expected_result
        ) if expected_result else None
        
        return EvaluationResult(
            question=question,
            generated_code=code,
            execution_result=execution_result,
            syntax_valid=syntax_valid,
            execution_success=execution_result['type'] != 'error',
            execution_time=execution_time,
            llm_api_time=llm_api_time,
            total_time=llm_api_time + execution_time,
            token_count=token_count,
            cost=cost,
            safety_score=safety_score,
            correctness_score=correctness_score
        )
    
    def _check_syntax(self, code: str) -> bool:
        """Check if code is syntactically valid"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def _check_safety(self, code: str) -> float:
        """Check code safety (0.0 to 1.0)"""
        dangerous_patterns = [
            'open(', 'write(', 'exec(', 'eval(',
            'subprocess', 'os.system', 'import os',
            'requests.get', 'urllib'
        ]
        score = 1.0
        for pattern in dangerous_patterns:
            if pattern in code:
                score -= 0.2
        return max(0.0, score)
    
    def _check_correctness(self, result: Dict, expected: Dict) -> float:
        """Compare result with expected output (0.0 to 1.0)"""
        # Implementation depends on result type
        # This is a simplified version
        if result['type'] == expected['type']:
            if result['type'] == 'number':
                return 1.0 if abs(result['data'] - expected['data']) < 0.01 else 0.0
            elif result['type'] == 'table':
                # Compare table structures and values
                return self._compare_tables(result, expected)
        return 0.0
```

### Benchmark Dataset

Create a standardized test suite:

```python
# evaluation/benchmark.py
BENCHMARK_QUESTIONS = [
    {
        "question": "Calculate the mean of column 'price'",
        "expected_type": "number",
        "expected_value": 123.45,
        "csv_file": "test_data.csv"
    },
    {
        "question": "Filter rows where 'status' equals 'active'",
        "expected_type": "table",
        "expected_rows": 50,
        "csv_file": "test_data.csv"
    },
    {
        "question": "Create a bar chart of 'category' counts",
        "expected_type": "chart",
        "csv_file": "test_data.csv"
    },
    # ... more test cases
]
```

### Evaluation Report Format

```json
{
  "evaluation_date": "2024-01-15",
  "llm_provider": "openai",
  "model": "gpt-4",
  "total_questions": 100,
  "metrics": {
    "syntax_correctness": 0.98,
    "execution_success_rate": 0.85,
    "average_response_time": 3.2,
    "average_cost_per_request": 0.05,
    "safety_score": 1.0,
    "user_satisfaction": 4.2
  },
  "comparison": {
    "vs_gpt-3.5": {
      "win_rate": 0.75,
      "tie_rate": 0.15,
      "loss_rate": 0.10
    }
  }
}
```

---

## Summary

### Technical Requirements Checklist

- [ ] Create LLM provider abstraction layer
- [ ] Implement provider-specific adapters
- [ ] Add configuration management
- [ ] Update dependencies
- [ ] Refactor code generation function
- [ ] Add error handling and retry logic
- [ ] Implement cost tracking
- [ ] Add logging and monitoring

### Evaluation Metrics Checklist

- [ ] Code correctness metrics
- [ ] Performance metrics
- [ ] Cost metrics
- [ ] Safety metrics
- [ ] User experience metrics
- [ ] Comparative evaluation framework
- [ ] Benchmark dataset
- [ ] Automated evaluation pipeline




