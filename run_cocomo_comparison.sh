#!/bin/bash
# Run COCOMO II Module Comparison Analysis
#
# This script runs the complete COCOMO II comparison analysis including:
# 1. Linear regression analysis for each schema (LOC, FP, UCP)
# 2. Scatter plots with regression lines showing y = ax + b relationships
# 3. Traditional vs ML model comparisons
# 4. Summary statistics and comparisons

echo "=========================================="
echo "COCOMO II MODULE COMPARISON ANALYSIS"
echo "=========================================="

echo ""
echo "1. Running Linear Regression Analysis..."
echo "   Creating scatter plots with regression lines for each schema"
python cocomo_ii_linear_analysis.py

echo ""
echo "2. Running Traditional vs ML Model Comparison..."
echo "   Comparing COCOMO II traditional formulas with ML models"
python compare_models.py

echo ""
echo "3. Running Validation Tests..."
python test_cocomo_comparison.py

echo ""
echo "=========================================="
echo "ANALYSIS COMPLETE!"
echo "=========================================="
echo ""
echo "Generated files:"
echo "• cocomo_ii_linear_analysis_loc.png - LOC schema scatter plot with regression"
echo "• cocomo_ii_linear_analysis_fp.png - FP schema scatter plot with regression"
echo "• cocomo_ii_linear_analysis_ucp.png - UCP schema scatter plot with regression"
echo "• cocomo_ii_schemas_comparison.png - Combined schemas comparison"
echo "• comparison_effort_*.png - Traditional vs ML effort comparisons"
echo "• comparison_error_*.png - Error analysis charts"
echo "• comparison_*.csv - Detailed results and metrics"
echo ""
echo "For a simple demo, run: python demo.py"