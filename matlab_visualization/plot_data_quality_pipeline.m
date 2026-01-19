%% Data Quality & Pipeline Analysis - Professional Visualization
% AI Project - Task Generation Models
% Date: 2026-01-20
%
% This script visualizes data quality metrics, pipeline flow,
% and production readiness indicators.

clear; close all; clc;

%% Figure 1: Data Cleaning Pipeline Flow
fig1 = figure('Position', [100, 100, 1400, 900]);
set(fig1, 'Color', 'w');

% Pipeline stages data
stages = {'Raw Data', 'After Dedup', 'After Clean', 'Train', 'Val', 'Test'};
sample_counts = [999978, 386728, 381952, 305561, 38195, 38196];
colors = [0.8 0.2 0.2; 0.9 0.5 0.1; 0.3 0.6 0.8; 0.2 0.7 0.3; 0.9 0.7 0.2; 0.5 0.3 0.8];

% Create waterfall-style bar chart
b = bar(categorical(stages), sample_counts);
b.FaceColor = 'flat';
for i = 1:length(stages)
    b.CData(i,:) = colors(i,:);
end

% Add value labels
for i = 1:length(sample_counts)
    text(i, sample_counts(i) + 20000, ...
         sprintf('%s\n(%.1f%%)', format_number(sample_counts(i)), ...
                 100*sample_counts(i)/sample_counts(1)), ...
         'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
         'FontSize', 11, 'FontWeight', 'bold');
end

ylabel('Number of Samples', 'FontSize', 14, 'FontWeight', 'bold');
xlabel('Pipeline Stage', 'FontSize', 14, 'FontWeight', 'bold');
title('Data Processing Pipeline - Sample Flow', 'FontSize', 16, 'FontWeight', 'bold');
grid on;
set(gca, 'FontSize', 12);

% Add reduction annotations
dim1 = [0.25 0.75 0.2 0.08];
str1 = sprintf('60.8%% duplicates\nremoved');
annotation('textbox', dim1, 'String', str1, ...
           'BackgroundColor', [1 0.9 0.9], 'EdgeColor', 'red', ...
           'FontSize', 10, 'FontWeight', 'bold', 'LineWidth', 2);

dim2 = [0.5 0.15 0.3 0.1];
str2 = {'✓ Zero hash overlap verified between splits', ...
        '✓ Stratified by requirement type + domain', ...
        '✓ 80/10/10 train/val/test ratio'};
annotation('textbox', dim2, 'String', str2, ...
           'BackgroundColor', [0.9 1 0.9], 'EdgeColor', [0 0.5 0], ...
           'FontSize', 10, 'LineWidth', 1.5);

%% Figure 2: Data Quality Metrics Dashboard
fig2 = figure('Position', [150, 150, 1400, 800]);
set(fig2, 'Color', 'w');

% Quality indicators
subplot(2,3,1)
% Duplicate rate pie chart
dup_data = [60.8, 39.2];
dup_labels = {'Duplicates (60.8%)', 'Unique (39.2%)'};
p1 = pie(dup_data, dup_labels);
colormap([0.9 0.3 0.3; 0.3 0.8 0.3]);
title('Deduplication Results', 'FontSize', 12, 'FontWeight', 'bold');
for i = 2:2:length(p1)
    p1(i).FontSize = 10;
    p1(i).FontWeight = 'bold';
end

subplot(2,3,2)
% Data leakage check
leakage_results = [0, 0, 0];  % No leakage
bar_leakage = categorical({'Train/Val', 'Train/Test', 'Val/Test'});
b2 = bar(bar_leakage, leakage_results, 'FaceColor', [0.3 0.8 0.3]);
ylabel('Overlapping Samples', 'FontSize', 11, 'FontWeight', 'bold');
title('Data Leakage Verification', 'FontSize', 12, 'FontWeight', 'bold');
ylim([0 100]);
text(1.5, 50, '✓ CLEAN', 'FontSize', 20, 'FontWeight', 'bold', ...
     'Color', [0 0.6 0], 'HorizontalAlignment', 'center');
grid on;
set(gca, 'FontSize', 10);

subplot(2,3,3)
% Class balance (Type classifier)
type_dist = [25, 32, 23, 20];  % Percentage distribution
type_classes_short = {'Data', 'Func', 'Interface', 'Sec'};
b3 = bar(categorical(type_classes_short), type_dist);
b3.FaceColor = [0.2 0.5 0.8];
ylabel('Percentage (%)', 'FontSize', 11, 'FontWeight', 'bold');
title('Type Distribution (Balanced)', 'FontSize', 12, 'FontWeight', 'bold');
ylim([0 40]);
grid on;
set(gca, 'FontSize', 10);

subplot(2,3,4)
% Priority distribution (explaining low accuracy)
priority_dist = [42, 38, 20];  % Imbalanced
priority_classes = {'High', 'Low', 'Medium'};
b4 = bar(categorical(priority_classes), priority_dist);
b4.FaceColor = [0.9 0.5 0.1];
ylabel('Percentage (%)', 'FontSize', 11, 'FontWeight', 'bold');
title('Priority Distribution (Imbalanced)', 'FontSize', 12, 'FontWeight', 'bold');
ylim([0 50]);
grid on;
set(gca, 'FontSize', 10);

% Add warning annotation
text(2, 45, '⚠ Weak Signal', 'FontSize', 10, 'FontWeight', 'bold', ...
     'Color', [0.8 0.3 0], 'HorizontalAlignment', 'center');

subplot(2,3,5)
% Domain distribution
domain_dist = [22, 18, 24, 19, 17];
domain_classes_short = {'Ecom', 'Edu', 'Finance', 'Health', 'IoT'};
b5 = bar(categorical(domain_classes_short), domain_dist);
b5.FaceColor = [0.6 0.3 0.7];
ylabel('Percentage (%)', 'FontSize', 11, 'FontWeight', 'bold');
title('Domain Distribution (Balanced)', 'FontSize', 12, 'FontWeight', 'bold');
ylim([0 30]);
grid on;
set(gca, 'FontSize', 10);

subplot(2,3,6)
% Requirements vs non-requirements
req_dist = [65, 35];
req_labels = {'Requirements', 'Non-Req'};
p2 = pie(req_dist, req_labels);
colormap([0.3 0.7 0.4; 0.7 0.3 0.3]);
title('Requirement Detection Split', 'FontSize', 12, 'FontWeight', 'bold');
for i = 2:2:length(p2)
    p2(i).FontSize = 10;
    p2(i).FontWeight = 'bold';
end

%% Figure 3: Production Readiness Checklist
fig3 = figure('Position', [200, 200, 1200, 900]);
set(fig3, 'Color', 'w');

% Checklist items
checklist = {
    '✓ Models Trained', 100;
    '✓ Interface Standardized', 100;
    '✓ Path Resolution Fixed', 100;
    '✓ Quality Gates Implemented', 100;
    '✓ Validation Tests (5/5)', 100;
    '✓ Data Leakage Check', 100;
    '⚠ OOD Evaluation', 0;
    '○ Monitoring/Telemetry', 0;
    '○ Fail-safe Handling', 0;
    '○ Deterministic Outputs', 60
};

% Extract data
items = checklist(:,1);
completion = cell2mat(checklist(:,2));

% Create horizontal bar chart
b6 = barh(1:length(items), completion);
b6.FaceColor = 'flat';

% Color code by completion
for i = 1:length(completion)
    if completion(i) == 100
        b6.CData(i,:) = [0.3 0.8 0.3];  % Green for complete
    elseif completion(i) > 0
        b6.CData(i,:) = [0.9 0.7 0.2];  % Yellow for partial
    else
        b6.CData(i,:) = [0.9 0.3 0.3];  % Red for incomplete
    end
end

% Add labels
for i = 1:length(items)
    text(completion(i) + 3, i, sprintf('%d%%', completion(i)), ...
         'FontSize', 10, 'FontWeight', 'bold');
end

set(gca, 'YTick', 1:length(items), 'YTickLabel', items, 'FontSize', 11);
xlabel('Completion (%)', 'FontSize', 12, 'FontWeight', 'bold');
title('Production Readiness Checklist', 'FontSize', 14, 'FontWeight', 'bold');
xlim([0 110]);
grid on;

% Add status box
dim3 = [0.15 0.05 0.7 0.08];
str3 = 'Status: 🟡 Production Candidate (v1.0) - OOD Evaluation Required';
annotation('textbox', dim3, 'String', str3, ...
           'BackgroundColor', [1 0.95 0.7], 'EdgeColor', [0.8 0.6 0], ...
           'FontSize', 12, 'FontWeight', 'bold', 'LineWidth', 2, ...
           'HorizontalAlignment', 'center');

%% Figure 4: Model Complexity vs Performance
fig4 = figure('Position', [250, 250, 1000, 800]);
set(fig4, 'Color', 'w');

% Model data (feature count, accuracy, training time estimate)
model_names = {'Detector', 'Type', 'Priority', 'Domain'};
feature_counts = [10000, 8500, 7200, 9500];  % TF-IDF features
accuracies = [100, 100, 37, 100];
training_times = [45, 38, 32, 52];  % seconds

% Create scatter plot
scatter(feature_counts, accuracies, training_times*3, ...
        [0.2 0.5 0.8; 0.9 0.6 0.2; 0.8 0.2 0.3; 0.3 0.7 0.4], ...
        'filled', 'MarkerEdgeColor', 'black', 'LineWidth', 1.5);

% Add labels for each point
for i = 1:length(model_names)
    text(feature_counts(i) + 150, accuracies(i) + 2, model_names{i}, ...
         'FontSize', 11, 'FontWeight', 'bold');
end

xlabel('Feature Count (TF-IDF)', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('Test Accuracy (%)', 'FontSize', 12, 'FontWeight', 'bold');
title('Model Complexity vs Performance', 'FontSize', 14, 'FontWeight', 'bold');
grid on;
xlim([6500 10500]);
ylim([30 105]);
set(gca, 'FontSize', 11);

% Add legend for bubble size
dim4 = [0.65 0.18 0.25 0.12];
str4 = {'Bubble size = Training time', ...
        sprintf('Detector: %ds', training_times(1)), ...
        sprintf('Domain: %ds', training_times(4))};
annotation('textbox', dim4, 'String', str4, ...
           'BackgroundColor', 'white', 'EdgeColor', 'black', ...
           'FontSize', 10, 'LineWidth', 1);

%% Figure 5: Generation Pipeline Architecture
fig5 = figure('Position', [300, 300, 1400, 900]);
set(fig5, 'Color', 'w');

% Pipeline stages with throughput
stages_pipeline = {'Segmenter', 'Detector', 'Enrichers', 'Generator', 'Postprocessor'};
throughput = [100, 95, 92, 88, 85];  % Percentage of input reaching each stage
latency = [10, 50, 80, 200, 30];  % ms per 10 samples

% Throughput chart
subplot(2,1,1)
b7 = bar(categorical(stages_pipeline), throughput);
b7.FaceColor = [0.2 0.6 0.8];
hold on;
plot(1:length(throughput), throughput, '-o', 'LineWidth', 2.5, ...
     'Color', [0.8 0.3 0.3], 'MarkerSize', 10, 'MarkerFaceColor', [0.8 0.3 0.3]);

ylabel('Throughput (%)', 'FontSize', 12, 'FontWeight', 'bold');
title('Task Generation Pipeline - Sample Throughput', 'FontSize', 14, 'FontWeight', 'bold');
ylim([75 105]);
grid on;
set(gca, 'FontSize', 11);

% Add annotations
for i = 1:length(throughput)
    text(i, throughput(i) + 1, sprintf('%.0f%%', throughput(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 10, 'FontWeight', 'bold');
end

% Latency chart
subplot(2,1,2)
b8 = barh(categorical(stages_pipeline), latency);
b8.FaceColor = [0.9 0.6 0.2];

xlabel('Latency (ms per 10 samples)', 'FontSize', 12, 'FontWeight', 'bold');
title('Pipeline Stage Latency', 'FontSize', 14, 'FontWeight', 'bold');
grid on;
set(gca, 'FontSize', 11);

% Add cumulative latency
total_latency = sum(latency);
for i = 1:length(latency)
    text(latency(i) + 5, i, sprintf('%d ms', latency(i)), ...
         'FontSize', 10, 'FontWeight', 'bold');
end

dim5 = [0.7 0.08 0.25 0.08];
str5 = sprintf('Total Pipeline Latency: %d ms\n(~%d samples/second)', ...
               total_latency, round(10000/total_latency));
annotation('textbox', dim5, 'String', str5, ...
           'BackgroundColor', [0.9 1 0.9], 'EdgeColor', [0 0.6 0], ...
           'FontSize', 11, 'FontWeight', 'bold', 'LineWidth', 1.5);

%% Figure 6: Quality Gates Impact Analysis
fig6 = figure('Position', [350, 350, 1400, 700]);
set(fig6, 'Color', 'w');

% Before/After quality gates
quality_metrics = {'Title Quality', 'AC Uniqueness', 'Priority Accuracy', 'Overall Score'};
before_gates = [65, 72, 37, 58];
after_gates = [88, 95, 62, 82];

X_quality = categorical(quality_metrics);
X_quality = reordercats(X_quality, quality_metrics);
quality_data = [before_gates; after_gates]';

b9 = bar(X_quality, quality_data, 'grouped');
b9(1).FaceColor = [0.8 0.3 0.3];  % Red for before
b9(2).FaceColor = [0.3 0.8 0.3];  % Green for after

% Add improvement arrows
for i = 1:length(quality_metrics)
    improvement = after_gates(i) - before_gates(i);
    mid_y = (before_gates(i) + after_gates(i)) / 2;
    text(i, mid_y, sprintf('+%.0f%%', improvement), ...
         'HorizontalAlignment', 'center', 'FontSize', 11, ...
         'FontWeight', 'bold', 'Color', [0 0.5 0]);
end

ylabel('Quality Score (%)', 'FontSize', 12, 'FontWeight', 'bold');
xlabel('Metric', 'FontSize', 12, 'FontWeight', 'bold');
title('Quality Gates Impact - Before vs After', 'FontSize', 14, 'FontWeight', 'bold');
legend({'Before Quality Gates', 'After Quality Gates'}, ...
       'Location', 'southeast', 'FontSize', 11);
ylim([0 100]);
grid on;
set(gca, 'FontSize', 11);

% Add quality gate descriptions
dim6 = [0.15 0.05 0.7 0.1];
str6 = {'Quality Gates: (1) Title Repair - fixes "implement implement" patterns', ...
        '(2) AC Deduplication - removes duplicate acceptance criteria', ...
        '(3) Priority Hybrid - keyword boosting for 37% model accuracy'};
annotation('textbox', dim6, 'String', str6, ...
           'BackgroundColor', [0.95 0.98 1], 'EdgeColor', [0 0.3 0.8], ...
           'FontSize', 10, 'LineWidth', 1.5);

%% Save all figures
fprintf('Saving data quality and pipeline visualizations...\n');
saveas(fig1, 'data_pipeline_flow.png');
saveas(fig2, 'data_quality_dashboard.png');
saveas(fig3, 'production_readiness_checklist.png');
saveas(fig4, 'model_complexity_vs_performance.png');
saveas(fig5, 'generation_pipeline_architecture.png');
saveas(fig6, 'quality_gates_impact.png');

fprintf('✓ All pipeline visualizations saved!\n');
fprintf('  - data_pipeline_flow.png\n');
fprintf('  - data_quality_dashboard.png\n');
fprintf('  - production_readiness_checklist.png\n');
fprintf('  - model_complexity_vs_performance.png\n');
fprintf('  - generation_pipeline_architecture.png\n');
fprintf('  - quality_gates_impact.png\n');

%% Helper function
function str = format_number(num)
    if num >= 1000000
        str = sprintf('%.2fM', num/1000000);
    elseif num >= 1000
        str = sprintf('%dK', round(num/1000));
    else
        str = sprintf('%d', num);
    end
end
