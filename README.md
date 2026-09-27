<p align="center">
  <img src="docs/handsome-dan.svg" alt="A row of seven rainbow-colored Handsome Dan bulldogs in Yale-blue bandanas" width="720">
</p>

<h1 align="center">Yale SOM Course Explorer (MCP)</h1>

<p align="center">
  Same Yale SOM course explorer as before — browse courses as cards, chat with the assistant —
  but the catalogue tools now live on a <strong>FastMCP server</strong> (<code>mcp_server.py</code>).
</p>

---

## What’s the same / what’s new

**Same as the Lecture 8 course explorer**

- Glass course cards for every Yale SOM course
- Search and category filters
- Chat assistant in the bottom-right corner
- React + FastAPI + Portkey (`gpt-5.6-luna` by default)

**New for Lecture 9 (MCP)**

- `mcp_server.py` at the project root — FastMCP tools over `data/yale_som.db`
- Tools: `search_courses`, `get_course`, `list_courses_by_faculty`
- The PydanticAI agent attaches that server with `MCPToolset` (in-process for class)
- Local catalogue tools in `backend/tools.py` are empty — course facts come from MCP only

---

## Project layout

```
.
├── .env.example
├── mcp_server.py          # FastMCP catalogue tools
├── data/
│   ├── yale_som_classes.json
│   └── yale_som.db        # not in git — see Setup
├── backend/
│   ├── main.py
│   ├── agent.py           # MCPToolset → mcp_server
│   ├── tools.py           # stub (tools live on MCP)
│   ├── models.py
│   ├── prompts/prompt.md
│   └── requirements.txt
├── frontend/
└── output/audit_trail.json
```

---

## Setup

You need **Python 3.12+**, **Node.js 20+**, and a **Portkey API key**.

**1. API key.** Copy `.env.example` to `.env` and fill in:

```
PORTKEY_API_KEY=your-portkey-api-key-here
```

Never commit the real `.env`.

**2. Course database.** Put `yale_som.db` in `data/` (Lecture 8 `data.zip` if you don’t have it). Cards still load from `yale_som_classes.json`; the MCP tools need the SQLite file.

**3. Backend:**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**4. Frontend:**

```powershell
cd frontend
npm install
```

---

## Running the app

**Terminal 1 — backend** (start first):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --port 8000
```

**Terminal 2 — frontend:**

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173**. API docs: **http://127.0.0.1:8000/docs**.

Ask the chat something like “What does MGT 409 cover?” — answers should come through MCP tools (`tools_used` in the reply / audit trail).

### Optional: run the MCP server alone (stdio or HTTP)

```powershell
python mcp_server.py
python mcp_server.py --http
```

HTTP URL: `http://127.0.0.1:8001/mcp`  
For class, the agent already loads MCP in-process — you usually don’t need a second terminal.

---

## API

| Method | Route | What it does |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/courses?q=...` | All courses, optional text filter |
| `POST` | `/api/chat` | `{"message": "..."}` → reply + `tools_used` |

---

## Notes

- **Budget.** Use `gpt-5.6-luna` via Portkey for class. Override with `MODEL_NAME` in `.env` if needed.
- **Handsome Dan.** If you edit the mascot component, regenerate the README banner:

  ```powershell
  cd frontend
  node render-dan.mjs
  ```
