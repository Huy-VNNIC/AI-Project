#!/usr/bin/env python3
"""Replace non-T1-compatible Unicode chars in main.tex with LaTeX equivalents."""

text = open('main.tex', encoding='utf-8').read()

lines = text.split('\n')
result = []
for line in lines:
    stripped = line.lstrip()
    is_full_comment = stripped.startswith('%')
    
    if not is_full_comment:
        # ± → $\pm$
        line = line.replace('\u00b1', r'$\pm$')
        # ² → $^2$
        line = line.replace('\u00b2', r'$^2$')
        # × → $\times$
        line = line.replace('\u00d7', r'$\times$')
        # " (left double quote) → ``
        line = line.replace('\u201c', '``')
        # " (right double quote) → ''
        line = line.replace('\u201d', "''")
        # ' (right single quote / smart apostrophe) → ASCII apostrophe
        line = line.replace('\u2019', "'")
    result.append(line)

text2 = '\n'.join(result)
open('main.tex', 'w', encoding='utf-8').write(text2)

print('Done. Remaining non-ASCII in non-comment lines:')
for i, line in enumerate(text2.split('\n'), 1):
    if not line.lstrip().startswith('%') and any(ord(c) > 127 for c in line):
        print(f'  L{i}: {line[:120]}')
