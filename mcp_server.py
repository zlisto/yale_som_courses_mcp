"""Yale SOM course catalogue MCP — Lecture 9.

Reads data/yale_som.db only. Never invents courses, times, or faculty.

Run (stdio):     python mcp_server.py
Run (HTTP):      python mcp_server.py --http
HTTP URL:        http://127.0.0.1:8001/mcp
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from fastmcp import FastMCP

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "data" / "yale_som.db"
MAX_RESULTS = 15

mcp = FastMCP("yale-som-courses")


def _connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Missing {DB_PATH} — copy yale_som.db into data/ (Lecture 8 pack)"
        )
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _clip(text: str | None, limit: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _summary(row: sqlite3.Row) -> dict[str, str]:
    return {
        "number": row["course_number"] or "",
        "section": row["section"] or "",
        "title": row["course_title"] or "",
        "faculty": row["faculty_1"] or "",
        "category": row["course_category"] or "",
        "type": row["course_type"] or "",
        "session": row["course_session"] or "",
        "day_time": row["daytimes"] or "TBA",
        "room": row["room"] or "TBA",
        "units": row["units"] or "",
        "syllabus": row["syllabus"] or row["old_syllabus"] or "",
        "description": _clip(row["course_description"], 500),
        "faculty_bio": _clip(row["faculty_bio"], 300),
    }


@mcp.tool
def search_courses(query: str, limit: int = 10) -> dict:
    """Search Yale SOM courses by keyword across number, title, faculty, category, and description.

    Use this for topic questions, course numbers, or professor name fragments.
    Returns only rows that match the database — never invents courses.
    """
    needle = (query or "").strip()
    if not needle:
        return {
            "total_matches": 0,
            "returned": 0,
            "note": "Empty query — pass a topic, course number, or faculty name.",
            "courses": [],
        }
    limit = max(1, min(int(limit or 10), MAX_RESULTS))
    like = f"%{needle}%"
    sql = """
        SELECT * FROM courses
        WHERE course_number LIKE ?
           OR course_title LIKE ?
           OR faculty_1 LIKE ?
           OR course_category LIKE ?
           OR course_type LIKE ?
           OR course_description LIKE ?
        ORDER BY course_number, section
        LIMIT ?
    """
    args = (like, like, like, like, like, like, limit)
    with _connect() as con:
        rows = con.execute(sql, args).fetchall()
    return {
        "total_matches": len(rows),
        "returned": len(rows),
        "note": "" if rows else f"No courses matched {needle!r} in yale_som.db.",
        "courses": [_summary(r) for r in rows],
    }


@mcp.tool
def get_course(course_number: str, section: str = "") -> dict:
    """Look up one Yale SOM course by course number (e.g. 'MGT 409'). Optional section filter."""
    number = (course_number or "").strip()
    if not number:
        return {"found": False, "note": "Pass a course_number like MGT 409.", "courses": []}
    section = (section or "").strip()
    with _connect() as con:
        if section:
            rows = con.execute(
                "SELECT * FROM courses WHERE course_number = ? AND section = ? "
                "ORDER BY section",
                (number, section),
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT * FROM courses WHERE course_number = ? ORDER BY section",
                (number,),
            ).fetchall()
    if not rows:
        with _connect() as con:
            rows = con.execute(
                "SELECT * FROM courses WHERE course_number LIKE ? ORDER BY section LIMIT ?",
                (f"%{number}%", MAX_RESULTS),
            ).fetchall()
    return {
        "found": bool(rows),
        "note": "" if rows else f"No course found for {number!r}.",
        "courses": [_summary(r) for r in rows],
    }


@mcp.tool
def list_courses_by_faculty(name: str, limit: int = 15) -> dict:
    """List courses taught by a faculty member (substring match on faculty_1)."""
    name = (name or "").strip()
    if not name:
        return {
            "total_matches": 0,
            "returned": 0,
            "note": "Pass a faculty name fragment.",
            "courses": [],
        }
    limit = max(1, min(int(limit or 15), MAX_RESULTS))
    with _connect() as con:
        rows = con.execute(
            "SELECT * FROM courses WHERE faculty_1 LIKE ? "
            "ORDER BY course_number, section LIMIT ?",
            (f"%{name}%", limit),
        ).fetchall()
    return {
        "total_matches": len(rows),
        "returned": len(rows),
        "note": "" if rows else f"No faculty matched {name!r}.",
        "courses": [_summary(r) for r in rows],
    }


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
