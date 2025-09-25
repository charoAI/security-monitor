# Comprehensive list of reliable RSS feeds for security and geopolitical news

DEFAULT_SOURCES = [
    # Major News Outlets - Global Coverage
    {'name': 'BBC World', 'url': 'http://feeds.bbci.co.uk/news/world/rss.xml', 'type': 'news', 'active': True},
    {'name': 'Reuters World News', 'url': 'https://feeds.reuters.com/Reuters/worldNews', 'type': 'news', 'active': True},
    {'name': 'Al Jazeera', 'url': 'https://www.aljazeera.com/xml/rss/all.xml', 'type': 'news', 'active': True},
    {'name': 'CNN World', 'url': 'http://rss.cnn.com/rss/cnn_world.rss', 'type': 'news', 'active': True},
    {'name': 'Guardian World', 'url': 'https://www.theguardian.com/world/rss', 'type': 'news', 'active': True},
    {'name': 'AP News', 'url': 'https://feeds.apnews.com/rss/apf-topnews', 'type': 'news', 'active': True},
    
    # Security Focused
    {'name': 'Krebs on Security', 'url': 'https://krebsonsecurity.com/feed/', 'type': 'cyber', 'active': True},
    {'name': 'The Hacker News', 'url': 'https://feeds.feedburner.com/TheHackersNews', 'type': 'cyber', 'active': True},
    {'name': 'Schneier on Security', 'url': 'https://www.schneier.com/blog/atom.xml', 'type': 'analysis', 'active': True},
    {'name': 'Dark Reading', 'url': 'https://www.darkreading.com/rss.xml', 'type': 'cyber', 'active': True},
    {'name': 'Threatpost', 'url': 'https://threatpost.com/feed/', 'type': 'cyber', 'active': True},
    {'name': 'BleepingComputer', 'url': 'https://www.bleepingcomputer.com/feed/', 'type': 'cyber', 'active': True},
    
    # Geopolitical & Conflict
    {'name': 'Bellingcat', 'url': 'https://www.bellingcat.com/feed/', 'type': 'geopolitical', 'active': True},
    {'name': 'War on the Rocks', 'url': 'https://warontherocks.com/feed/', 'type': 'geopolitical', 'active': True},
    {'name': 'Foreign Affairs', 'url': 'https://www.foreignaffairs.com/rss', 'type': 'geopolitical', 'active': True},
    {'name': 'Defense One', 'url': 'https://www.defenseone.com/rss/', 'type': 'geopolitical', 'active': True},
    {'name': 'Stratfor', 'url': 'https://worldview.stratfor.com/feed', 'type': 'geopolitical', 'active': True},
    
    # Government Sources
    {'name': 'CISA Alerts', 'url': 'https://www.cisa.gov/uscert/ncas/alerts.xml', 'type': 'government', 'active': True},
    {'name': 'US State Dept', 'url': 'https://www.state.gov/rss-feed/press-releases/feed/', 'type': 'government', 'active': True},
    
    # Regional Focus
    {'name': 'Kyiv Independent', 'url': 'https://kyivindependent.com/feed/', 'type': 'news', 'active': True},
    {'name': 'Moscow Times', 'url': 'https://www.themoscowtimes.com/rss/news', 'type': 'news', 'active': True},
    {'name': 'Times of Israel', 'url': 'https://www.timesofisrael.com/feed/', 'type': 'news', 'active': True},
    {'name': 'South China Morning Post', 'url': 'https://www.scmp.com/rss/91/feed', 'type': 'news', 'active': True},
]