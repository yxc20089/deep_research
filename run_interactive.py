"""Interactive research runner with enhanced progress tracking."""
import asyncio
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.open_deep_research.deep_researcher import deep_researcher
from src.open_deep_research.configuration import Configuration

load_dotenv()

class ProgressTracker:
    """Track research progress and estimate completion time."""

    def __init__(self):
        self.start_time = time.time()
        self.steps = []
        self.current_step = None
        self.research_topics = []
        self.config = Configuration.from_runnable_config()

    def start_step(self, node_name: str, details: str = ""):
        """Start tracking a new step."""
        self.current_step = {
            "name": node_name,
            "details": details,
            "start_time": time.time()
        }

    def end_step(self):
        """End the current step."""
        if self.current_step:
            self.current_step["duration"] = time.time() - self.current_step["start_time"]
            self.steps.append(self.current_step)
            self.current_step = None

    def get_elapsed_time(self):
        """Get elapsed time as a formatted string."""
        elapsed = time.time() - self.start_time
        return str(timedelta(seconds=int(elapsed)))

    def estimate_remaining(self, current_iteration: int, max_iterations: int):
        """Estimate remaining time based on average step duration."""
        if not self.steps:
            return "calculating..."

        avg_duration = sum(s["duration"] for s in self.steps) / len(self.steps)
        remaining_steps = (max_iterations - current_iteration) * 3  # rough estimate
        estimated_seconds = remaining_steps * avg_duration

        return str(timedelta(seconds=int(estimated_seconds)))

    def get_progress_bar(self, current: int, total: int, width: int = 30):
        """Generate a progress bar."""
        filled = int(width * current / total)
        bar = "█" * filled + "░" * (width - filled)
        percentage = int(100 * current / total)
        return f"[{bar}] {percentage}%"


def extract_research_info(state):
    """Extract research information from state."""
    info = {
        "iteration": 0,
        "topics": [],
        "notes_count": 0
    }

    if "research_iterations" in state:
        info["iteration"] = state["research_iterations"]

    if "notes" in state:
        info["notes_count"] = len(state["notes"])

    if "research_topic" in state:
        info["topics"] = [state["research_topic"]]

    # Try to extract topics from supervisor messages
    if "supervisor_messages" in state:
        for msg in state["supervisor_messages"]:
            if hasattr(msg, "tool_calls"):
                for tc in msg.tool_calls:
                    if tc.get("name") == "ConductResearch":
                        topic = tc.get("args", {}).get("research_topic", "")
                        if topic:
                            info["topics"].append(topic[:100])

    return info


async def interactive_research(question: str, verbose: bool = False):
    """Run research with interactive clarification support and detailed progress."""
    print(f"\n{'='*80}")
    print(f"🔬 DEEP RESEARCH SESSION")
    print(f"{'='*80}")
    print(f"📝 Question: {question}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    config = Configuration.from_runnable_config()
    print(f"\n⚙️  Configuration:")
    print(f"   • Search API: {config.search_api.value}")
    print(f"   • Research Model: {config.research_model}")
    print(f"   • Max Concurrent Units: {config.max_concurrent_research_units}")
    print(f"   • Max Iterations: {config.max_researcher_iterations}")
    print(f"{'='*80}\n")

    messages = [{"role": "user", "content": question}]
    tracker = ProgressTracker()

    while True:
        state = {"messages": messages}
        final_state = None
        step_count = 0

        async for event in deep_researcher.astream(state, stream_mode="updates"):
            step_count += 1

            for node_name, node_state in event.items():
                tracker.start_step(node_name)

                # Extract information
                info = extract_research_info(node_state)

                # Determine node type and display appropriate info
                if node_name == "clarify_with_user":
                    print(f"\n{'─'*80}")
                    print(f"📋 STEP {step_count}: Clarifying Requirements")
                    print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    print(f"{'─'*80}")

                elif node_name == "create_research_brief":
                    print(f"\n{'─'*80}")
                    print(f"📝 STEP {step_count}: Creating Research Plan")
                    print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    print(f"{'─'*80}")

                elif node_name == "research_supervisor":
                    iteration = info["iteration"]
                    max_iter = config.max_researcher_iterations
                    progress_bar = tracker.get_progress_bar(iteration, max_iter)

                    print(f"\n{'─'*80}")
                    print(f"🎯 STEP {step_count}: Research Supervisor (Iteration {iteration}/{max_iter})")
                    print(f"   {progress_bar}")
                    print(f"⏱️  Elapsed: {tracker.get_elapsed_time()} | ETA: {tracker.estimate_remaining(iteration, max_iter)}")
                    print(f"📊 Notes Collected: {info['notes_count']}")

                    if info["topics"]:
                        print(f"\n🔍 Research Topics Assigned:")
                        for i, topic in enumerate(info["topics"][-3:], 1):  # Show last 3
                            print(f"   {i}. {topic[:100]}...")
                    print(f"{'─'*80}")

                elif "researcher" in node_name.lower():
                    print(f"\n{'─'*80}")
                    print(f"🔎 STEP {step_count}: Researcher Working")

                    if info["topics"]:
                        print(f"📌 Topic: {info['topics'][0][:150]}...")

                    # Show tool call iterations if available
                    if "tool_call_iterations" in node_state:
                        tool_iter = node_state["tool_call_iterations"]
                        max_tool_iter = config.max_react_tool_calls
                        tool_progress = tracker.get_progress_bar(tool_iter, max_tool_iter, width=20)
                        print(f"🔧 Tool Calls: {tool_progress} ({tool_iter}/{max_tool_iter})")

                    print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    print(f"{'─'*80}")

                elif node_name == "compress_research":
                    print(f"\n{'─'*80}")
                    print(f"📦 STEP {step_count}: Compressing Research Findings")
                    print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    print(f"📊 Notes to Compress: {info['notes_count']}")
                    print(f"{'─'*80}")

                elif node_name == "write_report":
                    print(f"\n{'─'*80}")
                    print(f"📄 STEP {step_count}: Writing Final Report")
                    print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    print(f"📊 Using {info['notes_count']} research notes")
                    print(f"{'─'*80}")

                tracker.end_step()
                final_state = node_state

        # Check if there's a clarification question
        if final_state and "messages" in final_state:
            last_message = final_state["messages"][-1]

            if hasattr(last_message, "content"):
                content = last_message.content

                # Check if it's asking for clarification
                if isinstance(content, str) and "?" in content and len(content) < 500:
                    print(f"\n{'='*80}")
                    print("💬 CLARIFICATION NEEDED")
                    print(f"{'='*80}\n")
                    print(content)
                    print(f"\n{'='*80}")

                    # Get user response
                    response = input("\n👉 Your response (or press Enter to continue): ").strip()

                    if response:
                        messages.append({"role": "assistant", "content": content})
                        messages.append({"role": "user", "content": response})
                        print("\n📝 Continuing research with your clarification...\n")
                        tracker = ProgressTracker()  # Reset tracker
                        continue
                    else:
                        print("\n⏭️  Proceeding with comprehensive research...\n")
                        messages.append({"role": "assistant", "content": content})
                        messages.append({"role": "user", "content": "Please proceed with comprehensive research on all aspects."})
                        tracker = ProgressTracker()  # Reset tracker
                        continue

                # Otherwise, it's the final report
                print(f"\n{'='*80}")
                print("✅ RESEARCH COMPLETE")
                print(f"{'='*80}")
                print(f"⏱️  Total Time: {tracker.get_elapsed_time()}")
                print(f"📊 Total Steps: {len(tracker.steps)}")
                print(f"{'='*80}\n")
                print(content)
                print(f"\n{'='*80}")
                return content

        print("\n⚠️  No report generated. Something went wrong.")
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
        print("="*80)
        print("\nUsage: python run_interactive.py 'Your question' [--verbose]")
        print("\nExample:")
        print("  python run_interactive.py 'How could Kongming win in The Three Kingdoms?'")
        print("  python run_interactive.py 'Latest AI trends' --verbose")

if __name__ == "__main__":
    main()
