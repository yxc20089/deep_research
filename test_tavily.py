"""Simple test script to verify Tavily integration."""
import os
from dotenv import load_dotenv
from tavily import TavilyClient

# Load environment variables
load_dotenv()

def test_tavily_search():
    """Test Tavily search functionality."""
    # Check if API key is set
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key or api_key == "your_tavily_api_key_here":
        print("❌ Error: TAVILY_API_KEY not set in .env file")
        print("\nTo get a Tavily API key:")
        print("1. Visit https://tavily.com")
        print("2. Sign up for a free account")
        print("3. Copy your API key")
        print("4. Add it to the .env file: TAVILY_API_KEY=your_actual_key")
        return False

    try:
        # Initialize Tavily client
        print("🔍 Initializing Tavily client...")
        client = TavilyClient(api_key=api_key)

        # Perform a simple search
        print("🌐 Performing test search: 'artificial intelligence'...")
        response = client.search(
            query="artificial intelligence",
            max_results=3
        )

        # Display results
        print("\n✅ Tavily search successful!")
        print(f"\n📊 Found {len(response.get('results', []))} results:")

        for i, result in enumerate(response.get('results', []), 1):
            print(f"\n{i}. {result.get('title', 'No title')}")
            print(f"   URL: {result.get('url', 'No URL')}")
            print(f"   Snippet: {result.get('content', 'No content')[:150]}...")

        print("\n✅ Tavily integration is working correctly!")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to .env if not already set")
        print("2. Run: uvx --refresh --from 'langgraph-cli[inmem]' --with-editable . --python 3.11 langgraph dev --allow-blocking")
        print("3. Open LangGraph Studio in your browser")
        print("4. Start asking research questions!")

        return True

    except Exception as e:
        print(f"❌ Error testing Tavily: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your TAVILY_API_KEY is correct in .env")
        print("2. Check your internet connection")
        print("3. Visit https://tavily.com to verify your account status")
        return False

if __name__ == "__main__":
    test_tavily_search()
