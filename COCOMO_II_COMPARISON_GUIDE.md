# COCOMO II Module Comparison Guide

## Overview

This guide explains how to use the COCOMO II module comparison functionality that was implemented to analyze linear relationships between size metrics and software development effort.

## Features

The COCOMO II comparison module provides:

1. **Linear Regression Analysis**: Creates scatter plots showing the relationship between size metrics (KLOC, FP, UCP) and effort
2. **Regression Lines**: Displays linear regression lines with equations y = ax + b where:
   - `y`: effort_pm (effort in person-months)
   - `x`: metric (KLOC/FP/UCP size)
   - `a`: slope coefficient (how effort increases with size)
   - `b`: intercept (base effort when size = 0)
3. **Statistical Analysis**: Shows R², p-values, and other regression statistics
4. **Schema Comparison**: Compares all three schemas (LOC, FP, UCP) on the same chart
5. **Traditional vs ML**: Compares traditional COCOMO II with machine learning models

## Quick Start

### Run Complete Analysis
```bash
./run_cocomo_comparison.sh
```

### Run Individual Components

**Linear Regression Analysis Only:**
```bash
python cocomo_ii_linear_analysis.py
```

**Traditional vs ML Comparison:**
```bash
python compare_models.py
```

**Test All Functionality:**
```bash
python test_cocomo_comparison.py
```

**Simple Demo:**
```bash
python demo.py
```

## Generated Output Files

### Linear Regression Analysis Charts
- `cocomo_ii_linear_analysis_loc.png` - LOC schema analysis with scatter plot and regression line
- `cocomo_ii_linear_analysis_fp.png` - Function Points schema analysis  
- `cocomo_ii_linear_analysis_ucp.png` - Use Case Points schema analysis
- `cocomo_ii_schemas_comparison.png` - Combined comparison of all schemas

### Traditional vs ML Comparison Charts  
- `comparison_effort_LOC.png` - Effort predictions comparison for LOC
- `comparison_effort_FP.png` - Effort predictions comparison for Function Points
- `comparison_effort_UCP.png` - Effort predictions comparison for Use Case Points
- `comparison_error_*.png` - Error analysis charts
- `comparison_mmre.png` - Mean Magnitude of Relative Error comparison
- `comparison_pred25.png` - PRED(25) accuracy comparison

### Data Files
- `comparison_results.csv` - Detailed prediction results
- `comparison_metrics.csv` - Summary statistics and accuracy metrics

## Understanding the Linear Regression Results

### Example Output Analysis

```
Schema     Hệ số a      Hệ số b      R²         p-value      Số mẫu    
LOC        0.1018       0.13         0.135      5.117e-44    1341      
FP         0.0854       3.05         0.404      1.971e-23    195       
UCP        -0.0054      42.70        0.015      1.553e-01    138       
```

**Interpretation:**

- **LOC Schema**: y = 0.1018x + 0.13
  - Each additional KLOC increases effort by ~0.1 person-months
  - Base effort is 0.13 person-months
  - R² = 0.135 indicates moderate correlation
  - p-value < 0.05 shows statistical significance

- **FP Schema**: y = 0.0854x + 3.05  
  - Each additional Function Point increases effort by ~0.085 person-months
  - Base effort is 3.05 person-months
  - R² = 0.404 indicates good correlation
  - Strong statistical significance

- **UCP Schema**: y = -0.0054x + 42.70
  - Negative slope suggests data quality issues or outliers
  - R² = 0.015 indicates poor correlation
  - p-value > 0.05 indicates no statistical significance

## Data Sources

The analysis uses processed datasets from:
- `processed_data/loc_based.csv` - Lines of Code based projects
- `processed_data/fp_based.csv` - Function Points based projects  
- `processed_data/ucp_based.csv` - Use Case Points based projects

## Requirements

- Python 3.12+
- Required packages: matplotlib, pandas, numpy, scikit-learn, seaborn, tabulate, joblib

Install dependencies:
```bash
pip install matplotlib pandas numpy scikit-learn seaborn tabulate joblib
```

## Troubleshooting

**Missing Data Files**: Ensure processed data files exist in `processed_data/` directory

**Display Issues**: The analysis uses 'Agg' backend for matplotlib to avoid display issues in headless environments

**Model Warnings**: sklearn version warnings can be safely ignored - models work correctly across versions

**Statistical Interpretation**: 
- R² < 0.3: Weak correlation
- R² 0.3-0.7: Moderate correlation  
- R² > 0.7: Strong correlation
- p-value < 0.05: Statistically significant

## Advanced Usage

### Custom Analysis
You can modify `cocomo_ii_linear_analysis.py` to:
- Change outlier filtering percentiles
- Adjust plot styling and colors
- Add additional statistical metrics
- Filter data by specific criteria

### Integration
The modules can be imported and used programmatically:

```python
from cocomo_ii_linear_analysis import load_datasets, perform_linear_regression_analysis
from demo import cocomo_ii_basic_estimate
from cocomo_ii_api import CocomoIIAPI

# Load and analyze data
datasets = load_datasets()
for schema, data in datasets.items():
    analysis = perform_linear_regression_analysis(data['size'].values, data['effort_pm'].values)
    print(f"{schema}: y = {analysis['slope']:.3f}x + {analysis['intercept']:.3f}")
```

## Support

For issues or questions about the COCOMO II comparison functionality, refer to:
- Test script: `test_cocomo_comparison.py`
- Example usage: `demo.py`
- Complete analysis: `run_cocomo_comparison.sh`