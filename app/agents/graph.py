"""LangGraph StateGraph definition and workflow execution engine."""

from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agents.nodes.analyze import analyze_node
from app.agents.nodes.conflict_check import conflict_check_node
from app.agents.nodes.human_review import human_review_node
from app.agents.nodes.ingest import ingest_node
from app.agents.nodes.report import generate_report_node
from app.agents.nodes.retrieve import retrieve_node
from app.agents.nodes.sanitize import sanitize_node
from app.agents.nodes.verify_citations import verify_citations_node
from app.agents.state import AgentState
from app.core.logging import logger


def should_continue_to_report(state: AgentState) -> str:
    """Conditional edge: check if human decisions have been provided."""
    approvals = state.get("approvals", {})
    # If decisions have been provided, proceed to generate_report; otherwise pause
    if approvals:
        return "generate_report"
    return "pause"


def build_review_graph(checkpointer: Any | None = None) -> Any:
    """Build and compile the LumenReview LangGraph state machine."""
    workflow = StateGraph(AgentState)

    # 1. Register nodes
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("sanitize", sanitize_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("verify_citations", verify_citations_node)
    workflow.add_node("conflict_check", conflict_check_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("generate_report", generate_report_node)

    # 2. Add sequential edges
    workflow.add_edge(START, "ingest")
    workflow.add_edge("ingest", "sanitize")
    workflow.add_edge("sanitize", "retrieve")
    workflow.add_edge("retrieve", "analyze")
    workflow.add_edge("analyze", "verify_citations")
    workflow.add_edge("verify_citations", "conflict_check")
    workflow.add_edge("conflict_check", "human_review")

    # 3. Add conditional routing for human-in-the-loop gate
    workflow.add_conditional_edges(
        "human_review",
        should_continue_to_report,
        {
            "generate_report": "generate_report",
            "pause": END,
        },
    )
    workflow.add_edge("generate_report", END)

    memory = checkpointer or MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app


# Module-level compiled graph with memory checkpointer
review_graph = build_review_graph()


def execute_review_analysis(
    run_id: str,
    raw_input: str,
    requirements: list | None = None,
    graph: Any | None = None,
) -> AgentState:
    """Execute review agent pipeline up to the human review gate."""
    target_graph = graph or review_graph
    config = {"configurable": {"thread_id": run_id}}

    initial_state: AgentState = {
        "run_id": run_id,
        "raw_input": raw_input,
        "requirements": requirements or [],
        "current_req": None,
        "retrieved_clauses": {},
        "findings": [],
        "conflict_findings": [],
        "approvals": {},
        "report": None,
        "trace": [],
        "status": "initialized",
        "security_warnings": [],
        "errors": [],
    }

    logger.info("Starting review graph execution for run %s", run_id)
    final_state = target_graph.invoke(initial_state, config=config)
    return final_state


def resume_review_with_decisions(
    run_id: str,
    approvals: dict[str, dict[str, Any]],
    current_state: AgentState,
    graph: Any | None = None,
) -> AgentState:
    """Resume execution from human review gate after reviewer decisions are submitted."""
    target_graph = graph or review_graph
    config = {"configurable": {"thread_id": run_id}}

    updated_state = dict(current_state)
    updated_state["approvals"] = approvals

    logger.info("Resuming review graph for run %s with %d decisions", run_id, len(approvals))
    final_state = target_graph.invoke(updated_state, config=config)
    return final_state
