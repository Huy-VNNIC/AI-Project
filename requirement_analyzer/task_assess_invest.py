"""
Rule-based INVEST analyzer for generated tasks.

Usage:
    from requirement_analyzer.task_invest import (
        TaskInvestAnalyzer,
        evaluate_generated_tasks,
        evaluate_generation_response,
    )

    scored_tasks = evaluate_generated_tasks(tasks)
    scored_response = evaluate_generation_response({"tasks": tasks})

CLI:
    python -m requirement_analyzer.task_invest path/to/tasks.json
    python -m requirement_analyzer.task_invest --stdin < response.json
"""

from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union


DEFAULT_MIN_TOTAL = 20
DEFAULT_MIN_DIMENSION = 3
SMALL_WORD_THRESHOLD = 100
VERY_LARGE_WORD_THRESHOLD = 180
SMALL_AC_THRESHOLD = 5
HIGH_STORY_POINTS = 8

DEPENDENCY_PATTERNS = (
    r"\bdepends on\b",
    r"\brequires\b",
    r"\bblocked by\b",
    r"\bafter\b",
    r"\bbefore this\b",
    r"phụ thuộc",
    r"cần hoàn thành trước",
    r"sau khi",
    r"chờ ",
)
PRESCRIPTIVE_PATTERNS = (
    r"\bmust use only\b",
    r"\buse exactly\b",
    r"\bdo not change\b",
    r"\bbắt buộc\b",
    r"\bchỉ được dùng\b",
    r"\bkhông được thay đổi\b",
)
VALUE_PATTERNS = (
    r"\bas a\b",
    r"\buser\b",
    r"\bcustomer\b",
    r"\badmin\b",
    r"\boperator\b",
    r"\bngười dùng\b",
    r"\bkhách hàng\b",
    r"\bquản trị\b",
    r"\bbusiness\b",
    r"\bvalue\b",
)
VAGUE_PATTERNS = (
    r"\btbd\b",
    r"\bmaybe\b",
    r"\bsomehow\b",
    r"\bappropriate\b",
    r"\buser-friendly\b",
    r"\boptimize\b",
    r"chưa rõ",
    r"để sau",
    r"nếu cần",
)
TESTABLE_BAD_PATTERNS = (
    r"\bfast\b",
    r"\bsecure\b",
    r"\bintuitive\b",
    r"\beasy to use\b",
    r"\brobust\b",
    r"\btốt\b",
    r"\ban toàn\b",
    r"\bthân thiện\b",
)
TECHNICAL_ONLY_PATTERNS = (
    r"\brefactor\b",
    r"\bcleanup\b",
    r"\bmigration\b",
    r"\binfrastructure\b",
    r"\binternal\b",
    r"\bmiddleware\b",
    r"\bdb schema\b",
    r"\bdatabase schema\b",
)


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _normalize_acceptance_criteria(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    text = str(raw).strip()
    return [text] if text else []


def _contains_any(text: str, patterns: Sequence[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _count_matches(text: str, patterns: Sequence[str]) -> int:
    return sum(1 for pattern in patterns if re.search(pattern, text, re.IGNORECASE))


def _unique(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


@dataclass
class TaskSnapshot:
    task_id: Optional[str]
    title: str
    description: str
    acceptance_criteria: List[str]
    story_points: Optional[int]
    dependencies: List[str]
    labels: List[str]
    type: Optional[str]
    role: Optional[str]

    @property
    def full_text(self) -> str:
        return "\n".join(
            [self.title, self.description, *self.acceptance_criteria]
        ).strip()

    @property
    def word_count(self) -> int:
        return len(self.full_text.split())


@dataclass
class DimensionResult:
    score: int
    reasons: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class TaskInvestAnalyzer:
    """Rule-based analyzer for INVEST quality on generated tasks."""

    def __init__(
        self,
        min_total: int = DEFAULT_MIN_TOTAL,
        min_dimension: int = DEFAULT_MIN_DIMENSION,
    ) -> None:
        self.min_total = min_total
        self.min_dimension = min_dimension

    def analyze_task(self, task: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        snapshot = self._coerce_task(task)
        dimensions = {
            "independent": self._score_independent(snapshot),
            "negotiable": self._score_negotiable(snapshot),
            "valuable": self._score_valuable(snapshot),
            "estimable": self._score_estimable(snapshot),
            "small": self._score_small(snapshot),
            "testable": self._score_testable(snapshot),
        }
        total = sum(result.score for result in dimensions.values())
        weak_dimensions = [
            name for name, result in dimensions.items()
            if result.score < self.min_dimension
        ]

        issues = _unique(
            reason
            for result in dimensions.values()
            for reason in result.reasons
        )
        suggestions = _unique(
            suggestion
            for result in dimensions.values()
            for suggestion in result.suggestions
        )

        if not weak_dimensions and total >= self.min_total:
            recommended_action = "keep"
        elif "small" in weak_dimensions:
            recommended_action = "split"
        elif "independent" in weak_dimensions:
            recommended_action = "review_dependencies"
        else:
            recommended_action = "refine"

        return {
            "score": {
                name: result.score for name, result in dimensions.items()
            },
            "total": total,
            "grade": self._grade(total),
            "meets_invest": total >= self.min_total and not weak_dimensions,
            "weak_dimensions": weak_dimensions,
            "issues": issues,
            "suggestions": suggestions,
            "recommended_action": recommended_action,
            "thresholds": {
                "min_total": self.min_total,
                "min_dimension": self.min_dimension,
            },
        }

    def analyze_tasks(
        self,
        tasks: Sequence[Union[Dict[str, Any], Any]],
        inplace: bool = False,
    ) -> List[Dict[str, Any]]:
        analyzed: List[Dict[str, Any]] = []
        for task in tasks:
            base = task if inplace else deepcopy(task)
            if hasattr(base, "model_dump"):
                base = base.model_dump()
            elif hasattr(base, "dict") and not isinstance(base, dict):
                base = base.dict()
            if not isinstance(base, dict):
                raise TypeError("Each task must be a dict-like object or GeneratedTask")
            base["invest"] = self.analyze_task(base)
            analyzed.append(base)
        return analyzed

    def analyze_response(
        self,
        payload: Dict[str, Any],
        inplace: bool = False,
    ) -> Dict[str, Any]:
        result = payload if inplace else deepcopy(payload)
        tasks = result.get("tasks")
        if isinstance(tasks, list):
            result["tasks"] = self.analyze_tasks(tasks, inplace=False)
        return result

    def _coerce_task(self, task: Union[Dict[str, Any], Any]) -> TaskSnapshot:
        if hasattr(task, "model_dump"):
            raw = task.model_dump()
        elif hasattr(task, "dict") and not isinstance(task, dict):
            raw = task.dict()
        elif isinstance(task, dict):
            raw = task
        else:
            raise TypeError("Task must be a dict-like object or GeneratedTask")

        return TaskSnapshot(
            task_id=raw.get("task_id"),
            title=str(raw.get("title") or "").strip(),
            description=str(raw.get("description") or "").strip(),
            acceptance_criteria=_normalize_acceptance_criteria(raw.get("acceptance_criteria")),
            story_points=_safe_int(raw.get("story_points")),
            dependencies=[str(item).strip() for item in raw.get("dependencies", []) if str(item).strip()],
            labels=[str(item).strip() for item in raw.get("labels", []) if str(item).strip()],
            type=str(raw.get("type") or "").strip() or None,
            role=str(raw.get("role") or "").strip() or None,
        )

    def _score_independent(self, task: TaskSnapshot) -> DimensionResult:
        score = 5
        reasons: List[str] = []
        suggestions: List[str] = []
        text = task.full_text.lower()

        if task.dependencies:
            score -= 2
            reasons.append("Task khai báo dependency trực tiếp.")
            suggestions.append("Tách bớt dependency hoặc chuyển dependency thành contract rõ ràng.")
        if _contains_any(text, DEPENDENCY_PATTERNS):
            score -= 2
            reasons.append("Task mô tả theo chuỗi phụ thuộc với task khác.")
            suggestions.append("Viết lại task để nó có thể hoàn thành độc lập hơn.")
        if task.word_count > VERY_LARGE_WORD_THRESHOLD:
            score -= 1
            reasons.append("Task quá dài, thường kéo theo nhiều phần phụ thuộc.")

        return DimensionResult(score=max(1, score), reasons=reasons, suggestions=suggestions)

    def _score_negotiable(self, task: TaskSnapshot) -> DimensionResult:
        score = 5
        reasons: List[str] = []
        suggestions: List[str] = []
        text = task.full_text.lower()

        if _contains_any(text, PRESCRIPTIVE_PATTERNS):
            score -= 2
            reasons.append("Task chốt cứng giải pháp kỹ thuật hoặc ràng buộc implementation.")
            suggestions.append("Giữ mục tiêu và acceptance criteria, bớt khóa cứng công nghệ khi không bắt buộc.")
        if len(task.acceptance_criteria) >= 6:
            score -= 1
            reasons.append("Task có quá nhiều acceptance criteria, dễ thành spec đóng cứng.")
            suggestions.append("Tách task hoặc gom AC theo outcome chính.")

        return DimensionResult(score=max(1, score), reasons=reasons, suggestions=suggestions)

    def _score_valuable(self, task: TaskSnapshot) -> DimensionResult:
        score = 3
        reasons: List[str] = []
        suggestions: List[str] = []
        text = task.full_text.lower()

        if _contains_any(text, VALUE_PATTERNS):
            score += 2
        else:
            reasons.append("Task chưa thể hiện rõ actor hoặc giá trị người dùng/business.")
            suggestions.append("Viết lại theo outcome: ai nhận giá trị gì từ task này.")

        if _contains_any(text, TECHNICAL_ONLY_PATTERNS) and not _contains_any(text, VALUE_PATTERNS):
            score -= 2
            reasons.append("Task thiên về kỹ thuật nội bộ, khó hiện ra business value.")
            suggestions.append("Liên kết task kỹ thuật với user story hoặc capability cụ thể.")

        return DimensionResult(score=max(1, min(5, score)), reasons=reasons, suggestions=suggestions)

    def _score_estimable(self, task: TaskSnapshot) -> DimensionResult:
        score = 5
        reasons: List[str] = []
        suggestions: List[str] = []
        text = task.full_text.lower()
        vague_hits = _count_matches(text, VAGUE_PATTERNS)

        if not task.description:
            score -= 2
            reasons.append("Task thiếu description.")
            suggestions.append("Bổ sung phạm vi, đầu vào, đầu ra và constraint chính.")
        if not task.acceptance_criteria:
            score -= 2
            reasons.append("Task thiếu acceptance criteria.")
            suggestions.append("Thêm acceptance criteria cụ thể để estimate chắc hơn.")
        elif len(task.acceptance_criteria) == 1:
            score -= 1
            reasons.append("Task mới có 1 acceptance criterion, thông tin estimate còn mỏng.")
        if vague_hits:
            score -= min(2, vague_hits)
            reasons.append("Task chứa ngôn ngữ mơ hồ hoặc placeholder.")
            suggestions.append("Loại bỏ từ mơ hồ như TBD, maybe, appropriate và thay bằng tiêu chí rõ ràng.")

        return DimensionResult(score=max(1, score), reasons=reasons, suggestions=suggestions)

    def _score_small(self, task: TaskSnapshot) -> DimensionResult:
        score = 5
        reasons: List[str] = []
        suggestions: List[str] = []

        if task.story_points is not None and task.story_points > HIGH_STORY_POINTS:
            score -= 3
            reasons.append("Story points cao, task có khả năng quá lớn.")
            suggestions.append("Tách task theo flow, role hoặc acceptance criteria.")
        elif task.story_points is not None and task.story_points > 5:
            score -= 2
            reasons.append("Story points vượt ngưỡng task nhỏ.")
            suggestions.append("Kiểm tra có thể chia nhỏ theo từng outcome hay không.")

        if task.word_count > VERY_LARGE_WORD_THRESHOLD:
            score -= 2
            reasons.append("Task có mô tả quá dài.")
        elif task.word_count > SMALL_WORD_THRESHOLD:
            score -= 1
            reasons.append("Task khá dài, có thể đang ôm nhiều scope.")

        if len(task.acceptance_criteria) > SMALL_AC_THRESHOLD:
            score -= 2
            reasons.append("Task có quá nhiều acceptance criteria.")
            suggestions.append("Chia task thành các backlog item nhỏ hơn.")
        elif len(task.acceptance_criteria) > 3:
            score -= 1

        return DimensionResult(score=max(1, score), reasons=reasons, suggestions=suggestions)

    def _score_testable(self, task: TaskSnapshot) -> DimensionResult:
        score = 5
        reasons: List[str] = []
        suggestions: List[str] = []
        ac_text = " ".join(task.acceptance_criteria).lower()

        if not task.acceptance_criteria:
            score = 1
            reasons.append("Task không có acceptance criteria để kiểm thử.")
            suggestions.append("Thêm acceptance criteria dạng pass/fail.")
            return DimensionResult(score=score, reasons=reasons, suggestions=suggestions)

        if len(task.acceptance_criteria) == 1:
            score -= 1
            reasons.append("Task chỉ có một acceptance criterion.")
        if _contains_any(ac_text, TESTABLE_BAD_PATTERNS):
            score -= 2
            reasons.append("Acceptance criteria dùng từ định tính, khó verify khách quan.")
            suggestions.append("Đổi sang điều kiện đo được hoặc quan sát được.")
        if not re.search(r"\b(if|when|then|must|should|can|under|within|less than|greater than)\b", ac_text, re.IGNORECASE):
            score -= 1
            reasons.append("Acceptance criteria thiếu cấu trúc điều kiện/kỳ vọng rõ ràng.")
            suggestions.append("Viết AC theo dạng điều kiện và kết quả mong đợi.")

        return DimensionResult(score=max(1, score), reasons=reasons, suggestions=suggestions)

    def _grade(self, total: int) -> str:
        if total >= 25:
            return "Excellent"
        if total >= 20:
            return "Good"
        if total >= 15:
            return "Fair"
        return "Poor"


def score_task(
    task: Union[Dict[str, Any], Any],
    *,
    min_invest_total: int = DEFAULT_MIN_TOTAL,
    min_per_dimension: int = DEFAULT_MIN_DIMENSION,
) -> Dict[str, Any]:
    analyzer = TaskInvestAnalyzer(
        min_total=min_invest_total,
        min_dimension=min_per_dimension,
    )
    return analyzer.analyze_task(task)


def evaluate_generated_tasks(
    tasks: Sequence[Union[Dict[str, Any], Any]],
    *,
    min_invest_total: int = DEFAULT_MIN_TOTAL,
    min_per_dimension: int = DEFAULT_MIN_DIMENSION,
    inplace: bool = False,
) -> List[Dict[str, Any]]:
    analyzer = TaskInvestAnalyzer(
        min_total=min_invest_total,
        min_dimension=min_per_dimension,
    )
    return analyzer.analyze_tasks(tasks, inplace=inplace)


def evaluate_generation_response(
    data: Dict[str, Any],
    *,
    min_invest_total: int = DEFAULT_MIN_TOTAL,
    min_per_dimension: int = DEFAULT_MIN_DIMENSION,
    inplace: bool = False,
) -> Dict[str, Any]:
    analyzer = TaskInvestAnalyzer(
        min_total=min_invest_total,
        min_dimension=min_per_dimension,
    )
    return analyzer.analyze_response(data, inplace=inplace)


def load_tasks_from_json_file(path: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    with open(path, encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "tasks" in data:
        return data
    raise ValueError("JSON must be a task list or an object containing a 'tasks' field.")


def _main(argv: Optional[List[str]] = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return

    if args[0] == "--stdin":
        data = json.loads(sys.stdin.read())
    else:
        data = load_tasks_from_json_file(args[0])

    if isinstance(data, list):
        output = {
            "tasks": evaluate_generated_tasks(data),
            "total_tasks": len(data),
        }
    else:
        output = evaluate_generation_response(data)

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))


__all__ = [
    "TaskInvestAnalyzer",
    "score_task",
    "evaluate_generated_tasks",
    "evaluate_generation_response",
    "load_tasks_from_json_file",
]


if __name__ == "__main__":
    _main()
