"""V1 Executive Summary Synthesis Prompt."""

SYSTEM_REPORT_V1 = """You are LumenReview Lead Homologation Specialist.
Summarize the findings and human review decisions for an automotive lighting review run.
Provide an executive summary synthesizing:
1. Overall compliance status (Pass, Conditional Pass, or Fail).
2. Major regulatory non-compliances identified and approved by the reviewer.
3. Key ambiguity or testability gaps that need immediate engineering clarification.
4. Actionable next steps before vehicle homologation certification.
"""


def build_report_prompt(requirements_count: int, approved_findings: list[dict]) -> str:
    findings_bullets = []
    for f in approved_findings:
        findings_bullets.append(
            f"- [{f.get('severity', 'info').upper()}] {f.get('title')}: {f.get('explanation')}"
        )
    joined_findings = "\n".join(findings_bullets) if findings_bullets else "No issues flagged."

    return (
        f"{SYSTEM_REPORT_V1}\n\n"
        f"Total Requirements Evaluated: {requirements_count}\n"
        f"Total Approved Findings: {len(approved_findings)}\n\n"
        f"Approved Findings Detail:\n{joined_findings}\n\n"
        f"Generate a professional, structured executive summary (2-3 paragraphs) in clean Markdown."
    )
