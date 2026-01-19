"""
OOD Evaluation Step 1: Generate Outputs
Fill generated_* columns in OOD template CSV
"""
import sys
import csv
import hashlib
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from requirement_analyzer.task_gen.pipeline import TaskGenerationPipeline


def generate_ood_outputs(input_csv: str, output_csv: str, mode: str = "model", requirement_threshold: float = None):
    """
    Read CSV with requirement_sentence, generate tasks, fill columns
    
    Args:
        input_csv: Path to template CSV with requirement_sentence filled
        output_csv: Path to output CSV with generated_* columns filled
        mode: Generation mode (model, template, llm)
        requirement_threshold: Custom threshold for requirement detection (None = use default)
    """
    print(f"🔄 Loading pipeline (mode={mode})...")
    pipeline = TaskGenerationPipeline(
        model_dir="requirement_analyzer/models/task_gen/models",
        generator_mode=mode
    )
    
    # Log actual generator used
    used_generator_class = type(pipeline.generator).__name__
    used_mode = pipeline.generator_mode
    print(f"🧩 Generator class: {used_generator_class}")
    print(f"🧩 Mode: {used_mode}")
    
    print(f"📖 Reading {input_csv}...")
    rows = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"   Found {len(rows)} rows")
    
    # Process each row
    print(f"\n🚀 Generating outputs...")
    for i, row in enumerate(rows, 1):
        req = row.get('requirement_sentence', '').strip()
        
        # Generate row_id (hash of requirement for reproducible tracking)
        row['row_id'] = hashlib.sha1(req.encode('utf-8')).hexdigest()[:12]
        
        if not req:
            print(f"   {i}/{len(rows)} - SKIP (empty requirement)")
            continue
        
        print(f"   {i}/{len(rows)} - Processing: {req[:60]}...")
        
        try:
            # Generate tasks (with custom threshold for OOD if provided)
            kwargs = {'text': req, 'max_tasks': 1}
            if requirement_threshold is not None:
                kwargs['requirement_threshold'] = requirement_threshold
            
            result = pipeline.generate_tasks(**kwargs)
            
            tasks = result.tasks  # Use attribute, not dict access
            
            if not tasks:
                print(f"      ⚠️  No tasks generated")
                row['generated_title'] = "[NO OUTPUT]"
                row['generated_description'] = ""
                row['generated_type'] = ""
                row['generated_priority'] = ""
                row['generated_domain'] = ""
                row['generated_role'] = ""
                row['used_generator_class'] = used_generator_class
                row['used_mode'] = used_mode
                continue
            
            # Take first task (Pydantic model, not dict)
            task = tasks[0]
            
            # Fill columns
            row['generated_title'] = task.title
            row['generated_description'] = task.description
            row['generated_type'] = task.type
            row['generated_priority'] = task.priority
            row['generated_domain'] = task.domain
            row['generated_role'] = task.role
            row['used_generator_class'] = used_generator_class
            row['used_mode'] = used_mode
            
            # Acceptance criteria
            acs = task.acceptance_criteria
            for j in range(1, 7):
                key = f'generated_ac_{j}'
                row[key] = acs[j-1] if j-1 < len(acs) else ''
            
            print(f"      ✅ Generated: {task.title[:40]}...")
        
        except Exception as e:
            print(f"      ❌ Error: {e}")
            row['generated_title'] = f"[ERROR: {str(e)[:50]}]"
    
    # Write output with dynamic fieldnames
    print(f"\n💾 Writing {output_csv}...")
    
    # Base columns in desired order
    base_cols = [
        'row_id', 'id', 'domain_expected', 'requirement_sentence',
        'generated_title', 'generated_description', 'generated_type',
        'generated_priority', 'generated_domain', 'generated_role',
        'used_generator_class', 'used_mode',
        'generated_ac_1', 'generated_ac_2', 'generated_ac_3',
        'generated_ac_4', 'generated_ac_5', 'generated_ac_6',
        'score_title_clarity', 'score_desc_correctness', 'score_ac_testability',
        'score_label_type', 'score_label_domain', 'score_priority_reasonable',
        'domain_applicable', 'has_duplicates', 'flag_generic', 'flag_wrong_intent', 'notes'
    ]
    
    # Collect all keys from all rows
    all_keys = set()
    for r in rows:
        all_keys.update(r.keys())
    
    # Keep base order first, then append any extra keys (future-proof)
    fieldnames = [col for col in base_cols if col in all_keys] + \
                 sorted([k for k in all_keys if k not in base_cols])
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Done! Output written to {output_csv}")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {output_csv}")
    print(f"   2. Manually score each row (score_* columns)")
    print(f"   3. Run: python scripts/eval/02_summarize_ood_scores.py {output_csv}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate OOD outputs')
    parser.add_argument('input_csv', help='Input CSV with requirement_sentence filled')
    parser.add_argument('output_csv', help='Output CSV with generated_* filled')
    parser.add_argument('--mode', default='model', choices=['model', 'template', 'llm'],
                       help='Generation mode')
    
    args = parser.parse_args()
    
    generate_ood_outputs(args.input_csv, args.output_csv, args.mode)
