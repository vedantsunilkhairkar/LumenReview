"""Severity and Verification badges."""


def render_severity_badge(severity: str) -> str:
    sev = severity.lower()
    badge_class = f"lr-badge lr-badge-{sev}"
    return f'<span class="{badge_class}">{severity.upper()}</span>'


def render_issue_type_badge(issue_type: str) -> str:
    clean_type = issue_type.replace("_", " ").title()
    if issue_type == "value_engineering":
        return '<span style="background: #ECFDF5; color: #047857; border: 1px solid #6EE7B7; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">💎 VALUE ENGINEERING</span>'
    elif issue_type == "conflict":
        return '<span style="background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">⚡ CONFLICT</span>'
    return f'<span style="background: #F1F5F9; color: #475569; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">{clean_type}</span>'


def render_market_badge(market_scope: str | None) -> str:
    if not market_scope or market_scope == "Global":
        return '<span style="background: #F8FAFC; color: #64748B; border: 1px solid #CBD5E1; padding: 0.2rem 0.45rem; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">🌐 GLOBAL</span>'
    elif market_scope == "Cross_Market_Conflict":
        return '<span style="background: #FEF2F2; color: #991B1B; border: 1px solid #F87171; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">⚖️ UNECE vs FMVSS 108</span>'
    elif market_scope == "FMVSS_108":
        return '<span style="background: #EFF6FF; color: #1E40AF; border: 1px solid #93C5FD; padding: 0.2rem 0.45rem; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">🇺🇸 FMVSS 108</span>'
    elif market_scope == "UNECE":
        return '<span style="background: #F0FDF4; color: #166534; border: 1px solid #86EFAC; padding: 0.2rem 0.45rem; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">🇪🇺 UNECE</span>'
    return f'<span style="background: #F8FAFC; color: #64748B; padding: 0.2rem 0.45rem; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">{market_scope}</span>'


def render_financial_badge(val: float | None, fin_type: str | None) -> str:
    if not val or not fin_type or fin_type == "none":
        return ""
    if fin_type == "tooling_risk":
        return f'<span style="background: #FFFBEB; color: #B45309; border: 1px solid #FCD34D; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">⚠️ TOOLING RISK: €{val:,.0f}</span>'
    elif fin_type == "bom_cost_out":
        return f'<span style="background: #ECFDF5; color: #047857; border: 1px solid #6EE7B7; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">💰 BOM SAVINGS: €{val:,.2f}/unit</span>'
    elif fin_type == "warranty_risk":
        return f'<span style="background: #FEF2F2; color: #B91C1C; border: 1px solid #FCA5A5; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.72rem; font-weight: 700;">🛡️ RECALL/WARRANTY: €{val:,.0f}</span>'
    return ""


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
