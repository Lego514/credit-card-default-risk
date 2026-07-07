"""LLM insight layer: turns the SQL results and model metrics into a weekly
risk memo a portfolio manager would actually read.

Design notes (the part interviewers ask about):
- The LLM never sees raw customer data — only aggregated query results, so
  there is nothing to hallucinate customer-level facts from and no PII leaves
  the machine.
- Every number in the memo must come from the supplied tables; the prompt
  forbids introducing figures that are not present (grounding).
- The memo is generated, then a human reviews it — this is a drafting tool,
  not an autonomous reporting pipeline.

Usage:
    set ANTHROPIC_API_KEY=sk-ant-...   (Windows)
    python ai_insights/generate_risk_memo.py
Writes ai_insights/risk_memo.md. See sample_output.md for an example run.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "sql" / "results"
METRICS = ROOT / "reports" / "model_metrics.json"
PROMPT_TEMPLATE = Path(__file__).parent / "prompt.md"
OUTPUT = Path(__file__).parent / "risk_memo.md"

MODEL = "claude-sonnet-5"


def gather_context() -> str:
    parts = []
    for csv in sorted(RESULTS.glob("*.csv")):
        parts.append(f"### {csv.stem}\n```\n{csv.read_text(encoding='utf-8').strip()}\n```")
    parts.append(f"### model_metrics\n```json\n{METRICS.read_text(encoding='utf-8').strip()}\n```")
    return "\n\n".join(parts)


def main() -> None:
    prompt = PROMPT_TEMPLATE.read_text(encoding="utf-8").replace("{{DATA}}", gather_context())

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY is not set. See sample_output.md for an example memo.")

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    memo = message.content[0].text
    OUTPUT.write_text(memo, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}\n\n{memo}")


if __name__ == "__main__":
    main()
