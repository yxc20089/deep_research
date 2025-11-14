"""Interactive research runner with enhanced progress tracking."""
import asyncio
import sys
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from src.open_deep_research.deep_researcher import deep_researcher
from src.open_deep_research.configuration import Configuration

load_dotenv()

class OutputLogger:
    """Log output to both console and file."""

    def __init__(self, log_dir="research_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"research_{timestamp}.log"
        self.report_file = None

    def print(self, message="", to_file=True, to_console=True):
        """Print to both console and file."""
        if to_console:
            print(message)
        if to_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                # Strip ANSI color codes for file output
                clean_msg = message.replace("═", "=").replace("─", "-")
                clean_msg = clean_msg.replace("█", "#").replace("░", "-")
                f.write(clean_msg + "\n")

    def save_report(self, question: str, report: str):
        """Save the final report to a separate file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create safe filename from question
        safe_question = "".join(c if c.isalnum() or c in " _-" else "_" for c in question)
        safe_question = safe_question[:50]  # Limit length

        self.report_file = self.log_dir / f"report_{timestamp}_{safe_question}.md"

        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(f"# Research Report\n\n")
            f.write(f"**Question:** {question}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(report)

        return self.report_file

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
    logger = OutputLogger()

    logger.print(f"\n{'='*80}")
    logger.print(f"🔬 DEEP RESEARCH SESSION")
    logger.print(f"{'='*80}")
    logger.print(f"📝 Question: {question}")
    logger.print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    config = Configuration.from_runnable_config()
    logger.print(f"\n⚙️  Configuration:")
    logger.print(f"   • Search API: {config.search_api.value}")
    logger.print(f"   • Research Model: {config.research_model}")
    logger.print(f"   • Max Concurrent Units: {config.max_concurrent_research_units}")
    logger.print(f"   • Max Iterations: {config.max_researcher_iterations}")
    logger.print(f"📁 Log file: {logger.log_file}")
    logger.print(f"{'='*80}\n")

    messages = [{"role": "user", "content": question}]
    tracker = ProgressTracker()

    overall_step_count = 0  # Track across all iterations

    while True:
        state = {"messages": messages}
        final_state = None

        async for event in deep_researcher.astream(state, stream_mode="updates"):
            overall_step_count += 1

            for node_name, node_state in event.items():
                tracker.start_step(node_name)

                # Extract information
                info = extract_research_info(node_state)

                # Determine node type and display appropriate info
                if node_name == "clarify_with_user":
                    logger.print(f"\n{'─'*80}")
                    logger.print(f"📋 STEP {overall_step_count}: Clarifying Requirements")
                    logger.print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    logger.print(f"{'─'*80}")

                elif node_name == "write_research_brief":
                    logger.print(f"\n{'─'*80}")
                    logger.print(f"📝 STEP {overall_step_count}: Creating Research Plan")
                    logger.print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    logger.print(f"{'─'*80}")

                elif node_name == "research_supervisor":
                    iteration = info["iteration"]
                    max_iter = config.max_researcher_iterations
                    progress_bar = tracker.get_progress_bar(iteration, max_iter)

                    logger.print(f"\n{'─'*80}")
                    logger.print(f"🎯 STEP {overall_step_count}: Research Supervisor (Iteration {iteration}/{max_iter})")
                    logger.print(f"   {progress_bar}")
                    logger.print(f"⏱️  Elapsed: {tracker.get_elapsed_time()} | ETA: {tracker.estimate_remaining(iteration, max_iter)}")
                    logger.print(f"📊 Notes Collected: {info['notes_count']}")

                    if info["topics"]:
                        logger.print(f"\n🔍 Research Topics Assigned ({len(info['topics'])} topics):")
                        for i, topic in enumerate(info["topics"][-5:], 1):  # Show last 5
                            logger.print(f"   {i}. {topic[:120]}...")
                    logger.print(f"{'─'*80}")

                elif "researcher" in node_name.lower():
                    # Extract researcher number/ID from node name if possible
                    researcher_id = node_name.replace("researcher_", "").replace("researcher", "")

                    logger.print(f"\n{'─'*80}")
                    logger.print(f"🔎 STEP {overall_step_count}: Researcher{' ' + researcher_id if researcher_id else ''} Working")

                    if info["topics"]:
                        logger.print(f"📌 Topic: {info['topics'][0][:180]}...")

                    # Show tool call iterations if available
                    if "tool_call_iterations" in node_state:
                        tool_iter = node_state["tool_call_iterations"]
                        max_tool_iter = config.max_react_tool_calls
                        tool_progress = tracker.get_progress_bar(tool_iter, max_tool_iter, width=20)
                        logger.print(f"🔧 Tool Calls: {tool_progress} ({tool_iter}/{max_tool_iter})")

                    logger.print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    logger.print(f"{'─'*80}")

                elif node_name == "compress_research":
                    logger.print(f"\n{'─'*80}")
                    logger.print(f"📦 STEP {overall_step_count}: Compressing Research Findings")
                    logger.print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    logger.print(f"📊 Notes to Compress: {info['notes_count']}")
                    logger.print(f"{'─'*80}")

                elif node_name == "write_report":
                    logger.print(f"\n{'─'*80}")
                    logger.print(f"📄 STEP {overall_step_count}: Writing Final Report")
                    logger.print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    logger.print(f"📊 Using {info['notes_count']} research notes")
                    logger.print(f"{'─'*80}")

                else:
                    # Log any other nodes we haven't explicitly handled
                    logger.print(f"\n{'─'*80}")
                    logger.print(f"⚙️  STEP {overall_step_count}: {node_name}")
                    logger.print(f"⏱️  Elapsed: {tracker.get_elapsed_time()}")
                    logger.print(f"{'─'*80}")

                tracker.end_step()
                final_state = node_state

        # Check if the graph ended (clarification or completion)
        if final_state and "messages" in final_state:
            last_message = final_state["messages"][-1]

            if hasattr(last_message, "content"):
                content = last_message.content

                # Check if we stopped after clarification step
                # The graph ends at clarify_with_user when it needs clarification
                clarify_node_ran = any(step["name"] == "clarify_with_user" for step in tracker.steps)
                research_nodes_ran = any("research" in step["name"].lower() or "write_report" in step["name"]
                                        for step in tracker.steps)

                # If only clarification ran (no research nodes), this is a clarification request
                if clarify_node_ran and not research_nodes_ran:
                    logger.print(f"\n{'='*80}")
                    logger.print("💬 CLARIFICATION NEEDED")
                    logger.print(f"{'='*80}\n")
                    logger.print(content)
                    logger.print(f"\n{'='*80}")

                    # Get user response
                    response = input("\n👉 Your response (or press Enter to skip): ").strip()

                    if response:
                        logger.print(f"User response: {response}", to_console=False)
                        # Add both the clarification question and user's answer to messages
                        messages.append(AIMessage(content=content))
                        messages.append(HumanMessage(content=response))
                        logger.print("\n📝 Continuing research with your clarification...\n")
                        tracker = ProgressTracker()  # Reset tracker
                        continue
                    else:
                        logger.print("\n⏭️  Proceeding with comprehensive research...\n")
                        messages.append(AIMessage(content=content))
                        messages.append(HumanMessage(content="Please proceed with comprehensive research on all aspects."))
                        tracker = ProgressTracker()  # Reset tracker
                        continue

                # Otherwise, it's the final report (research nodes have run)
                logger.print(f"\n{'='*80}")
                logger.print("✅ RESEARCH COMPLETE")
                logger.print(f"{'='*80}")
                logger.print(f"⏱️  Total Time: {tracker.get_elapsed_time()}")
                logger.print(f"📊 Total Steps: {len(tracker.steps)}")
                logger.print(f"{'='*80}\n")
                logger.print(content)
                logger.print(f"\n{'='*80}")

                # Save report to separate file
                report_file = logger.save_report(question, content)
                logger.print(f"\n📄 Report saved to: {report_file}")
                logger.print(f"📋 Full log saved to: {logger.log_file}")

                return content

        logger.print("\n⚠️  No report generated. Something went wrong.")
        break


def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    args = [arg for arg in sys.argv[1:] if arg not in ["--verbose", "-v"]]

    if args:
        # Single question mode
        question = " ".join(args)
        asyncio.run(interactive_research(question, verbose))
    else:
        # Interactive session mode
        print("="*80)
        print("🔬 DEEP RESEARCH - INTERACTIVE SESSION")
        print("="*80)
        print("\nWelcome! You can ask research questions and I'll conduct deep research.")
        print("Type 'quit', 'exit', or 'q' to end the session.")
        print("="*80)

        while True:
            try:
                print("\n" + "─"*80)
                question = input("❓ Your research question: ").strip()

                if not question:
                    print("⚠️  Please enter a question.")
                    continue

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using Deep Research! Goodbye.")
                    break

                # Run research
                asyncio.run(interactive_research(question, verbose))

                # Ask if user wants to continue
                print("\n" + "─"*80)
                continue_choice = input("🔄 Ask another question? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes', '']:
                    print("\n👋 Thank you for using Deep Research! Goodbye.")
                    break

            except KeyboardInterrupt:
                print("\n\n⚠️  Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Let's try again...")

if __name__ == "__main__":
    main()
