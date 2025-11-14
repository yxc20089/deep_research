# Quick Start Guide

## 1. Get API Keys

### Tavily API Key (Required)
1. Go to https://tavily.com
2. Sign up for a free account
3. Copy your API key from the dashboard

### OpenAI API Key (Required)
1. Go to https://platform.openai.com
2. Create an account or sign in
3. Navigate to API keys section
4. Create a new API key

## 2. Configure Environment

Edit the `.env` file and add your keys:

```bash
TAVILY_API_KEY=tvly-your-actual-key-here
OPENAI_API_KEY=sk-your-actual-key-here
```

## 3. Test Tavily Connection

Run the test script to verify Tavily is working:

```bash
python test_tavily.py
```

You should see search results if everything is configured correctly.

## 4. Start the Research Agent

Launch the LangGraph server:

```bash
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking
```

Or use the start script:

```bash
./start.sh
```

## 5. Use the Agent

1. Open LangGraph Studio in your browser (URL will be displayed in terminal)
2. In the Studio UI, enter a research question like:
   - "What are the latest developments in quantum computing?"
   - "Explain the current state of renewable energy adoption"
   - "What are the key differences between GPT-4 and Claude 3?"
3. Click Submit and watch the agent research using Tavily!

## Troubleshooting

### "TAVILY_API_KEY not set"
- Make sure you edited `.env` (not `.env.example`)
- Verify the key starts with `tvly-`
- No quotes needed around the key

### "Rate limit exceeded"
- Reduce `max_concurrent_research_units` in configuration
- Wait a few moments and try again

### "Module not found"
- Make sure you installed dependencies: `uv pip install -e .`
- Activate virtual environment: `source .venv/bin/activate`

## Example Research Questions

- "What are the latest AI breakthroughs in 2025?"
- "Compare different approaches to climate change mitigation"
- "Explain the current state of space exploration"
- "What are emerging trends in cybersecurity?"

## Next Steps

- Read the full README.md for advanced configuration
- Explore different model providers (Anthropic, Google, etc.)
- Adjust research depth and concurrency settings
- Try MCP server integration for specialized tools
