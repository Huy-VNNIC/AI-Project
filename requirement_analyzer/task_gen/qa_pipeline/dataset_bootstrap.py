"""
Dataset bootstrap for the QA pipeline.

Reads a corpus of requirement strings, runs them through the full
4-stage pipeline, and writes a JSONL dataset.  The output can later be
used to train a category-prediction classifier or as ground-truth
fixtures for regression tests.

Run:
    python -m requirement_analyzer.task_gen.qa_pipeline.dataset_bootstrap \\
        --corpus path/to/requirements.txt \\
        --out data/qa_dataset.jsonl

If --corpus is omitted, a built-in seed corpus (~30 bilingual reqs) is used.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable, List

from .pipeline import QAPipeline


SEED_CORPUS: List[str] = [
    # healthcare
    "Patient must register an account with email verification before booking.",
    "Patient books an appointment with a selected doctor and time slot.",
    "The system shall reject booking when the slot is already taken.",
    "Doctor can cancel an appointment up to 24 hours before the start time.",
    "Bệnh nhân có thể xem lịch sử khám bệnh trong 12 tháng gần nhất.",
    "Hệ thống phải mã hoá hồ sơ bệnh án khi lưu trữ và truyền tải.",
    # ecommerce
    "Customer adds a product to the cart and proceeds to checkout.",
    "Customer applies a discount code at checkout.",
    "Order is rejected when payment authorization fails.",
    "Khách hàng có thể trả hàng trong vòng 7 ngày kể từ khi nhận hàng.",
    # finance / payment
    "Payment must be encrypted in transit and at rest.",
    "User can transfer money between own accounts up to 100M VND per day.",
    "Withdrawal is rejected when the account balance is insufficient.",
    "Hệ thống phải khoá tài khoản sau 5 lần đăng nhập sai liên tiếp.",
    # auth / security
    "User logs in with email and password.",
    "Password reset link must expire after 30 minutes.",
    "Admin can view audit logs but cannot modify them.",
    "Người dùng có thể bật xác thực hai yếu tố qua ứng dụng OTP.",
    # performance / NFR
    "The login endpoint must respond in under 2 seconds for 100 concurrent users.",
    "The product search must return results within 500 ms.",
    # education
    "Teacher uploads a list of students from a CSV file.",
    "Student submits an assignment before the deadline.",
    "Hệ thống tự động tính điểm khi học sinh nộp bài trắc nghiệm.",
    # hotel
    "Guest searches for rooms by date range and number of guests.",
    "Guest cancels a reservation and receives a refund according to policy.",
    # iot
    "Device sends temperature readings every 30 seconds to the gateway.",
    "Gateway raises an alert when reading exceeds the configured threshold.",
    # data integrity / misc
    "User uploads a profile photo not exceeding 5 MB.",
    "Người dùng có thể tìm kiếm sản phẩm theo từ khoá và lọc theo giá.",
    "Admin exports a CSV report of all transactions for the previous month.",
]


def load_corpus(path: str | None) -> List[str]:
    if not path:
        return SEED_CORPUS
    p = Path(path)
    if not p.exists():
        print(f"⚠ corpus not found: {path} — falling back to seed", file=sys.stderr)
        return SEED_CORPUS
    out: List[str] = []
    for ln in p.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln and len(ln.split()) >= 3 and not ln.startswith("#"):
            out.append(ln)
    return out or SEED_CORPUS


def build_dataset(reqs: Iterable[str], out_path: str) -> dict:
    pipe = QAPipeline()
    out = pipe.run("\n".join(reqs))
    parsed = out.parsed
    cases = out.test_cases

    # group cases per requirement_ref
    by_req: dict = {}
    for tc in cases:
        by_req.setdefault(tc.requirement_ref, []).append(tc)
    by_req_sc: dict = {}
    for sc, p in zip(out.scenarios,
                     # rebuild ref index from order
                     []):
        pass
    # easier: rerun per-req for cleaner alignment
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for idx, p in enumerate(parsed, 1):
            ref = f"REQ-{idx:03d}"
            single = pipe.run(p.raw)   # re-run a single req for clean per-req payload
            row = {
                "requirement":  p.raw,
                "ref":          ref,
                "parsed":       single.parsed[0].to_dict() if single.parsed else p.to_dict(),
                "scenarios":    [s.to_dict() for s in single.scenarios],
                "test_cases":   [tc.to_dict() for tc in single.test_cases],
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1

    return {
        "rows":         n,
        "out_path":     out_path,
        "total_cases":  sum(len(v["test_cases"]) for v in
                            [json.loads(l) for l in
                             Path(out_path).read_text(encoding="utf-8").splitlines()]),
    }


def maybe_train_classifier(jsonl_path: str, model_out: str) -> dict | None:
    """Optional: train a small TF-IDF + LogisticRegression classifier
    that maps requirement text → most likely scenario category mix.

    Returns a small report dict; skips silently if sklearn isn't available.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        import joblib
    except ImportError:
        return None

    X: List[str] = []
    y: List[str] = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            req = row["requirement"]
            for tc in row["test_cases"]:
                X.append(req)
                y.append(tc["category"])
    if len(set(y)) < 2:
        return None

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=5000)),
        ("clf",   LogisticRegression(max_iter=1000, n_jobs=None)),
    ])
    pipe.fit(X, y)
    Path(model_out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, model_out)
    return {
        "model_path":  model_out,
        "samples":     len(X),
        "classes":     sorted(set(y)),
        "train_score": float(pipe.score(X, y)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=None,
                    help="path to a .txt file with one requirement per line")
    ap.add_argument("--out", default="data/qa_dataset.jsonl")
    ap.add_argument("--train", action="store_true",
                    help="also train a TF-IDF category classifier")
    ap.add_argument("--model-out", default="models/qa_category.joblib")
    args = ap.parse_args()

    reqs = load_corpus(args.corpus)
    print(f"→ loaded {len(reqs)} requirements")
    info = build_dataset(reqs, args.out)
    print(f"✓ wrote {info['rows']} rows · {info['total_cases']} test cases → {args.out}")

    if args.train:
        report = maybe_train_classifier(args.out, args.model_out)
        if report is None:
            print("⚠ scikit-learn not installed or not enough classes — skipped training")
        else:
            print(f"✓ trained classifier → {report['model_path']}  "
                  f"({report['samples']} samples, train_acc={report['train_score']:.3f})")


if __name__ == "__main__":
    main()
