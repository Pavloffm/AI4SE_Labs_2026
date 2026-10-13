"""Reproduce the paired accuracy and query timing analysis for Task 4."""

import csv
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
TASK2_DATA = HERE.parent / "Task_2" / "data"
TASK3_DATA = HERE.parent / "Task_3"
sys.path.insert(0, str(TASK2_DATA))
from evaluate_retrieval_predictions import load_database, row_multiset  # noqa: E402


APPROACHES = {
    "Tree of Thought": TASK2_DATA / "restaurants_dataset_predictions_tot.csv",
    "STAR": TASK2_DATA / "restaurants_dataset_predictions_star.csv",
    "SMART": TASK2_DATA / "restaurants_dataset_predictions_smart.csv",
}
TIMING_COLUMNS = {
    "Tree of Thought": "Tree-of-Thought",
    "STAR": "STAR",
    "SMART": "SMART",
}


def load_accuracy():
    csv.field_size_limit(1_000_000_000)
    with (TASK2_DATA / "restaurants_dataset.csv").open(
        encoding="utf-8", newline=""
    ) as source:
        labels = list(csv.DictReader(source))

    outcomes = {}
    connection = load_database()
    try:
        for approach, path in APPROACHES.items():
            with path.open(encoding="utf-8", newline="") as source:
                predictions = list(csv.DictReader(source))
            if [row["question"] for row in predictions] != [
                row["question"] for row in labels
            ]:
                raise ValueError(f"Question order or coverage differs in {path}")
            correct = []
            for prediction, label in zip(predictions, labels):
                actual = connection.execute(prediction["predicted_sql"]).fetchall()
                expected = json.loads(label["result"])
                correct.append(row_multiset(actual) == row_multiset(expected))
            outcomes[approach] = correct
    finally:
        connection.close()
    return outcomes


def load_timings(outcomes):
    path = TASK3_DATA / "query_efficiency_per_query.csv"
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    if any(len(values) != len(rows) for values in outcomes.values()):
        raise ValueError("Accuracy outcomes do not cover every timing row")

    shared_correct = [
        index
        for index in range(len(rows))
        if all(outcomes[approach][index] for approach in APPROACHES)
    ]
    if not shared_correct:
        raise ValueError("No questions are answered correctly by every approach")

    timings = {approach: [] for approach in APPROACHES}
    for index, row in enumerate(rows):
        for approach in APPROACHES:
            value = row[f"{TIMING_COLUMNS[approach]}_median_ms"].strip()
            if index in shared_correct:
                if not value:
                    raise ValueError(
                        f"Missing timing for shared-correct question {index + 1} "
                        f"({approach})"
                    )
                timings[approach].append(float(value))
            elif value:
                raise ValueError(
                    f"Unexpected timing for excluded question {index + 1} "
                    f"({approach})"
                )
    return rows, timings, len(shared_correct)


def wilson_interval(successes, count):
    z = 1.959963984540054
    proportion = successes / count
    denominator = 1 + z * z / count
    center = (proportion + z * z / (2 * count)) / denominator
    margin = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / count + z * z / (4 * count * count)
        )
        / denominator
    )
    return center - margin, center + margin


def exact_mcnemar(first_only, second_only):
    discordant = first_only + second_only
    if discordant == 0:
        return 1.0
    lower = min(first_only, second_only)
    one_tail = sum(math.comb(discordant, index) for index in range(lower + 1))
    return min(1.0, 2 * one_tail / (2**discordant))


def holm_adjust(p_values):
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    adjusted = {}
    running_max = 0.0
    total = len(ordered)
    for index, (name, value) in enumerate(ordered):
        running_max = max(running_max, (total - index) * value)
        adjusted[name] = min(1.0, running_max)
    return adjusted


def average_ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    tie_groups = []
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + 1 + end) / 2
        for position in range(start, end):
            ranks[order[position]] = rank
        if end - start > 1:
            tie_groups.append(end - start)
        start = end
    return ranks, tie_groups


def wilcoxon_signed_rank(first, second):
    differences = [left - right for left, right in zip(first, second)]
    nonzero = [difference for difference in differences if difference != 0]
    if not nonzero:
        return 0.0, 1.0
    ranks, _ties = average_ranks([abs(value) for value in nonzero])
    positive_rank_sum = sum(
        rank for rank, difference in zip(ranks, nonzero) if difference > 0
    )
    total_rank = sum(ranks)
    variance = sum(rank * rank for rank in ranks) / 4
    if variance == 0:
        return positive_rank_sum, 1.0
    distance = abs(positive_rank_sum - total_rank / 2)
    z = max(0.0, distance - 0.5) / math.sqrt(variance)
    p_value = math.erfc(z / math.sqrt(2))
    return positive_rank_sum, p_value


def friedman_test(columns):
    names = list(columns)
    count = len(columns[names[0]])
    rank_sums = {name: 0.0 for name in names}
    tie_correction_total = 0
    for index in range(count):
        row_ranks, ties = average_ranks([columns[name][index] for name in names])
        for name, rank in zip(names, row_ranks):
            rank_sums[name] += rank
        tie_correction_total += sum(size**3 - size for size in ties)

    groups = len(names)
    statistic = (
        12 / (count * groups * (groups + 1))
        * sum(rank_sum**2 for rank_sum in rank_sums.values())
        - 3 * count * (groups + 1)
    )
    correction = 1 - tie_correction_total / (count * (groups**3 - groups))
    if correction > 0:
        statistic /= correction
    # The chi square survival probability for two degrees of freedom is this expression.
    p_value = math.exp(-statistic / 2)
    return statistic, p_value


def accuracy_analysis(outcomes):
    count = len(next(iter(outcomes.values())))
    summary = {}
    for approach, values in outcomes.items():
        correct = sum(values)
        low, high = wilson_interval(correct, count)
        summary[approach] = {
            "correct": correct,
            "total": count,
            "accuracy_percent": correct * 100 / count,
            "wilson_95_percent": [low * 100, high * 100],
        }

    comparisons = {}
    raw_p_values = {}
    names = list(outcomes)
    for first_index, first in enumerate(names):
        for second in names[first_index + 1 :]:
            first_only = sum(
                left and not right
                for left, right in zip(outcomes[first], outcomes[second])
            )
            second_only = sum(
                right and not left
                for left, right in zip(outcomes[first], outcomes[second])
            )
            name = f"{first} versus {second}"
            p_value = exact_mcnemar(first_only, second_only)
            raw_p_values[name] = p_value
            comparisons[name] = {
                "first_only_correct": first_only,
                "second_only_correct": second_only,
                "accuracy_difference_percentage_points": (
                    summary[first]["accuracy_percent"]
                    - summary[second]["accuracy_percent"]
                ),
                "mcnemar_exact_p": p_value,
            }

    adjusted = holm_adjust(raw_p_values)
    for name, value in adjusted.items():
        comparisons[name]["holm_adjusted_p"] = value
    return summary, comparisons


def timing_analysis(timings):
    summary = {}
    for approach, values in timings.items():
        summary[approach] = {
            "mean_ms": statistics.mean(values),
            "median_ms": statistics.median(values),
            "p95_ms": sorted(values)[math.ceil(0.95 * len(values)) - 1],
        }

    overall_statistic, overall_p = friedman_test(timings)
    names = list(timings)
    comparisons = {}
    raw_p_values = {}
    for first_index, first in enumerate(names):
        for second in names[first_index + 1 :]:
            rank_sum, p_value = wilcoxon_signed_rank(
                timings[first], timings[second]
            )
            name = f"{first} versus {second}"
            raw_p_values[name] = p_value
            comparisons[name] = {
                "median_paired_difference_ms": statistics.median(
                    left - right
                    for left, right in zip(timings[first], timings[second])
                ),
                "positive_rank_sum": rank_sum,
                "wilcoxon_approximate_p": p_value,
            }

    adjusted = holm_adjust(raw_p_values)
    for name, value in adjusted.items():
        comparisons[name]["holm_adjusted_p"] = value
    return summary, {
        "friedman_statistic": overall_statistic,
        "friedman_p": overall_p,
        "pairwise": comparisons,
    }


def write_accuracy_chart(summary):
    width, height = 760, 470
    left, top, chart_width, chart_height = 92, 40, 610, 320
    colors = ["#3666a6", "#d9822b", "#32865b"]
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="380" y="25" text-anchor="middle" font-family="sans-serif" font-size="18">Exact accuracy by prompt</text>',
    ]
    for tick in range(0, 101, 20):
        y = top + chart_height * (100 - tick) / 100
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_width}" y2="{y:.1f}" stroke="#dddddd"/>')
        svg.append(f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-family="sans-serif" font-size="13">{tick}%</text>')
    for index, (approach, result) in enumerate(summary.items()):
        center = left + chart_width * (index + 0.5) / len(summary)
        bar_width = 100
        bar_height = chart_height * result["accuracy_percent"] / 100
        y = top + chart_height - bar_height
        low, high = result["wilson_95_percent"]
        low_y = top + chart_height * (100 - low) / 100
        high_y = top + chart_height * (100 - high) / 100
        svg.append(f'<rect x="{center - bar_width / 2:.1f}" y="{y:.1f}" width="{bar_width}" height="{bar_height:.1f}" fill="{colors[index]}"/>')
        svg.append(f'<line x1="{center:.1f}" y1="{high_y:.1f}" x2="{center:.1f}" y2="{low_y:.1f}" stroke="#202020" stroke-width="2"/>')
        svg.append(f'<line x1="{center - 8:.1f}" y1="{high_y:.1f}" x2="{center + 8:.1f}" y2="{high_y:.1f}" stroke="#202020" stroke-width="2"/>')
        svg.append(f'<line x1="{center - 8:.1f}" y1="{low_y:.1f}" x2="{center + 8:.1f}" y2="{low_y:.1f}" stroke="#202020" stroke-width="2"/>')
        svg.append(f'<text x="{center:.1f}" y="{y - 12:.1f}" text-anchor="middle" font-family="sans-serif" font-size="14">{result["accuracy_percent"]:.2f}%</text>')
        svg.append(f'<text x="{center:.1f}" y="{top + chart_height + 25}" text-anchor="middle" font-family="sans-serif" font-size="13">{approach}</text>')
    svg.extend([
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_height}" stroke="#222222"/>',
        f'<line x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}" stroke="#222222"/>',
        '<text x="25" y="200" transform="rotate(-90 25 200)" text-anchor="middle" font-family="sans-serif" font-size="14">Accuracy in percent</text>',
        '<text x="380" y="430" text-anchor="middle" font-family="sans-serif" font-size="12">Whiskers show Wilson 95 percent intervals</text>',
        '</svg>',
    ])
    (HERE / "task4_accuracy.svg").write_text("\n".join(svg), encoding="utf-8")


def write_latency_chart(timings):
    width, height = 820, 500
    left, top, chart_width, chart_height = 100, 50, 650, 340
    colors = ["#3666a6", "#d9822b", "#32865b"]
    all_values = [value for values in timings.values() for value in values]
    minimum = max(1.0, min(all_values))
    maximum = max(all_values)
    low_log = math.floor(math.log10(minimum))
    high_log = math.ceil(math.log10(maximum))
    if high_log == low_log:
        high_log += 1
    low, high = 10**low_log, 10**high_log

    def x_position(value):
        return left + chart_width * (math.log10(value) - low_log) / (high_log - low_log)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="410" y="27" text-anchor="middle" font-family="sans-serif" font-size="18">Per question query timing distribution</text>',
    ]
    for exponent in range(low_log, high_log + 1):
        value = 10**exponent
        x = x_position(value)
        svg.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + chart_height}" stroke="#dddddd"/>')
        svg.append(f'<text x="{x:.1f}" y="{top + chart_height + 22}" text-anchor="middle" font-family="sans-serif" font-size="13">{value}</text>')
    for tick in range(0, 101, 20):
        y = top + chart_height * (100 - tick) / 100
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_width}" y2="{y:.1f}" stroke="#eeeeee"/>')
        svg.append(f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-family="sans-serif" font-size="13">{tick}%</text>')
    for index, (approach, values) in enumerate(timings.items()):
        ordered = sorted(values)
        points = []
        for position, value in enumerate(ordered, start=1):
            x = x_position(max(value, low))
            y = top + chart_height * (1 - position / len(ordered))
            points.append(f"{x:.1f},{y:.1f}")
        svg.append(f'<polyline fill="none" stroke="{colors[index]}" stroke-width="3" points="{" ".join(points)}"/>')
        legend_y = top + 20 + index * 23
        svg.append(f'<line x1="{left + 400}" y1="{legend_y}" x2="{left + 430}" y2="{legend_y}" stroke="{colors[index]}" stroke-width="3"/>')
        svg.append(f'<text x="{left + 438}" y="{legend_y + 5}" font-family="sans-serif" font-size="13">{approach}</text>')
    svg.extend([
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_height}" stroke="#222222"/>',
        f'<line x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}" stroke="#222222"/>',
        '<text x="28" y="220" transform="rotate(-90 28 220)" text-anchor="middle" font-family="sans-serif" font-size="14">Questions at or below this time</text>',
        '<text x="425" y="455" text-anchor="middle" font-family="sans-serif" font-size="14">Query time in milliseconds on a logarithmic scale</text>',
        '</svg>',
    ])
    (HERE / "task4_latency.svg").write_text("\n".join(svg), encoding="utf-8")


def main():
    outcomes = load_accuracy()
    timing_rows, timings, timed_question_count = load_timings(outcomes)

    accuracy_summary, accuracy_tests = accuracy_analysis(outcomes)
    timing_summary, timing_tests = timing_analysis(timings)
    result = {
        "question_count": len(next(iter(outcomes.values()))),
        "timed_question_count": timed_question_count,
        "accuracy": accuracy_summary,
        "accuracy_pairwise_tests": accuracy_tests,
        "timing": timing_summary,
        "timing_tests": timing_tests,
    }
    (HERE / "task4_analysis.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    write_accuracy_chart(accuracy_summary)
    write_latency_chart(timings)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
