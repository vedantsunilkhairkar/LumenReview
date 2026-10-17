"""Severity and Verification badges."""


def render_severity_badge(severity: str) -> str:
    sev = severity.lower()
    badge_class = f"lr-badge lr-badge-{sev}"
    return f'<span class="{badge_class}">{severity.upper()}</span>'


def render_issue_type_badge(issue_type: str) -> str:
    clean_type = issue_type.replace("_", " ").title()
    return f'<span style="background: #F1F5F9; color: #475569; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">{clean_type}</span>'


def render_verification_badge(is_verified: bool) -> str:
    if is_verified:
        return '<span class="lr-badge lr-badge-verified">✓ CITATION VERIFIED</span>'
    return '<span class="lr-badge lr-badge-unverified">⚠ UNVERIFIED CITATION</span>'


def render_decision_badge(decision: str) -> str:
    dec = decision.lower()
    if dec == "approved":
        return '<span style="background: #DCFCE7; color: #166534; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">APPROVED</span>'
    elif dec == "rejected":
        return '<span style="background: #FEE2E2; color: #991B1B; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">REJECTED</span>'
    elif dec == "edited":
        return '<span style="background: #FEF3C7; color: #92400E; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">EDITED & APPROVED</span>'
    return '<span style="background: #F1F5F9; color: #64748B; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">PENDING REVIEW</span>'
