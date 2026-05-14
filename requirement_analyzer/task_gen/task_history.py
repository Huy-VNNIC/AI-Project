"""
Task History Manager
====================
Saves and loads task generation history to disk.
Each session is stored as a JSON file with timestamp.
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# History stored in requirement_analyzer/data/task_history/
HISTORY_DIR = Path(__file__).parent.parent / "data" / "task_history"


def _ensure_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def save_history(
    tasks: List[Dict[str, Any]],
    source_text: str,
    filename: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Save a task generation session to history.

    Returns:
        session_id (str)
    """
    _ensure_dir()
    session_id = str(uuid.uuid4())[:8]
    ts = datetime.now().isoformat()

    record = {
        "session_id": session_id,
        "created_at": ts,
        "source_filename": filename,
        "total_tasks": len(tasks),
        "source_preview": source_text[:200] + ("..." if len(source_text) > 200 else ""),
        "metadata": metadata or {},
        "tasks": tasks
    }

    out_file = HISTORY_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_id}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, default=str)

    return session_id


def list_history(limit: int = 20) -> List[Dict[str, Any]]:
    """
    List recent task generation sessions (most recent first).

    Returns:
        List of session summaries (no tasks payload)
    """
    _ensure_dir()
    files = sorted(HISTORY_DIR.glob("*.json"), reverse=True)[:limit]
    summaries = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fp:
                record = json.load(fp)
            summaries.append({
                "session_id": record.get("session_id"),
                "created_at": record.get("created_at"),
                "source_filename": record.get("source_filename"),
                "total_tasks": record.get("total_tasks", 0),
                "source_preview": record.get("source_preview", ""),
                "file": f.name
            })
        except Exception:
            continue
    return summaries


def get_history_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Load a specific history session by session_id.

    Returns:
        Full record with tasks, or None if not found
    """
    _ensure_dir()
    for f in HISTORY_DIR.glob("*.json"):
        if session_id in f.name:
            try:
                with open(f, encoding="utf-8") as fp:
                    return json.load(fp)
            except Exception:
                return None
    return None


def delete_history_session(session_id: str) -> bool:
    """Delete a history session by session_id"""
    _ensure_dir()
    for f in HISTORY_DIR.glob("*.json"):
        if session_id in f.name:
            f.unlink()
            return True
    return False
