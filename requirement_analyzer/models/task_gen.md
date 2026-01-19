# Dataset Quality Report

Generated: 2026-01-20 01:35:17

Dataset: `/home/dtu/AI-Project/AI-Project/requirement_analyzer/dataset_large_1m`

## Overall Statistics
- **Total files**: 100
- **Total rows**: 999,978
- **Duplicates**: 608,048 (60.81%)

## Missing Values
| Column | Count | Percentage |
|--------|-------|------------|
| text | 0 | 0.00% |
| is_requirement | 0 | 0.00% |
| type | 0 | 0.00% |
| priority | 0 | 0.00% |
| domain | 0 | 0.00% |

## Text Length Statistics
| Metric | Value |
|--------|-------|
| Min | 31.00 |
| Max | 87.00 |
| Mean | 57.14 |
| Median | 58.00 |
| Std | 8.45 |

## Label Distributions

### Is Requirement
| Value | Count | Percentage |
|-------|-------|------------|
| 0 | 197,813 | 19.98% |
| 1 | 792,187 | 80.02% |

### Type Distribution
| Type | Count |
|------|-------|
| functional | 638,008 |
| non_requirement | 197,813 |
| data | 76,885 |
| security | 59,765 |
| interface | 17,529 |

### Priority Distribution
| Priority | Count |
|----------|-------|
| Medium | 529,027 |
| none | 197,813 |
| High | 175,618 |
| Low | 87,542 |

### Domain Distribution
| Domain | Count |
|--------|-------|
| general | 197,813 |
| finance | 158,673 |
| healthcare | 158,524 |
| education | 158,369 |
| ecommerce | 158,337 |
| iot | 158,284 |

## Recommendations

⚠️ **Class imbalance detected**: requirement vs non-requirement ratio is 4.00. Consider using `class_weight='balanced'` in models.

⚠️ **High duplicate rate** (60.81%). Consider deduplication.