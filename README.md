# Deep Research

A deep research agent powered by LangGraph and Tavily web search. This project is based on LangChain's Open Deep Research and configured to use Tavily as the primary search engine.

## Features

- **Automated Research**: AI-powered research agent that conducts deep research on any topic
- **Tavily Integration**: Uses Tavily's powerful web search API for finding and extracting relevant information
- **Parallel Processing**: Multiple research units work concurrently for faster results
- **Comprehensive Reports**: Generates well-structured, cited research reports
- **Configurable**: Supports multiple LLM providers (OpenAI, Anthropic, Google, etc.)

## Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip
- API Keys:
  - Tavily API key (required for web search)
  - OpenAI API key (default LLM provider) or other supported providers

## Quick Start

### 1. Clone or navigate to the project directory

```bash
cd deep_research
```

### 2. Set up environment variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
TAVILY_API_KEY=your_tavily_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # or other LLM provider
```

**Get your Tavily API key**: Sign up at [https://tavily.com](https://tavily.com) to get a free API key.

### 3. Create a virtual environment and install dependencies

Using UV (recommended):
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

Or using pip:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 4. Run the research agent

Start the LangGraph development server:

```bash
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking
```

This will start the server and open LangGraph Studio in your browser:
- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs

### 5. Test the search

In LangGraph Studio:
1. Enter a research question in the `messages` input field
2. Click `Submit`
3. Watch as the agent searches the web using Tavily and compiles a comprehensive report

## Configuration

The agent is configured to use Tavily search by default. You can customize various settings in the configuration:

- **Search API**: Tavily (default), OpenAI native search, Anthropic native search
- **Models**: Configure different models for summarization, research, compression, and final report
- **Concurrency**: Adjust the number of parallel research units
- **Iterations**: Set maximum research iterations

Access configuration through:
- Environment variables in `.env`
- LangGraph Studio UI (Manage Assistants tab)
- Direct modification of `src/open_deep_research/configuration.py`

## Project Structure

```
deep_research/
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── langgraph.json       # LangGraph configuration
├── pyproject.toml       # Python project dependencies
├── README.md            # This file
└── src/
    └── open_deep_research/
        ├── configuration.py  # Configuration management
        ├── deep_researcher.py # Main LangGraph implementation
        ├── prompts.py       # System prompts
        ├── state.py         # Graph state definitions
        └── utils.py         # Utility functions
```

## How It Works

1. **User Query**: You provide a research question
2. **Planning**: The agent analyzes the question and creates research sub-topics
3. **Parallel Research**: Multiple research units search the web using Tavily in parallel
4. **Summarization**: Results are summarized and consolidated
5. **Reflection**: The agent reflects on findings and conducts additional searches if needed
6. **Report Generation**: A comprehensive, cited report is generated

## Troubleshooting

### No API Key Error
Make sure you've set `TAVILY_API_KEY` in your `.env` file.

### Rate Limits
If you encounter rate limits, reduce `max_concurrent_research_units` in the configuration.

### Model Not Found
Ensure your LLM provider API key is set correctly in `.env`.

## Credits

Based on [LangChain's Open Deep Research](https://github.com/langchain-ai/open_deep_research) project.

## License

MIT License
