"""Compare v2 vs v3 quality improvements"""
import csv

v2_rows = list(csv.DictReader(open('scripts/eval/ood_generated.csv')))
v3_rows = list(csv.DictReader(open('scripts/eval/ood_generated_v3.csv')))

v2_success = [r for r in v2_rows if r['generated_title'] != '[NO OUTPUT]']
v3_success = [r for r in v3_rows if r['generated_title'] != '[NO OUTPUT]']

print('=' * 80)
print('V2 vs V3 COMPARISON')
print('=' * 80)
print(f'\nCoverage:')
print(f'  V2: {len(v2_success)}/250 ({100*len(v2_success)/250:.1f}%)')
print(f'  V3: {len(v3_success)}/250 ({100*len(v3_success)/250:.1f}%)')
print(f'  Delta: {len(v3_success) - len(v2_success):+d}')

print(f'\nQuality Comparison (first 10 rows):')
print('=' * 80)

improvements = 0
for i in range(min(10, len(v2_success), len(v3_success))):
    req = v2_success[i]['requirement_sentence'][:65]
    v2_title = v2_success[i]['generated_title']
    v3_title = v3_success[i]['generated_title']
    
    print(f'\n{i+1}. {req}...')
    print(f'   V2: {v2_title}')
    print(f'   V3: {v3_title}')
    
    # Check for improvements
    generic_words = ['system', 'application', 'platform', 'feature']
    v2_has_generic = any(g in v2_title.lower() for g in generic_words)
    v3_has_generic = any(g in v3_title.lower() for g in generic_words)
    
    if v2_has_generic and not v3_has_generic:
        print('   ✅ IMPROVED: Removed generic terms')
        improvements += 1
    elif v2_title != v3_title:
        if len(v3_title.split()) > len(v2_title.split()):
            print('   🔄 More specific')
        else:
            print('   🔄 Changed')

print(f'\n{"-" * 80}')
print(f'Total improvements in first 10: {improvements}')
