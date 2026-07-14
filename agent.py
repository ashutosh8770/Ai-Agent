
"""My Assignment - Build an autonomous AI agent capable of collecting information from external sources, analyzing it, and generating a structured, actionable summary."""
"""
Autonomous AI Research Agent
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("Missing dependency 'duckduckgo-search'. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from google import genai
except ImportError:
    print("Missing dependency 'google-genai'. Run: pip install -r requirements.txt")
    sys.exit(1)



#  COLLECTION LAYER


def collect_information(topic: str, num_sources: int = 8) -> list[dict]:
    """
    Search the web for a topic and return a list of source snippets.
    Each item: {"title": str, "url": str, "snippet": str}
    """
    print(f"[collect] Searching the web for: '{topic}' ...")
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(topic, max_results=num_sources):
                results.append({
                    "title": r.get("title", "").strip(),
                    "url": r.get("href", "").strip(),
                    "snippet": r.get("body", "").strip(),
                })
    except Exception as e:
        print(f"[collect] Warning: search failed ({e}). Continuing with 0 sources.")

    print(f"[collect] Retrieved {len(results)} sources.")
    return results



# 2. ANALYSIS LAYER






def analyze_with_gemini(topic: str, sources: list[dict], model: str = "gemini-2.5-flash") -> dict:
    """
    Send collected sources to Gemini and get back a structured JSON analysis.
    """
    print("[analyze] Sending collected data to Gemini for synthesis ...")

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    if sources:
        source_block = "\n\n".join(
            f"[{i+1}] TITLE: {s['title']}\nURL: {s['url']}\nSNIPPET: {s['snippet']}"
            for i, s in enumerate(sources)
        )
    else:
        source_block = "(No sources were retrieved. Note this clearly in the analysis.)"

    user_prompt = (
       """ ANALYSIS_SYSTEM_PROMPT"""
        + f"\n\nTOPIC: {topic}\n\nRAW SOURCES:\n{source_block}"
    )

    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config={"max_output_tokens": 2000, "temperature": 0.3},
    )

    raw_text = (response.text or "").strip()

    # Defensive parsing in case the model wraps JSON in fences despite instructions
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        analysis = json.loads(cleaned)
    except json.JSONDecodeError:
        print("[analyze] Warning: could not parse JSON, storing raw text instead.")
        analysis = {
            "topic": topic,
            "executive_summary": raw_text,
            "key_findings": [],
            "risks_or_concerns": [],
            "action_items": [],
            "open_questions": ["Model output was not valid JSON; see executive_summary."],
            "sources_used": [s["url"] for s in sources],
        }

    print("[analyze] Analysis complete.")
    return analysis



#  REPORTING LAYER


def build_markdown_report(analysis: dict, sources: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    lines.append(f"# Research Report: {analysis.get('topic', 'Untitled')}")
    lines.append(f"*Generated {now}*\n")

    lines.append("## Executive Summary")
    lines.append(analysis.get("executive_summary", "N/A") + "\n")

    lines.append("## Key Findings")
    findings = analysis.get("key_findings") or []
    if findings:
        for f in findings:
            lines.append(f"- {f}")
    else:
        lines.append("- No findings extracted.")
    lines.append("")

    lines.append("## Risks / Concerns")
    risks = analysis.get("risks_or_concerns") or []
    if risks:
        for r in risks:
            lines.append(f"- {r}")
    else:
        lines.append("- None identified.")
    lines.append("")

    lines.append("## Action Items")
    actions = analysis.get("action_items") or []
    if actions:
        lines.append("| Priority | Action | Rationale |")
        lines.append("|---|---|---|")
        for a in actions:
            lines.append(
                f"| {a.get('priority', 'n/a')} | {a.get('action', '')} | {a.get('rationale', '')} |"
            )
    else:
        lines.append("- No action items generated.")
    lines.append("")

    lines.append("## Open Questions")
    questions = analysis.get("open_questions") or []
    if questions:
        for q in questions:
            lines.append(f"- {q}")
    else:
        lines.append("- None.")
    lines.append("")

    lines.append("## Sources")
    if sources:
        for s in sources:
            lines.append(f"- [{s['title']}]({s['url']})")
    else:
        lines.append("- No sources retrieved.")

    return "\n".join(lines)


def save_report(topic: str, analysis: dict, sources: list[dict], out_format: str, out_dir: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in topic).strip()
    safe_name = safe_name.replace(" ", "_")[:60] or "report"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.join(out_dir, f"{safe_name}_{timestamp}")

    written = []

    if out_format in ("md", "both"):
        md_path = base + ".md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(build_markdown_report(analysis, sources))
        written.append(md_path)

    if out_format in ("json", "both"):
        json_path = base + ".json"
        payload = {"analysis": analysis, "raw_sources": sources}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        written.append(json_path)

    return written



# MAIN


def main():
    parser = argparse.ArgumentParser(description="Autonomous AI research agent")
    parser.add_argument("--topic", required=True, help="Topic to research")
    parser.add_argument("--num-sources", type=int, default=8, help="Number of web sources to collect")
    parser.add_argument("--format", choices=["md", "json", "both"], default="both", help="Output format")
    parser.add_argument("--out-dir", default="./reports", help="Directory to save the report in")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Gemini model to use for analysis")
    args = parser.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable is not set.")
        print('Set it first, e.g.: export GEMINI_API_KEY="AIza..."')
        sys.exit(1)

    sources = collect_information(args.topic, args.num_sources)
    analysis = analyze_with_gemini(args.topic, sources, model=args.model)
    written_files = save_report(args.topic, analysis, sources, args.format, args.out_dir)

    print("\n[done] Report saved to:")
    for f in written_files:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
