#!/usr/bin/env python3
"""Directly patch the compiled pdftex.map to fix bad .fd entries."""
import subprocess, os, shutil

PDFTEX_MAP = "/home/dtu/.texlive2021/texmf-var/fonts/map/pdftex/updmap/pdftex.map"
WORKDIR = "/home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP"

# Correct entries (no .fd references)
CORRECT_ENTRIES = {
    "t1-formata-regular": "t1-formata-regular FormataOTF-Reg < t1-formata-regular.pfb",
    "t1-formata-italic":  "t1-formata-italic FormataOTF-Italic < t1-formata-italic.pfb",
    "t1-formata-medium":  "t1-formata-medium FormataOTFMd < t1-formata-medium.pfb",
    "t1-formata-mediumitalic": "t1-formata-mediumitalic FormataOTFMdIt < t1-formata-mediumitalic.pfb",
    "t1-formata-light":   "t1-formata-light FormataOTF-Lt < t1-formata-light.pfb",
    "t1-formata-lightitalic": "t1-formata-lightitalic FormataOTF-LtIt < t1-formata-lightitalic.pfb",
    "t1-formata-bold":    "t1-formata-bold FormataOTF-Bold < t1-formata-bold.pfb",
    "t1-formata-bolditalic": "t1-formata-bolditalic FormataOTF-BdIt < t1-formata-bolditalic.pfb",
    "t1-formata-condmedium": "t1-formata-condmedium FormataOTFCond-Md < t1-formata-condmedium.pfb",
    "t1-formata-condmediumital": "t1-formata-condmediumital FormataOTFCond-MdIt < t1-formata-condmediumital.pfb",
    "t1-formata-regsymb": "t1-formata-regsymb FormataOTF-Reg < t1-formata-regsymb.pfb",
    # Times
    "t1-times":           "t1-times TimesLTStd-Roman < t1-times.pfb",
    "t1-times-italic":    "t1-times-italic TimesLTStd-Italic < t1-times-italic.pfb",
    "t1-times-bold":      "t1-times-bold TimesLTStd-Bold < t1-times-bold.pfb",
    "t1-times-bolditalic":"t1-times-bolditalic TimesLTStd-BoldItalic < t1-times-bolditalic.pfb",
    # GiovanniStd
    "t1-giovannistd-bookitalic": "t1-giovannistd-bookitalic GiovanniStd-BookItalic < t1-giovannistd-bookitalic.pfb",
}

if not os.path.exists(PDFTEX_MAP):
    print(f"pdftex.map not found at {PDFTEX_MAP}")
    # Try to find it
    result = subprocess.run(['kpsewhich', 'pdftex.map'], capture_output=True, text=True)
    PDFTEX_MAP = result.stdout.strip()
    print(f"Found at: {PDFTEX_MAP}")

# Backup
backup = PDFTEX_MAP + ".bak"
if not os.path.exists(backup):
    shutil.copy2(PDFTEX_MAP, backup)
    print(f"Backed up to {backup}")

with open(PDFTEX_MAP) as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

new_lines = []
fixed = 0
for line in lines:
    stripped = line.rstrip()
    # Check if this line has a bad .fd reference
    parts = stripped.split()
    if parts and parts[0] in CORRECT_ENTRIES:
        # Replace with correct entry
        new_lines.append(CORRECT_ENTRIES[parts[0]] + "\n")
        fixed += 1
        print(f"  Fixed: {stripped}")
        print(f"      -> {CORRECT_ENTRIES[parts[0]]}")
    else:
        new_lines.append(line)

print(f"\nFixed {fixed} entries")

with open(PDFTEX_MAP, 'w') as f:
    f.writelines(new_lines)

print(f"Written: {PDFTEX_MAP}")

# Verify
with open(PDFTEX_MAP) as f:
    content = f.read()
bad_count = sum(1 for fd in ['t1formata.fd', 't1times.fd', 't1giovannistd.fd'] if fd in content)
print(f"Remaining bad .fd entries: {bad_count}")
print("Done!")
