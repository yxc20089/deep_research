"""Interactive research runner with clarification support."""
import asyncio
import sys
from dotenv import load_dotenv
from src.open_deep_research.deep_researcher import deep_researcher

load_dotenv()

async def interactive_research(question: str, verbose: bool = False):
    """Run research with interactive clarification support."""
    print(f"\n🔬 Starting Research: {question}\n")

    messages = [{"role": "user", "content": question}]

    while True:
        state = {"messages": messages}
        final_state = None
        step_count = 0

        print("🚀 Running research agent...")
        if not verbose:
            print("Progress: ", end="", flush=True)

        async for event in deep_researcher.astream(state, stream_mode="updates"):
            step_count += 1
            for node_name, node_state in event.items():
                if verbose:
                    print(f"  [{step_count}] {node_name}")
                else:
                    print(".", end="", flush=True)
                final_state = node_state

        if not verbose:
            print("\n")

        # Check if there's a clarification question
        if final_state and "messages" in final_state:
            last_message = final_state["messages"][-1]

            if hasattr(last_message, "content"):
                content = last_message.content

                # Check if it's asking for clarification (contains question marks)
                if isinstance(content, str) and "?" in content and len(content) < 500:
                    print("\n" + "=" * 80)
                    print("💬 CLARIFICATION NEEDED")
                    print("=" * 80 + "\n")
                    print(content)
                    print("\n" + "=" * 80)

                    # Get user response
                    response = input("\nYour response (or press Enter to skip and continue): ").strip()

                    if response:
                        # Add the response and continue
                        messages.append({"role": "assistant", "content": content})
                        messages.append({"role": "user", "content": response})
                        print("\n📝 Continuing research with your clarification...\n")
                        continue
                    else:
                        print("\n⏭️  Skipping clarification and proceeding with research...\n")
                        # Skip clarification by providing a generic response
                        messages.append({"role": "assistant", "content": content})
                        messages.append({"role": "user", "content": "Please proceed with comprehensive research on all aspects."})
                        continue

                # Otherwise, it's the final report
                print("\n" + "=" * 80)
                print("📊 FINAL RESEARCH REPORT")
                print("=" * 80 + "\n")
                print(content)
                print("\n" + "=" * 80)
                return content

        # If we got here without finding a report, something went wrong
        print("\n⚠️  No report generated. Final state:")
        print(final_state)
        break

def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    args = [arg for arg in sys.argv[1:] if arg not in ["--verbose", "-v"]]

    if args:
        question = " ".join(args)
        asyncio.run(interactive_research(question, verbose))
    else:
        print("🔬 Interactive Deep Research")
        print("=" * 80)
        print("\nThis tool will run deep research and allow you to answer")
        print("clarification questions interactively.\n")
        print("Usage: python run_interactive.py 'Your question' [--verbose]")
        print("\nExample:")
        print("  python run_interactive.py 'How could Kongming win in The Three Kingdoms?'")
        print("  python run_interactive.py 'Latest AI trends' --verbose")

if __name__ == "__main__":
    main()
