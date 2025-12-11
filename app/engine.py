# app/engine.py
import asyncio
import uuid
from typing import Dict, Any, Optional, Callable

class WorkflowEngine:
    def __init__(self):
        self.graphs: Dict[str, Dict[str, Any]] = {}
        self.runs: Dict[str, Dict[str, Any]] = {}
        self.node_registry: Dict[str, Callable] = {}

    def register_node(self, name: str, fn: Callable):
        self.node_registry[name] = fn

    def create_graph(self, graph_id: str, nodes: Dict[str, Any], edges: Dict[str, Optional[str]], start_node: str):
        self.graphs[graph_id] = {"nodes": nodes, "edges": edges, "start_node": start_node}
        return graph_id

    def get_graph(self, graph_id: str):
        return self.graphs.get(graph_id)

    def get_run(self, run_id: str):
        return self.runs.get(run_id)

    async def _execute_run(self, run_id: str):
        run = self.runs[run_id]
        graph = self.get_graph(run["graph_id"])
        state = run["state"]
        logs = run["logs"]
        current = graph["start_node"]
        step = 0

        try:
            while current:
                step += 1
                node_fn = self.node_registry.get(current)
                if not node_fn:
                    logs[step] = f"Node '{current}' not registered. Stopping."
                    run["status"] = "failed"
                    break

                logs[step] = f"Start node '{current}'"
                if asyncio.iscoroutinefunction(node_fn):
                    res = await node_fn(state)
                else:
                    loop = asyncio.get_running_loop()
                    res = await loop.run_in_executor(None, node_fn, state)

                if isinstance(res, dict):
                    delta = res.get("state")
                    if isinstance(delta, dict):
                        state.update(delta)
                    next_node = res.get("next", graph["edges"].get(current))
                else:
                    next_node = graph["edges"].get(current)

                logs[step] += f" -> next: {next_node}"
                run["state"] = state
                run["logs"] = logs
                current = next_node

                await asyncio.sleep(0)

            if run["status"] != "failed":
                run["status"] = "completed"
        except Exception as e:
            run["status"] = "failed"
            logs[step + 1] = f"Exception: {repr(e)}"

    def run_graph(self, graph_id: str, initial_state: Dict[str, Any]):
        if graph_id not in self.graphs:
            raise ValueError("Graph not found")

        run_id = str(uuid.uuid4())
        self.runs[run_id] = {
            "run_id": run_id,
            "graph_id": graph_id,
            "state": initial_state.copy(),
            "logs": {},
            "status": "running"
        }
        asyncio.create_task(self._execute_run(run_id))
        return run_id

engine = WorkflowEngine()
