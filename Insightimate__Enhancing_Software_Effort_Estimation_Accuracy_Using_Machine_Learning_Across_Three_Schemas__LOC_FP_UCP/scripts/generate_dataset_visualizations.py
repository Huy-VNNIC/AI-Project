#!/usr/bin/env python3
"""
Generate high-quality visualizations for dataset analysis in paper.
Addresses reviewer concerns about table readability by providing visual summaries.

Usage:
    python generate_dataset_visualizations.py

Outputs:
    - dataset_timeline_enhanced.png: Temporal coverage by schema
    - dataset_composition.png: Pie chart showing project distribution
    - schema_comparison.png: Multi-panel comparison of schemas
    - deduplication_impact.png: Before/after deduplication visualization
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import seaborn as sns

# Set publication-quality style
plt.style.use('seaborn-v0_8-paper')
sns.set_context("paper", font_scale=1.2)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['mathtext.fontset'] = 'stix'

# Dataset manifest data (from Table S1)
datasets_loc = [
    {'name': 'DASE', 'year': 2023, 'raw': 1203, 'dup_rm': 120, 'invalid_rm': 33, 'final': 1050},
    {'name': 'Freeman', 'year': 2022, 'raw': 487, 'dup_rm': 28, 'invalid_rm': 9, 'final': 450},
    {'name': 'Derek Jones', 'year': 2022, 'raw': 328, 'dup_rm': 12, 'invalid_rm': 4, 'final': 312},
    {'name': 'NASA93', 'year': 1993, 'raw': 93, 'dup_rm': 0, 'invalid_rm': 0, 'final': 93},
    {'name': 'Telecom1', 'year': 2001, 'raw': 18, 'dup_rm': 0, 'invalid_rm': 0, 'final': 18},
    {'name': 'Maxwell', 'year': 2002, 'raw': 62, 'dup_rm': 0, 'invalid_rm': 0, 'final': 62},
    {'name': 'Miyazaki', 'year': 1994, 'raw': 48, 'dup_rm': 0, 'invalid_rm': 0, 'final': 48},
    {'name': 'Chinese', 'year': 2007, 'raw': 499, 'dup_rm': 10, 'invalid_rm': 3, 'final': 486},
    {'name': 'Finnish', 'year': 1990, 'raw': 38, 'dup_rm': 0, 'invalid_rm': 0, 'final': 38},
    {'name': 'Kitchenham', 'year': 2002, 'raw': 145, 'dup_rm': 0, 'invalid_rm': 0, 'final': 145},
    {'name': 'COCOMO81', 'year': 1981, 'raw': 63, 'dup_rm': 0, 'invalid_rm': 0, 'final': 63},
]

datasets_fp = [
    {'name': 'Albrecht', 'year': 1979, 'raw': 26, 'dup_rm': 2, 'invalid_rm': 0, 'final': 24},
    {'name': 'Desharnais', 'year': 1989, 'raw': 81, 'dup_rm': 3, 'invalid_rm': 1, 'final': 77},
    {'name': 'Kemerer', 'year': 1987, 'raw': 15, 'dup_rm': 0, 'invalid_rm': 0, 'final': 15},
    {'name': 'ISBSG subset', 'year': 2005, 'raw': 45, 'dup_rm': 2, 'invalid_rm': 1, 'final': 42},
]

datasets_ucp = [
    {'name': 'Silhavy', 'year': 2017, 'raw': 74, 'dup_rm': 3, 'invalid_rm': 0, 'final': 71},
    {'name': 'Huynh', 'year': 2023, 'raw': 53, 'dup_rm': 4, 'invalid_rm': 1, 'final': 48},
    {'name': 'Karner', 'year': 1993, 'raw': 12, 'dup_rm': 0, 'invalid_rm': 0, 'final': 12},
]

def create_temporal_timeline():
    """Enhanced temporal coverage visualization"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Aggregate by year and schema
    years = range(1979, 2024)
    loc_by_year = {y: 0 for y in years}
    fp_by_year = {y: 0 for y in years}
    ucp_by_year = {y: 0 for y in years}
    
    for ds in datasets_loc:
        loc_by_year[ds['year']] += ds['final']
    for ds in datasets_fp:
        fp_by_year[ds['year']] += ds['final']
    for ds in datasets_ucp:
        ucp_by_year[ds['year']] += ds['final']
    
    # Create bar positions
    x = np.array(list(years))
    loc_vals = np.array([loc_by_year[y] for y in years])
    fp_vals = np.array([fp_by_year[y] for y in years])
    ucp_vals = np.array([ucp_by_year[y] for y in years])
    
    # Stacked bars
    width = 0.8
    p1 = ax.bar(x, loc_vals, width, label='LOC', color='#3498db', alpha=0.85)
    p2 = ax.bar(x, fp_vals, width, bottom=loc_vals, label='FP', color='#e74c3c', alpha=0.85)
    p3 = ax.bar(x, ucp_vals, width, bottom=loc_vals+fp_vals, label='UCP', color='#2ecc71', alpha=0.85)
    
    # Formatting
    ax.set_xlabel('Publication Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Projects', fontsize=14, fontweight='bold')
    ax.set_title('Dataset Temporal Coverage (1979-2023)', fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='upper left', framealpha=0.95, fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Highlight key periods
    ax.axvspan(1979, 1995, alpha=0.1, color='gray', label='Era 1: Early FP/LOC')
    ax.axvspan(1996, 2010, alpha=0.1, color='blue', label='Era 2: PROMISE expansion')
    ax.axvspan(2011, 2023, alpha=0.15, color='green', label='Era 3: UCP + aggregation')
    
    # Set x-axis ticks to show key years only
    key_years = [1979, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023]
    ax.set_xticks(key_years)
    ax.set_xticklabels(key_years, rotation=45)
    
    plt.tight_layout()
    plt.savefig('../figures/dataset_timeline_enhanced.png', dpi=300, bbox_inches='tight')
    print("✓ Created: dataset_timeline_enhanced.png")
    plt.close()


def create_composition_pie():
    """Dataset composition breakdown"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # By schema
    schemas = ['LOC', 'FP', 'UCP']
    counts = [
        sum(d['final'] for d in datasets_loc),
        sum(d['final'] for d in datasets_fp),
        sum(d['final'] for d in datasets_ucp)
    ]
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    explode = (0.05, 0.05, 0.05)
    
    wedges, texts, autotexts = ax1.pie(counts, labels=schemas, autopct='%1.1f%%',
                                         colors=colors, explode=explode, startangle=90,
                                         textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax1.set_title('Projects by Schema\n(n=3,054 total)', fontsize=14, fontweight='bold', pad=20)
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # By source count
    source_counts = [len(datasets_loc), len(datasets_fp), len(datasets_ucp)]
    wedges2, texts2, autotexts2 = ax2.pie(source_counts, labels=schemas, autopct='%1.0f',
                                            colors=colors, explode=explode, startangle=90,
                                            textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax2.set_title('Number of Data Sources\n(18 total)', fontsize=14, fontweight='bold', pad=20)
    
    for autotext in autotexts2:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    plt.savefig('../figures/dataset_composition.png', dpi=300, bbox_inches='tight')
    print("✓ Created: dataset_composition.png")
    plt.close()


def create_schema_comparison():
    """Multi-panel comparison of schemas"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Cross-Schema Dataset Characteristics', fontsize=18, fontweight='bold', y=0.995)
    
    schemas_data = [
        ('LOC', datasets_loc, '#3498db'),
        ('FP', datasets_fp, '#e74c3c'),
        ('UCP', datasets_ucp, '#2ecc71')
    ]
    
    for idx, (schema, data, color) in enumerate(schemas_data):
        # Row 1: Project count distribution
        ax1 = axes[0, idx]
        names = [d['name'][:10] for d in data]  # Truncate names
        finals = [d['final'] for d in data]
        ax1.barh(names, finals, color=color, alpha=0.7)
        ax1.set_xlabel('Projects', fontsize=10, fontweight='bold')
        ax1.set_title(f'{schema} Schema\n({sum(finals)} projects)', fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Row 2: Deduplication impact
        ax2 = axes[1, idx]
        raw_total = sum(d['raw'] for d in data)
        dup_rm = sum(d['dup_rm'] for d in data)
        invalid_rm = sum(d['invalid_rm'] for d in data)
        final_total = sum(d['final'] for d in data)
        
        categories = ['Raw', 'Dup.\nRemoved', 'Invalid\nRemoved', 'Final']
        values = [raw_total, dup_rm, invalid_rm, final_total]
        colors_bar = [color, '#e67e22', '#e67e22', color]
        
        bars = ax2.bar(categories, values, color=colors_bar, alpha=0.7, edgecolor='black')
        ax2.set_ylabel('Count', fontsize=10, fontweight='bold')
        ax2.set_title(f'Data Cleaning Impact', fontsize=11, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../figures/schema_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Created: schema_comparison.png")
    plt.close()


def create_deduplication_impact():
    """Visualization of deduplication impact across all schemas"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    schemas = ['LOC', 'FP', 'UCP']
    data_sources = [datasets_loc, datasets_fp, datasets_ucp]
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    x = np.arange(len(schemas))
    width = 0.25
    
    raw_totals = [sum(d['raw'] for d in ds) for ds in data_sources]
    dup_removed = [sum(d['dup_rm'] for d in ds) for ds in data_sources]
    invalid_removed = [sum(d['invalid_rm'] for d in ds) for ds in data_sources]
    final_totals = [sum(d['final'] for d in ds) for ds in data_sources]
    
    # Stacked bars showing breakdown
    p1 = ax.bar(x - width, final_totals, width, label='Final (clean)', color=colors, alpha=0.9)
    p2 = ax.bar(x, dup_removed, width, label='Duplicates removed', color='#e67e22', alpha=0.7)
    p3 = ax.bar(x + width, invalid_removed, width, label='Invalid removed', color='#c0392b', alpha=0.7)
    
    # Formatting
    ax.set_xlabel('Schema', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Projects', fontsize=14, fontweight='bold')
    ax.set_title('Deduplication and Quality Control Impact', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(schemas, fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', framealpha=0.95, fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add percentage annotations
    for i, schema in enumerate(schemas):
        dedup_pct = (dup_removed[i] + invalid_removed[i]) / raw_totals[i] * 100
        ax.text(i, max(final_totals[i], dup_removed[i], invalid_removed[i]) + 50,
                f'-{dedup_pct:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold', color='red')
    
    plt.tight_layout()
    plt.savefig('../figures/deduplication_impact.png', dpi=300, bbox_inches='tight')
    print("✓ Created: deduplication_impact.png")
    plt.close()


def create_summary_table_figure():
    """Create a cleaner visual representation of the summary table"""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('tight')
    ax.axis('off')
    
    # Data for table
    table_data = [
        ['Schema', 'Sources', 'Period', 'Raw Projects', 'After Dedup.', 'Dedup. %'],
        ['LOC', '11', '1981-2023', '2,984', '2,765', '-7.3%'],
        ['FP', '4', '1979-2005', '167', '158', '-5.4%'],
        ['UCP', '3', '1993-2023', '139', '131', '-5.8%'],
        ['Total', '18', '1979-2023', '3,290', '3,054', '-7.2%']
    ]
    
    # Create table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.15, 0.15, 0.2, 0.2, 0.2, 0.15])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)
    
    # Style header row
    for i in range(6):
        cell = table[(0, i)]
        cell.set_facecolor('#34495e')
        cell.set_text_props(weight='bold', color='white')
    
    # Style data rows with alternating colors
    colors_rows = ['#ecf0f1', '#ffffff', '#ecf0f1', '#d5dbdb']
    for row in range(1, 5):
        for col in range(6):
            cell = table[(row, col)]
            cell.set_facecolor(colors_rows[row-1])
            if row == 4:  # Total row
                cell.set_text_props(weight='bold')
    
    # Highlight schema column
    for row in range(1, 5):
        table[(row, 0)].set_facecolor('#bdc3c7')
        table[(row, 0)].set_text_props(weight='bold')
    
    plt.savefig('../figures/dataset_summary_table.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Created: dataset_summary_table.png")
    plt.close()


def main():
    """Generate all visualizations"""
    print("\n" + "="*60)
    print("DATASET VISUALIZATION GENERATOR")
    print("Addressing Reviewer Feedback on Table 1 Readability")
    print("="*60 + "\n")
    
    print("Generating visualizations...")
    
    create_temporal_timeline()
    create_composition_pie()
    create_schema_comparison()
    create_deduplication_impact()
    create_summary_table_figure()
    
    print("\n" + "="*60)
    print("✓ All visualizations generated successfully!")
    print("="*60)
    print("\nGenerated files in ../figures/:")
    print("  1. dataset_timeline_enhanced.png - Temporal coverage")
    print("  2. dataset_composition.png - Schema distribution pie charts")
    print("  3. schema_comparison.png - Multi-panel schema analysis")
    print("  4. deduplication_impact.png - Data cleaning visualization")
    print("  5. dataset_summary_table.png - Clean table visualization")
    print("\nThese figures provide:")
    print("  • Visual clarity for dataset distribution")
    print("  • Transparent deduplication impact")
    print("  • Schema-specific characteristics")
    print("  • Publication-quality graphics (300 DPI)")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
