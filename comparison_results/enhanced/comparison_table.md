| Model             | Schema   |   MMRE vs COCOMO |   PRED(25) vs COCOMO | MMRE vs Actual   | PRED(25) vs Actual   | MAE      | RMSE     |
|:------------------|:---------|-----------------:|---------------------:|:-----------------|:---------------------|:---------|:---------|
| Linear_Regression | LOC      |           1.324  |               0.0909 | N/A              | N/A                  | N/A      | N/A      |
| Decision_Tree     | LOC      |           0.8557 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Random_Forest     | LOC      |           0.8992 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Gradient_Boosting | LOC      |           1.0479 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Linear_Regression | FP       |          21.945  |               0.1818 | 4.4999           | 0.0000               | 107.5358 | 280.2682 |
| Decision_Tree     | FP       |           0.663  |               0.0909 | 1.3712           | 0.1728               | 18.6321  | 23.6230  |
| Random_Forest     | FP       |           0.7081 |               0      | 0.6473           | 0.3951               | 12.6558  | 20.0085  |
| Gradient_Boosting | FP       |           0.6085 |               0.0909 | 1.1008           | 0.1975               | 16.1608  | 21.0946  |
| Linear_Regression | UCP      |           4.7679 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Decision_Tree     | UCP      |           1.5928 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Random_Forest     | UCP      |           1.1412 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Gradient_Boosting | UCP      |           2.2039 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Linear_Regression | All      |           9.3456 |               0.0909 | 4.4999           | 0.0000               | 107.5358 | 280.2682 |
| Decision_Tree     | All      |           1.0371 |               0.0303 | 1.3712           | 0.1728               | 18.6321  | 23.6230  |
| Random_Forest     | All      |           0.9162 |               0      | 0.6473           | 0.3951               | 12.6558  | 20.0085  |
| Gradient_Boosting | All      |           1.2868 |               0.0303 | 1.1008           | 0.1975               | 16.1608  | 21.0946  |