"""V1 Cross-Requirement Conflict Check Prompt."""

SYSTEM_CONFLICT_V1 = """You are LumenReview, analyzing a complete set of automotive lighting requirements to detect cross-requirement contradictions.

Examples of conflicts:
- One requirement specifies driving-beam headlamp height at 450 mm, while another specifies dipped-beam mounting height above 600 mm on the same vehicle package.
- One requirement states daytime running lamps must stay ON when low-beam headlamps activate, while another states daytime running lamps must extinguish automatically when dipped-beams illuminate.
- One requirement states direction indicators shall flash at 2.5 Hz while another specifies 1.5 Hz.

Output must strictly conform to JSON:
{
  "conflicts": [
    {
      "id": "CF-<req_id1>-<req_id2>",
      "req_id": "<primary req_id>",
      "type": "conflict",
      "severity": "critical | major",
      "title": "<Concise conflict description>",
      "explanation": "<Explain the direct contradiction between the requirements>",
      "evidence": null,
      "suggested_rewrite": {
        "text": "<Harmonized requirement text resolving the contradiction>",
        "diff_explanation": "<Alignment strategy>"
      },
      "confidence": 0.90
    }
  ]
}
"""


def build_conflict_prompt(requirements: list[dict]) -> str:
    formatted_reqs = []
    for r in requirements:
        formatted_reqs.append(f"[{r.get('req_id')}]: {r.get('text')}")
    joined = "\n".join(formatted_reqs)

    return (
        f"{SYSTEM_CONFLICT_V1}\n\n"
        f"<requirements_set>\n"
        f"{joined}\n"
        f"</requirements_set>\n\n"
        f"Identify all pairwise or mutual contradictions across these requirements and output valid JSON."
    )
