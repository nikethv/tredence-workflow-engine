# app/workflows.py

from .engine import engine
from .tools import get_tool
# NODE FUNCTIONS
def node_split_text(state):
    fn = get_tool("chunk_text")
    return fn(state)

def node_summarize_chunks(state):
    fn = get_tool("summarize_chunk")
    return fn(state)

def node_merge_summaries(state):
    fn = get_tool("merge_summaries")
    return fn(state)

def node_refine_summary(state):
    fn = get_tool("refine_summary")
    return fn(state)

def node_check_length(state):
    fn = get_tool("check_summary_length")
    return fn(state)

# REGISTER NODES WITH ENGINE

engine.register_node("split_text", node_split_text)
engine.register_node("summarize_chunks", node_summarize_chunks)
engine.register_node("merge_summaries", node_merge_summaries)
engine.register_node("refine_summary", node_refine_summary)
engine.register_node("check_summary_length", node_check_length)
# GRAPH DEFINITION
# IMPORTANT FIX:
# This MUST MATCH the ID you send in POST /graph/run
GRAPH_ID = "sample_graph"    # ← FIXED FROM workflow_summarization

NODES = {
    "split_text": {},
    "summarize_chunks": {},
    "merge_summaries": {},
    "refine_summary": {},
    "check_summary_length": {}
}

EDGES = {
    "split_text": "summarize_chunks",
    "summarize_chunks": "merge_summaries",
    "merge_summaries": "refine_summary",
    "refine_summary": "check_summary_length",
    "check_summary_length": None
}

# GRAPH REGISTRATION
def register_workflow():
    """
    Creates graph only if not already created.
    Prevents duplicate creation on app reload.
    """
    if not engine.get_graph(GRAPH_ID):
        engine.create_graph(GRAPH_ID, NODES, EDGES, "split_text")
    return GRAPH_ID
