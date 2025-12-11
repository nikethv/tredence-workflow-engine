# app/main.py
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import asyncio

from .models import GraphCreateRequest, GraphCreateResponse, GraphRunRequest, GraphRunResponse, RunStateResponse
from .engine import engine
from .workflows import register_workflow, GRAPH_ID

app = FastAPI(title="Tredence Workflow Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    register_workflow()

# simple root to avoid 404 when browsing /
@app.get("/")
async def root():
    return {"message": "Workflow Engine running"}

GRAPH_STORE: Dict[str, Dict] = {}

@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(req: GraphCreateRequest):
    nodes_map = {n.name: {} for n in req.nodes}
    edges_map = {n.name: n.next_node for n in req.nodes}
    engine.create_graph(req.graph_id, nodes_map, edges_map, req.start_node)
    GRAPH_STORE[req.graph_id] = {"nodes": nodes_map, "edges": edges_map, "start": req.start_node}
    return GraphCreateResponse(graph_id=req.graph_id)

@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(req: GraphRunRequest):
    if not engine.get_graph(req.graph_id):
        raise HTTPException(status_code=404, detail="Graph not found. Create first via /graph/create")
    initial = req.initial_state.copy()
    initial.setdefault("chunk_size", 200)
    initial.setdefault("max_summary_length", 300)
    run_id = engine.run_graph(req.graph_id, initial)
    # return immediately with run_id
    return GraphRunResponse(run_id=run_id)

@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
async def get_run_state(run_id: str):
    run = engine.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    logs = [run["logs"][k] for k in sorted(run["logs"].keys())]
    finished = run["status"] in ("completed", "failed")
    return RunStateResponse(run_id=run_id, state=run["state"], logs=logs, finished=finished)

@app.websocket("/graph/ws/{run_id}")
async def ws_logs(websocket: WebSocket, run_id: str):
    await websocket.accept()
    try:
        last = 0
        while True:
            run = engine.get_run(run_id)
            if not run:
                await websocket.send_text("Run not found")
                await websocket.close()
                return
            logs = [run["logs"][k] for k in sorted(run["logs"].keys())]
            new = logs[last:]
            for l in new:
                await websocket.send_text(l)
            last = len(logs)
            if run["status"] in ("completed", "failed"):
                await websocket.send_text(f"RUN:{run['status']}")
                await websocket.close()
                return
            await asyncio.sleep(0.4)
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass
