#!/bin/bash
# Quick start script for Deep Research with Tavily

echo "🚀 Starting Deep Research with Tavily..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ .env file created. Please add your API keys before continuing."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "📦 Virtual environment not found. Creating..."
    uv venv
    source .venv/bin/activate
    echo "📥 Installing dependencies..."
    uv pip install -e .
else
    source .venv/bin/activate
fi

echo ""
echo "🔍 Checking API keys..."
if grep -q "your_tavily_api_key_here" .env; then
    echo "⚠️  TAVILY_API_KEY not configured in .env"
    echo "   Get your key at: https://tavily.com"
fi

if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  OPENAI_API_KEY not configured in .env"
    echo "   Get your key at: https://platform.openai.com"
fi

echo ""
echo "🧪 Testing Tavily connection..."
python test_tavily.py

echo ""
echo "🎯 To start the LangGraph server, run:"
echo "   uvx --refresh --from 'langgraph-cli[inmem]' --with-editable . --python 3.11 langgraph dev --allow-blocking"
echo ""
echo "📚 Or read the README.md for more options"
