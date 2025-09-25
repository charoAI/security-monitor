"""Enhanced country intelligence with historical context from real APIs"""
import requests
import json
import re
from datetime import datetime

class CountryIntelligence:
    def __init__(self):
        # Free APIs that don't require keys
        self.rest_countries_api = "https://restcountries.com/v3.1"
        self.wikipedia_api = "https://en.wikipedia.org/api/rest_v1"
        self.geonames_api = "http://api.geonames.org"
        self.cache = {}

    def get_country_basics(self, country_name):
        """Get basic country information from REST Countries API"""
        try:
            # Try exact name first
            response = requests.get(
                f"{self.rest_countries_api}/name/{country_name}",
                params={'fullText': 'false'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()[0]  # Get first match

                basics = {
                    'official_name': data.get('name', {}).get('official', country_name),
                    'common_name': data.get('name', {}).get('common', country_name),
                    'capital': data.get('capital', ['Unknown'])[0] if data.get('capital') else 'Unknown',
                    'region': data.get('region', 'Unknown'),
                    'subregion': data.get('subregion', 'Unknown'),
                    'population': data.get('population', 0),
                    'area': data.get('area', 0),
                    'languages': list(data.get('languages', {}).values()),
                    'currencies': list(data.get('currencies', {}).keys()),
                    'borders': data.get('borders', []),
                    'timezones': data.get('timezones', []),
                    'flag': data.get('flags', {}).get('png', ''),
                    'coat_of_arms': data.get('coatOfArms', {}).get('png', ''),
                    'lat_lng': data.get('latlng', []),
                    'landlocked': data.get('landlocked', False),
                    'un_member': data.get('unMember', False),
                    'independence_day': data.get('independent', None),
                    'government_type': self._extract_government_type(data),
                    'gdp_info': 'See World Bank or IMF for current GDP data',
                    'calling_code': data.get('idd', {}).get('root', '') +
                                   (data.get('idd', {}).get('suffixes', [''])[0] if data.get('idd', {}).get('suffixes') else '')
                }

                print(f"[REST Countries] Retrieved basic data for {country_name}")
                return basics
            else:
                print(f"[REST Countries] No data found for {country_name}")
                return None

        except Exception as e:
            print(f"[REST Countries] Error: {e}")
            return None

    def _extract_government_type(self, data):
        """Extract government type from country data"""
        # REST Countries doesn't directly provide government type
        # We can infer from other fields
        name_data = data.get('name', {})
        official_name = name_data.get('official', '').lower()

        if 'republic' in official_name:
            if 'democratic' in official_name:
                return 'Democratic Republic'
            elif 'federal' in official_name:
                return 'Federal Republic'
            elif 'islamic' in official_name:
                return 'Islamic Republic'
            else:
                return 'Republic'
        elif 'kingdom' in official_name:
            return 'Monarchy'
        elif 'state' in official_name:
            return 'State'
        else:
            return 'Unknown'

    def get_wikipedia_extract(self, country_name):
        """Get Wikipedia extract and historical summary"""
        try:
            # Get page summary
            url = f"{self.wikipedia_api}/page/summary/{country_name.replace(' ', '_')}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                wiki_info = {
                    'title': data.get('title', country_name),
                    'extract': data.get('extract', ''),
                    'description': data.get('description', ''),
                    'page_url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                }

                # Try to get sections for more detailed history
                sections_url = f"{self.wikipedia_api}/page/sections/{country_name.replace(' ', '_')}"
                sections_response = requests.get(sections_url, timeout=10)

                if sections_response.status_code == 200:
                    sections = sections_response.json()
                    history_sections = []

                    for section in sections.get('sections', []):
                        title_lower = section.get('line', '').lower()
                        if any(keyword in title_lower for keyword in ['history', 'colonial', 'independence', 'war', 'conflict']):
                            history_sections.append({
                                'title': section.get('line', ''),
                                'level': section.get('toclevel', 0),
                                'anchor': section.get('anchor', '')
                            })

                    wiki_info['history_sections'] = history_sections

                print(f"[Wikipedia] Retrieved data for {country_name}")
                return wiki_info
            else:
                print(f"[Wikipedia] No data found for {country_name}")
                return None

        except Exception as e:
            print(f"[Wikipedia] Error: {e}")
            return None

    def get_cia_factbook_url(self, country_name):
        """Generate CIA World Factbook URL"""
        # Normalize country name for CIA Factbook URL format
        country_slug = country_name.lower().replace(' ', '-')

        # Handle special cases
        special_cases = {
            'united-states': 'united-states',
            'usa': 'united-states',
            'uk': 'united-kingdom',
            'south-korea': 'korea-south',
            'north-korea': 'korea-north',
            'democratic-republic-of-congo': 'congo-democratic-republic-of-the',
            'drc': 'congo-democratic-republic-of-the'
        }

        if country_slug in special_cases:
            country_slug = special_cases[country_slug]

        return f"https://www.cia.gov/the-world-factbook/countries/{country_slug}/"

    def get_historical_context(self, country_name, focus_areas=None):
        """Generate comprehensive historical context for a country"""

        # Check cache
        cache_key = f"{country_name}_{str(focus_areas)}"
        if cache_key in self.cache:
            print(f"Returning cached data for {country_name}")
            return self.cache[cache_key]

        print(f"\n=== Gathering Intelligence on {country_name} ===")

        intelligence = {
            'country': country_name,
            'timestamp': datetime.now().isoformat(),
            'basic_info': {},
            'historical_summary': '',
            'wikipedia_data': {},
            'reference_urls': {},
            'key_facts': [],
            'historical_timeline': [],
            'current_context': ''
        }

        # Get basic country info
        print("Fetching basic country information...")
        basics = self.get_country_basics(country_name)
        if basics:
            intelligence['basic_info'] = basics

            # Create key facts summary
            intelligence['key_facts'] = [
                f"Capital: {basics['capital']}",
                f"Population: {basics['population']:,}",
                f"Area: {basics['area']:,} km²",
                f"Region: {basics['region']}, {basics['subregion']}",
                f"Government: {basics['government_type']}",
                f"Languages: {', '.join(basics['languages'][:3])}",
                f"UN Member: {'Yes' if basics['un_member'] else 'No'}",
                f"Landlocked: {'Yes' if basics['landlocked'] else 'No'}"
            ]

        # Get Wikipedia data
        print("Fetching Wikipedia information...")
        wiki_data = self.get_wikipedia_extract(country_name)
        if wiki_data:
            intelligence['wikipedia_data'] = wiki_data
            intelligence['historical_summary'] = wiki_data.get('extract', '')

        # Generate reference URLs
        intelligence['reference_urls'] = {
            'CIA World Factbook': self.get_cia_factbook_url(country_name),
            'Wikipedia': wiki_data['page_url'] if wiki_data else f"https://en.wikipedia.org/wiki/{country_name.replace(' ', '_')}",
            'BBC Country Profile': f"https://www.bbc.com/news/world-{self._get_bbc_region(basics['region'] if basics else 'africa')}",
            'UN Data': f"http://data.un.org/en/iso/{self._get_country_code(country_name)}.html",
            'World Bank': f"https://data.worldbank.org/country/{country_name.lower().replace(' ', '-')}"
        }

        # Generate historical timeline structure
        intelligence['historical_timeline'] = self._generate_timeline_structure(country_name)

        # Add focus area analysis if specified
        if focus_areas:
            intelligence['focus_analysis'] = self._analyze_focus_areas(country_name, focus_areas, intelligence)

        # Cache the results
        self.cache[cache_key] = intelligence

        print(f"Intelligence gathering complete for {country_name}")
        return intelligence

    def _get_bbc_region(self, region):
        """Map region to BBC URL format"""
        region_map = {
            'Africa': 'africa',
            'Americas': 'latin-america',
            'Asia': 'asia',
            'Europe': 'europe',
            'Oceania': 'asia'  # BBC groups Oceania with Asia
        }
        return region_map.get(region, 'africa')

    def _get_country_code(self, country_name):
        """Get ISO country code (simplified)"""
        # This would ideally use a proper mapping
        # For now, return a default
        return country_name[:2].upper()

    def _generate_timeline_structure(self, country_name):
        """Generate a timeline structure for historical events"""
        # This would be populated with actual historical data
        # For now, we provide a structure
        return [
            {'period': 'Pre-Colonial', 'events': 'Indigenous societies and early history'},
            {'period': 'Colonial Era', 'events': 'European colonization and impact'},
            {'period': 'Independence', 'events': 'Path to sovereignty'},
            {'period': 'Post-Independence', 'events': 'Nation building and challenges'},
            {'period': 'Modern Era', 'events': 'Recent developments and current situation'}
        ]

    def _analyze_focus_areas(self, country_name, focus_areas, intelligence):
        """Analyze specific focus areas based on available data"""
        analysis = {}

        for area in focus_areas:
            if area.lower() == 'conflict':
                analysis['conflict'] = {
                    'current_status': f"Analysis of conflict situation in {country_name}",
                    'historical_conflicts': 'List of major historical conflicts',
                    'risk_assessment': 'Current conflict risk level'
                }
            elif area.lower() == 'economy':
                analysis['economy'] = {
                    'gdp_trends': 'Economic growth patterns',
                    'major_industries': 'Key economic sectors',
                    'trade_partners': 'Major trading relationships'
                }
            elif area.lower() == 'politics':
                analysis['politics'] = {
                    'government_structure': intelligence['basic_info'].get('government_type', 'Unknown'),
                    'recent_elections': 'Electoral history',
                    'political_stability': 'Stability assessment'
                }

        return analysis

    def generate_briefing(self, country_name, current_events=None):
        """Generate an intelligence briefing combining historical and current context"""

        intelligence = self.get_historical_context(country_name)

        briefing = f"""
INTELLIGENCE BRIEFING: {country_name.upper()}
{'='*50}

BASIC FACTS:
{chr(10).join('• ' + fact for fact in intelligence['key_facts'])}

HISTORICAL OVERVIEW:
{intelligence['historical_summary'][:500]}...

REFERENCE SOURCES:
{chr(10).join(f'• {name}: {url}' for name, url in intelligence['reference_urls'].items())}
"""

        if current_events:
            briefing += f"""
CURRENT SITUATION CONTEXT:
Based on current events, historical patterns suggest attention to:
• Historical precedents for current situation
• Similar events in the country's past
• Regional historical context
"""

        return briefing


if __name__ == "__main__":
    # Test the country intelligence system
    intel = CountryIntelligence()

    test_countries = ['Haiti', 'Ukraine', 'Taiwan']

    for country in test_countries:
        print("\n" + "="*70)

        # Get historical context
        context = intel.get_historical_context(
            country,
            focus_areas=['conflict', 'politics']
        )

        # Generate briefing
        briefing = intel.generate_briefing(
            country,
            current_events=['recent unrest', 'political crisis']
        )

        print(briefing[:1000])  # Print first 1000 chars of briefing