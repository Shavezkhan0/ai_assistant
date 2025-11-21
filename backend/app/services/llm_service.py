from groq import Groq
from app.config import settings

def get_settings():
    """Get settings instance"""
    return settings

class LLMService:
    def __init__(self):
        # Updated to supported model
        self.model_name = "llama-3.3-70b-versatile"  # ✅ Current supported model
        self._setup_client()
    
    def _setup_client(self):
        """Initialize the Groq client"""
        settings_instance = get_settings()
        api_key = settings_instance.groq_api_key
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
    
    def generate_response(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response from LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful college assistant. Provide clear, concise, and accurate information based on the provided notes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(error_msg)
            return error_msg
    
    def generate_response_with_context(self, query: str, context: str, max_tokens: int = 1024) -> str:
        """Generate response with provided context"""
        prompt = f"""Based on the following context from student notes, answer the question clearly and concisely.

Context:
{context}

Question: {query}

Answer:"""
        
        return self.generate_response(prompt, max_tokens)

# Create singleton instance
llm_service = LLMService()