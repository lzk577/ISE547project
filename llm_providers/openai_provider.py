"""
OpenAI Provider
Direct OpenAI API integration for GPT-4
"""
from openai import OpenAI
from typing import Dict, Optional

class OpenAIProvider:
    """OpenAI provider for direct API access"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.current_model = None
    
    def generate_code(self, system_prompt: str, user_prompt: str, 
                     model: str = "gpt-4", temperature: float = 0.3, 
                     max_tokens: int = 1000) -> str:
        """Generate code using OpenAI API"""
        self.current_model = model
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            code = response.choices[0].message.content.strip()
            
            # Track token usage
            if hasattr(response, 'usage'):
                self.last_usage = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            else:
                self.last_usage = None
            
            return code
        except Exception as e:
            raise Exception(f"Error generating code with {model}: {str(e)}")
    
    def get_model_name(self) -> str:
        """Get current model name"""
        return self.current_model or "unknown"
    
    def get_token_usage(self) -> Optional[Dict]:
        """Get last token usage"""
        return getattr(self, 'last_usage', None)




