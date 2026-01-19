"""
Analyze failure patterns in OOD evaluation
"""
import csv
from collections import Counter

def analyze_failures(input_csv: str):
    """
    Categorize and analyze failed generation cases
    """
    print(f"📖 Reading {input_csv}...")
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Separate success vs failure
    failed = [r for r in rows if r['generated_title'] == '[NO OUTPUT]']
    success = [r for r in rows if r['generated_title'] and r['generated_title'] != '[NO OUTPUT]']
    
    print(f"\n📊 Overview:")
    print(f"   Total: {len(rows)}")
    print(f"   Success: {len(success)} ({100*len(success)/len(rows):.1f}%)")
    print(f"   Failed: {len(failed)} ({100*len(failed)/len(rows):.1f}%)")
    
    # Analyze failure taxonomy
    print(f"\n🔍 Failure Analysis:")
    print(f"\n{'Category':<40} {'Count':<8} {'%'}")
    print("=" * 55)
    
    # Categorize failures
    categories = {
        'no_requirement_detected': [],  # "No requirements detected"
        'not_a_requirement': [],  # Description/note, not requirement
        'too_complex': [],  # Multiple clauses, long spec
        'modal_only': [],  # Only modal verbs (shall/may)
        'other': []
    }
    
    for row in failed:
        req = row['requirement_sentence'].strip()
        
        # Check patterns
        if any(word in req.lower() for word in ['is either', 'may include', 'consists of', 'is part of']):
            categories['not_a_requirement'].append(row)
        elif req.lower().startswith('a ') or req.lower().startswith('an '):
            # Often definitions: "A user shall have...", "An account is..."
            if 'shall' in req.lower() or 'must' in req.lower():
                categories['modal_only'].append(row)
            else:
                categories['not_a_requirement'].append(row)
        elif len(req) > 200:
            categories['too_complex'].append(row)
        elif any(phrase in req for phrase in ['These are', 'When in', 'During', 'Some of', 'At any moment']):
            categories['not_a_requirement'].append(row)
        else:
            categories['other'].append(row)
    
    # Print taxonomy
    total_failed = len(failed)
    for cat, items in categories.items():
        if items:
            pct = 100 * len(items) / total_failed
            label = cat.replace('_', ' ').title()
            print(f"{label:<40} {len(items):<8} {pct:>5.1f}%")
    
    # Show samples from each category
    print(f"\n📋 Sample Failed Requirements:\n")
    
    for cat, items in categories.items():
        if not items:
            continue
        
        label = cat.replace('_', ' ').title()
        print(f"{'─' * 60}")
        print(f"🔸 {label} ({len(items)} cases)")
        print(f"{'─' * 60}")
        
        for i, row in enumerate(items[:3], 1):  # Show 3 samples
            req = row['requirement_sentence']
            print(f"\n{i}. {req[:100]}...")
            if len(req) > 100:
                print(f"   [...{len(req)} chars total]")
        
        print()
    
    # Recommendations
    print(f"\n💡 Recommendations:\n")
    
    if len(categories['not_a_requirement']) > len(failed) * 0.3:
        print("✅ 1. Filter descriptions/notes from requirement dataset")
        print("   → Add rule: skip rows starting with 'A ', 'An ', 'These are', etc.")
    
    if len(categories['modal_only']) > 5:
        print("✅ 2. Improve modal verb handling")
        print("   → Extract main verb after 'shall/must', not just remove modal")
    
    if len(categories['too_complex']) > 10:
        print("✅ 3. Add sentence splitting for complex requirements")
        print("   → Split on conjunctions: 'and', 'or', semicolons")
    
    if len(categories['other']) > len(failed) * 0.2:
        print("✅ 4. Lower requirement detector threshold")
        print("   → Current may be too strict for OOD patterns")
    
    print(f"\n📁 Detailed failure list saved to: failure_analysis.txt")
    
    # Save detailed failure list
    with open('scripts/eval/failure_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("OOD EVALUATION - FAILURE ANALYSIS\n")
        f.write("=" * 70 + "\n\n")
        
        for cat, items in categories.items():
            if not items:
                continue
            
            label = cat.replace('_', ' ').upper()
            f.write(f"\n{'─' * 70}\n")
            f.write(f"{label} ({len(items)} cases)\n")
            f.write(f"{'─' * 70}\n\n")
            
            for i, row in enumerate(items, 1):
                f.write(f"{i}. ID: {row['id']}\n")
                f.write(f"   Domain: {row['domain_expected']}\n")
                f.write(f"   Requirement: {row['requirement_sentence']}\n\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_failures.py <ood_generated_csv>")
        sys.exit(1)
    
    analyze_failures(sys.argv[1])
