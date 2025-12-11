# app/tools.py
from typing import Dict

_TOOL_REG = {}

def register_tool(name: str, fn):
    _TOOL_REG[name] = fn

def get_tool(name: str):
    return _TOOL_REG.get(name)

# FIXED TOOL FUNCTIONS — ALWAYS RETURN:
# { "state": {}, "next_node": None, "logs": [] }
def chunk_text(state: Dict) -> Dict:
    text = state.get("text", "") or ""
    chunk_size = int(state.get("chunk_size", 200))

    if not text:
        return {
            "state": {"chunks": []},
            "next_node": None,
            "logs": ["No text found — created empty chunks list"]
        }

    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    new_state = state.copy()
    new_state["chunks"] = chunks

    return {
        "state": new_state,
        "next_node": None,
        "logs": [f"Split text into {len(chunks)} chunks"]
    }


def summarize_chunk(state: Dict) -> Dict:
    chunks = state.get("chunks", []) or []
    summaries = []

    for c in chunks:
        if "." in c:
            parts = [p.strip() for p in c.split(".") if p.strip()]
            if parts:
                summaries.append(parts[0] + ".")
                continue
        
        summaries.append(c[:max(20, len(c)//2)].strip())

    new_state = state.copy()
    new_state["summaries"] = summaries

    return {
        "state": new_state,
        "next_node": None,
        "logs": [f"Generated {len(summaries)} summaries"]
    }


def merge_summaries(state: Dict) -> Dict:
    summaries = state.get("summaries", []) or []
    merged = " ".join(summaries)

    new_state = state.copy()
    new_state["merged_summary"] = merged

    return {
        "state": new_state,
        "next_node": None,
        "logs": ["Merged all summaries"]
    }


def refine_summary(state: Dict) -> Dict:
    merged = state.get("merged_summary", "") or ""
    refined = " ".join(merged.split())

    max_len = int(state.get("max_summary_length", 300))
    if len(refined) > max_len:
        refined = refined[:max_len]
        if " " in refined:
            refined = refined.rsplit(" ", 1)[0]

    new_state = state.copy()
    new_state["refined_summary"] = refined

    return {
        "state": new_state,
        "next_node": None,
        "logs": ["Refined summary for size + formatting"]
    }


def check_summary_length(state: Dict) -> Dict:
    refined = state.get("refined_summary", "") or ""
    limit = int(state.get("max_summary_length", 300))

    if len(refined) >= limit:
        next_node = "refine_summary"
        log = "Summary exceeded limit → sending back to refine_summary"
    else:
        next_node = None
        log = "Summary is within limit → workflow finished"

    return {
        "state": state,
        "next_node": next_node,
        "logs": [log]
    }


# REGISTER TOOLS
register_tool("chunk_text", chunk_text)
register_tool("summarize_chunk", summarize_chunk)
register_tool("merge_summaries", merge_summaries)
register_tool("refine_summary", refine_summary)
register_tool("check_summary_length", check_summary_length)
