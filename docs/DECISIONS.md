# Architectural Decision Records (ADRs) - LumenReview

This document records key technical decisions, rationale, alternatives considered, and trade-offs.

---

## ADR-001: LangGraph for Workflow Orchestration & Human Approval Interrupts
- **Date**: 2026-10-17
- **Context**: The requirements review workflow requires a multi-step sequence (ingest, sanitize, retrieve, analyze, verify citations, conflict check, human review, report generation). The human review step requires pausing execution and resuming asynchronously when decisions are posted.
- **Decision**: Use `LangGraph` `StateGraph` with a persistent checkpointer.
- **Alternatives Considered**: 
  - Standard LangChain chains (stateless, poor interrupt support).
  - Celery / temporal (heavy external infrastructure dependencies).
- **Consequences**: First-class support for `human_review` node interrupts and graph resumption via SQLite checkpointer; typed state dictionary.

---

## ADR-002: Programmatic Citation Verification vs. LLM-as-a-Judge
- **Date**: 2026-10-17
- **Context**: LLMs can hallucinate clause numbers and invent plausible-sounding regulatory text. A core acceptance criterion is that every citation shown in the UI is verified.
- **Decision**: Implement a programmatic citation verification engine (`app/agents/nodes/verify_citations.py`) that strictly checks:
  1. Does the cited `chunk_id` exist in the local vector/document store?
  2. Does the quoted text exist in the source chunk via normalized token substring or Levenshtein ratio $\ge 0.90$?
- **Alternatives Considered**: LLM-as-a-judge (costs additional tokens, can itself hallucinate, slower).
- **Consequences**: 100% deterministic, zero cost, completely audit-proof for regulatory automotive compliance.

---

## ADR-003: Hybrid Retrieval (Dense Vector + BM25 Reciprocal Reranking)
- **Date**: 2026-10-17
- **Context**: Automotive lighting standards (UNECE R48, R112) contain exact numeric parameters (e.g. `1,000 lm`, `2.5% inclination`, `1.5 Hz`) and strict hierarchical clause numbers (e.g. `Clause 6.2.6.1.2`). Pure semantic vector embeddings frequently miss exact clause lookups.
- **Decision**: Combine ChromaDB dense vector similarity (`BAAI/bge-small-en-v1.5`) with sparse keyword matching (`rank_bm25`) using Reciprocal Rank Fusion (RRF).
- **Alternatives Considered**: Vector search only; ElasticSearch (too heavy for local single-binary demo).
- **Consequences**: Precise recall on exact clause numbers and photometric thresholds while maintaining semantic understanding.

---

## ADR-004: Provider-Agnostic LLM Layer with Default MockLLM
- **Date**: 2026-10-17
- **Context**: The system must run offline in Docker without requiring external API keys, but support Gemini, OpenAI, or Anthropic when keys are provided.
- **Decision**: Provide an abstract `LLMProvider` interface with a deterministic `MockLLM` containing realistic UNECE lighting test responses. When `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY` are detected, the system switches to the real provider.
- **Alternatives Considered**: Hardcoding OpenAI API client.
- **Consequences**: Guaranteed out-of-the-box demo experience, fast local test suite, zero-cost CI pipeline.

---

## ADR-005: Custom-Themed Streamlit UI with Injected CSS
- **Date**: 2026-10-17
- **Context**: Default Streamlit appearance looks like a prototype script. The project requires an enterprise-grade Linear/Notion feel with dark-navy sidebar and amber `#F5A623` accents.
- **Decision**: Create `ui/theme.py` with scoped CSS injection, Inter font family, 8px grid, custom card components, and split-pane workspace.
- **Alternatives Considered**: React/Next.js frontend (requires Node.js, separate build steps, multi-container orchestration overhead).
- **Consequences**: Single Python ecosystem, easy local launch, beautiful enterprise styling.
