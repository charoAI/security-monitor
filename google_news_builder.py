"""Generate Google News RSS feeds for specific topics/countries"""

def build_google_news_rss(query):
    """Build Google News RSS URL for a specific query"""
    import urllib.parse
    
    # Google News RSS format
    base_url = "https://news.google.com/rss/search"
    
    # Encode the query
    params = {
        'q': query,
        'hl': 'en-US',  # Language
        'gl': 'US',     # Country
        'ceid': 'US:en' # Country/Language pair
    }
    
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"

# Generate specific feeds
COUNTRY_SPECIFIC_FEEDS = {
    # Haiti-specific searches
    'Haiti Security': build_google_news_rss('Haiti gang violence security'),
    'Haiti Politics': build_google_news_rss('Haiti political crisis news'),
    'Haiti Crisis': build_google_news_rss('Haiti humanitarian crisis'),
    
    # Somalia-specific searches
    'Somalia Security': build_google_news_rss('Somalia al-Shabaab security'),
    'Somalia Politics': build_google_news_rss('Somalia government Mogadishu'),
    
    # Iraq-specific searches
    'Iraq Security': build_google_news_rss('Iraq ISIS security Baghdad'),
    'Iraq Politics': build_google_news_rss('Iraq government parliament'),
}

if __name__ == "__main__":
    print("Add these Google News feeds to your sources_config.json:")
    print()
    
    for name, url in COUNTRY_SPECIFIC_FEEDS.items():
        print(f'Name: Google News - {name}')
        print(f'URL: {url}')
        print()