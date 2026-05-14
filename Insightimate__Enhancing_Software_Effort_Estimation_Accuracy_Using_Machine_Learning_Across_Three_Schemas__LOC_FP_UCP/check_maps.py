#!/usr/bin/env python3
"""Check compiled pdftex.map for bad entries and fix them."""
import subprocess, os

# Find compiled pdftex.map
result = subprocess.run(['kpsewhich', 'pdftex.map'], capture_output=True, text=True)
pdftex_map = result.stdout.strip()
print(f"pdftex.map location: {pdftex_map}")

if not pdftex_map or not os.path.exists(pdftex_map):
    print("pdftex.map not found!")
else:
    with open(pdftex_map) as f:
        lines = f.readlines()
    
    bad_lines = [(i+1, l.rstrip()) for i, l in enumerate(lines) 
                 if 't1formata.fd' in l or 't1giovannistd.fd' in l or 
                    't1times.fd' in l or 't1helvetica.fd' in l]
    print(f"Total lines: {len(lines)}")
    print(f"Bad .fd entries: {len(bad_lines)}")
    for lineno, l in bad_lines:
        print(f"  line {lineno}: {l}")
    
    # Count t1-formata entries
    formata_lines = [(i+1, l.rstrip()) for i, l in enumerate(lines) if 't1-formata' in l]
    print(f"\nAll t1-formata entries ({len(formata_lines)}):")
    for lineno, l in formata_lines[:5]:
        print(f"  line {lineno}: {l}")
    if len(formata_lines) > 5:
        print(f"  ... and {len(formata_lines)-5} more")

# Also check local t1-formata.map
WORKDIR = "/home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP"
local_map = os.path.join(WORKDIR, "t1-formata.map")
print(f"\nLocal t1-formata.map ({local_map}):")
if os.path.exists(local_map):
    with open(local_map) as f:
        print(f.read())
else:
    print("NOT FOUND")

# Check TEXMFHOME map
texmf_map = "/home/dtu/texmf/fonts/map/dvips/ieee-access/t1-formata.map"
print(f"\nTEXMFHOME t1-formata.map ({texmf_map}):")
if os.path.exists(texmf_map):
    with open(texmf_map) as f:
        print(f.read())
else:
    print("NOT FOUND")
