from flask import Flask, render_template, request, jsonify
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path
import socket

# Set timeout for all network operations
socket.setdefaulttimeout(5)
from report_synthesizer import IntelligenceSynthesizer
from narrative_generator import NarrativeGenerator
from dynamic_feed_generator import DynamicFeedGenerator
from country_intelligence import CountryIntelligence
from google_news_engine import GoogleNewsEngine
try:
    from fast_llm_synthesizer import FastLLMSynthesizer, generate_chat_context
    llm_available = True
except ImportError:
    try:
        from llm_synthesizer import LLMSynthesizer
        llm_available = True
    except ImportError:
        llm_available = False
        print("LLM synthesizer not available. Install google-generativeai for enhanced narratives.")

app = Flask(__name__)

# Load sources from file
SOURCES_FILE = Path('sources_config.json')

def load_sources():
    if SOURCES_FILE.exists():
        with open(SOURCES_FILE, 'r') as f:
            data = json.load(f)
            # If sources list is small, offer to add more
            if len(data.get('sources', [])) < 10:
                try:
                    from default_sources import DEFAULT_SOURCES
                    existing_urls = [s['url'] for s in data['sources']]
                    max_id = max([s.get('id', 0) for s in data['sources']], default=0)

                    for source in DEFAULT_SOURCES:
                        if source['url'] not in existing_urls:
                            max_id += 1
                            source['id'] = max_id
                            data['sources'].append(source)

                    save_sources(data)
                except:
                    pass
            return data
    else:
        # Use comprehensive default sources
        try:
            from default_sources import DEFAULT_SOURCES
            sources_with_ids = []
            for i, source in enumerate(DEFAULT_SOURCES, 1):
                source['id'] = i
                sources_with_ids.append(source)

            default = {
                'sources': sources_with_ids,
                'blacklist': []
            }
        except:
            # Fallback to basic sources
            default = {
                'sources': [
                    {'id': 1, 'name': 'BBC World', 'url': 'http://feeds.bbci.co.uk/news/world/rss.xml', 'type': 'news', 'active': True},
                    {'id': 2, 'name': 'Reuters World', 'url': 'https://feeds.reuters.com/Reuters/worldNews', 'type': 'news', 'active': True},
                    {'id': 3, 'name': 'Al Jazeera', 'url': 'https://www.aljazeera.com/xml/rss/all.xml', 'type': 'news', 'active': True},
                    {'id': 4, 'name': 'Krebs on Security', 'url': 'https://krebsonsecurity.com/feed/', 'type': 'cyber', 'active': True},
                    {'id': 5, 'name': 'Bellingcat', 'url': 'https://www.bellingcat.com/feed/', 'type': 'geopolitical', 'active': True},
                ],
                'blacklist': []
            }
        save_sources(default)
        return default

def save_sources(data):
    with open(SOURCES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# All countries list (195 countries)
COUNTRIES = [
    'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia',
    'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus',
    'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil',
    'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada',
    'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica',
    'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Democratic Republic of the Congo', 'Denmark', 'Djibouti', 'Dominica',
    'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia',
    'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia',
    'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana',
    'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq',
    'Ireland', 'Israel', 'Italy', 'Ivory Coast', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan',
    'Kenya', 'Kiribati', 'Kosovo', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon',
    'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi',
    'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico',
    'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar',
    'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria',
    'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestine', 'Panama',
    'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania',
    'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe',
    'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia',
    'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan',
    'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand',
    'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda',
    'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City',
    'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe'
]

# Keywords for location filtering (expanded for major countries)
LOCATION_KEYWORDS = {
    'United States': ['US', 'USA', 'United States', 'America', 'Washington', 'Pentagon', 'White House', 'Biden'],
    'China': ['China', 'Chinese', 'Beijing', 'Shanghai', 'PRC', 'Xi Jinping', 'CCP'],
    'Russia': ['Russia', 'Russian', 'Moscow', 'Kremlin', 'Putin'],
    'United Kingdom': ['UK', 'Britain', 'British', 'England', 'London', 'Westminster'],
    'Ukraine': ['Ukraine', 'Ukrainian', 'Kyiv', 'Kiev', 'Zelensky'],
    'Israel': ['Israel', 'Israeli', 'Tel Aviv', 'Jerusalem', 'IDF'],
    'Iran': ['Iran', 'Iranian', 'Tehran', 'Persia'],
    'North Korea': ['North Korea', 'DPRK', 'Pyongyang', 'Kim Jong'],
    'Taiwan': ['Taiwan', 'Taiwanese', 'Taipei', 'TSMC'],
    'India': ['India', 'Indian', 'Delhi', 'Mumbai', 'Modi'],
    'Japan': ['Japan', 'Japanese', 'Tokyo', 'Kyoto'],
    'Germany': ['Germany', 'German', 'Berlin', 'Munich'],
    'France': ['France', 'French', 'Paris', 'Macron'],
    'Haiti': ['Haiti', 'Haitian', 'Port-au-Prince'],
    'Somalia': ['Somalia', 'Somali', 'Mogadishu', 'al-Shabaab'],
    'Afghanistan': ['Afghanistan', 'Afghan', 'Kabul', 'Taliban'],
    'Pakistan': ['Pakistan', 'Pakistani', 'Islamabad', 'Karachi'],
    'Nigeria': ['Nigeria', 'Nigerian', 'Lagos', 'Abuja'],
    'South Africa': ['South Africa', 'South African', 'Johannesburg', 'Cape Town'],
    'Brazil': ['Brazil', 'Brazilian', 'Brasilia', 'São Paulo'],
    'Mexico': ['Mexico', 'Mexican', 'Mexico City', 'AMLO'],
}

def filter_by_location(articles, countries=None):
    if not countries:
        return articles

    print(f"Filtering {len(articles)} articles for countries: {countries}")  # Debug

    filtered = []
    for article in articles:
        content = f"{article['title']} {article['summary']}".lower()

        for country in countries:
            found = False

            # Direct country name match (case insensitive)
            if country.lower() in content:
                if article not in filtered:
                    filtered.append(article)
                    try:
                        print(f"Found '{country}' in: {article['title'][:50]}...")
                    except UnicodeEncodeError:
                        print(f"Found '{country}' in article (unicode title)")
                    found = True
                    break

            # Check keyword aliases if available
            if not found and country in LOCATION_KEYWORDS:
                keywords = LOCATION_KEYWORDS[country]
                for keyword in keywords:
                    if keyword.lower() in content:
                        if article not in filtered:
                            filtered.append(article)
                            try:
                                print(f"Found '{keyword}' (alias for {country}) in: {article['title'][:50]}...")
                            except UnicodeEncodeError:
                                print(f"Found '{keyword}' (alias for {country}) in article (unicode title)")
                            found = True
                            break
                if found:
                    break

    print(f"Filtered down to {len(filtered)} articles")
    return filtered

def fetch_articles(limit=30):  # Increased limit to 30 articles per source
    import socket
    socket.setdefaulttimeout(5)  # Set 5 second timeout for feeds

    sources_data = load_sources()
    all_articles = []

    print(f"Fetching from {len(sources_data['sources'])} sources...")  # Debug
    active_sources = [s for s in sources_data['sources'] if s.get('active', True) and s['url'] not in sources_data.get('blacklist', [])]
    print(f"Active sources: {len(active_sources)}")

    # Process all active sources (removed temporary limit)
    for source in active_sources:
        try:
            print(f"Fetching {source['name']}...")  # Debug

            # Add timeout to prevent hanging
            feed = feedparser.parse(source['url'])

            if hasattr(feed, 'status') and feed.status >= 400:
                print(f"HTTP error {feed.status} for {source['name']}")
                continue

            if hasattr(feed, 'bozo_exception'):
                print(f"Feed parse warning for {source['name']}: {feed.bozo_exception}")

            article_count = 0
            for entry in feed.entries[:limit]:
                # Get summary or description
                summary = ''
                if hasattr(entry, 'summary'):
                    summary = entry.summary
                elif hasattr(entry, 'description'):
                    summary = entry.description

                # Clean HTML and preserve full content
                if summary:
                    summary = BeautifulSoup(summary, 'html.parser').get_text()
                    # Keep full summary but truncate at sentence boundary
                    if len(summary) > 1000:
                        # Find last complete sentence within 1000 chars
                        summary = summary[:1000]
                        last_period = summary.rfind('. ')
                        if last_period > 0:
                            summary = summary[:last_period + 1]

                article = {
                    'title': entry.get('title', 'No title'),
                    'summary': summary,
                    'link': entry.get('link', '#'),
                    'source': source['name'],
                    'type': source.get('type', 'general'),
                    'published': entry.get('published', entry.get('updated', '')),
                }
                all_articles.append(article)
                article_count += 1

            if article_count > 0:
                print(f"[OK] Got {article_count} articles from {source['name']}")
            else:
                print(f"[SKIP] No articles from {source['name']}")
        except Exception as e:
            print(f"[ERROR] Error fetching {source['name']}: {str(e)[:100]}")

    print(f"Total articles collected: {len(all_articles)}")
    return all_articles

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/fetch_news', methods=['POST'])
def fetch_news():
    data = request.json
    countries = data.get('countries', [])
    report_type = data.get('report_type', 'list')  # 'list' or 'synthesized'

    # Initialize Google News Engine
    google_engine = GoogleNewsEngine()

    # Start with RSS feeds if we still want them
    articles = fetch_articles()

    # If searching for specific countries, use Google News for comprehensive coverage
    if countries:
        print(f"\nSearching Google News for: {', '.join(countries)}")

        for country in countries:
            # Get comprehensive news from Google - works exactly like searching on Google.com
            print(f"\nGetting news for {country}...")

            # Get general country news AND security-focused news in one go
            country_articles = google_engine.get_country_news(country, days_back=7)

            print(f"  Found {len(country_articles)} articles from Google News")

            # Convert to our format
            for article in country_articles:
                articles.append({
                    'title': article['title'],
                    'link': article['link'],
                    'summary': article.get('summary', article['title']),
                    'source': article.get('source', 'Google News'),
                    'location': [country],
                    'published': article['published']
                })

        # Filter for the country (removes duplicates)
        articles = filter_by_location(articles, countries)

    else:
        # No specific countries - get breaking security news
        print("\nGetting global breaking security news...")
        breaking_articles = google_engine.get_breaking_security_news(hours_back=24)

        print(f"  Found {len(breaking_articles)} breaking security articles")

        for article in breaking_articles:
            articles.append({
                'title': article['title'],
                'link': article['link'],
                'summary': article.get('summary', article['title']),
                'source': article.get('source', 'Google News'),
                'location': [],
                'published': article['published']
            })

    # Generate synthesized report if requested
    if report_type == 'synthesized' and countries:
        synthesizer = IntelligenceSynthesizer()
        country_reports = synthesizer.synthesize_by_country(articles, countries)

        # Add historical intelligence for each country
        intel = CountryIntelligence()
        for country in countries:
            if country in country_reports:
                print(f"Fetching historical context for {country}...")
                historical_data = intel.get_historical_context(country)
                country_reports[country]['historical_context'] = {
                    'basic_facts': historical_data.get('key_facts', []),
                    'summary': historical_data.get('historical_summary', '')[:500],
                    'references': historical_data.get('reference_urls', {}),
                    'capital': historical_data.get('basic_info', {}).get('capital', 'Unknown'),
                    'population': historical_data.get('basic_info', {}).get('population', 0),
                    'government': historical_data.get('basic_info', {}).get('government_type', 'Unknown')
                }

        # Try Fast LLM synthesis with real content
        if llm_available:
            try:
                # Use the fast synthesizer that extracts real content
                fast_synth = FastLLMSynthesizer()
                for country, data in country_reports.items():
                    print(f"Generating narrative with real article content for {country}...")
                    result = fast_synth.synthesize_country_report(country, data['articles'])
                    data['narrative'] = result['narrative']
                    # CRITICAL: Store articles with content for chat
                    data['articles_with_content'] = result['articles_with_content']
                    # Generate chat context with real content
                    data['chat_context'] = generate_chat_context(country, result['articles_with_content'])
            except NameError:
                # Fall back to old LLM synthesizer if fast one not available
                try:
                    llm_synth = LLMSynthesizer()
                    for country, data in country_reports.items():
                        print(f"Using fallback LLM synthesis for {country}...")
                        data['narrative'] = llm_synth.synthesize_country_report(country, data['articles'])
                except Exception as e:
                    print(f"All LLM synthesis failed: {e}, using basic narrative")
                    narrative_gen = NarrativeGenerator()
                    for country, data in country_reports.items():
                        data['narrative'] = narrative_gen.generate_country_narrative(country, data['articles'])
        else:
            narrative_gen = NarrativeGenerator()
            for country, data in country_reports.items():
                data['narrative'] = narrative_gen.generate_country_narrative(country, data['articles'])

        return jsonify({
            'report_type': 'synthesized',
            'country_reports': {
                country: {
                    'narrative': data['narrative'],
                    'executive_summary': synthesizer.generate_executive_summary(country, data),
                    'threat_level': synthesizer.assess_threat_level(data),
                    'key_points': synthesizer.extract_key_points(data['articles']),
                    'article_count': len(data['articles']),
                    'sources': list(data['sources']),
                    'themes': {
                        theme: len(articles_list)
                        for theme, articles_list in data['themes'].items()
                    },
                    'detailed_articles': data['articles'][:10],  # Include first 10 for reference
                    'historical_context': data.get('historical_context', {})  # Include historical intelligence
                }
                for country, data in country_reports.items()
            },
            'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'total_articles': len(articles)
        })

    return jsonify({
        'report_type': 'list',
        'articles': articles,
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'count': len(articles)
    })

@app.route('/api/sources', methods=['GET'])
def get_sources():
    return jsonify(load_sources())

@app.route('/api/sources', methods=['POST'])
def add_source():
    data = request.json
    sources_data = load_sources()

    # Generate new ID
    new_id = max([s['id'] for s in sources_data['sources']], default=0) + 1

    new_source = {
        'id': new_id,
        'name': data['name'],
        'url': data['url'],
        'type': data.get('type', 'general'),
        'active': True
    }

    sources_data['sources'].append(new_source)
    save_sources(sources_data)

    return jsonify({'success': True, 'source': new_source})

@app.route('/api/sources/<int:source_id>', methods=['DELETE'])
def delete_source(source_id):
    sources_data = load_sources()
    sources_data['sources'] = [s for s in sources_data['sources'] if s['id'] != source_id]
    save_sources(sources_data)
    return jsonify({'success': True})

@app.route('/api/sources/<int:source_id>/toggle', methods=['POST'])
def toggle_source(source_id):
    sources_data = load_sources()
    for source in sources_data['sources']:
        if source['id'] == source_id:
            source['active'] = not source.get('active', True)
            save_sources(sources_data)
            return jsonify({'success': True, 'active': source['active']})
    return jsonify({'success': False})

@app.route('/api/sources/<int:source_id>/blacklist', methods=['POST'])
def blacklist_source(source_id):
    sources_data = load_sources()
    for source in sources_data['sources']:
        if source['id'] == source_id:
            if source['url'] not in sources_data.get('blacklist', []):
                if 'blacklist' not in sources_data:
                    sources_data['blacklist'] = []
                sources_data['blacklist'].append(source['url'])
                save_sources(sources_data)
                return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/countries', methods=['GET'])
def get_countries():
    return jsonify(COUNTRIES)

@app.route('/api/historical', methods=['POST'])
def get_historical_context():
    """Get historical context for a country"""
    data = request.json
    country = data.get('country')

    if not country:
        return jsonify({'error': 'Country name required'}), 400

    try:
        intel = CountryIntelligence()
        historical_data = intel.get_historical_context(country)
        briefing = intel.generate_briefing(country)

        return jsonify({
            'country': country,
            'briefing': briefing,
            'data': historical_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_analyst():
    """Chat with AI analyst about a specific country's situation"""
    data = request.json
    country = data.get('country')
    question = data.get('question')
    context = data.get('context', '')  # Previous reports/articles

    if not country or not question:
        return jsonify({'error': 'Country and question required'}), 400

    try:
        # Get historical/CIA Factbook data if asking about facts
        historical_context = ""
        if any(keyword in question.lower() for keyword in ['gdp', 'economy', 'population', 'capital', 'government', 'history', 'cia', 'factbook', 'facts']):
            try:
                intel = CountryIntelligence()
                historical_data = intel.get_historical_context(country)

                # Add relevant facts to context
                if historical_data.get('basic_info'):
                    info = historical_data['basic_info']
                    historical_context = f"\nCountry Facts:\n"
                    historical_context += f"- Capital: {info.get('capital', 'Unknown')}\n"
                    historical_context += f"- Population: {info.get('population', 0):,}\n"
                    historical_context += f"- Area: {info.get('area', 0):,} km²\n"
                    historical_context += f"- Government: {info.get('government_type', 'Unknown')}\n"
                    historical_context += f"- Languages: {', '.join(info.get('languages', [])[:3])}\n"

                    # Add CIA Factbook reference
                    if historical_data.get('reference_urls'):
                        cia_url = historical_data['reference_urls'].get('CIA World Factbook', '')
                        historical_context += f"\nCIA Factbook: {cia_url}\n"
            except:
                pass  # If historical fetch fails, continue without it

        # Initialize LLM
        if llm_available:
            from llm_synthesizer import LLMSynthesizer
            llm = LLMSynthesizer()

            # Create chat prompt
            if llm.use_gemini:
                from datetime import datetime
                current_date = datetime.now().strftime('%Y-%m-%d')
                prompt = f"""You are a concise intelligence analyst specializing in {country}.

TODAY'S DATE: {current_date}
IMPORTANT: Only call events "recent" if they happened within the last 7 days. Always include the specific date when mentioning events.

{historical_context}

Recent News:
{context[:1000]}

Question: {question}

Instructions:
- Answer in 2-3 short sentences maximum
- ALWAYS include specific dates when mentioning events
- Use simple bullet points (dash - not asterisk *)
- NO markdown formatting (no **, no *, no ###)
- Include specific facts and numbers when available
- Keep total response under 100 words
- Write in plain text only"""

                response = llm.model.generate_content(prompt)
                answer = response.text

            elif llm.use_openai:
                # OpenAI version
                messages = [
                    {"role": "system", "content": f"You are a concise intelligence analyst specializing in {country}. Answer in plain text only. NO markdown. Use dash (-) for bullets, not asterisks. Keep under 100 words."},
                    {"role": "user", "content": f"{historical_context}\n\nRecent News:\n{context[:1000]}\n\nQuestion: {question}\n\nAnswer in 2-3 sentences with facts. Use plain text only."}
                ]
                response = llm.openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=200  # Reduced from 500
                )
                answer = response.choices[0].message.content
            else:
                answer = "**Analysis:** Configure Gemini API in .env file for chat features."

            return jsonify({'answer': answer})

        else:
            return jsonify({'answer': '**Note:** Add GEMINI_API_KEY to .env file to enable chat.'})

    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': 'Failed to process question'}), 500

# Scheduled Reports API Endpoints
@app.route('/api/scheduled-reports', methods=['GET'])
def get_scheduled_reports():
    """Get all scheduled reports"""
    from scheduled_reports import ScheduledReport
    db = ScheduledReport()
    reports = db.get_all_reports()
    db.close()
    return jsonify(reports)

@app.route('/api/scheduled-reports', methods=['POST'])
def create_scheduled_report():
    """Create a new scheduled report"""
    from scheduled_reports import ScheduledReport

    data = request.json
    db = ScheduledReport()

    try:
        report_id = db.create_report(
            name=data['name'],
            countries=data['countries'],
            prompt=data.get('prompt', ''),
            schedule_type=data['schedule_type'],
            schedule_time=data['schedule_time'],
            timezone=data.get('timezone', 'America/New_York'),
            email_recipients=data.get('email_recipients', [])
        )
        db.close()
        return jsonify({'id': report_id, 'message': 'Report created successfully'}), 201
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/scheduled-reports/<int:report_id>', methods=['DELETE'])
def delete_scheduled_report(report_id):
    """Delete a scheduled report"""
    from scheduled_reports import ScheduledReport

    db = ScheduledReport()
    if db.delete_report(report_id):
        db.close()
        return jsonify({'message': 'Report deleted successfully'})
    else:
        db.close()
        return jsonify({'error': 'Report not found'}), 404

@app.route('/api/scheduled-reports/<int:report_id>/toggle', methods=['POST'])
def toggle_scheduled_report(report_id):
    """Toggle a scheduled report's active status"""
    from scheduled_reports import ScheduledReport

    db = ScheduledReport()
    if db.toggle_report(report_id):
        db.close()
        return jsonify({'message': 'Report toggled successfully'})
    else:
        db.close()
        return jsonify({'error': 'Report not found'}), 404

@app.route('/api/scheduled-reports/<int:report_id>/run', methods=['POST'])
def run_scheduled_report(report_id):
    """Manually run a scheduled report"""
    from report_scheduler import get_scheduler

    try:
        scheduler = get_scheduler()
        result = scheduler.run_report_now(report_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start the scheduler when the app starts
    from report_scheduler import get_scheduler
    scheduler = get_scheduler()
    scheduler.start()
    app.run(debug=True, port=5000)