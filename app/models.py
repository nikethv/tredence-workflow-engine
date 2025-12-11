from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class NodeCreateModel(BaseModel):
    name: str
    function: str
    next_node: Optional[str] = None

class GraphCreateRequest(BaseModel):
    graph_id: str
    start_node: str
    nodes: List[NodeCreateModel]

class GraphCreateResponse(BaseModel):
    graph_id: str

class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

class GraphRunResponse(BaseModel):
    run_id: str

class RunStateResponse(BaseModel):
    run_id: str
    state: Dict[str, Any]
    logs: List[str]
    finished: bool
