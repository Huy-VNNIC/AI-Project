"""
OOD Evaluation Step 2: Summarize Scores
Generate OOD evaluation report from human-scored CSV
"""
import sys
import csv
import json
from pathlib import Path
from collections import defaultdict


def summarize_ood_scores(scored_csv: str, output_report: str):
    """
    Read human-scored CSV, calculate metrics, generate report
    
    Args:
        scored_csv: CSV with all score_* columns filled by human
        output_report: Markdown report path
    """
    print(f"📖 Reading {scored_csv}...")
    rows = []
    with open(scored_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    total = len(rows)
    print(f"   Found {total} scored rows")
    
    # Skip rows without scores
    scored_rows = [r for r in rows if r.get('score_title_clarity', '').strip()]
    valid = len(scored_rows)
    
    if valid == 0:
        print("❌ No scored rows found! Please fill score_* columns.")
        return
    
    print(f"   Valid scores: {valid}/{total}")
    
    # Calculate metrics
    scores = {
        'title_clarity': [],
        'desc_correctness': [],
        'ac_testability': [],
        'label_type': [],
        'label_domain': [],
        'priority_reasonable': [],
    }
    
    duplicate_count = 0
    
    for row in scored_rows:
        try:
            scores['title_clarity'].append(float(row['score_title_clarity']))
            scores['desc_correctness'].append(float(row['score_desc_correctness']))
            scores['ac_testability'].append(float(row['score_ac_testability']))
            scores['label_type'].append(float(row['score_label_type']))
            scores['label_domain'].append(float(row['score_label_domain']))
            scores['priority_reasonable'].append(float(row['score_priority_reasonable']))
            
            if row.get('has_duplicates', '0') == '1':
                duplicate_count += 1
        except:
            pass
    
    # Calculate averages
    avg_title = sum(scores['title_clarity']) / len(scores['title_clarity']) if scores['title_clarity'] else 0
    avg_desc = sum(scores['desc_correctness']) / len(scores['desc_correctness']) if scores['desc_correctness'] else 0
    avg_ac = sum(scores['ac_testability']) / len(scores['ac_testability']) if scores['ac_testability'] else 0
    
    avg_type = sum(scores['label_type']) / len(scores['label_type']) if scores['label_type'] else 0
    avg_domain = sum(scores['label_domain']) / len(scores['label_domain']) if scores['label_domain'] else 0
    avg_priority = sum(scores['priority_reasonable']) / len(scores['priority_reasonable']) if scores['priority_reasonable'] else 0
    
    duplicate_rate = duplicate_count / valid if valid > 0 else 0
    
    # Overall score
    overall_quality = (avg_title + avg_desc + avg_ac) / 3
    
    # Pass/fail
    PASS_THRESHOLD = 3.5
    DUPLICATE_THRESHOLD = 0.10
    LABEL_THRESHOLD = 0.80
    
    quality_pass = overall_quality >= PASS_THRESHOLD
    duplicate_pass = duplicate_rate <= DUPLICATE_THRESHOLD
    type_pass = avg_type >= LABEL_THRESHOLD
    domain_pass = avg_domain >= LABEL_THRESHOLD
    
    all_pass = quality_pass and duplicate_pass and type_pass and domain_pass
    
    # Breakdown by domain
    domain_breakdown = defaultdict(lambda: {
        'count': 0,
        'avg_quality': 0,
        'quality_scores': []
    })
    
    for row in scored_rows:
        domain = row.get('domain_expected', 'unknown')
        try:
            title_score = float(row['score_title_clarity'])
            desc_score = float(row['score_desc_correctness'])
            ac_score = float(row['score_ac_testability'])
            quality = (title_score + desc_score + ac_score) / 3
            
            domain_breakdown[domain]['count'] += 1
            domain_breakdown[domain]['quality_scores'].append(quality)
        except:
            pass
    
    for domain, data in domain_breakdown.items():
        if data['quality_scores']:
            data['avg_quality'] = sum(data['quality_scores']) / len(data['quality_scores'])
    
    # Top 20 worst examples
    scored_with_quality = []
    for row in scored_rows:
        try:
            title_score = float(row['score_title_clarity'])
            desc_score = float(row['score_desc_correctness'])
            ac_score = float(row['score_ac_testability'])
            quality = (title_score + desc_score + ac_score) / 3
            
            scored_with_quality.append((row, quality))
        except:
            pass
    
    scored_with_quality.sort(key=lambda x: x[1])
    worst_20 = scored_with_quality[:min(20, len(scored_with_quality))]
    
    # Generate report
    print(f"\n📊 Generating report...")
    
    report_lines = []
    report_lines.append("# OOD Evaluation Report")
    report_lines.append("")
    report_lines.append(f"**Generated:** {Path.cwd()}")
    report_lines.append(f"**Input:** {scored_csv}")
    report_lines.append(f"**Total rows:** {total}")
    report_lines.append(f"**Valid scores:** {valid}")
    report_lines.append("")
    
    # Overall result
    status = "✅ **PASS**" if all_pass else "❌ **FAIL**"
    report_lines.append(f"## Overall Result: {status}")
    report_lines.append("")
    
    # Quality metrics
    report_lines.append("## Quality Metrics (1-5 scale)")
    report_lines.append("")
    report_lines.append("| Metric | Average | Pass? |")
    report_lines.append("|--------|---------|-------|")
    report_lines.append(f"| Title Clarity | {avg_title:.2f} | {'✅' if avg_title >= PASS_THRESHOLD else '❌'} |")
    report_lines.append(f"| Description Correctness | {avg_desc:.2f} | {'✅' if avg_desc >= PASS_THRESHOLD else '❌'} |")
    report_lines.append(f"| AC Testability | {avg_ac:.2f} | {'✅' if avg_ac >= PASS_THRESHOLD else '❌'} |")
    report_lines.append(f"| **Overall Quality** | **{overall_quality:.2f}** | **{'✅' if quality_pass else '❌'} (≥{PASS_THRESHOLD})** |")
    report_lines.append("")
    
    # Label accuracy
    report_lines.append("## Label Accuracy (0-1 scale)")
    report_lines.append("")
    report_lines.append("| Label | Accuracy | Pass? |")
    report_lines.append("|-------|----------|-------|")
    report_lines.append(f"| Type | {avg_type:.2%} | {'✅' if type_pass else '❌'} (≥{LABEL_THRESHOLD:.0%}) |")
    report_lines.append(f"| Domain | {avg_domain:.2%} | {'✅' if domain_pass else '❌'} (≥{LABEL_THRESHOLD:.0%}) |")
    report_lines.append(f"| Priority Reasonableness | {avg_priority:.2%} | ℹ️ (info only) |")
    report_lines.append("")
    
    # Duplicate rate
    report_lines.append("## Duplicate Rate")
    report_lines.append("")
    report_lines.append(f"- **Duplicate AC count:** {duplicate_count}/{valid} ({duplicate_rate:.1%})")
    report_lines.append(f"- **Pass?** {'✅' if duplicate_pass else '❌'} (≤{DUPLICATE_THRESHOLD:.0%})")
    report_lines.append("")
    
    # Breakdown by domain
    report_lines.append("## Breakdown by Domain")
    report_lines.append("")
    report_lines.append("| Domain | Count | Avg Quality | Pass? |")
    report_lines.append("|--------|-------|-------------|-------|")
    for domain in sorted(domain_breakdown.keys()):
        data = domain_breakdown[domain]
        report_lines.append(f"| {domain} | {data['count']} | {data['avg_quality']:.2f} | {'✅' if data['avg_quality'] >= PASS_THRESHOLD else '❌'} |")
    report_lines.append("")
    
    # Top 20 worst
    report_lines.append("## Top 20 Worst Examples")
    report_lines.append("")
    report_lines.append("| ID | Requirement | Generated Title | Quality | Notes |")
    report_lines.append("|----|-------------|-----------------|---------|-------|")
    for row, quality in worst_20:
        id_val = row.get('id', '?')
        req = row.get('requirement_sentence', '')[:50]
        title = row.get('generated_title', '')[:40]
        notes = row.get('notes', '')[:50]
        report_lines.append(f"| {id_val} | {req}... | {title}... | {quality:.2f} | {notes} |")
    report_lines.append("")
    
    # Recommendations
    report_lines.append("## Recommendations")
    report_lines.append("")
    
    if all_pass:
        report_lines.append("✅ **Model is production-ready!**")
        report_lines.append("")
        report_lines.append("- All metrics passed OOD evaluation")
        report_lines.append("- Consider updating status to **Production Ready**")
        report_lines.append("- Monitor in-production performance")
    else:
        report_lines.append("❌ **Model needs improvement:**")
        report_lines.append("")
        
        if not quality_pass:
            report_lines.append(f"- 🔴 **Quality Score:** {overall_quality:.2f} < {PASS_THRESHOLD} → Improve generation prompts/model")
        
        if not duplicate_pass:
            report_lines.append(f"- 🔴 **Duplicate Rate:** {duplicate_rate:.1%} > {DUPLICATE_THRESHOLD:.0%} → Strengthen deduplication")
        
        if not type_pass:
            report_lines.append(f"- 🔴 **Type Accuracy:** {avg_type:.1%} < {LABEL_THRESHOLD:.0%} → Retrain type classifier")
        
        if not domain_pass:
            report_lines.append(f"- 🔴 **Domain Accuracy:** {avg_domain:.1%} < {LABEL_THRESHOLD:.0%} → Retrain domain classifier")
        
        report_lines.append("")
        report_lines.append("**Next steps:**")
        report_lines.append("1. Analyze worst examples")
        report_lines.append("2. Retrain models with OOD data")
        report_lines.append("3. Re-run OOD evaluation")
    
    # Write report
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"✅ Report written to {output_report}")
    print(f"\n📊 Summary:")
    print(f"   Overall Quality: {overall_quality:.2f}/5.0 {'✅' if quality_pass else '❌'}")
    print(f"   Type Accuracy:   {avg_type:.1%} {'✅' if type_pass else '❌'}")
    print(f"   Domain Accuracy: {avg_domain:.1%} {'✅' if domain_pass else '❌'}")
    print(f"   Duplicate Rate:  {duplicate_rate:.1%} {'✅' if duplicate_pass else '❌'}")
    print(f"\n   🎯 Overall: {status}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Summarize OOD scores')
    parser.add_argument('scored_csv', help='CSV with human scores filled')
    parser.add_argument('--output', default='docs/OOD_REPORT.md',
                       help='Output report path')
    
    args = parser.parse_args()
    
    summarize_ood_scores(args.scored_csv, args.output)
