"""Run deep research locally without LangGraph Studio UI."""
import asyncio
import sys
from dotenv import load_dotenv
from src.open_deep_research.deep_researcher import deep_researcher
from src.open_deep_research.configuration import Configuration

# Load environment variables
load_dotenv()

async def run_research(question: str):
    """Run a research query and print results."""
    print(f"\n🔬 Starting Deep Research on: '{question}'")
    print("=" * 80)

    # Create initial state
    initial_state = {
        "messages": [{"role": "user", "content": question}]
    }

    # Run the graph
    print("\n🚀 Running research agent...\n")

    try:
        final_state = None
        async for event in deep_researcher.astream(
            initial_state,
            stream_mode="updates"
        ):
            # Print updates as they come in
            for node_name, node_state in event.items():
                print(f"\n📍 Node: {node_name}")

                # Print messages if available
                if "messages" in node_state and node_state["messages"]:
                    for msg in node_state["messages"]:
                        if hasattr(msg, "content"):
                            content = msg.content
                            if isinstance(content, str) and len(content) > 200:
                                print(f"   {content[:200]}...")
                            else:
                                print(f"   {content}")

                final_state = node_state

        # Print final report
        print("\n" + "=" * 80)
        print("📊 FINAL RESEARCH REPORT")
        print("=" * 80 + "\n")

        if final_state and "messages" in final_state:
            for msg in final_state["messages"]:
                if hasattr(msg, "content") and isinstance(msg.content, str):
                    print(msg.content)
                    print()

        print("\n✅ Research completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during research: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        print("🔬 Deep Research - Local Runner")
        print("=" * 80)
        print("\nEnter your research question (or 'quit' to exit):")
        question = input("\n> ").strip()

        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            return

    if not question:
        print("❌ No question provided. Usage:")
        print("   python run_research.py 'Your research question here'")
        print("   OR run without arguments for interactive mode")
        return

    # Run the async function
    asyncio.run(run_research(question))

if __name__ == "__main__":
    main()
