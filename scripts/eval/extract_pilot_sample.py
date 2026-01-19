"""
Extract random sample for pilot OOD evaluation
"""
import csv
import random
from pathlib import Path

def extract_pilot_sample(input_csv: str, output_csv: str, sample_size: int = 50, seed: int = 42):
    """
    Extract random sample of successful rows for pilot evaluation
    
    Args:
        input_csv: Full OOD generated CSV
        output_csv: Pilot sample CSV
        sample_size: Number of rows to sample
        seed: Random seed for reproducibility (default: 42)
    """
    # Set seed for reproducibility
    random.seed(seed)
    
    print(f"📖 Reading {input_csv}...")
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
    
    # Filter success rows only
    success_rows = [
        row for row in all_rows 
        if row['generated_title'] and row['generated_title'] != '[NO OUTPUT]'
    ]
    
    print(f"   Total rows: {len(all_rows)}")
    print(f"   Success rows: {len(success_rows)}")
    print(f"   Failed rows: {len(all_rows) - len(success_rows)}")
    
    # Random sample
    if len(success_rows) <= sample_size:
        sample = success_rows
        print(f"\n⚠️  Only {len(success_rows)} success rows, using all")
    else:
        sample = random.sample(success_rows, sample_size)
        print(f"\n✅ Sampled {sample_size} random rows")
    
    # Add scoring columns
    scoring_columns = [
        'score_title_clarity',
        'score_desc_correctness',
        'score_ac_testability',
        'score_label_type',
        'score_label_domain',
        'score_priority_reasonable',
        'domain_applicable',
        'has_duplicates',
        'flag_generic',
        'flag_wrong_intent',
        'notes'
    ]
    
    fieldnames = list(sample[0].keys()) + scoring_columns
    
    # Write pilot CSV
    print(f"💾 Writing {output_csv}...")
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in sample:
            # Add empty scoring columns
            for col in scoring_columns:
                row[col] = ''
            writer.writerow(row)
    
    print(f"✅ Pilot sample ready!")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {output_csv}")
    print(f"   2. Score each row using OOD_SCORING_RUBRIC.md")
    print(f"   3. Run: python scripts/eval/02_summarize_ood_scores.py {output_csv}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python extract_pilot_sample.py <input_csv> <output_csv> [sample_size] [seed]")
        print("Example: python extract_pilot_sample.py ood_generated.csv ood_pilot.csv 50 42")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    sample_size = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 42
    
    extract_pilot_sample(input_csv, output_csv, sample_size, seed)
