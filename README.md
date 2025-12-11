A lightweight backend workflow engine inspired by LangGraph - built using FastAPI, async execution, a tool registry, and clean, maintainable code.

This satisfies all requirements from the Tredence AI Engineering Internship Assignment.

📁 Project Structure
.
├── app/
│   ├── engine.py          # Core workflow engine
│   ├── main.py            # FastAPI app + routes
│   ├── models.py          # Pydantic API models
│   ├── tools.py           # Tool registry + summarization tools
│   ├── workflows.py       # Workflow registration and node mapping
│   └── __init__.py
│
├── scripts/               # (Optional) Helper scripts / curl examples / test clients
│   ├── create_graph.json
│   ├── run_graph.json
│   └── test_ws.py
│
├── requirements.txt
└── README.md

🚀 Features at a Glance
✔ Minimal Workflow Engine

Nodes = Python functions

Shared state passed between nodes

Edges define execution order

Supports:

Sequential execution

Branching (return {"next": "other_node"})

Looping (node returns itself as next step)

Async execution via background tasks

✔ Tool Registry

Tools stored in a simple dictionary:

register_tool("chunk_text", chunk_text)


Nodes call them via:

fn = get_tool("chunk_text")
return fn(state)

✔ FastAPI Endpoints
Method	Endpoint	Description
POST	/graph/create	Register a graph (nodes + edges)
POST	/graph/run	Execute graph, returns run_id
GET	/graph/state/{run_id}	Get full state + logs
WebSocket	/graph/ws/{run_id}	Live log updates
✔ Implemented Sample Workflow

Summarization + Refinement workflow (Option B)

Split text

Summarize each chunk

Merge summaries

Refine

Re-loop until summary length < threshold

▶️ How to Run the Project
1. Clone the repository
git clone <your_repo_url>
cd <project_folder>

2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

3. Install dependencies
pip install -r requirements.txt

4. Start server
uvicorn app.main:app --reload

5. Open Swagger UI
http://127.0.0.1:8000/docs

🧪 Example API Requests
A) Create Graph

Body (scripts/create_graph.json):

{
  "graph_id": "sample_graph",
  "start_node": "split_text",
  "nodes": [
    {"name": "split_text", "function": "split_text", "next_node": "summarize_chunks"},
    {"name": "summarize_chunks", "function": "summarize_chunks", "next_node": "merge_summaries"},
    {"name": "merge_summaries", "function": "merge_summaries", "next_node": "refine_summary"},
    {"name": "refine_summary", "function": "refine_summary", "next_node": "check_summary_length"},
    {"name": "check_summary_length", "function": "check_summary_length", "next_node": null}
  ]
}

B) Run Graph

Body (scripts/run_graph.json):

{
  "graph_id": "sample_graph",
  "initial_state": {
    "text": "FastAPI is a modern framework...",
    "chunk_size": 50,
    "max_summary_length": 150
  }
}

C) Check Status
GET /graph/state/{run_id}

📌 What This Engine Supports

Clean async execution

Deterministic state transitions

Real-time logs (WebSocket)

Dynamic tool-based processing

Extensible workflow structure


👨‍💻 Author

Niketh V
Backend Developer | AI Engineering Enthusiast