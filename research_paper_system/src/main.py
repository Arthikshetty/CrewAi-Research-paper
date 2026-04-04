import argparse
import json
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.crew import ResearchPaperCrew

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Research Paper Discovery & Analysis System")
    parser.add_argument("topic", type=str, nargs="?", default=None, help="Research topic to analyze")
    parser.add_argument("--years", type=int, default=5, help="Number of years to search (default: 5)")
    parser.add_argument("--min-papers", type=int, default=30, help="Minimum papers to find (default: 30)")
    parser.add_argument("--num-ideas", type=int, default=5, help="Number of ideas to generate (default: 5)")
    parser.add_argument("--output", type=str, default="results.json", help="Output file path")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode with pre-computed sample data")

    args = parser.parse_args()

    # ---------- Demo mode ----------
    if args.demo:
        demo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "demo", "demo_results.json",
        )
        if not os.path.exists(demo_path):
            print("ERROR: demo_results.json not found. Run the full pipeline first.")
            sys.exit(1)
        with open(demo_path, "r", encoding="utf-8") as f:
            results = json.load(f)
        out = args.output
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Demo results written to {out}")
        print(f"Topic: {results.get('topic', '?')}")
        print(f"Papers: {results.get('paper_count', 0)}")
        sys.exit(0)

    # ---------- Normal mode ----------
    if not args.topic:
        parser.error("topic is required unless --demo is specified")

    logger.info(f"Starting analysis for topic: {args.topic}")
    logger.info(f"Parameters: years={args.years}, min_papers={args.min_papers}, num_ideas={args.num_ideas}")

    crew = ResearchPaperCrew()
    results = crew.run(
        topic=args.topic,
        years=args.years,
        min_papers=args.min_papers,
        num_ideas=args.num_ideas,
    )

    # Save results
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    logger.info(f"Results saved to {args.output}")

    # Print summary
    print("\n" + "=" * 70)
    print(f"RESEARCH ANALYSIS COMPLETE: {args.topic}")
    print("=" * 70)
    print(f"Papers discovered: {results.get('paper_count', 0)}")

    if results.get("best_base_papers"):
        bp = results["best_base_papers"][0]
        print(f"\nBest Base Paper: {bp['title']}")
        print(f"  Cited by {bp['total_incoming_citations']} discovered papers")

    if results.get("top_authors"):
        print(f"\nTop Authors:")
        for i, author in enumerate(results["top_authors"][:5], 1):
            print(f"  {i}. {author['author_name']} ({author['total_papers_on_topic']} papers)")

    print(f"\nFull results: {args.output}")


if __name__ == "__main__":
    main()
