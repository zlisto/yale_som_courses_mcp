"""Yale SOM course catalogue MCP — Lecture 9 starter.

In class you'll add real tools that read data/yale_som.db.
Right now there is one placeholder tool so the server runs.

Run (stdio):     python mcp_server.py
Run (HTTP):      python mcp_server.py --http
HTTP URL:        http://127.0.0.1:8001/mcp
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fastmcp import FastMCP

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "data" / "yale_som.db"

mcp = FastMCP("yale-som-courses")


@mcp.tool
def yo() -> str:
    """Placeholder tool — replace with real catalogue tools in class."""
    return "yo"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yale SOM courses MCP server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Serve Streamable HTTP on port 8001 (keeps FastAPI free on 8000)",
    )
    args = parser.parse_args()
    if args.http:
        mcp.run(transport="http", host="127.0.0.1", port=8001)
    else:
        mcp.run()
