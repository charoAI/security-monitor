"""
Ollama integration for local LLM processing
Free, private, and runs entirely on your machine
"""
import os
import requests
import json
from typing import List, Dict, Any

class OllamaSynthesizer:
    def __init__(self, model="mistral", base_url="http://localhost:11434"):
        """
        Initialize Ollama synthesizer

        Args:
            model: Model name (mistral, llama3, mixtral, etc.)
            base_url: Ollama API endpoint
        """
        self.model = os.getenv('OLLAMA_MODEL', model)
        self.base_url = os.getenv('OLLAMA_URL', base_url)
        self.timeout = 120  # Ollama can be slow on first run

        # Test connection
        self.test_connection()

    def test_connection(self):
        """Test if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                print(f"Warning: Ollama may not be running at {self.base_url}")
                return False

            # Check if model is available
            models = response.json().get('models', [])
            model_names = [m['name'].split(':')[0] for m in models]

            if self.model not in model_names:
                print(f"Warning: Model {self.model} not found. Available models: {model_names}")
                print(f"Pull the model with: ollama pull {self.model}")
                return False

            return True
        except requests.exceptions.ConnectionError:
            print(f"Warning: Cannot connect to Ollama at {self.base_url}")
            print("Make sure Ollama is running: ollama serve")
            return False
        except Exception as e:
            print(f"Warning: Ollama connection test failed: {e}")
            return False

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text using Ollama

        Args:
            prompt: Input prompt
            temperature: Creativity level (0.0 to 1.0)

        Returns:
            Generated text
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                print(f"Ollama error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.Timeout:
            print("Ollama request timed out. The model might be loading for the first time.")
            return None
        except Exception as e:
            print(f"Ollama generation error: {e}")
            return None

    def synthesize_report(self, country: str, articles: List[Dict],
                         threat_level: str, prompt: str = None) -> Dict[str, Any]:
        """
        Synthesize intelligence report using Ollama

        Args:
            country: Country name
            articles: List of news articles
            threat_level: Assessed threat level
            prompt: Custom analysis prompt

        Returns:
            Synthesized report dictionary
        """
        # Prepare article summaries
        article_text = "\n\n".join([
            f"Title: {article.get('title', 'No title')}\n"
            f"Summary: {article.get('summary', article.get('description', 'No summary'))[:500]}"
            for article in articles[:10]  # Limit to prevent context overflow
        ])

        # Build the prompt
        system_prompt = f"""You are a security intelligence analyst. Analyze the following news about {country} and provide a concise executive summary.

Current Threat Level: {threat_level}

Recent News:
{article_text}

{prompt if prompt else 'Focus on security implications, risks, and actionable intelligence.'}

Provide a professional intelligence briefing in 200 words or less."""

        # Generate the report
        response = self.generate(system_prompt, temperature=0.3)  # Lower temp for factual

        if response:
            return {
                'country': country,
                'threat_level': threat_level,
                'executive_summary': response,
                'article_count': len(articles),
                'llm_provider': f'Ollama/{self.model}'
            }
        else:
            # Fallback to basic synthesis
            return {
                'country': country,
                'threat_level': threat_level,
                'executive_summary': f"Analysis of {len(articles)} articles for {country} indicates {threat_level} threat level. Key topics include recent security developments and regional concerns.",
                'article_count': len(articles),
                'llm_provider': 'Fallback'
            }

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Chat conversation using Ollama

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Creativity level

        Returns:
            Assistant's response
        """
        # Convert to single prompt (Ollama doesn't have native chat format for all models)
        prompt = ""
        for msg in messages:
            if msg['role'] == 'user':
                prompt += f"User: {msg['content']}\n"
            elif msg['role'] == 'assistant':
                prompt += f"Assistant: {msg['content']}\n"
        prompt += "Assistant: "

        return self.generate(prompt, temperature)

    @staticmethod
    def install_instructions():
        """Return installation instructions for Ollama"""
        return """
        To use Ollama for FREE local LLM:

        1. Install Ollama:
           - Windows/Mac: Download from https://ollama.ai
           - Linux: curl -fsSL https://ollama.ai/install.sh | sh

        2. Start Ollama service:
           ollama serve

        3. Pull a model (choose one):
           ollama pull mistral      # 7B, fast, good quality
           ollama pull llama3       # 8B, great reasoning
           ollama pull mixtral      # 47B, best quality (needs 32GB RAM)

        4. Set in your .env file:
           LLM_PROVIDER=ollama
           OLLAMA_MODEL=mistral    # or your chosen model
           OLLAMA_URL=http://localhost:11434

        Benefits:
        - Completely FREE (no API costs)
        - 100% private (runs locally)
        - No rate limits
        - Works offline
        """