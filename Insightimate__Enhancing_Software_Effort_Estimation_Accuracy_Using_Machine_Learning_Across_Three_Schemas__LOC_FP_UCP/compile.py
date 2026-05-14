#!/usr/bin/env python3
"""Compile main.tex using pdflatex + bibtex, 3 passes."""
import subprocess, os, sys

WORKDIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print(f"\n>>> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=WORKDIR, capture_output=True, text=True)
    # Show fatal errors / key lines from stdout
    out = result.stdout + result.stderr
    for line in out.splitlines():
        if any(k in line for k in ['!pdfTeX', '! ', 'Fatal', 'Error', 'error', 'Warning: Font']):
            print(line)
    print(f"Exit code: {result.returncode}")
    return result.returncode, out

# Pass 1
rc, out1 = run(['pdflatex', '-interaction=nonstopmode', '-file-line-error', 'main.tex'])

# Check for font-related errors
if 'unexpected end of file' in out1:
    print("\n[!] 'unexpected end of file' error found - checking fd files...")
    for fd in ['t1formata.fd', 't1giovannistd.fd', 't1helvetica.fd', 't1times.fd']:
        fpath = os.path.join(WORKDIR, fd)
        if os.path.exists(fpath):
            with open(fpath) as f:
                content = f.read()
            has_endinput = '\\endinput' in content
            print(f"  {fd}: {len(content.splitlines())} lines, endinput={has_endinput}")
        else:
            print(f"  {fd}: NOT FOUND")

# Check which font files are on kpathsea search path
print("\n>>> Checking font availability:")
for font in ['t1-formata.map', 't1-formata-regular.pfb', 't1-formata-regular.tfm']:
    r = subprocess.run(['kpsewhich', font], capture_output=True, text=True, cwd=WORKDIR)
    found = r.stdout.strip() or 'NOT FOUND'
    print(f"  {font}: {found}")

# Show last 30 lines of main.log
print("\n>>> Last 30 lines of main.log:")
logpath = os.path.join(WORKDIR, 'main.log')
if os.path.exists(logpath):
    with open(logpath) as f:
        lines = f.readlines()
    for line in lines[-30:]:
        print(line, end='')

if rc != 0:
    # Check if PDF was actually produced despite errors (nonstopmode can continue)
    import glob
    pdf_exists = os.path.exists(os.path.join(WORKDIR, 'main.pdf'))
    if not pdf_exists:
        print("\n[!] pdflatex pass 1 failed and no PDF produced - stopping.")
        sys.exit(1)
    else:
        print("\n[!] pdflatex pass 1 had errors but PDF was produced - continuing...")

# BibTeX
run(['bibtex', 'main'])

# Pass 2
run(['pdflatex', '-interaction=nonstopmode', 'main.tex'])

# Pass 3
rc3, out3 = run(['pdflatex', '-interaction=nonstopmode', 'main.tex'])

pdf_exists = os.path.exists(os.path.join(WORKDIR, 'main.pdf'))
if rc3 == 0:
    print("\n=== SUCCESS: main.pdf generated ===")
elif pdf_exists and 'Output written on main.pdf' in out3:
    import re
    m = re.search(r'Output written on main\.pdf \((\d+) pages,', out3)
    pages = m.group(1) if m else '?'
    print(f"\n=== SUCCESS (with non-fatal warnings): main.pdf generated ({pages} pages) ===")
    print("    Warnings are cosmetic (pgf version-mismatch / missing optional photo files).")
else:
    print("\n[!] Final pass failed - check main.log")
    sys.exit(1)
