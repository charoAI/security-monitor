from collections import defaultdict
from datetime import datetime
import re

class IntelligenceSynthesizer:
    """Synthesizes articles into professional intelligence reports by country"""
    
    def __init__(self):
        self.threat_keywords = [
            'attack', 'threat', 'conflict', 'crisis', 'violence', 'military',
            'terrorist', 'bombing', 'explosion', 'killed', 'wounded', 'fighting',
            'sanctions', 'tensions', 'war', 'missile', 'nuclear'
        ]
        
        self.economic_keywords = [
            'economy', 'economic', 'trade', 'sanctions', 'gdp', 'inflation',
            'currency', 'market', 'financial', 'investment', 'growth', 'recession'
        ]
        
        self.political_keywords = [
            'election', 'government', 'president', 'minister', 'parliament',
            'policy', 'diplomatic', 'democracy', 'protest', 'opposition', 'coup'
        ]
        
        self.humanitarian_keywords = [
            'humanitarian', 'refugee', 'aid', 'crisis', 'hunger', 'famine',
            'disease', 'hospital', 'emergency', 'disaster', 'flood', 'earthquake'
        ]
    
    def synthesize_by_country(self, articles, countries):
        """Group and synthesize articles by country"""
        country_data = defaultdict(lambda: {
            'articles': [],
            'themes': defaultdict(list),
            'key_events': [],
            'sources': set()
        })
        
        # Group articles by country
        for article in articles:
            content = f"{article['title']} {article['summary']}".lower()
            
            for country in countries:
                if country.lower() in content:
                    country_data[country]['articles'].append(article)
                    country_data[country]['sources'].add(article['source'])
                    
                    # Categorize by theme
                    if any(keyword in content for keyword in self.threat_keywords):
                        country_data[country]['themes']['Security Threats'].append(article)
                    
                    if any(keyword in content for keyword in self.economic_keywords):
                        country_data[country]['themes']['Economic Developments'].append(article)
                    
                    if any(keyword in content for keyword in self.political_keywords):
                        country_data[country]['themes']['Political Affairs'].append(article)
                    
                    if any(keyword in content for keyword in self.humanitarian_keywords):
                        country_data[country]['themes']['Humanitarian Situation'].append(article)
        
        return country_data
    
    def generate_executive_summary(self, country, data):
        """Generate executive summary for a country"""
        if not data['articles']:
            return f"No significant intelligence available for {country} in the current reporting period."
        
        summary_parts = []
        article_count = len(data['articles'])
        
        # Overall assessment
        summary_parts.append(
            f"Analysis of {article_count} reports from {len(data['sources'])} sources reveals "
            f"significant developments in {country}."
        )
        
        # Theme-based summary
        if data['themes']['Security Threats']:
            threat_count = len(data['themes']['Security Threats'])
            summary_parts.append(
                f"Security concerns dominate with {threat_count} threat-related reports."
            )
        
        if data['themes']['Political Affairs']:
            pol_count = len(data['themes']['Political Affairs'])
            summary_parts.append(
                f"Political developments include {pol_count} significant events."
            )
        
        if data['themes']['Humanitarian Situation']:
            human_count = len(data['themes']['Humanitarian Situation'])
            summary_parts.append(
                f"Humanitarian issues reported in {human_count} articles require attention."
            )
        
        return " ".join(summary_parts)
    
    def extract_key_points(self, articles, max_points=5):
        """Extract key bullet points from articles"""
        points = []
        seen_topics = set()
        
        for article in articles[:max_points]:
            # Extract first sentence or key point
            title = article['title']
            summary = article['summary']
            
            # Clean and truncate
            point = title if len(title) < 100 else summary[:100]
            
            # Avoid duplicates
            topic_key = point[:30].lower()
            if topic_key not in seen_topics:
                points.append(point)
                seen_topics.add(topic_key)
        
        return points
    
    def assess_threat_level(self, data):
        """Assess overall threat level based on content"""
        if not data['articles']:
            return "UNDETERMINED"

        threat_score = 0
        total_articles = len(data['articles'])

        # Count threat indicators - more sensitive scoring
        for article in data['articles']:
            content = f"{article['title']} {article.get('summary', '')}".lower()

            # Critical indicators (score 4)
            critical_terms = ['killed', 'dead', 'death toll', 'massacre', 'genocide',
                            'bombing', 'airstrike', 'missile strike', 'drone strike']

            # High indicators (score 3)
            high_terms = ['explosion', 'attack', 'war', 'combat', 'fighting',
                         'terrorist', 'violence', 'casualties', 'wounded', 'injured']

            # Moderate indicators (score 2)
            moderate_terms = ['conflict', 'crisis', 'threat', 'armed', 'military',
                            'security', 'insurgent', 'militant', 'rebel']

            # Low indicators (score 1)
            low_terms = ['tension', 'protest', 'sanctions', 'dispute', 'unrest']

            # Score based on severity
            article_score = 0
            if any(term in content for term in critical_terms):
                article_score = 4
            elif any(term in content for term in high_terms):
                article_score = 3
            elif any(term in content for term in moderate_terms):
                article_score = 2
            elif any(term in content for term in low_terms):
                article_score = 1

            threat_score += article_score

        avg_score = threat_score / total_articles if total_articles > 0 else 0

        # More nuanced thresholds
        if avg_score >= 3.0:
            return "CRITICAL"
        elif avg_score >= 2.0:
            return "HIGH"
        elif avg_score >= 1.0:
            return "MODERATE"
        elif avg_score >= 0.5:
            return "LOW"
        else:
            return "MINIMAL"