"""Simplified research runner with cleaner output."""
import asyncio
import sys
from dotenv import load_dotenv
from src.open_deep_research.deep_researcher import deep_researcher
from src.open_deep_research.configuration import Configuration

load_dotenv()

async def research(question: str, verbose: bool = False):
    """Run research and return the final report."""
    print(f"\n🔬 Researching: {question}\n")

    initial_state = {"messages": [{"role": "user", "content": question}]}

    final_state = None
    step_count = 0

    async for event in deep_researcher.astream(
        initial_state,
        stream_mode="updates"
    ):
        step_count += 1
        for node_name, node_state in event.items():
            if verbose:
                print(f"  [{step_count}] {node_name}")
            else:
                print(".", end="", flush=True)
            final_state = node_state

    print("\n")

    # Extract and return final report
    if final_state and "messages" in final_state:
        for msg in final_state["messages"]:
            if hasattr(msg, "content") and isinstance(msg.content, str):
                # Return the last substantial message
                if len(msg.content) > 100:
                    return msg.content

    return "No report generated."

def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # Remove flags from args
    args = [arg for arg in sys.argv[1:] if arg not in ["--verbose", "-v"]]

    if args:
        question = " ".join(args)
        report = asyncio.run(research(question, verbose))
        print("\n" + "=" * 80)
        print("RESEARCH REPORT")
        print("=" * 80 + "\n")
        print(report)
    else:
        print("Usage: python run_research_simple.py 'Your question' [--verbose]")
        print("\nExample:")
        print("  python run_research_simple.py 'What is quantum computing?'")
        print("  python run_research_simple.py 'Latest AI trends' --verbose")

if __name__ == "__main__":
    main()
