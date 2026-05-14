#!/usr/bin/env python3
"""Run compile.py and show summary."""
import subprocess, os, sys

WORKDIR = "/home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP"

r = subprocess.run([sys.executable, 'compile.py'], capture_output=True, cwd=WORKDIR)
out = r.stdout.decode('utf-8', errors='replace') + r.stderr.decode('utf-8', errors='replace')
for line in out.splitlines():
    l = line.strip()
    if any(k in l for k in ['>>>', 'Exit code', '=== ', '[!]', 'Output written']):
        print(line)

import os
pdf = os.path.join(WORKDIR, 'main.pdf')
if os.path.exists(pdf):
    size = os.path.getsize(pdf)
    print(f"\nmain.pdf: {size:,} bytes ({size/1024/1024:.2f} MB)")
