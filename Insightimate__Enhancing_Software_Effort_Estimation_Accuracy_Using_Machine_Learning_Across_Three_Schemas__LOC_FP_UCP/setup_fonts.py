#!/usr/bin/env python3
import subprocess, os, shutil

WORKDIR = '/home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP'
TEMPLATE = WORKDIR + '/template_IEEE/ACCESS_latex_template_20240429/ACCESS_latex_template_20240429'
TEXMFHOME = '/home/dtu/texmf'

os.chdir(WORKDIR)
print("=== Step 1: Install fonts to TEXMFHOME ===")

for d in ['fonts/type1/ieee-access','fonts/tfm/ieee-access',
          'fonts/map/dvips/ieee-access','tex/latex/ieee-access']:
    os.makedirs(f'{TEXMFHOME}/{d}', exist_ok=True)

pfb=tfm=fd=0
for fname in sorted(os.listdir(TEMPLATE)):
    src = os.path.join(TEMPLATE, fname)
    if not os.path.isfile(src):
        continue
    if fname.endswith('.pfb'):
        shutil.copy2(src, f'{TEXMFHOME}/fonts/type1/ieee-access/{fname}')
        pfb += 1
    elif fname.endswith('.tfm'):
        shutil.copy2(src, f'{TEXMFHOME}/fonts/tfm/ieee-access/{fname}')
        tfm += 1
    elif fname.endswith('.fd'):
        shutil.copy2(src, f'{TEXMFHOME}/tex/latex/ieee-access/{fname}')
        fd += 1

print(f"Installed: {pfb} PFB, {tfm} TFM, {fd} FD files")

print("\n=== Step 2: Create font map files ===")
map_dir = f'{TEXMFHOME}/fonts/map/dvips/ieee-access'

with open(f'{map_dir}/t1-formata.map', 'w') as f:
    for n in ['regular','italic','medium','mediumitalic','light','lightitalic',
              'bold','bolditalic','condmedium','condmediumital','regsymb']:
        f.write(f't1-formata-{n} <t1-formata-{n}.pfb\n')
print("  t1-formata.map created")

with open(f'{map_dir}/t1-giovannistd.map', 'w') as f:
    f.write('t1-giovannistd-bookitalic <t1-giovannistd-bookitalic.pfb\n')
print("  t1-giovannistd.map created")

with open(f'{map_dir}/t1-times.map', 'w') as f:
    for s in ['', '-italic', '-bold', '-bolditalic']:
        f.write(f't1-times{s} <t1-times{s}.pfb\n')
print("  t1-times.map created")

print("\n=== Step 3: Update TeX database ===")
r = subprocess.run(['mktexlsr', TEXMFHOME], capture_output=True, text=True)
if r.returncode == 0:
    print("  mktexlsr: OK")
else:
    print(f"  mktexlsr error: {r.stderr[:300]}")

print("\n=== Step 4: Register fonts with updmap-user ===")
for mapname in ['t1-formata.map', 't1-giovannistd.map', 't1-times.map']:
    r = subprocess.run(['updmap-user', '--enable', f'Map={mapname}'],
                       capture_output=True, text=True)
    status = "OK" if r.returncode == 0 else f"FAILED: {r.stderr[:100]}"
    print(f"  {mapname}: {status}")

print("\n=== Step 5: Copy original ieeeaccess.cls from template ===")
shutil.copy2(f'{TEMPLATE}/ieeeaccess.cls', f'{WORKDIR}/ieeeaccess.cls')
print("  ieeeaccess.cls restored from template")

print("\n=== Step 6: Restore main.tex from backup with proper structure ===")
with open(f'{WORKDIR}/main_backup.tex', 'r') as f:
    content = f.read()

# Update date to current
content = content.replace(
    'Date of publication xxxx 00, 0000, date of current version xxxx 00, 0000.',
    'Date of publication April 17, 2026, date of current version April 17, 2026.'
)
content = content.replace(
    '10.1109/ACCESS.2024.0429000',
    '10.1109/ACCESS.2026.XXXXXX'
)

# Add \EOD before \end{document} if not present
if r'\EOD' not in content:
    content = content.replace(r'\end{document}', '\\EOD\n\\end{document}')

with open(f'{WORKDIR}/main.tex', 'w') as f:
    f.write(content)

lines = content.count('\n') + 1
print(f"  main.tex written: {lines} lines")
print("\n=== Done. Ready to compile. ===")
