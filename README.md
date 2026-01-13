# AI Research Assistant

A powerful AI-powered research assistant that combines intelligent query optimization, multi-source searching, and automated report generation.

## Features

- **LLM Query Optimization**: Uses Groq's LLM to convert natural language queries into optimized search terms
- **Multi-Source Research**: Performs multiple searches to gather comprehensive information
- **Citation Management**: Automatically extracts and includes citations from search results
- **Customizable Reports**: Generate short, medium, or long reports based on your needs
- **Multiple Interfaces**: Web UI (Streamlit), CLI, and Interactive agents
- **Comprehensive Logging**: Track all operations, searches, and errors with detailed logs

## Quick Start

### Web Application
```bash
streamlit run web_app.py
```

### CLI
```bash
python research_assistant.py
```

## Installation

1. Clone: `git clone https://github.com/jaingaurav1601/ai-research-assistant.git`
2. Install: `pip install -r requirements.txt`
3. Configure: Set `GROQ_API_KEY` in `.env` or Streamlit secrets

## Logging

All operations are logged to the `logs/` directory:
- `research_assistant.log` - Core research operations
- `streamlit_app.log` - Web app events

View logs: `tail -f logs/research_assistant.log`

Search logs: `grep "quantum tunneling" logs/research_assistant.log`

Filter by level: `grep "ERROR" logs/research_assistant.log`

## Testing

```bash
python test_research_assistant.py
```

Runs 22 comprehensive tests covering:
- Search functionality (6 tests)
- Report generation (5 tests) 
- Research workflows (5 tests)
- Special queries like quantum tunneling (4 tests)
- Error handling (2 tests)

## Architecture

```
AI Research Assistant
├── research_assistant.py    # Core engine
├── web_app.py              # Streamlit UI  
├── logging_config.py       # Logging setup
├── test_research_assistant.py  # Tests (22 tests)
├── requirements.txt        # Dependencies
└── logs/                   # Generated logs
    ├── research_assistant.log
    └── streamlit_app.log
```

## Report Customization

- **Short**: 300 tokens, quick overview
- **Medium**: 700 tokens, balanced detail
- **Long**: 1200 tokens, comprehensive analysis

## Troubleshooting

### Missing API Key
Set `GROQ_API_KEY` in `.env` or Streamlit secrets

### Search Returns No Results
Try a more specific term or use the web app for automatic optimization

### Log Files Growing
Logs rotate daily and are stored in `logs/` directory

## Security

✅ API keys in environment variables  
✅ No hardcoded credentials  
✅ User agent headers for API requests  
✅ Timeout protection on network requests

## Performance

- Multi-query searches: 2-5 seconds
- Report generation: <5 seconds
- Efficient memory usage
- No rate limits (DuckDuckGo)

## License

See LICENSE file
