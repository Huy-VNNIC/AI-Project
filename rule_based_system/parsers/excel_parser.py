"""
Excel/CSV parser module.
Parser cho Excel / CSV requirement table.
Tự động map column names → CanonicalRequirement fields.
"""

import re
import os
from ..models.canonical import CanonicalRequirement


# Map tên cột → field của schema
COLUMN_ALIASES = {
    # actor
    "actor": "actor", "user": "actor", "role": "actor", "stakeholder": "actor",

    # action
    "action": "action", "verb": "action", "operation": "action",

    # objects
    "object": "objects", "target": "objects", "entity": "objects",

    # conditions
    "condition": "conditions", "precondition": "conditions",
    "pre-condition": "conditions", "prerequisite": "conditions",
    "given": "conditions",

    # expected
    "expected": "expected", "expected result": "expected",
    "expected outcome": "expected", "result": "expected",
    "acceptance criteria": "expected", "output": "expected",
    "postcondition": "expected",

    # raw text (requirement description)
    "requirement": "raw_text", "req": "raw_text", "description": "raw_text",
    "feature": "raw_text", "story": "raw_text", "title": "raw_text",
    "detail": "raw_text", "note": "raw_text",

    # req_type
    "type": "req_type", "category": "req_type", "kind": "req_type",

    # priority (bonus field)
    "priority": "priority",
}


def parse_excel(filepath: str) -> list[CanonicalRequirement]:
    """
    Parse Excel/CSV file → list CanonicalRequirement.
    Tự detect sheet, tự map columns.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Cần cài: pip install pandas openpyxl")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(filepath, encoding="utf-8-sig")
    else:
        # Đọc sheet đầu tiên có data
        xl = pd.ExcelFile(filepath)
        df = pd.read_excel(xl, sheet_name=xl.sheet_names[0])

    # Xoá hàng trống
    df = df.dropna(how="all")

    # Map columns
    col_map = _build_column_map(df.columns.tolist())

    results = []
    for idx, row in df.iterrows():
        req = _row_to_requirement(row, col_map, idx)
        if req and req.is_valid():
            results.append(req)

    return results


def _build_column_map(columns: list) -> dict:
    """
    Tạo map: tên cột gốc → schema field.
    Case-insensitive matching.
    """
    mapping = {}
    for col in columns:
        normalized = str(col).lower().strip()
        if normalized in COLUMN_ALIASES:
            mapping[col] = COLUMN_ALIASES[normalized]
        else:
            # Fuzzy match: tìm alias gần nhất
            for alias, field in COLUMN_ALIASES.items():
                if alias in normalized or normalized in alias:
                    mapping[col] = field
                    break
    return mapping


def _row_to_requirement(row, col_map: dict, idx: int) -> CanonicalRequirement | None:
    """Convert 1 row DataFrame → CanonicalRequirement."""
    data = {}
    for col, field in col_map.items():
        val = row.get(col, "")
        if val is None or str(val).strip() in ("", "nan", "NaN", "None"):
            continue
        val = str(val).strip()

        if field == "objects":
            # Tách objects bởi "," hoặc "/"
            data["objects"] = [o.strip() for o in re.split(r"[,/]", val) if o.strip()]
        elif field == "conditions":
            data["conditions"] = [val]
        else:
            data[field] = val

    if not data:
        return None

    # Nếu chỉ có raw_text — parse minimal
    if "action" not in data and "raw_text" in data:
        tokens = data["raw_text"].lower().split()
        data["action"] = tokens[0] if tokens else "execute"
        data["objects"] = tokens[1:3] if len(tokens) > 1 else []

    return CanonicalRequirement(
        actor=data.get("actor", "user"),
        action=data.get("action", ""),
        objects=data.get("objects", []),
        conditions=data.get("conditions", []),
        expected=data.get("expected", ""),
        req_type=data.get("req_type", "functional"),
        source_format="excel",
        raw_text=data.get("raw_text", f"Row {idx + 2}"),
    )
