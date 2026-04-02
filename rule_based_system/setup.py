#!/usr/bin/env python3
"""
Setup and run script for Rule-Based Test Case Generator.
Installs dependencies and runs the quick_start demo in one command.

Usage:
    python3 setup.py
"""

import subprocess
import sys
import os
import platform


def run_command(cmd, description):
    """Run a shell command and report status."""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0 and "already satisfied" not in result.stderr.lower():
            print(f"⚠️  {description}: {result.stderr}")
        else:
            print(f"✅ {description} complete")
        return True
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False


def main():
    """Main setup function."""
    print("\n" + "="*70)
    print("🚀 RULE-BASED TEST CASE GENERATOR - SETUP & RUN")
    print("="*70)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"\n📂 Working directory: {script_dir}")
    
    # Step 1: Install requirements
    print("\n" + "-"*70)
    print("Step 1: Installing Python Dependencies")
    print("-"*70)
    
    if not run_command(
        f"{sys.executable} -m pip install -q -r requirements.txt",
        "Installing requirements.txt"
    ):
        print("⚠️  Continue anyway...")
    
    # Step 2: Download spaCy model
    print("\n" + "-"*70)
    print("Step 2: Downloading spaCy Model")
    print("-"*70)
    
    if not run_command(
        f"{sys.executable} -m spacy download -q en_core_web_sm",
        "Downloading en_core_web_sm"
    ):
        print("⚠️  spaCy model may need manual download")
        print(f"   Run: {sys.executable} -m spacy download en_core_web_sm")
    
    # Step 3: Run quick start
    print("\n" + "-"*70)
    print("Step 3: Running Quick Start Demo")
    print("-"*70)
    
    try:
        import rule_based_system
        from rule_based_system.quick_start import quick_start
        
        print("\n✅ All imports successful!")
        print("\n" + "="*70)
        
        # Run the demo
        quick_start()
        
        print("\n" + "="*70)
        print("✨ SETUP COMPLETE!")
        print("="*70)
        print("\n📚 Next Steps:")
        print("  1. Check sample_output/ for generated test cases")
        print("  2. Start API server: python3 main.py")
        print("  3. Open: http://localhost:8001/docs")
        print("\n💡 Usage Examples:")
        print("  • python3 quick_start.py  (run demo)")
        print("  • python3 main.py         (start REST API)")
        print("  • From code: from rule_based_system import run_pipeline")
        print("\n" + "="*70 + "\n")
        
        return 0
    
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nTroubleshooting:")
        print(f"  • Run: {sys.executable} -m pip install --upgrade pip")
        print(f"  • Run: {sys.executable} -m pip install -r requirements.txt")
        print(f"  • Run: {sys.executable} -m spacy download en_core_web_sm")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
