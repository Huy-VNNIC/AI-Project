#!/usr/bin/env python3
WORKDIR = '/home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP'
with open(WORKDIR+'/main.log') as f:
    lines = f.readlines()

# Check last error count and if PDF produced
errors = [l for l in lines if l.startswith('! ')]
print(f'Total error lines: {len(errors)}')
print('First 3 errors:')
for e in errors[:3]:
    print(' ', e.rstrip())

# Find "Output written" line
for l in lines:
    if 'Output written' in l:
        print('Output:', l.rstrip())

# Check if any tikz/pgfplot warnings about empty output
for l in lines:
    if 'empty' in l.lower() and ('plot' in l.lower() or 'tikz' in l.lower()):
        print('Empty:', l.rstrip())
