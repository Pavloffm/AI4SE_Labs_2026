# Task 2 Prompt Approaches

For Task 2, I adapted the three methods from Task 1 to the restaurant database. Each CSV contains SQL that returns `LOCATION.HOUSE_NUMBER` and `RESTAURANT.NAME`, in the same order as the reference results.

## Tree of Thought

File: `restaurants_dataset_predictions_tot.csv`

I compared possible interpretations of each question, checked which tables and filters were needed, then chose a query. For questions asking for the best restaurant, the query sorts by rating and returns the top result.

## STAR

File: `restaurants_dataset_predictions_star.csv`

I used STAR to organize each query. The situation identifies the relevant database tables. The task describes what the question asks for. The action applies the location, cuisine, street, and rating filters. The result returns the matching house numbers and restaurant names. The SQL uses common table expressions to keep these steps clear.

## SMART

File: `restaurants_dataset_predictions_smart.csv`

I used SMART to keep each query focused on the requested details. Rating thresholds make the result measurable, and the supplied schema keeps the query achievable. For a request for one restaurant, the query returns at most one match.

These files were prepared using the three framework approaches. They are not records of separate hosted model sessions, and inference times were not recorded.

## Running the evaluator

Copy the prediction file you want to test to `data/restaurants_dataset_predictions.csv`, then run `data/evaluate_retrieval_predictions.py`. The evaluator compares returned rows, not the SQL formatting.

See `Task_2_Report.md` for the scores and chart.
