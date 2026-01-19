#!/usr/bin/env python3
"""
Run MATLAB Visualization Scripts
Alternative: Use Octave (free, open-source MATLAB alternative)
"""
import subprocess
import sys
from pathlib import Path

def check_matlab():
    """Check if MATLAB is available"""
    try:
        result = subprocess.run(['matlab', '-batch', 'disp("MATLAB OK")'], 
                               capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def check_octave():
    """Check if Octave is available"""
    try:
        result = subprocess.run(['octave', '--version'], 
                               capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def run_matlab_script(script_path, use_octave=False):
    """Run a MATLAB/Octave script"""
    script_path = Path(script_path)
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        if use_octave:
            print(f"🔧 Running with Octave: {script_path.name}")
            cmd = ['octave', '--no-gui', '--eval', f"run('{script_path}')"]
        else:
            print(f"🔧 Running with MATLAB: {script_path.name}")
            cmd = ['matlab', '-batch', f"run('{script_path}')"]
        
        result = subprocess.run(cmd, cwd=script_path.parent, 
                               capture_output=False, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Success: {script_path.name}\n")
            return True
        else:
            print(f"❌ Failed: {script_path.name} (exit code {result.returncode})\n")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout: {script_path.name}\n")
        return False
    except Exception as e:
        print(f"❌ Error running {script_path.name}: {e}\n")
        return False

def main():
    print("=" * 70)
    print("  MATLAB/Octave Visualization Runner")
    print("=" * 70)
    print()
    
    # Check availability
    has_matlab = check_matlab()
    has_octave = check_octave()
    
    if not has_matlab and not has_octave:
        print("❌ Neither MATLAB nor Octave found!")
        print("\nInstall options:")
        print("  1. MATLAB: https://www.mathworks.com/products/matlab.html")
        print("  2. Octave (free): sudo apt install octave  # Ubuntu/Debian")
        print("                    brew install octave      # macOS")
        print("                    https://www.gnu.org/software/octave/")
        return 1
    
    use_octave = not has_matlab
    
    if use_octave:
        print("✓ Using Octave (MATLAB alternative)")
    else:
        print("✓ Using MATLAB")
    
    print()
    
    # Find visualization directory
    viz_dir = Path(__file__).parent / "matlab_visualization"
    
    if not viz_dir.exists():
        print(f"❌ Visualization directory not found: {viz_dir}")
        return 1
    
    # Run master script
    master_script = viz_dir / "run_all_visualizations.m"
    
    if master_script.exists():
        print("Running master script (all visualizations)...\n")
        success = run_matlab_script(master_script, use_octave)
        
        if success:
            print("\n" + "=" * 70)
            print("✅ All visualizations generated successfully!")
            print("=" * 70)
            print(f"\nOutput location: {viz_dir}")
            print("\nGenerated files:")
            
            # List PNG files
            png_files = sorted(viz_dir.glob("*.png"))
            for png in png_files:
                print(f"  - {png.name}")
            
            return 0
        else:
            print("\n⚠️  Some errors occurred. Check output above.")
            return 1
    else:
        print(f"❌ Master script not found: {master_script}")
        print("\nAvailable scripts:")
        for script in sorted(viz_dir.glob("*.m")):
            print(f"  - {script.name}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
