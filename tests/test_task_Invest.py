#!/usr/bin/env python3
"""
Test runner for requirement_analyzer.task_invest.

Usage:
    python AI-Project\\tests\\test_task_Invest.py path\\to\\tasks.json
    python AI-Project\\tests\\test_task_Invest.py path\\to\\tasks.json --pretty
    python AI-Project\\tests\\test_task_Invest.py --stdin < response.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from requirement_analyzer.task_assess_invest import (  # noqa: E402
    evaluate_generated_tasks,
    evaluate_generation_response,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run rule-based INVEST analysis against a JSON input."
    )
    parser.add_argument(
        "json_path",
        nargs="?",
        help="Path to JSON file. JSON can be a task list or an object containing 'tasks'.",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read JSON input from stdin instead of a file.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print full analyzed JSON instead of summary only.",
    )
    parser.add_argument(
        "--min-total",
        type=int,
        default=20,
        help="Minimum total INVEST score to consider a task acceptable.",
    )
    parser.add_argument(
        "--min-dimension",
        type=int,
        default=3,
        help="Minimum score per INVEST dimension.",
    )
    return parser.parse_args()


def _load_input(args: argparse.Namespace) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    if args.stdin:
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("No JSON data received from stdin.")
        return json.loads(raw)

    if not args.json_path:
        raise ValueError("Missing JSON input. Provide a file path or use --stdin.")

    input_path = Path(args.json_path)
    if not input_path.exists():
        raise FileNotFoundError(f"JSON file not found: {input_path}")

    with input_path.open(encoding="utf-8") as file_obj:
        return json.load(file_obj)


def _analyze(
    payload: Union[List[Dict[str, Any]], Dict[str, Any]],
    min_total: int,
    min_dimension: int,
) -> Dict[str, Any]:
    if isinstance(payload, list):
        analyzed_tasks = evaluate_generated_tasks(
            payload,
            min_invest_total=min_total,
            min_per_dimension=min_dimension,
        )
        return {
            "tasks": analyzed_tasks,
            "total_tasks": len(analyzed_tasks),
        }

    if isinstance(payload, dict):
        return evaluate_generation_response(
            payload,
            min_invest_total=min_total,
            min_per_dimension=min_dimension,
        )

    raise TypeError("JSON root must be a list of tasks or an object containing 'tasks'.")


def _validate_output(result: Dict[str, Any]) -> Tuple[int, int]:
    tasks = result.get("tasks")
    if not isinstance(tasks, list):
        raise AssertionError("Output must contain a 'tasks' list.")

    passed = 0
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise AssertionError(f"Task #{index} is not a JSON object.")

        invest = task.get("invest")
        if not isinstance(invest, dict):
            raise AssertionError(f"Task #{index} is missing 'invest' result.")

        required_keys = {
            "score",
            "total",
            "grade",
            "meets_invest",
            "weak_dimensions",
            "issues",
            "suggestions",
            "recommended_action",
            "thresholds",
        }
        missing = required_keys - set(invest.keys())
        if missing:
            raise AssertionError(f"Task #{index} missing INVEST keys: {sorted(missing)}")

        score = invest.get("score")
        if not isinstance(score, dict):
            raise AssertionError(f"Task #{index} has invalid 'score' payload.")

        for dim in ("independent", "negotiable", "valuable", "estimable", "small", "testable"):
            dim_value = score.get(dim)
            if not isinstance(dim_value, int):
                raise AssertionError(f"Task #{index} dimension '{dim}' must be int.")
            if dim_value < 1 or dim_value > 5:
                raise AssertionError(f"Task #{index} dimension '{dim}' out of range 1..5.")

        total = invest.get("total")
        if not isinstance(total, int):
            raise AssertionError(f"Task #{index} has non-integer total score.")

        expected_total = sum(score[dim] for dim in score)
        if total != expected_total:
            raise AssertionError(
                f"Task #{index} total score mismatch: expected {expected_total}, got {total}."
            )

        if invest.get("meets_invest") is True:
            passed += 1

    return len(tasks), passed


def _print_summary(result: Dict[str, Any], total_tasks: int, passed_tasks: int) -> None:
    failed_tasks = total_tasks - passed_tasks
    print("=== INVEST Test Summary ===")
    print(f"Total tasks: {total_tasks}")
    print(f"Tasks meeting INVEST threshold: {passed_tasks}")
    print(f"Tasks below threshold: {failed_tasks}")


def _print_failed_tasks(result: Dict[str, Any]) -> None:
    failed = []
    for index, task in enumerate(result.get("tasks", []), start=1):
        invest = task.get("invest", {})
        if not invest.get("meets_invest", False):
            failed.append((index, task, invest))

    print()
    print("=== Tasks Not Meeting INVEST ===")
    if not failed:
        print("None")
        return

    for index, task, invest in failed:
        title = task.get("title") or f"Task #{index}"
        weak = invest.get("weak_dimensions") or []
        issues = invest.get("issues") or []
        print(
            f"[{index}] {title} | total={invest.get('total')} | "
            f"grade={invest.get('grade')} | action={invest.get('recommended_action')}"
        )
        if weak:
            print(f"    weak_dimensions={', '.join(weak)}")
        if issues:
            print(f"    issues={'; '.join(issues[:3])}")


def main() -> None:
    args = _parse_args()
    try:
        payload = _load_input(args)
        result = _analyze(payload, args.min_total, args.min_dimension)
        total_tasks, passed_tasks = _validate_output(result)
    except Exception as exc:
        print(f"TEST FAILED: {exc}")
        sys.exit(1)

    _print_summary(result, total_tasks, passed_tasks)

    if args.pretty:
        print()
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

    _print_failed_tasks(result)

    print("TEST PASSED")


if __name__ == "__main__":
    main()
