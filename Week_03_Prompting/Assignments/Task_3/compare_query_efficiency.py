import argparse
import csv
import json
import math
import random
import statistics
import sys
import time
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
TASK2_DATA = HERE.parent / "Task_2" / "data"
LABELS_PATH = TASK2_DATA / "restaurants_dataset.csv"
PREDICTION_FILES = {
    "Tree-of-Thought": TASK2_DATA / "restaurants_dataset_predictions_tot.csv",
    "STAR": TASK2_DATA / "restaurants_dataset_predictions_star.csv",
    "SMART": TASK2_DATA / "restaurants_dataset_predictions_smart.csv",
}

sys.path.insert(0, str(TASK2_DATA))
from evaluate_retrieval_predictions import load_database  # noqa: E402


def row_multiset(rows):
    return Counter(tuple(row) for row in rows)


def load_inputs():
    csv.field_size_limit(1_000_000_000)
    with LABELS_PATH.open(encoding="utf-8", newline="") as source:
        labels = list(csv.DictReader(source))
    expected_questions = [row["question"] for row in labels]
    expected_results = [json.loads(row["result"]) for row in labels]

    predictions = {}
    for approach, path in PREDICTION_FILES.items():
        with path.open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        if [row["question"] for row in rows] != expected_questions:
            raise ValueError(f"Question order or coverage differs in {path}")
        predictions[approach] = [row["predicted_sql"] for row in rows]

    if not expected_questions:
        raise ValueError("No labeled questions found")
    return expected_questions, expected_results, predictions


def percentile_95(values):
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def benchmark(repeats, warmups):
    questions, expected_results, predictions = load_inputs()
    connections = {}
    try:
        for approach in PREDICTION_FILES:
            connection = load_database()
            connection.execute("PRAGMA query_only = ON")
            connections[approach] = connection

        samples_ms = {name: [[] for _ in questions] for name in PREDICTION_FILES}
        output_rows = {name: [0] * len(questions) for name in PREDICTION_FILES}
        correct_by_query = {name: [False] * len(questions) for name in PREDICTION_FILES}

        # Warm each statement and check its result against the reference once.
        for approach, sql_statements in predictions.items():
            connection = connections[approach]
            for index, sql in enumerate(sql_statements):
                result = None
                for _ in range(warmups):
                    result = connection.execute(sql).fetchall()
                output_rows[approach][index] = len(result)
                if row_multiset(result) == row_multiset(expected_results[index]):
                    correct_by_query[approach][index] = True

        shared_correct = [
            index
            for index in range(len(questions))
            if all(correct_by_query[approach][index] for approach in PREDICTION_FILES)
        ]
        if not shared_correct:
            raise ValueError("No questions are answered correctly by every approach")

        # Interleave approaches and questions on each round to reduce order bias.
        rng = random.Random(2026)
        approach_names = list(PREDICTION_FILES)
        for _ in range(repeats):
            indices = shared_correct.copy()
            rng.shuffle(indices)
            for index in indices:
                round_approaches = approach_names.copy()
                rng.shuffle(round_approaches)
                for approach in round_approaches:
                    start = time.perf_counter_ns()
                    connections[approach].execute(
                        predictions[approach][index]
                    ).fetchall()
                    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
                    samples_ms[approach][index].append(elapsed_ms)

        per_query_medians = {
            approach: [
                statistics.median(query_samples) if query_samples else None
                for query_samples in queries
            ]
            for approach, queries in samples_ms.items()
        }
        summary = []
        for approach, values in per_query_medians.items():
            timed_values = [values[index] for index in shared_correct]
            summary.append(
                {
                    "approach": approach,
                    "queries": len(shared_correct),
                    "shared_correct_queries": len(shared_correct),
                    "repeats_per_query": repeats,
                    "warmups_per_query": warmups,
                    "mean_query_ms": statistics.mean(timed_values),
                    "median_query_ms": statistics.median(timed_values),
                    "p95_query_ms": percentile_95(timed_values),
                    "estimated_batch_ms": sum(timed_values),
                    "mean_rows_returned": statistics.mean(
                        output_rows[approach][index] for index in shared_correct
                    ),
                    "exact_correct": sum(correct_by_query[approach]),
                    "exact_accuracy_percent": 100 * sum(correct_by_query[approach]) / len(questions),
                }
            )

        per_query = []
        for index, question in enumerate(questions):
            row = {"question": question}
            for approach in PREDICTION_FILES:
                row[f"{approach}_median_ms"] = per_query_medians[approach][index]
                row[f"{approach}_rows_returned"] = output_rows[approach][index]
            per_query.append(row)
        return summary, per_query
    finally:
        for connection in connections.values():
            connection.close()


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(
            destination, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument(
        "--summary-csv", type=Path, default=HERE / "query_efficiency_summary.csv"
    )
    parser.add_argument(
        "--per-query-csv", type=Path, default=HERE / "query_efficiency_per_query.csv"
    )
    args = parser.parse_args()
    if args.repeats < 1 or args.warmups < 1:
        parser.error("--repeats and --warmups must be positive integers")

    summary, per_query = benchmark(args.repeats, args.warmups)
    write_csv(args.summary_csv, summary)
    write_csv(args.per_query_csv, per_query)

    print("Warm repeated SQLite execution + fetch on questions every approach answers correctly; lower latency is faster.")
    print(
        f"{'Approach':<18} {'Mean ms/query':>14} {'Median ms/query':>16} "
        f"{'P95 ms/query':>13} {'Batch ms*':>11} {'Accuracy':>10}"
    )
    for row in summary:
        print(
            f"{row['approach']:<18} {row['mean_query_ms']:>14.4f} "
            f"{row['median_query_ms']:>16.4f} {row['p95_query_ms']:>13.4f} "
            f"{row['estimated_batch_ms']:>11.2f} "
            f"{row['exact_accuracy_percent']:>9.2f}%"
        )
    print("* Estimated as the sum of per-question median latencies.")
    if summary:
        print(f"Timing questions shared by all approaches: {summary[0]['shared_correct_queries']}")
    print(f"Summary: {args.summary_csv}")
    print(f"Per-query measurements: {args.per_query_csv}")


if __name__ == "__main__":
    main()
