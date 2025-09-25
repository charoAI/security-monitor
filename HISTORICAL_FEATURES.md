# Historical Intelligence Features

## Overview
The security monitoring system now includes comprehensive historical context and reference data for all countries, providing deeper intelligence analysis capabilities.

## Data Sources Integrated

### 1. REST Countries API
- **Data Provided**: Basic country facts
  - Official and common names
  - Capital cities
  - Population statistics
  - Geographic data (area, borders, coordinates)
  - Languages and currencies
  - Government type
  - UN membership status
  - Timezones

### 2. Wikipedia API
- **Data Provided**: Historical summaries
  - Country overview and description
  - Historical narrative extract
  - Links to detailed Wikipedia articles
  - Historical timeline sections

### 3. CIA World Factbook (Reference Links)
- **Data Provided**: Direct links to comprehensive country profiles
  - Detailed historical background
  - Government and politics
  - Economy and infrastructure
  - Security and military
  - Transnational issues

### 4. Additional Reference Sources
- BBC Country Profiles
- UN Data Portal
- World Bank Data
- Regional news sources

## Key Features

### Universal Country Coverage
- Works for ALL 195 countries automatically
- No need to manually configure data sources
- Dynamic fetching of historical context on demand

### Historical Context Integration
When generating reports, the system now includes:
- Basic country facts (capital, population, government)
- Historical summary (up to 500 characters)
- Reference URLs for deeper research
- Government structure information

### Enhanced Intelligence Analysis
The system combines:
- **Historical Data**: Background, key facts, references
- **Current News**: 100+ articles per country from Google News
- **Contextual Analysis**: Links current events to historical patterns

## API Endpoints

### `/api/historical` (POST)
Get historical context for any country:
```json
{
  "country": "Haiti"
}
```

Returns:
- Complete historical briefing
- Basic facts
- Reference URLs
- Historical timeline structure

### Enhanced `/api/fetch_news` (POST)
Now includes historical context in synthesized reports:
```json
{
  "countries": ["Haiti"],
  "report_type": "synthesized"
}
```

Returns news PLUS:
- Historical context
- Basic country facts
- Reference sources
- Government information

## Usage Examples

### 1. Historical Context Query
User: "What is the historical background of Haiti?"
System provides:
- Colonial history (French colony, slave revolt)
- Independence (1804, first black republic)
- Political instability patterns
- Previous international interventions

### 2. Current Events Analysis
User: "Why is Haiti experiencing gang violence?"
System provides:
- Current news (100+ articles)
- Historical context of weak institutions
- Pattern of political instability
- Previous security crises

### 3. Reference Research
User: "I need authoritative sources on Somalia"
System provides:
- CIA World Factbook link
- Wikipedia comprehensive article
- BBC Country Profile
- UN and World Bank data portals

## Benefits

1. **Comprehensive Intelligence**: Combines historical context with current events
2. **Universal Coverage**: Works for any country without configuration
3. **Authoritative Sources**: Links to CIA, UN, World Bank data
4. **Contextual Understanding**: Historical patterns inform current analysis
5. **Research Ready**: Multiple reference sources for deeper investigation

## Technical Implementation

### Caching
- Historical data is cached to reduce API calls
- Cache refreshes periodically for updated information

### Error Handling
- Graceful fallback if APIs are unavailable
- Alternative data sources attempted automatically

### Performance
- Asynchronous fetching where possible
- Lightweight API calls (REST Countries, Wikipedia)
- No API keys required for basic functionality

## Future Enhancements

Potential additions:
- UCDP conflict database integration
- World Bank economic indicators
- Freedom House democracy scores
- Global Terrorism Database
- Historical leader database
- Treaty and alliance information

## Testing

Run tests:
```bash
python test_historical_integration.py
python country_intelligence.py
```

These demonstrate:
- Fetching historical data for any country
- Combining with current news
- Generating comprehensive briefings
- Reference source compilation