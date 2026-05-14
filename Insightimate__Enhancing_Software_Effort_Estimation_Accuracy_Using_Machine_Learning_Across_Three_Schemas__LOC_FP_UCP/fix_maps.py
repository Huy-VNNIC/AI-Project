#!/usr/bin/env python3
"""Fix font map files - remove incorrect .fd references and create correct format."""
import subprocess, os, re

WORKDIR = "/home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP"
TEXMFHOME = "/home/dtu/texmf/fonts/map/dvips/ieee-access"

def get_ps_name(pfb_path):
    """Extract PostScript font name from .pfb file."""
    result = subprocess.run(['strings', pfb_path], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        # Try /FontName /Fontname entry
        m = re.search(r'/FontName\s+/(\S+)', line)
        if m:
            return m.group(1)
        # Try %!PS-AdobeFont-1.0: FontName
        if line.startswith('%!PS') or line.startswith('%!Font'):
            parts = line.split()
            if len(parts) >= 2 and ':' in line:
                return line.split(':')[1].strip().split()[0]
    return None

# Get PS names for all pfb files
pfb_files = sorted(f for f in os.listdir(WORKDIR) if f.endswith('.pfb'))
print("=== PFB files and PS names ===")
ps_names = {}
for pfb in pfb_files:
    ps = get_ps_name(os.path.join(WORKDIR, pfb))
    tfm = pfb[:-4]  # strip .pfb
    ps_names[tfm] = ps
    print(f"  {pfb} -> PS: {ps}")

# Create correct t1-formata.map
formata_entries = [
    ("t1-formata-regular",      ps_names.get("t1-formata-regular", "Formata-Regular")),
    ("t1-formata-italic",       ps_names.get("t1-formata-italic", "Formata-Italic")),
    ("t1-formata-medium",       ps_names.get("t1-formata-medium", "Formata-Medium")),
    ("t1-formata-mediumitalic",  ps_names.get("t1-formata-mediumitalic", "Formata-MediumItalic")),
    ("t1-formata-light",        ps_names.get("t1-formata-light", "Formata-Light")),
    ("t1-formata-lightitalic",  ps_names.get("t1-formata-lightitalic", "Formata-LightItalic")),
    ("t1-formata-bold",         ps_names.get("t1-formata-bold", "Formata-Bold")),
    ("t1-formata-bolditalic",   ps_names.get("t1-formata-bolditalic", "Formata-BoldItalic")),
    ("t1-formata-condmedium",   ps_names.get("t1-formata-condmedium", "Formata-CondMedium")),
    ("t1-formata-condmediumital", ps_names.get("t1-formata-condmediumital", "Formata-CondMediumItalic")),
    ("t1-formata-regsymb",      ps_names.get("t1-formata-regsymb", "Formata-RegSymb")),
]

def map_line(tfm, ps):
    if ps:
        return f"{tfm} {ps} < {tfm}.pfb\n"
    else:
        return f"{tfm} < {tfm}.pfb\n"

formata_map = "".join(map_line(t, p) for t, p in formata_entries)
print("\n=== New t1-formata.map ===")
print(formata_map)

# Write to workdir and TEXMFHOME
for path in [os.path.join(WORKDIR, "t1-formata.map"), os.path.join(TEXMFHOME, "t1-formata.map")]:
    with open(path, 'w') as f:
        f.write(formata_map)
    print(f"Written: {path}")

# Also check and fix times and giovannistd maps (copy from template if they exist)
TEMPLATE = os.path.join(WORKDIR, "template_IEEE/ACCESS_latex_template_20240429/ACCESS_latex_template_20240429")
for mapname in ["t1-times.map", "t1-giovannistd.map"]:
    tmpl_path = os.path.join(TEMPLATE, mapname)
    if os.path.exists(tmpl_path):
        with open(tmpl_path) as f:
            content = f.read()
        print(f"\n=== {mapname} (from template) ===")
        print(content)
        for path in [os.path.join(WORKDIR, mapname), os.path.join(TEXMFHOME, mapname)]:
            with open(path, 'w') as f:
                f.write(content)
            print(f"Written: {path}")

# Update mktexlsr
r = subprocess.run(['mktexlsr', '/home/dtu/texmf'], capture_output=True, text=True)
print(f"\nmktexlsr: {r.returncode} - {r.stdout.strip()}")

# Re-register map files with updmap-user
for mapname in ["t1-formata.map", "t1-times.map", "t1-giovannistd.map"]:
    r = subprocess.run(['updmap-user', '--enable', f'Map={mapname}'], capture_output=True, text=True)
    status = "OK" if r.returncode == 0 else f"FAIL: {r.stderr[:100]}"
    print(f"updmap-user {mapname}: {status}")

print("\n=== Done fixing map files ===")
