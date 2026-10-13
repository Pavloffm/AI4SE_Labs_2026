# Task 3 Query Efficiency

I compare how long each SQL query takes to run and return its results. I think this makes sense because a useful answer should also arrive quickly, especially as a database grows. Speed complements accuracy because it cannot tell us whether an answer is correct.

Each query that all three approaches answered correctly was warmed up twice and timed seven times. I use the median time for each query, then summarize the results across the 128 questions shared by all three approaches. Incorrect answers are excluded from timing, so an approach cannot appear faster by returning a wrong result. Accuracy is still measured across all 155 questions. Lower times mean faster queries.

| Prompt approach | Mean ms per query | Median ms per query | Estimated total seconds | Exact accuracy |
|-----------------|-------------------|---------------------|-------------------------|----------------|
| Tree-of-Thought | 6.80              | 1.48                | 0.871                   | 89.68%         |
| STAR            | 6.78              | 1.48                | 0.868                   | 90.32%         |
| SMART           | 6.68              | 1.47                | 0.855                   | 82.58%         |

On the shared correct questions, query times were very close across all three approaches. SMART was slightly faster in this run, while also having the lowest overall accuracy. These timings describe this database and run, not model response time.
