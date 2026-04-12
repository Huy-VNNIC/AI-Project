"""
Post-process generated tasks to improve INVEST compliance.

Usage:
    python -m requirement_analyzer.task_refine_invest input.json
    python -m requirement_analyzer.task_refine_invest input.json --output refined_tasks.json
    python -m requirement_analyzer.task_refine_invest --stdin < tasks.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from requirement_analyzer.task_assess_invest import (
    evaluate_generated_tasks,
    evaluate_generation_response,
)


TaskLike = Dict[str, Any]

TECH_STACK_PATTERNS = (
    r"\bjava\b",
    r"\bspring boot\b",
    r"\bpython\b",
    r"\bdjango\b",
    r"\breact\b",
    r"\bangular\b",
    r"\bvue\b",
    r"\bpostgresql\b",
    r"\bmongodb\b",
    r"\boracle\b",
)
DEPENDENCY_PHRASES = (
    r"\bdepends on\b",
    r"\brequires\b",
    r"\bblocked by\b",
    r"\bafter\b",
    r"phụ thuộc",
    r"cần hoàn thành trước",
    r"sau khi",
)


def _normalize_ac(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    text = str(raw).strip()
    return [text] if text else []


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _sanitize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def _ensure_period(text: str) -> str:
    text = _sanitize_text(text)
    if not text:
        return text
    if text[-1] not in ".!?":
        return text + "."
    return text


def _build_capability_phrase(task: TaskLike) -> str:
    title = _sanitize_text(str(task.get("title") or ""))
    if not title:
        return "support the required workflow"
    title = re.sub(r"^(hệ thống phải|system shall|system must)\s+", "", title, flags=re.IGNORECASE)
    return title[:1].lower() + title[1:] if title else "support the required workflow"


def _extract_actor(task: TaskLike) -> str:
    text = " ".join(
        [
            str(task.get("title") or ""),
            str(task.get("description") or ""),
        ]
    ).lower()
    if "bác sĩ" in text or "doctor" in text:
        return "bác sĩ"
    if "điều dưỡng" in text or "nurse" in text:
        return "điều dưỡng"
    if "admin" in text or "quản trị" in text:
        return "quản trị viên"
    if "bệnh nhân" in text or "patient" in text:
        return "bệnh nhân"
    return "người dùng được phân quyền"


def _extract_business_value(task: TaskLike) -> str:
    text = " ".join(
        [
            str(task.get("title") or ""),
            str(task.get("description") or ""),
        ]
    ).lower()
    if "báo cáo" in text or "report" in text:
        return "hỗ trợ ra quyết định và theo dõi hoạt động"
    if "audit" in text or "log" in text:
        return "đảm bảo truy vết và tuân thủ"
    if "tích hợp" in text or "integration" in text:
        return "đồng bộ dữ liệu và giảm thao tác thủ công"
    if "thanh toán" in text or "payment" in text:
        return "xử lý viện phí chính xác và nhanh hơn"
    if "bảo hiểm" in text or "insurance" in text:
        return "xác thực quyền lợi và giảm sai sót nghiệp vụ"
    return "thực hiện đúng nghiệp vụ và giảm thao tác thủ công"


def _story_points_for_refined(task: TaskLike) -> int:
    sp = _safe_int(task.get("story_points"))
    if sp is None:
        return 3
    return min(sp, 5)


class InvestTaskRefiner:
    """Refine tasks heuristically to improve INVEST compliance."""

    def __init__(self, min_total: int = 20, min_dimension: int = 3):
        self.min_total = min_total
        self.min_dimension = min_dimension

    def refine_payload(self, payload: Union[List[TaskLike], Dict[str, Any]]) -> Dict[str, Any]:
        before = self._analyze(payload)
        raw_tasks = before["tasks"]

        refined_tasks: List[TaskLike] = []
        for task in raw_tasks:
            if task.get("invest", {}).get("meets_invest", False):
                kept = deepcopy(task)
                kept["invest_refinement"] = {
                    "status": "kept",
                    "reason": "Task already meets INVEST thresholds.",
                    "original_title": str(task.get("title") or "Untitled task"),
                    "original_description": str(task.get("description") or ""),
                    "original_acceptance_criteria": _normalize_ac(task.get("acceptance_criteria")),
                }
                refined_tasks.append(kept)
                continue

            refined = self._refine_task(task)
            refined_tasks.extend(refined)

        after = {
            "tasks": evaluate_generated_tasks(
                refined_tasks,
                min_invest_total=self.min_total,
                min_per_dimension=self.min_dimension,
            ),
            "total_tasks": len(refined_tasks),
        }
        invest_ready_tasks = [
            deepcopy(task)
            for task in after["tasks"]
            if task.get("invest", {}).get("meets_invest", False)
        ]
        refined_ready_tasks = [
            deepcopy(task)
            for task in after["tasks"]
            if task.get("invest", {}).get("meets_invest", False)
            and task.get("invest_refinement", {}).get("status") == "refined"
        ]
        invest_not_ready_tasks = [
            deepcopy(task)
            for task in after["tasks"]
            if not task.get("invest", {}).get("meets_invest", False)
        ]
        return {
            "summary_before": self._summarize(before),
            "summary_after": self._summarize(after),
            "tasks": after["tasks"],
            "total_tasks": after["total_tasks"],
            "invest_ready_tasks": invest_ready_tasks,
            "invest_ready_total": len(invest_ready_tasks),
            "refined_ready_tasks": refined_ready_tasks,
            "refined_ready_total": len(refined_ready_tasks),
            "invest_not_ready_tasks": invest_not_ready_tasks,
            "invest_not_ready_total": len(invest_not_ready_tasks),
        }

    def _analyze(self, payload: Union[List[TaskLike], Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(payload, list):
            tasks = evaluate_generated_tasks(
                payload,
                min_invest_total=self.min_total,
                min_per_dimension=self.min_dimension,
            )
            return {"tasks": tasks, "total_tasks": len(tasks)}
        return evaluate_generation_response(
            payload,
            min_invest_total=self.min_total,
            min_per_dimension=self.min_dimension,
        )

    def _summarize(self, analyzed: Dict[str, Any]) -> Dict[str, int]:
        tasks = analyzed.get("tasks", [])
        meets = sum(1 for task in tasks if task.get("invest", {}).get("meets_invest", False))
        return {
            "total_tasks": len(tasks),
            "meeting_invest": meets,
            "not_meeting_invest": len(tasks) - meets,
        }

    def _refine_task(self, task: TaskLike) -> List[TaskLike]:
        weak = set(task.get("invest", {}).get("weak_dimensions", []))

        working = deepcopy(task)
        original_title = str(working.get("title") or "Untitled task")
        original_description = str(working.get("description") or "")
        original_acceptance_criteria = _normalize_ac(working.get("acceptance_criteria"))
        notes: List[str] = []

        if "independent" in weak:
            self._fix_independent(working, notes)
        if "negotiable" in weak:
            self._fix_negotiable(working, notes)
        if "valuable" in weak:
            self._fix_valuable(working, notes)
        if "estimable" in weak:
            self._fix_estimable(working, notes)
        if "testable" in weak:
            self._fix_testable(working, notes)

        refined_tasks = [working]
        if "small" in weak:
            split_tasks = self._split_large_task(working, notes)
            refined_tasks = split_tasks if len(split_tasks) > 1 else [working]

        final_tasks: List[TaskLike] = []
        for item in refined_tasks:
            item["story_points"] = _story_points_for_refined(item)
            item["dependencies"] = [
                str(dep).strip() for dep in item.get("dependencies", []) if str(dep).strip()
            ]
            item["acceptance_criteria"] = _normalize_ac(item.get("acceptance_criteria"))
            item["description"] = _ensure_period(str(item.get("description") or ""))

            # 👇 ADD 2 FIELD QUAN TRỌNG CHO UI
            item["refined_title"] = item.get("title")
            item["refined_description"] = item.get("description")

            # 👇 OPTIONAL (nếu UI dùng)
            item["refined"] = item.get("description")

            item["invest_refinement"] = {
                "status": "refined",
                "original_title": original_title,
                "original_description": original_description,
                "original_acceptance_criteria": original_acceptance_criteria,
                "notes": notes or ["Task was normalized to improve INVEST compliance."],
            }

            final_tasks.append(item)
        return final_tasks

    def _fix_independent(self, task: TaskLike, notes: List[str]) -> None:
        task["dependencies"] = []
        for field in ("title", "description"):
            text = str(task.get(field) or "")
            for pattern in DEPENDENCY_PHRASES:
                text = re.sub(pattern + r".*$", "", text, flags=re.IGNORECASE)
            task[field] = _sanitize_text(text)
        notes.append("Removed explicit dependencies and dependency wording.")

    def _fix_negotiable(self, task: TaskLike, notes: List[str]) -> None:
        for field in ("title", "description"):
            text = str(task.get(field) or "")
            for pattern in TECH_STACK_PATTERNS:
                text = re.sub(pattern, "nền tảng được phê duyệt", text, flags=re.IGNORECASE)
            task[field] = _sanitize_text(text)
        notes.append("Relaxed technology-specific wording to keep focus on outcome.")

    def _fix_valuable(self, task: TaskLike, notes: List[str]) -> None:
        actor = _extract_actor(task)
        capability = _build_capability_phrase(task)
        value = _extract_business_value(task)
        task["description"] = (
            f"As {actor}, I need the system to {capability} so that {value}."
        )
        notes.append("Rewrote description to make actor and business value explicit.")

    def _fix_estimable(self, task: TaskLike, notes: List[str]) -> None:
        if not str(task.get("description") or "").strip():
            capability = _build_capability_phrase(task)
            task["description"] = _ensure_period(
                f"Implement capability to {capability} within a single workflow."
            )

        ac = _normalize_ac(task.get("acceptance_criteria"))
        if len(ac) < 2:
            capability = _build_capability_phrase(task)
            ac.extend(
                [
                    f"When a valid request is submitted, the system must {capability}.",
                    "Then the result must be stored or displayed with a clear success state.",
                ]
            )
        task["acceptance_criteria"] = _dedupe_keep_order(ac)
        notes.append("Added description and baseline acceptance criteria for estimation.")

    def _fix_testable(self, task: TaskLike, notes: List[str]) -> None:
        capability = _build_capability_phrase(task)
        ac = _normalize_ac(task.get("acceptance_criteria"))
        if not ac:
            ac = [
                f"When the actor performs the workflow, the system must {capability}.",
                "If input data is invalid, the system must reject the request and show a clear error.",
                "Then authorized users can verify the final result from the UI or report output.",
            ]
        else:
            rewritten = []
            for index, criterion in enumerate(ac, start=1):
                criterion = _sanitize_text(criterion)
                if re.search(r"\b(when|if|then|must|should|can|within|less than|greater than)\b", criterion, re.IGNORECASE):
                    rewritten.append(_ensure_period(criterion))
                elif index == 1:
                    rewritten.append(_ensure_period(f"When the workflow starts, {criterion}"))
                else:
                    rewritten.append(_ensure_period(f"Then {criterion[:1].lower() + criterion[1:]}"))
            ac = rewritten
        if len(ac) < 3:
            ac.append("Then the outcome must be auditable or observable by authorized users.")
        task["acceptance_criteria"] = _dedupe_keep_order(ac)
        notes.append("Rewrote acceptance criteria into verifiable condition/outcome statements.")

    def _split_large_task(self, task: TaskLike, notes: List[str]) -> List[TaskLike]:
        title = _sanitize_text(str(task.get("title") or "Untitled task"))
        ac = _normalize_ac(task.get("acceptance_criteria"))
        pieces: List[str] = []

        split_candidates = re.split(r"\s*(?:,|/| và | and )\s*", title, maxsplit=2, flags=re.IGNORECASE)
        split_candidates = [item.strip(" -") for item in split_candidates if item.strip(" -")]

        if len(split_candidates) > 1 and len(title.split()) > 6:
            pieces = split_candidates[:2]
        elif len(ac) >= 4:
            pieces = [ac[0], ac[1]]

        if not pieces:
            task["story_points"] = 5
            notes.append("Reduced story points to keep the task within a smaller delivery unit.")
            return [task]

        split_tasks: List[TaskLike] = []
        base_role = task.get("role")
        base_type = task.get("type")
        base_priority = task.get("priority")
        base_domain = task.get("domain")
        base_confidence = task.get("confidence")

        for index, piece in enumerate(pieces, start=1):
            new_task = deepcopy(task)
            new_title = piece
            if index == 1 and not re.search(r"\b(implement|enable|manage|support|allow|provide|hệ thống phải)\b", piece, re.IGNORECASE):
                new_title = f"Implement {piece}"
            new_task["title"] = _sanitize_text(new_title)
            new_task["description"] = _ensure_period(
                f"As {_extract_actor(task)}, I need the system to {_build_capability_phrase({'title': new_task['title']})} so that {_extract_business_value(task)}."
            )
            new_task["acceptance_criteria"] = [
                f"When the workflow for '{new_task['title']}' is triggered, the system must complete it successfully.",
                "If input data is invalid, the system must reject the request and show a clear error.",
                "Then authorized users can verify the completed result from the output screen or report.",
            ]
            new_task["story_points"] = 3
            new_task["dependencies"] = []
            new_task["role"] = base_role
            new_task["type"] = base_type
            new_task["priority"] = base_priority
            new_task["domain"] = base_domain
            new_task["confidence"] = base_confidence
            split_tasks.append(new_task)

        notes.append("Split a large task into smaller task units.")
        return split_tasks


def _dedupe_keep_order(items: Sequence[str]) -> List[str]:
    seen = set()
    output: List[str] = []
    for item in items:
        clean = _ensure_period(item)
        if clean and clean not in seen:
            seen.add(clean)
            output.append(clean)
    return output


def load_json_input(path: str) -> Union[List[TaskLike], Dict[str, Any]]:
    with open(path, encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "tasks" in data:
        return data
    raise ValueError("JSON root must be a task list or an object containing 'tasks'.")


def save_json_output(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, ensure_ascii=False, indent=2, default=str)


def _build_default_output_path(input_path: str) -> str:
    source = Path(input_path)
    return str(source.with_name(f"{source.stem}_invest_refined.json"))


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refine tasks that do not meet INVEST.")
    parser.add_argument("json_path", nargs="?", help="Path to task JSON input.")
    parser.add_argument("--stdin", action="store_true", help="Read JSON from stdin.")
    parser.add_argument("--output", help="Path to write refined JSON output.")
    parser.add_argument("--min-total", type=int, default=20, help="Minimum total INVEST score.")
    parser.add_argument("--min-dimension", type=int, default=3, help="Minimum per-dimension score.")
    return parser.parse_args(argv)


def _read_payload(args: argparse.Namespace) -> Tuple[Union[List[TaskLike], Dict[str, Any]], Optional[str]]:
    if args.stdin:
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("No JSON received from stdin.")
        return json.loads(raw), None
    if not args.json_path:
        raise ValueError("Missing JSON input path.")
    return load_json_input(args.json_path), args.json_path


def _print_refined_tasks(tasks: Sequence[TaskLike]) -> None:
    print()
    print("=== Refined Tasks Meeting INVEST ===")
    if not tasks:
        print("None")
        return

    for index, task in enumerate(tasks, start=1):
        invest = task.get("invest", {})
        print(
            f"[{index}] {task.get('title', 'Untitled task')} | "
            f"total={invest.get('total')} | grade={invest.get('grade')}"
        )
        notes = task.get("invest_refinement", {}).get("notes") or []
        if notes:
            print(f"    notes={'; '.join(notes[:2])}")


def main(argv: Optional[List[str]] = None) -> None:
    args = _parse_args(argv)
    payload, input_path = _read_payload(args)

    refiner = InvestTaskRefiner(
        min_total=args.min_total,
        min_dimension=args.min_dimension,
    )
    result = refiner.refine_payload(payload)

    output_path = args.output or (_build_default_output_path(input_path) if input_path else None)
    if output_path:
        save_json_output(output_path, result)
        print(f"Refined tasks written to: {output_path}")

    before = result["summary_before"]
    after = result["summary_after"]
    print("=== INVEST Refinement Summary ===")
    print(
        f"Before: total={before['total_tasks']}, "
        f"meeting={before['meeting_invest']}, not_meeting={before['not_meeting_invest']}"
    )
    print(
        f"After:  total={after['total_tasks']}, "
        f"meeting={after['meeting_invest']}, not_meeting={after['not_meeting_invest']}"
    )
    _print_refined_tasks(result.get("refined_ready_tasks", []))

    if not output_path:
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
