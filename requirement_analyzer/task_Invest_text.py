import re
from typing import List, Dict

# INVEST criteria checker and refiner + Task -> User Story generator

USER_STORY_PATTERN = r"As (?:a|an|the) .+, I want .+"
FULL_USER_STORY_PATTERN = r"As (?:a|an|the) .+, I want .+, so that .+"

class InvestAnalyzer:
    def __init__(self):
        pass

    def analyze_many(self, text: str) -> List[Dict]:
        """
        Analyze one input that may contain multiple tasks combined together.
        """
        if self._is_user_story(text):
            return [self._analyze_user_story(text)]

        decomposed_results = self._decompose_requirement(text)
        if decomposed_results:
            return decomposed_results

        sub_tasks = self._split_composite_task(text)
        if len(sub_tasks) <= 1:
            return [self._analyze_task(text)]

        results = []
        for sub_task in sub_tasks:
            analysis = self._analyze_task(sub_task)
            analysis["source_task"] = text
            analysis["issues"].insert(0, "Composite task detected and split into smaller user stories.")
            results.append(analysis)
        return results

    def _decompose_requirement(self, text: str) -> List[Dict]:
        """
        Domain-oriented decomposition for large management requirements.
        """
        normalized = re.sub(r"\s+", " ", text.strip())
        lower = normalized.lower()

        if "quản lý hồ sơ bệnh nhân" in lower or "manage patient record" in lower or "patient record" in lower:
            return self._build_patient_record_stories(normalized)

        return []

    def _build_patient_record_stories(self, original_text: str) -> List[Dict]:
        story_specs = [
            {
                "title": "Patient Record Management - Happy Path",
                "story": "As a Nurse, I want to create patient record, so that I can store patient info",
                "acceptance_criteria": [
                    'When nurse clicks "Add Patient", form appears with required fields',
                    "When valid personal information is submitted, the patient record is saved successfully",
                ],
                "note": "Happy path flow for creating a patient profile."
            },
            {
                "title": "Patient Record Management - Edge Cases & Validation",
                "story": "As a Nurse, I want the patient record form to validate duplicate IDs and missing information, so that inaccurate records are prevented",
                "acceptance_criteria": [
                    "Validate duplicate patient ID",
                    "Handle incomplete information",
                ],
                "note": "Validation and edge cases for patient record management."
            },
            {
                "title": "Patient Record Management - CRUD Create",
                "story": "As a Nurse, I want to create new patient record in system, so that I can register a patient for treatment",
                "acceptance_criteria": [
                    "Create new patient record in system",
                ],
                "note": "CRUD create flow."
            },
            {
                "title": "Patient Record Management - CRUD Read",
                "story": "As a Nurse, I want to view and search patient records by ID or name, so that I can access patient history quickly",
                "acceptance_criteria": [
                    "View/Search patient records by ID or name",
                    "Display personal information, medical history, lab results, and treatment history",
                ],
                "note": "CRUD read flow."
            },
            {
                "title": "Patient Record Management - CRUD Update",
                "story": "As a Nurse, I want to update patient information and history, so that the record stays accurate during treatment",
                "acceptance_criteria": [
                    "Update patient information, history",
                ],
                "note": "CRUD update flow."
            },
        ]

        results = []
        for spec in story_specs:
            analysis = self._analyze_user_story(spec["story"])
            analysis["title"] = spec["title"]
            analysis["original"] = original_text
            analysis["generated_from_task"] = spec["story"]
            analysis["acceptance_criteria"] = spec["acceptance_criteria"]
            analysis["issues"].insert(0, f"Requirement decomposed into story slice: {spec['note']}")
            results.append(analysis)
        return results

    def analyze(self, text: str) -> Dict:
        """
        Detect input type:
        - If already a user story → refine
        - If task → convert to user story first
        """

        if self._is_user_story(text):
            return self._analyze_user_story(text)
        else:
            return self._analyze_task(text)

    # ---------------- DETECTION ----------------
    def _is_user_story(self, text: str) -> bool:
        return bool(re.search(USER_STORY_PATTERN, text, re.IGNORECASE))

    # ---------------- TASK HANDLING ----------------
    def _analyze_task(self, task: str) -> Dict:
        generated_story = self._task_to_user_story(task)
        analysis = self._analyze_user_story(generated_story)

        analysis["original"] = task
        analysis["generated_from_task"] = generated_story
        analysis["issues"].insert(0, "Input detected as a task and converted into a user story.")

        return analysis

    def _split_composite_task(self, task: str) -> List[str]:
        """
        Split a large combined task into smaller task phrases.
        """
        normalized = task.strip()
        if not normalized:
            return []

        normalized = re.sub(r"\s+", " ", normalized)
        normalized = re.sub(r"\s+(in|on|for)\s+one\s+(screen|page|flow)\b", "", normalized, flags=re.IGNORECASE)

        leading_match = re.match(r"^(create|build|implement|add|fix|update)\s+", normalized, re.IGNORECASE)
        leading_verb = leading_match.group(1).lower() if leading_match else ""
        remainder = re.sub(r"^(create|build|implement|add|fix|update)\s+", "", normalized, flags=re.IGNORECASE)

        parts = [
            piece.strip(" ,.")
            for piece in re.split(r",| and | & ", remainder, flags=re.IGNORECASE)
            if piece.strip(" ,.")
        ]

        if len(parts) <= 1:
            return [task.strip()]

        result = []
        for index, part in enumerate(parts):
            part = self._normalize_task_phrase(part, leading_verb if index == 0 else "")
            result.append(part)
        return result

    def _normalize_task_phrase(self, task: str, fallback_verb: str = "") -> str:
        task = task.strip().lower()

        replacements = {
            "forgot password": "reset password",
            "social login": "support social login",
            "audit log": "view audit logs",
            "admin dashboard": "access the admin dashboard",
        }

        for source, target in replacements.items():
            if task == source:
                return target

        if re.match(r"^(login|log in)$", task):
            return "log in"
        if re.match(r"^(register|signup|sign up)$", task):
            return "register an account"

        if re.match(r"^(create|build|implement|add|fix|update)\s+", task):
            return task

        if fallback_verb:
            return f"{fallback_verb} {task}"

        return task

    def _task_to_user_story(self, task: str) -> str:
        """
        Convert task → basic user story
        """

        task = task.strip().lower()

        # Heuristic role detection
        if any(k in task for k in ["admin", "manage", "dashboard"]):
            role = "admin"
        elif any(k in task for k in ["login", "register", "user", "account"]):
            role = "user"
        else:
            role = "user"

        # Clean verb
        task_clean = re.sub(r"^(create|build|implement|add|fix|update)\s+", "", task)

        return f"As a {role}, I want to {task_clean}, so that I can use the feature effectively"

    # ---------------- USER STORY ANALYSIS ----------------
    def _analyze_user_story(self, story: str) -> Dict:
        result = {
            "original": story,
            "issues": [],
            "refined": story
        }
        criteria = self._evaluate_invest_criteria(story)

        # Check standard format
        if not re.search(FULL_USER_STORY_PATTERN, story, re.IGNORECASE):
            result["issues"].append("❌ Missing standard format")
            story = self._fix_format(story)

        # Check Small
        if len(story.split()) > 30:
            result["issues"].append("❌ Story too large (not SMALL)")
            story = self._make_smaller(story)

        # Check Testable
        if "so that" not in story.lower():
            result["issues"].append("❌ Not TESTABLE")
            story += " so that the system behavior can be verified"

        # Check Valuable
        if re.search(r"so that (something|stuff|things)", story, re.IGNORECASE):
            result["issues"].append("❌ Weak VALUE")
            story = re.sub(r"something|stuff|things", "I achieve a clear benefit", story, flags=re.IGNORECASE)

        # Check Estimable
        if re.search(r"improve|optimize|enhance", story, re.IGNORECASE):
            result["issues"].append("❌ Not ESTIMABLE")
            story = self._make_estimable(story)

        result["refined"] = story
        result["criteria"] = criteria
        result["score"] = sum(1 for item in criteria.values() if item["pass"])
        return result

    def _evaluate_invest_criteria(self, story: str) -> Dict:
        lower = story.lower()
        word_count = len(story.split())
        has_value = "so that" in lower
        has_standard_format = bool(re.search(FULL_USER_STORY_PATTERN, story, re.IGNORECASE))
        has_large_scope = bool(re.search(r"\band\b|\bor\b|including|all|everything|dashboard|module|system|end-to-end|complete", lower))
        locked_solution = bool(re.search(r"using|with react|with vue|with java|mysql|postgres|redis|microservice|specific library", lower))
        vague_terms = bool(re.search(r"improve|optimize|enhance|something|stuff|things|etc|maybe|somehow", lower))
        test_hint = bool(re.search(r"so that|if|when|then|given|must|should|validate|success|error|within|under", lower))

        return {
            "independent": {
                "pass": not has_large_scope or word_count < 18,
                "reason": "The story looks reasonably independent." if (not has_large_scope or word_count < 18) else "The story appears to bundle multiple scopes and should be split."
            },
            "negotiable": {
                "pass": not locked_solution,
                "reason": "The story focuses on the business need." if not locked_solution else "The story locks the team into a technical solution too early."
            },
            "valuable": {
                "pass": has_value,
                "reason": "The story clearly states the expected value." if has_value else "Add the value statement after 'so that'."
            },
            "estimable": {
                "pass": word_count >= 8 and not vague_terms,
                "reason": "There is enough detail to estimate." if (word_count >= 8 and not vague_terms) else "The story is too vague or too short to estimate well."
            },
            "small": {
                "pass": word_count <= 30 and not has_large_scope,
                "reason": "The scope looks small enough." if (word_count <= 30 and not has_large_scope) else "The scope may be too large for a single story."
            },
            "testable": {
                "pass": has_standard_format or test_hint,
                "reason": "The story can be verified with acceptance criteria." if (has_standard_format or test_hint) else "Add clearer test conditions or acceptance criteria."
            }
        }

    # ---------------- FIX METHODS ----------------
    def _fix_format(self, story: str) -> str:
        return f"As a user, I want {story.strip()}, so that I can achieve my goal"

    def _make_smaller(self, story: str) -> str:
        parts = story.split(',')
        return parts[0] if parts else story

    def _make_estimable(self, story: str) -> str:
        return re.sub(
            r"improve|optimize|enhance",
            "specifically improve measurable performance",
            story,
            flags=re.IGNORECASE
        )


# ---------------- CLI ----------------

def refine_user_stories(inputs: List[str]):
    analyzer = InvestAnalyzer()

    for i, text in enumerate(inputs, 1):
        results = analyzer.analyze_many(text)

        for j, result in enumerate(results, 1):
            print(f"\n=== Item {i}.{j} ===")
            print(f"Input: {result['original']}")

            if "source_task" in result:
                print(f"Source Task: {result['source_task']}")

            if "generated_from_task" in result:
                print(f"Generated User Story: {result['generated_from_task']}")

            if result["issues"]:
                print("Issues:")
                for issue in result["issues"]:
                    print(f" - {issue}")
            else:
                print("✅ Meets INVEST")

            print(f"Refined: {result['refined']}")


if __name__ == "__main__":
    print("Enter tasks or user stories (type 'END' to finish):")
    inputs = []

    while True:
        line = input("> ")
        if line.strip().upper() == "END":
            break
        if line.strip():
            inputs.append(line.strip())

    refine_user_stories(inputs)
