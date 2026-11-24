# Assessment by laguna-s-2.1
# Week 03 Prompting
- Awarded: 4.5b out of 5b
- Commentary: The student demonstrates a strong end-to-end pipeline: selecting three prompting frameworks (Tree of Thought, STAR, SMART), adapting them to SQL generation over a restaurant database, and producing predictions, accuracy reports, a novel query-latency metric with implementation, and a full statistical analysis with visualizations. Task 2 is solid overall — predictions and a visualization are present — but inference time measurement was explicitly not done, which is a required deliverable. Task 4 is especially thorough, with exact McNemar and Friedman/Wilcoxon tests, Wilson intervals, and two SVG charts. No images were unreadable.

## Task 1
- Awarded: 1b   (max 1b)
- Commentary: Three prompting frameworks were correctly chosen from https://frompting.com (Tree of Thought, STAR, SMART — none being ROSES or zero-shot as prohibited). Each prompt is formulated as a structured template with placeholders and an explicit output format matching its framework. For each framework the student explains why it was chosen and provides the source URL, and the output is a data file (Solution_1.md) containing both the formulated prompts and the rationale. This satisfies all stated requirements.

## Task 2
- Awarded: 0.5b   (max 1b)
- Commentary: The student adapted the three Task 1 frameworks to SQL generation over the restaurant database, producing three prediction CSVs (restaurants_dataset_predictions_tot.csv, _star.csv, _smart.csv) with question and predicted_sql columns and prompt identification by filename. A brief report (Task_2_Report.md) compares accuracy across the three approaches and includes a visualization (task2_accuracy.svg). Scores: Tree-of-Thought 139/155 (89.68%), STAR 140/155 (90.32%), SMART 128/155 (82.58%). However, the assignment explicitly requires that inference times be measured ("Make sure to measure inference times"), and the student explicitly states these were not recorded. This missing required element prevents full credit.

## Task 3
- Awarded: 1b   (max 1b)
- Commentary: The student proposes query execution latency as a new metric, arguing that a fast answer complements accuracy (it cannot verify correctness). The metric is implemented in compare_query_efficiency.py with warmups, repeated interleaved runs, per-question medians, and shared-correct filtering so incorrect results do not bias timing. Result files (query_efficiency_summary.csv, query_efficiency_per_query.csv) and a report (Task_3_Report.md) present the values and comparison. The student discusses how the metric complements rather than replaces the accuracy metric. All requirements are satisfied.

## Task 4
- Awarded: 2b   (max 2b)
- Commentary: The report (Task_4_Report.md) provides a detailed reiteration of the comparison using both accuracy and query latency. It includes accuracy tables with Wilson 95% intervals and two SVG charts (task4_accuracy.svg, task4_latency.svg). Statistical significance is determined with exact McNemar tests (Holm-adjusted) for accuracy and a Friedman test with pairwise Wilcoxon signed-rank tests (Holm-adjusted) for timing. The analysis correctly concludes that SMART differs significantly from the other two on accuracy, while timing differences are not significant. The student explains the results by considering the prompts, the model, and the coding agent, and explicitly acknowledges the limitation that saved predictions do not isolate model/agent effects. A reproducible implementation (analyze_task4.py) and machine-readable output (task4_analysis.json) are included. This fully satisfies all requirements.
