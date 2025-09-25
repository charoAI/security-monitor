import re
from datetime import datetime
from collections import defaultdict, Counter
import random

class NarrativeGenerator:
    """Generates readable narrative intelligence reports from collected articles"""
    
    def __init__(self):
        self.transition_phrases = [
            "Meanwhile", "In parallel developments", "Simultaneously", 
            "Adding to the complexity", "Of particular concern", "Notably",
            "In a related development", "Furthermore", "Additionally"
        ]
    
    def generate_country_narrative(self, country, articles):
        """Generate a flowing narrative report for a single country"""
        if not articles:
            return f"No significant intelligence was collected regarding {country} during the reporting period."
        
        # Analyze themes and patterns
        themes = self._analyze_themes(articles)
        timeline = self._build_timeline(articles)
        key_actors = self._extract_key_actors(articles)
        sentiment = self._analyze_sentiment(articles)
        
        # Build narrative sections
        narrative = []
        
        # Opening paragraph - Overview
        narrative.append(self._generate_opening(country, articles, themes, sentiment))
        
        # Security situation
        if themes['security']:
            narrative.append(self._generate_security_section(country, themes['security']))
        
        # Political developments
        if themes['political']:
            narrative.append(self._generate_political_section(country, themes['political']))
        
        # Economic situation
        if themes['economic']:
            narrative.append(self._generate_economic_section(country, themes['economic']))
        
        # Humanitarian concerns
        if themes['humanitarian']:
            narrative.append(self._generate_humanitarian_section(country, themes['humanitarian']))
        
        # Closing assessment
        narrative.append(self._generate_assessment(country, themes, sentiment))
        
        return "\n\n".join(narrative)
    
    def _analyze_themes(self, articles):
        """Categorize articles by theme"""
        themes = {
            'security': [],
            'political': [],
            'economic': [],
            'humanitarian': [],
            'other': []
        }
        
        security_terms = ['attack', 'military', 'conflict', 'violence', 'killed', 'wounded',
                         'terrorist', 'bombing', 'explosion', 'missile', 'war', 'troops']
        political_terms = ['election', 'government', 'president', 'minister', 'parliament',
                          'vote', 'party', 'opposition', 'protest', 'diplomatic']
        economic_terms = ['economy', 'trade', 'sanctions', 'market', 'currency', 'GDP',
                         'inflation', 'unemployment', 'exports', 'imports']
        humanitarian_terms = ['humanitarian', 'refugee', 'aid', 'crisis', 'hunger',
                             'medical', 'hospital', 'disaster', 'emergency']
        
        for article in articles:
            content = f"{article['title']} {article['summary']}".lower()
            categorized = False
            
            if any(term in content for term in security_terms):
                themes['security'].append(article)
                categorized = True
            if any(term in content for term in political_terms):
                themes['political'].append(article)
                categorized = True
            if any(term in content for term in economic_terms):
                themes['economic'].append(article)
                categorized = True
            if any(term in content for term in humanitarian_terms):
                themes['humanitarian'].append(article)
                categorized = True
            if not categorized:
                themes['other'].append(article)
        
        return themes
    
    def _analyze_sentiment(self, articles):
        """Analyze overall sentiment of coverage"""
        negative_terms = ['crisis', 'attack', 'killed', 'threat', 'concern', 'problem',
                         'conflict', 'violence', 'deteriorating', 'worsening']
        positive_terms = ['progress', 'improvement', 'success', 'agreement', 'peace',
                         'growth', 'recovery', 'stable', 'resolution']
        
        negative_count = 0
        positive_count = 0
        
        for article in articles:
            content = f"{article['title']} {article['summary']}".lower()
            negative_count += sum(1 for term in negative_terms if term in content)
            positive_count += sum(1 for term in positive_terms if term in content)
        
        if negative_count > positive_count * 2:
            return 'highly_negative'
        elif negative_count > positive_count:
            return 'negative'
        elif positive_count > negative_count:
            return 'positive'
        else:
            return 'mixed'
    
    def _extract_key_actors(self, articles):
        """Extract mentioned organizations, leaders, groups"""
        actors = []
        for article in articles:
            content = f"{article['title']} {article['summary']}"
            # Look for capitalized words that might be names/organizations
            potential_actors = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', content)
            actors.extend(potential_actors)
        
        return Counter(actors).most_common(5)
    
    def _build_timeline(self, articles):
        """Build chronological timeline of events"""
        # Sort articles by date if available
        return sorted(articles, key=lambda x: x.get('published', ''), reverse=True)
    
    def _generate_opening(self, country, articles, themes, sentiment):
        """Generate opening overview paragraph"""
        article_count = len(articles)
        theme_counts = {k: len(v) for k, v in themes.items() if v}
        dominant_theme = max(theme_counts, key=theme_counts.get) if theme_counts else 'general'
        
        sentiment_descriptions = {
            'highly_negative': 'deeply concerning',
            'negative': 'troubling',
            'mixed': 'mixed',
            'positive': 'encouraging'
        }
        
        sentiment_desc = sentiment_descriptions.get(sentiment, 'complex')
        
        opening = f"The security and political situation in {country} presents a {sentiment_desc} picture "
        opening += f"based on analysis of {article_count} intelligence reports from the past 24-48 hours. "
        
        if dominant_theme == 'security':
            opening += f"Security concerns dominate the current intelligence picture, with {theme_counts['security']} "
            opening += f"reports highlighting ongoing threats and incidents. "
        elif dominant_theme == 'political':
            opening += f"Political developments are at the forefront, with {theme_counts['political']} "
            opening += f"reports covering governmental and diplomatic activities. "
        elif dominant_theme == 'humanitarian':
            opening += f"Humanitarian issues require urgent attention, with {theme_counts['humanitarian']} "
            opening += f"reports documenting critical needs and crises. "
        
        # Add source diversity note
        sources = list(set(a['source'] for a in articles))
        opening += f"This assessment draws from {len(sources)} different intelligence sources, "
        opening += f"providing a multi-faceted view of the evolving situation."
        
        return opening
    
    def _generate_security_section(self, country, articles):
        """Generate security-focused narrative section"""
        if not articles:
            return ""
        
        section = "**Security Developments**\n\n"
        
        # Extract key security events
        events = []
        for article in articles[:5]:  # Focus on top 5 most relevant
            title = article['title']
            summary = article['summary'][:200]
            events.append({'title': title, 'summary': summary, 'source': article['source']})
        
        # Build narrative from events
        section += f"The security landscape in {country} has been marked by significant developments. "
        
        for i, event in enumerate(events):
            if i == 0:
                section += f"{event['title']}. {event['summary']} "
            else:
                transition = self.transition_phrases[i % len(self.transition_phrases)]
                section += f"{transition}, {event['summary'].lower()} "
            
            if i == 2:  # Add source attribution midway
                section += f"(Source: {event['source']}). "
        
        # Add assessment
        section += f"\n\nThese security developments suggest "
        if len(events) > 3:
            section += f"a deteriorating security environment requiring close monitoring. "
        else:
            section += f"ongoing instability that could escalate without intervention. "
        
        return section
    
    def _generate_political_section(self, country, articles):
        """Generate political narrative section"""
        if not articles:
            return ""
        
        section = "**Political Landscape**\n\n"
        section += f"Political dynamics in {country} reflect "
        
        # Identify key political themes
        content = ' '.join([f"{a['title']} {a['summary']}" for a in articles]).lower()
        
        if 'election' in content:
            section += "electoral tensions and democratic processes under strain. "
        elif 'protest' in content:
            section += "growing civil unrest and public dissatisfaction with current leadership. "
        elif 'government' in content:
            section += "ongoing governmental challenges and institutional pressures. "
        else:
            section += "complex political maneuvering among various factions. "
        
        # Add specific examples
        for article in articles[:3]:
            section += f"{article['summary'][:150]}... "
        
        return section
    
    def _generate_economic_section(self, country, articles):
        """Generate economic narrative section"""
        if not articles:
            return ""
        
        section = "**Economic Indicators**\n\n"
        section += f"Economic conditions in {country} "
        
        content = ' '.join([f"{a['title']} {a['summary']}" for a in articles]).lower()
        
        if 'sanction' in content:
            section += "continue to be impacted by international sanctions, "
        if 'inflation' in content or 'currency' in content:
            section += "show signs of monetary instability, "
        if 'trade' in content:
            section += "reflect changing trade dynamics, "
        
        section += "with reports indicating "
        
        for article in articles[:2]:
            section += f"{article['summary'][:100]}... "
        
        return section
    
    def _generate_humanitarian_section(self, country, articles):
        """Generate humanitarian narrative section"""
        if not articles:
            return ""
        
        section = "**Humanitarian Concerns**\n\n"
        section += f"The humanitarian situation in {country} demands immediate attention. "
        
        # Extract key humanitarian issues
        issues = []
        for article in articles[:3]:
            summary = article['summary'][:150]
            issues.append(summary)
        
        section += ' '.join(issues)
        section += f" International aid organizations report increasing needs for basic services and support."
        
        return section
    
    def _generate_assessment(self, country, themes, sentiment):
        """Generate closing assessment and outlook"""
        assessment = "**Assessment and Outlook**\n\n"
        
        # Calculate risk level
        total_articles = sum(len(v) for v in themes.values())
        security_weight = len(themes['security']) / max(total_articles, 1)
        
        if security_weight > 0.5 or sentiment == 'highly_negative':
            assessment += f"The situation in {country} remains highly volatile with significant risks to regional stability. "
            assessment += "Immediate international attention and coordinated response mechanisms are recommended. "
        elif security_weight > 0.3 or sentiment == 'negative':
            assessment += f"Current trends in {country} suggest moderate to high risk of further deterioration. "
            assessment += "Enhanced monitoring and preventive diplomatic engagement are advised. "
        else:
            assessment += f"While challenges persist in {country}, the situation appears manageable with current resources. "
            assessment += "Continued observation and support for local institutions is recommended. "
        
        # Add forward-looking statement
        assessment += "\n\nKey indicators to monitor in the coming days include: "
        
        indicators = []
        if themes['security']:
            indicators.append("security incident frequency")
        if themes['political']:
            indicators.append("political stability measures")
        if themes['humanitarian']:
            indicators.append("humanitarian access and aid delivery")
        if themes['economic']:
            indicators.append("economic indicators and market responses")
        
        assessment += ", ".join(indicators) + "."
        
        return assessment