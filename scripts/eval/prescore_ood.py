"""
Auto pre-score OOD pilot to reduce manual work
Fills in binary/flag columns that can be automated
"""
import csv
import re
from difflib import SequenceMatcher

def prescore_ood(input_csv: str, output_csv: str):
    """
    Automatically fill flag columns to reduce manual scoring work
    
    Fills:
    - domain_applicable (1 if domain in scope, 0 if OOD)
    - flag_generic (1 if title contains generic terms)
    - has_duplicates (1 if AC has duplicates)
    - flag_wrong_intent (1 if title doesn't match requirement keywords)
    """
    print(f"📖 Reading {input_csv}...")
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Known domains (in-scope for model)
    IN_SCOPE_DOMAINS = {'ecommerce', 'finance', 'healthcare', 'iot', 'education'}
    
    # Generic terms that indicate poor title quality
    GENERIC_TERMS = {
        'system', 'application', 'platform', 'feature', 'functionality',
        'solution', 'tool', 'module', 'service', 'capability', 'product'
    }
    
    print(f"\n🤖 Auto-scoring {len(rows)} rows...")
    
    for i, row in enumerate(rows, 1):
        # Skip if no output
        if not row.get('generated_title') or row.get('generated_title') == '[NO OUTPUT]':
            continue
        
        # 1. domain_applicable
        domain = row.get('generated_domain', '').lower()
        row['domain_applicable'] = '1' if domain in IN_SCOPE_DOMAINS else '0'
        
        # 2. flag_generic (title contains generic terms)
        title = row.get('generated_title', '').lower()
        has_generic = any(term in title for term in GENERIC_TERMS)
        row['flag_generic'] = '1' if has_generic else '0'
        
        # 3. has_duplicates (check AC for duplicates)
        ac_list = []
        for j in range(1, 7):
            ac = row.get(f'generated_ac_{j}', '').strip()
            if ac:
                ac_list.append(ac.lower())
        
        # Check for near-duplicates (similarity > 0.85)
        has_dup = False
        for idx_i in range(len(ac_list)):
            for idx_j in range(idx_i + 1, len(ac_list)):
                sim = SequenceMatcher(None, ac_list[idx_i], ac_list[idx_j]).ratio()
                if sim > 0.85:
                    has_dup = True
                    break
            if has_dup:
                break
        
        row['has_duplicates'] = '1' if has_dup else '0'
        
        # 4. flag_wrong_intent (title doesn't contain main keywords from requirement)
        requirement = row.get('requirement_sentence', '').lower()
        
        # Extract key nouns from requirement (simple heuristic)
        # Skip common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
                     'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'should', 'could', 'may', 'might', 'must', 'shall', 'can'}
        
        # Extract words longer than 4 chars, not in stop_words
        req_words = [w for w in re.findall(r'\b\w+\b', requirement) 
                    if len(w) > 4 and w not in stop_words]
        
        # Check if title contains at least one key requirement word
        title_words = set(re.findall(r'\b\w+\b', title))
        has_keyword = any(word in title_words for word in req_words[:5])  # Top 5 words
        
        row['flag_wrong_intent'] = '0' if has_keyword else '1'
        
        if i % 10 == 0:
            print(f"   Scored {i}/{len(rows)}...")
    
    # Write output
    print(f"\n💾 Writing {output_csv}...")
    
    # Keep all existing columns
    fieldnames = list(rows[0].keys()) if rows else []
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Done! Pre-scored output written to {output_csv}")
    print(f"\n📋 Auto-scored columns:")
    print(f"   ✅ domain_applicable (in-scope vs OOD)")
    print(f"   ✅ flag_generic (generic terms in title)")
    print(f"   ✅ has_duplicates (AC similarity check)")
    print(f"   ✅ flag_wrong_intent (keyword mismatch)")
    print(f"\n⚠️  Still need manual scoring:")
    print(f"   - score_title_clarity (1-5)")
    print(f"   - score_desc_correctness (1-5)")
    print(f"   - score_ac_testability (1-5)")
    print(f"   - score_label_type (0/1)")
    print(f"   - score_label_domain (0/1)")
    print(f"   - score_priority_reasonable (0/1)")
    print(f"   - notes (text)")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python prescore_ood.py <input_csv> <output_csv>")
        print("Example: python prescore_ood.py ood_pilot_v3.csv ood_pilot_v3_prescored.csv")
        sys.exit(1)
    
    prescore_ood(sys.argv[1], sys.argv[2])
