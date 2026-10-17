"""Mock LLM Provider with realistic UNECE R48/R112 automotive fixtures."""

import re
from typing import TypeVar

from pydantic import BaseModel

from app.llm.base import BaseLLMProvider
from app.llm.schemas import (
    ConflictAnalysisResult,
    Evidence,
    FindingItem,
    RequirementAnalysisResult,
    SuggestedRewrite,
)

T = TypeVar("T", bound=BaseModel)


class MockLLM(BaseLLMProvider):
    """Deterministic, offline-ready mock LLM simulating expert homologation analysis."""

    def generate(
        self,
        prompt: str,
        response_model: type[T] | None = None,
        temperature: float = 0.0,
    ) -> T | str:
        # 1. Conflict detection prompt handling
        if response_model == ConflictAnalysisResult or "Identify all pairwise" in prompt:
            return self._handle_conflict_detection(prompt, response_model)

        # 2. Executive summary / report generation prompt handling
        if (
            response_model is None
            or "Executive Summary" in prompt
            or "Lead Homologation Specialist" in prompt
        ):
            return self._handle_report_generation(prompt)

        # 3. Requirement Analysis prompt handling
        if response_model == RequirementAnalysisResult or "Analyze requirement" in prompt:
            return self._handle_requirement_analysis(prompt, response_model)

        return "Mock response generated."

    def _extract_req_info(self, prompt: str) -> tuple[str, str]:
        req_id_match = re.search(r"<requirement id=['\"]?([^'\">]+)['\"]?>", prompt)
        req_id = req_id_match.group(1) if req_id_match else "REQ-001"

        text_match = re.search(r"<requirement[^>]*>(.*?)</requirement>", prompt, re.DOTALL)
        req_text = text_match.group(1).strip() if text_match else prompt
        return req_id, req_text

    def _handle_requirement_analysis(
        self, prompt: str, response_model: type[T] | None
    ) -> RequirementAnalysisResult:
        req_id, req_text = self._extract_req_info(prompt)
        text_lower = req_text.lower()
        issues: list[FindingItem] = []

        # Scenario 1: Luminous flux > 2000 lm missing headlamp cleaning
        has_high_flux = any(
            w in text_lower for w in ["flux", "lumen", "2,500", "2500", "3000", "3,200", "2200"]
        )
        has_cleaner_mandate = (
            "with cleaning" in text_lower
            or "equipped with cleaning" in text_lower
            or "incorporate a headlamp cleaning" in text_lower
            or "with washer" in text_lower
        )
        if has_high_flux and (
            not has_cleaner_mandate
            or "without" in text_lower
            or "no clean" in text_lower
            or "missing clean" in text_lower
        ):
            issues.append(
                FindingItem(
                    id=f"F-{req_id}-1",
                    req_id=req_id,
                    type="non_compliant",
                    severity="critical",
                    title="Missing Mandatory Headlamp Cleaning Device for Flux > 2,000 lm",
                    explanation=(
                        "Requirement specifies a principal passing beam luminous flux exceeding 2,000 lumens "
                        "without requiring an automated headlamp cleaning device as mandated by UNECE R48."
                    ),
                    evidence=Evidence(
                        chunk_id="R48-6.2.7",
                        quote="objective luminous flux which exceeds 2,000 lumens must only be installed in conjunction with the installation of headlamp cleaning devices",
                        document="UNECE Regulation No. 48",
                        clause_id="6.2.7.3",
                        page=1,
                    ),
                    suggested_rewrite=SuggestedRewrite(
                        text=(
                            f"{req_text.rstrip('.')} and shall incorporate a headlamp cleaning system "
                            "complying with UNECE Regulation No. 45."
                        ),
                        diff_explanation="Appended mandatory UNECE R45 cleaning device requirement for high-flux LED/HID headlamps.",
                    ),
                    confidence=0.98,
                )
            )

        # Scenario 2: Direction indicator flashing frequency out of bounds
        if "indicator" in text_lower or "turn signal" in text_lower or "flash" in text_lower:
            if (
                "2.5 hz" in text_lower
                or "2.5hz" in text_lower
                or "40" in text_lower
                or "150" in text_lower
                or "fast" in text_lower
            ):
                issues.append(
                    FindingItem(
                        id=f"F-{req_id}-1",
                        req_id=req_id,
                        type="non_compliant",
                        severity="critical",
                        title="Direction Indicator Flashing Frequency Exceeds Legal Limit",
                        explanation=(
                            "The specified flash rate is outside the permitted legal range of 90 +/- 30 periods "
                            "per minute (1.5 +/- 0.5 Hz)."
                        ),
                        evidence=Evidence(
                            chunk_id="R48-6.5.7",
                            quote="The frequency of the light flash must be 90 +/- 30 periods per minute (1.5 +/- 0.5 Hz)",
                            document="UNECE Regulation No. 48",
                            clause_id="6.5.9",
                            page=1,
                        ),
                        suggested_rewrite=SuggestedRewrite(
                            text="The direction-indicator lamp shall flash at an operating frequency of 1.5 Hz +/- 0.5 Hz (90 +/- 30 periods per minute).",
                            diff_explanation="Corrected flash frequency to UNECE R48 clause 6.5.9 bounds.",
                        ),
                        confidence=0.99,
                    )
                )

        # Scenario 3: Ambiguous or subjective language
        if any(
            w in text_lower
            for w in [
                "sufficient",
                "as bright as possible",
                "promptly",
                "normal conditions",
                "reasonable",
                "quickly",
            ]
        ):
            issues.append(
                FindingItem(
                    id=f"F-{req_id}-2" if issues else f"F-{req_id}-1",
                    req_id=req_id,
                    type="ambiguous",
                    severity="major",
                    title="Vague or Unquantified Acceptance Criteria",
                    explanation=(
                        "Requirement contains subjective terms ('sufficient', 'promptly', or 'as bright as possible') "
                        "that cannot be objectively verified during laboratory homologation."
                    ),
                    evidence=None,
                    suggested_rewrite=SuggestedRewrite(
                        text=re.sub(
                            r"(sufficiently|promptly|as bright as possible|sufficient)",
                            "within 100 milliseconds and maintaining a minimum illuminance of 12.0 lux at point 75R",
                            req_text,
                            flags=re.IGNORECASE,
                        ),
                        diff_explanation="Replaced subjective terminology with measurable photometric and timing thresholds.",
                    ),
                    confidence=0.92,
                )
            )

        # Scenario 4: Non-testable requirement
        if (
            "robust" in text_lower
            or "weatherproof" in text_lower
            or "never fail" in text_lower
            or "ideal" in text_lower
        ):
            issues.append(
                FindingItem(
                    id=f"F-{req_id}-3" if issues else f"F-{req_id}-1",
                    req_id=req_id,
                    type="non_testable",
                    severity="minor",
                    title="Non-Testable Blanket Reliability Claim",
                    explanation="Phrasing lacks a defined environmental standard (e.g. ISO 16750 or IP6K9K ingress test specification).",
                    evidence=None,
                    suggested_rewrite=SuggestedRewrite(
                        text=f"{req_text.rstrip('.')} verified in accordance with ISO 20653 IP6K9K and ISO 16750-4 thermal cycling tests.",
                        diff_explanation="Referenced specific automotive environmental test standards.",
                    ),
                    confidence=0.88,
                )
            )

        # Scenario 5: Stop lamp mounting height below 350 mm
        if "stop lamp" in text_lower and any(
            h in text_lower for h in ["280", "280 mm", "250", "300"]
        ):
            issues.append(
                FindingItem(
                    id=f"F-{req_id}-1" if not issues else f"F-{req_id}-2",
                    req_id=req_id,
                    type="non_compliant",
                    severity="major",
                    title="Stop Lamp Mounting Height Below Minimum Statutory Limit",
                    explanation="Specified mounting height is below the 350 mm statutory minimum specified in UNECE R48 Clause 6.7.4.2.",
                    evidence=Evidence(
                        chunk_id="R48-6.7.4",
                        quote="not less than 350 mm and not more than 1,500 mm above the ground",
                        document="UNECE Regulation No. 48 - Installation of Lighting Devices",
                        clause_id="6.7.4.2",
                        page=1,
                    ),
                    suggested_rewrite=SuggestedRewrite(
                        text=re.sub(r"(\d+\s*mm)", "not less than 350 mm", req_text),
                        diff_explanation="Corrected lower mounting threshold to UNECE R48 350 mm statutory minimum.",
                    ),
                    confidence=0.96,
                )
            )

        # Scenario 6: DRL remaining on when headlamps are activated
        if ("daytime running" in text_lower or "drl" in text_lower) and any(
            w in text_lower
            for w in ["remain illuminated", "active simultaneously", "turned on", "switched on"]
        ):
            issues.append(
                FindingItem(
                    id=f"F-{req_id}-1" if not issues else f"F-{req_id}-2",
                    req_id=req_id,
                    type="non_compliant",
                    severity="critical",
                    title="DRL Must Switch Off Automatically When Headlamps Are On",
                    explanation="UNECE R48 Clause 6.19.7.2 mandates that daytime running lamps must switch OFF automatically when headlamps are switched ON.",
                    evidence=Evidence(
                        chunk_id="R48-6.19.7",
                        quote="daytime running lamps must switch OFF automatically when the front fog lamps or headlamps are switched ON",
                        document="UNECE Regulation No. 48 - Installation of Lighting Devices",
                        clause_id="6.19.7.2",
                        page=1,
                    ),
                    suggested_rewrite=SuggestedRewrite(
                        text=f"{req_text.rstrip('.')} and shall extinguish automatically upon headlamp activation.",
                        diff_explanation="Enforced mandatory DRL automatic deactivation with headlamps per UNECE R48 6.19.7.2.",
                    ),
                    confidence=0.98,
                )
            )

        # Scenario 7: Direction indicator non-amber colour
        if (
            "direction" in text_lower or "turn signal" in text_lower or "indicator" in text_lower
        ) and "white" in text_lower:
            issues.append(
                FindingItem(
                    id=f"F-{req_id}-1" if not issues else f"F-{req_id}-2",
                    req_id=req_id,
                    type="non_compliant",
                    severity="critical",
                    title="Direction-Indicator Prescribed Colour Must Be Amber",
                    explanation="UNECE R48 Clause 5.15 prescribes that the colour of light emitted by direction-indicator lamps must be amber, not white.",
                    evidence=Evidence(
                        chunk_id="R48-5.15",
                        quote="Direction-indicator lamp: Amber",
                        document="UNECE Regulation No. 48 - Installation of Lighting Devices",
                        clause_id="5.15",
                        page=1,
                    ),
                    suggested_rewrite=SuggestedRewrite(
                        text=re.sub(r"\bwhite\b", "amber", req_text, flags=re.IGNORECASE),
                        diff_explanation="Aligned lamp colour with statutory amber requirement per UNECE R48 Clause 5.15.",
                    ),
                    confidence=0.99,
                )
            )

        # Scenario 5: Intentional Bad Citation test case
        if "hallucinated_citation" in text_lower:
            issues.append(
                FindingItem(
                    id=f"F-{req_id}-bad-1",
                    req_id=req_id,
                    type="non_compliant",
                    severity="major",
                    title="Test Finding with Hallucinated Citation",
                    explanation="Simulated hallucinated clause reference.",
                    evidence=Evidence(
                        chunk_id="R999-FAKE-CLAUSE",
                        quote="This text does not exist anywhere in real UNECE regulations.",
                        document="UNECE Fake",
                        clause_id="999.1",
                    ),
                    confidence=0.90,
                )
            )

        # If no issues flagged, return clean status
        summary = (
            f"Requirement {req_id} complies with reviewed UNECE regulations."
            if not issues
            else f"Identified {len(issues)} issue(s) requiring remediation."
        )

        result = RequirementAnalysisResult(
            req_id=req_id,
            issues=issues,
            compliance_summary=summary,
        )
        return result

    def _handle_conflict_detection(
        self, prompt: str, response_model: type[T] | None
    ) -> ConflictAnalysisResult:
        conflicts: list[FindingItem] = []
        prompt_lower = prompt.lower()

        # Check for DRL vs Low-Beam contradiction
        if "daytime running" in prompt_lower or "drl" in prompt_lower:
            if "remain on" in prompt_lower and (
                "switch off" in prompt_lower or "extinguish" in prompt_lower
            ):
                conflicts.append(
                    FindingItem(
                        id="CF-DRL-01",
                        req_id="REQ-DRL",
                        type="conflict",
                        severity="critical",
                        title="Direct Contradiction in Daytime Running Lamp Deactivation Logic",
                        explanation=(
                            "One requirement specifies that Daytime Running Lamps (DRLs) must remain continuously illuminated "
                            "at full intensity when dipped-beam headlamps are active, while another requirement specifies "
                            "that DRLs must automatically extinguish upon headlamp activation."
                        ),
                        evidence=Evidence(
                            chunk_id="R48-6.19.7",
                            quote="daytime running lamps must switch OFF automatically when the front fog lamps or headlamps are switched ON",
                            document="UNECE Regulation No. 48",
                            clause_id="6.19.7.2",
                            page=1,
                        ),
                        suggested_rewrite=SuggestedRewrite(
                            text="The daytime running lamps shall switch OFF automatically when headlamps are switched ON, except when used for intermittent optical signalling.",
                            diff_explanation="Harmonized to conform strictly with UNECE R48 paragraph 6.19.7.2.",
                        ),
                        confidence=0.95,
                    )
                )

        return ConflictAnalysisResult(conflicts=conflicts)

    def _handle_report_generation(self, prompt: str) -> str:
        return (
            "### Executive Summary\n\n"
            "The automated requirements review analyzed the submitted automotive lighting specifications against "
            "UNECE Regulation No. 48 (Installation of Lighting and Light-Signalling Devices) and UNECE Regulation No. 112 "
            "(Motor Vehicle Headlamps Emitting Asymmetrical Passing Beam).\n\n"
            "#### Key Findings & Remediation\n"
            "- **Photometric & Safety Systems**: Critical non-compliances were identified in requirements specifying "
            "high-flux LED headlamps exceeding 2,000 lumens without headlamp cleaning devices (UNECE R48 Clause 6.2.7.3).\n"
            "- **Signalling & Tell-Tales**: Direction-indicator flashing frequencies outside the statutory 1.5 +/- 0.5 Hz "
            "band were detected and remediated.\n"
            "- **Homologation Readiness**: All approved findings have been programmatically verified against authentic "
            "UNECE regulatory clauses. Recommended rewrites provide testable criteria suitable for certification testing."
        )
