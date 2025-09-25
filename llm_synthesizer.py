import os
import json
from typing import List, Dict, Any
from datetime import datetime
from token_optimizer import TokenOptimizer
from security_article_analyzer import SecurityArticleAnalyzer

class LLMSynthesizer:
    """Use LLM to create professional intelligence narratives"""

    def __init__(self):
        # Check for Gemini first (free option)
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')

        self.use_gemini = bool(self.gemini_key)
        self.use_openai = bool(self.openai_key)
        self.use_llm = self.use_gemini or self.use_openai

        if self.use_gemini:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.genai = genai
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("Using Google Gemini for narrative generation")
            except ImportError:
                print("Please install google-generativeai: pip install google-generativeai")
                self.use_gemini = False
        elif self.use_openai:
            try:
                import openai
                openai.api_key = self.openai_key
                self.openai = openai
                self.model = "gpt-3.5-turbo"
                print("Using OpenAI for narrative generation")
            except ImportError:
                print("Please install openai: pip install openai")
                self.use_openai = False
    
    def synthesize_country_report(self, country: str, articles: List[Dict], use_deep_analysis: bool = True) -> str:
        """Generate a professional narrative report for a country using ACTUAL article content"""

        if not self.use_llm or not articles:
            return self._basic_synthesis(country, articles)

        try:
            # Extract actual article content if not already present
            from article_extractor import ArticleExtractor

            # Check if articles already have full content
            if not any(a.get('full_content') for a in articles):
                print(f"Extracting actual article content for {country}...")
                extractor = ArticleExtractor()
                articles = extractor.extract_articles_parallel(articles[:30])  # Limit to top 30 for speed

            if use_deep_analysis:
                # Use security analyzer for deep analysis
                analyzer = SecurityArticleAnalyzer()
                analysis = analyzer.analyze_articles_deeply(articles, country, max_articles=10)

                # Use the deep analysis for LLM
                article_data = analyzer.prepare_for_llm(analysis)
                print(f"Using deep analysis: {analysis['deep_analysis_count']} articles with full text")
            else:
                # Original optimization approach (for fallback)
                optimizer = TokenOptimizer()
                optimized_articles = optimizer.optimize_for_llm(articles, max_articles=15)
                article_data = self._prepare_articles(optimized_articles)

            if self.use_gemini:
                # Use Gemini
                full_prompt = f"{self._get_system_prompt()}\n\n{self._create_analysis_prompt(country, article_data)}"

                response = self.model.generate_content(
                    full_prompt,
                    generation_config={
                        'temperature': 0.7,
                        'max_output_tokens': 1500,
                    }
                )

                narrative = response.text
                return narrative

            elif self.use_openai:
                # Use OpenAI
                response = self.openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": self._create_analysis_prompt(country, article_data)}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )

                narrative = response.choices[0].message.content
                return narrative

        except Exception as e:
            print(f"LLM synthesis failed: {e}")
            return self._basic_synthesis(country, articles)
    
    def _get_system_prompt(self) -> str:
        """System prompt for intelligence analyst role"""
        return """You are a senior intelligence analyst preparing briefing documents for government officials.
        
        Your reports should:
        1. Synthesize multiple sources into coherent analysis
        2. Identify patterns, trends, and connections between events
        3. Assess implications for regional stability and security
        4. Provide context from historical and geopolitical perspectives
        5. Use professional, measured language appropriate for high-level briefings
        6. Avoid speculation - base analysis on reported facts
        7. Highlight critical developments requiring immediate attention
        
        Structure your analysis with:
        - Executive Assessment (2-3 sentences overview)
        - Current Situation (detailed narrative of recent developments)
        - Analysis (implications and connections)
        - Outlook (likely near-term developments)
        
        Write in a clear, professional tone similar to CIA World Factbook or State Department briefings."""
    
    def _create_analysis_prompt(self, country: str, article_data: str) -> str:
        """Create the analysis request prompt"""
        return f"""Analyze the following intelligence collected about {country} from multiple news sources.
Create a professional intelligence briefing that synthesizes these reports.

Raw Intelligence Reports:
{article_data}

Your task: Write a 3-4 paragraph intelligence assessment that:

PARAGRAPH 1 - Situation Overview:
Open with the most significant development. Connect it to the broader context. State why this matters now.

PARAGRAPH 2 - Analysis:
Connect the dots between different reports. What patterns emerge? How do political, security, and economic factors interact? What are the underlying drivers of current events?

PARAGRAPH 3 - Implications & Outlook:
What do these developments mean for stability? What should we watch for next? What are the risks?

Write in the style of a CIA World Intelligence Review or State Department briefing. Be specific, analytical, and direct. Use active voice. Connect events to show causation, not just correlation. Focus on WHY these events matter, not just WHAT happened."""
    
    def _prepare_articles(self, articles: List[Dict]) -> str:
        """Prepare article data for LLM consumption - now with ACTUAL CONTENT"""
        article_summaries = []

        # Helper to format date
        def format_date(date_str):
            if not date_str:
                return ""
            # Try to extract just the date part
            if "," in date_str:
                return f" ({date_str.split(',')[0]})"
            return f" ({date_str[:10]})" if len(date_str) > 10 else f" ({date_str})"

        # Group by relevance if available
        high_relevance = [a for a in articles if a.get('relevance_score', 0) >= 10]
        medium_relevance = [a for a in articles if 5 <= a.get('relevance_score', 0) < 10]

        # Add high relevance articles first
        if high_relevance:
            article_summaries.append("CRITICAL:")
            for article in high_relevance[:5]:
                date = format_date(article.get('published', ''))
                article_summaries.append(f"• {article.get('title', 'No title')}{date}")

        # Add medium relevance
        if medium_relevance:
            article_summaries.append("\nKEY UPDATES:")
            for article in medium_relevance[:5]:
                date = format_date(article.get('published', ''))
                article_summaries.append(f"• {article.get('title', 'No title')}{date}")

        # If no relevance scoring, just use first 10
        if not high_relevance and not medium_relevance:
            for article in articles[:10]:
                date = format_date(article.get('published', ''))
                article_summaries.append(f"• {article.get('title', 'No title')[:100]}{date}")

        return "\n".join(article_summaries)
    
    def _basic_synthesis(self, country: str, articles: List[Dict]) -> str:
        """Fallback synthesis without LLM"""
        if not articles:
            return f"No significant intelligence available for {country} during the reporting period."
        
        # Group by themes
        security_articles = []
        political_articles = []
        other_articles = []
        
        for article in articles:
            content = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            if any(term in content for term in ['attack', 'violence', 'military', 'conflict']):
                security_articles.append(article)
            elif any(term in content for term in ['government', 'election', 'political']):
                political_articles.append(article)
            else:
                other_articles.append(article)
        
        narrative = f"""**Executive Assessment**
        
Intelligence reporting on {country} over the past 48 hours encompasses {len(articles)} separate items from multiple sources, revealing a complex operational environment requiring continued monitoring.

**Current Situation**

"""
        
        if security_articles:
            narrative += f"Security dynamics in {country} reflect heightened tensions. "
            narrative += f"Reports indicate {security_articles[0].get('title', 'security incidents')}. "
            if len(security_articles) > 1:
                narrative += f"Additional security concerns include {security_articles[1].get('summary', '')[:200]}... "
        
        if political_articles:
            narrative += f"\n\nPolitical developments suggest institutional challenges. "
            narrative += f"{political_articles[0].get('summary', '')[:300]}... "
        
        narrative += f"""\n\n**Analysis**

The convergence of these factors suggests {country} faces a period of elevated risk. The multiplicity of security incidents, combined with political uncertainty, creates conditions conducive to further instability. International observers should note the potential for rapid escalation given current dynamics.

**Outlook**

Near-term indicators suggest continued volatility. Key variables to monitor include response from security forces, international diplomatic engagement, and public reaction to ongoing events. The situation requires enhanced intelligence collection and analysis."""
        
        return narrative


class AlternativeLLM:
    """Alternative using free/local models"""
    
    def __init__(self):
        # Option 1: Use Anthropic Claude API (if you have access)
        # Option 2: Use Google's Gemini API (has free tier)
        # Option 3: Use local models via Ollama
        self.provider = os.getenv('LLM_PROVIDER', 'none')
    
    def synthesize_with_gemini(self, country: str, articles: List[Dict]) -> str:
        """Use Google Gemini (has free tier)"""
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = self._create_prompt(country, articles)
        response = model.generate_content(prompt)
        
        return response.text
    
    def synthesize_with_ollama(self, country: str, articles: List[Dict]) -> str:
        """Use Ollama for local LLM (free, runs on your machine)"""
        import requests
        
        # Requires Ollama installed locally with a model like llama2 or mistral
        prompt = self._create_prompt(country, articles)
        
        response = requests.post('http://localhost:11434/api/generate', 
            json={
                "model": "mistral",  # or "llama2"
                "prompt": prompt,
                "stream": False
            })
        
        if response.status_code == 200:
            return response.json()['response']
        return None
    
    def _create_prompt(self, country: str, articles: List[Dict]) -> str:
        article_text = "\n\n".join([
            f"{a.get('title', 'No title')}: {a.get('summary', '')[:300]}"
            for a in articles[:10]
        ])
        
        return f"""As an intelligence analyst, create a professional narrative assessment of the situation in {country} based on these reports:

{article_text}

Provide a cohesive analysis that connects these events and assesses their significance for regional stability. Write in the style of a government intelligence briefing."""