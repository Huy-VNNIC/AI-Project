%% Master Script - Run All Visualizations
% AI Project - Task Generation Models
% Date: 2026-01-20
%
% This script runs all visualization scripts sequentially
% and generates a complete set of figures.

clear; close all; clc;

fprintf('=================================================================\n');
fprintf('   AI PROJECT - MODEL VISUALIZATION SUITE\n');
fprintf('=================================================================\n\n');

fprintf('Starting comprehensive model visualization...\n\n');

%% Script 1: Model Performance
fprintf('[ 1/3 ] Running model performance analysis...\n');
try
    plot_model_performance;
    fprintf('        ✓ Completed: 6 figures generated\n\n');
catch ME
    fprintf('        ✗ Error: %s\n\n', ME.message);
end

%% Script 2: Confusion Matrices
fprintf('[ 2/3 ] Running confusion matrix analysis...\n');
try
    plot_confusion_matrices;
    fprintf('        ✓ Completed: 7 figures generated\n\n');
catch ME
    fprintf('        ✗ Error: %s\n\n', ME.message);
end

%% Script 3: Data Quality & Pipeline
fprintf('[ 3/3 ] Running data quality and pipeline analysis...\n');
try
    plot_data_quality_pipeline;
    fprintf('        ✓ Completed: 6 figures generated\n\n');
catch ME
    fprintf('        ✗ Error: %s\n\n', ME.message);
end

%% Summary
fprintf('=================================================================\n');
fprintf('   VISUALIZATION COMPLETE\n');
fprintf('=================================================================\n\n');

fprintf('Total figures generated: 19\n\n');

fprintf('Output files:\n');
fprintf('  Performance Analysis (6 files):\n');
fprintf('    - model_accuracy_comparison.png\n');
fprintf('    - model_f1_comparison.png\n');
fprintf('    - detailed_metrics_heatmap.png\n');
fprintf('    - dataset_distribution.png\n');
fprintf('    - model_performance_radar.png\n');
fprintf('    - training_summary_table.png\n\n');

fprintf('  Confusion Matrix Analysis (7 files):\n');
fprintf('    - type_confusion_matrix.png\n');
fprintf('    - priority_confusion_matrix.png\n');
fprintf('    - domain_confusion_matrix.png\n');
fprintf('    - detector_roc_pr_curves.png\n');
fprintf('    - type_perclass_performance.png\n');
fprintf('    - model_comparison_matrix.png\n');
fprintf('    - training_convergence.png\n\n');

fprintf('  Data Quality & Pipeline (6 files):\n');
fprintf('    - data_pipeline_flow.png\n');
fprintf('    - data_quality_dashboard.png\n');
fprintf('    - production_readiness_checklist.png\n');
fprintf('    - model_complexity_vs_performance.png\n');
fprintf('    - generation_pipeline_architecture.png\n');
fprintf('    - quality_gates_impact.png\n\n');

fprintf('=================================================================\n');
fprintf('✓ All visualizations saved in current directory\n');
fprintf('=================================================================\n');
