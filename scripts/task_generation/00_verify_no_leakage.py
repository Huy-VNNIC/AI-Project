"""
Script 0: Data Leakage Verification
Checks if train/val/test splits have overlapping text (hash-based)
"""
import os
import sys
import hashlib
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


def text_hash(text):
    """Create MD5 hash of normalized text"""
    if pd.isna(text):
        return None
    normalized = str(text).lower().strip()
    return hashlib.md5(normalized.encode()).hexdigest()


def verify_splits(splits_dir):
    """Verify no text overlap between train/val/test splits"""
    splits_path = Path(splits_dir)
    
    print("=" * 70)
    print("DATA LEAKAGE VERIFICATION")
    print("=" * 70)
    
    # Load splits
    train_file = splits_path / "train.parquet"
    val_file = splits_path / "val.parquet"
    test_file = splits_path / "test.parquet"
    
    if not all([train_file.exists(), val_file.exists(), test_file.exists()]):
        print("❌ ERROR: Split files not found")
        print(f"   Expected location: {splits_path}")
        print(f"   Run 03_build_splits.py first")
        return False
    
    print(f"\n📂 Loading splits from: {splits_path}")
    train_df = pd.read_parquet(train_file)
    val_df = pd.read_parquet(val_file)
    test_df = pd.read_parquet(test_file)
    
    print(f"   Train: {len(train_df):,} samples")
    print(f"   Val:   {len(val_df):,} samples")
    print(f"   Test:  {len(test_df):,} samples")
    print(f"   Total: {len(train_df) + len(val_df) + len(test_df):,} samples")
    
    # Compute hashes
    print(f"\n🔍 Computing text hashes...")
    train_df['_hash'] = train_df['text'].apply(text_hash)
    val_df['_hash'] = val_df['text'].apply(text_hash)
    test_df['_hash'] = test_df['text'].apply(text_hash)
    
    # Remove None hashes (if any)
    train_hashes = set(train_df['_hash'].dropna())
    val_hashes = set(val_df['_hash'].dropna())
    test_hashes = set(test_df['_hash'].dropna())
    
    print(f"   Train unique hashes: {len(train_hashes):,}")
    print(f"   Val unique hashes:   {len(val_hashes):,}")
    print(f"   Test unique hashes:  {len(test_hashes):,}")
    
    # Check overlaps
    print(f"\n🔬 Checking for overlaps...")
    overlap_train_val = train_hashes & val_hashes
    overlap_train_test = train_hashes & test_hashes
    overlap_val_test = val_hashes & test_hashes
    
    print(f"\n{'=' * 70}")
    print("RESULTS")
    print("=" * 70)
    
    issues_found = False
    
    # Train/Val overlap
    if len(overlap_train_val) > 0:
        print(f"❌ LEAKAGE DETECTED: Train/Val overlap = {len(overlap_train_val):,} samples")
        issues_found = True
        
        # Show examples
        print(f"\n   Example overlapping texts:")
        sample_hashes = list(overlap_train_val)[:3]
        for h in sample_hashes:
            train_text = train_df[train_df['_hash'] == h]['text'].iloc[0]
            val_text = val_df[val_df['_hash'] == h]['text'].iloc[0]
            print(f"   - Train: {train_text[:80]}...")
            print(f"     Val:   {val_text[:80]}...")
            print()
    else:
        print(f"✅ Train/Val overlap: 0 (CLEAN)")
    
    # Train/Test overlap
    if len(overlap_train_test) > 0:
        print(f"❌ LEAKAGE DETECTED: Train/Test overlap = {len(overlap_train_test):,} samples")
        issues_found = True
        
        # Show examples
        print(f"\n   Example overlapping texts:")
        sample_hashes = list(overlap_train_test)[:3]
        for h in sample_hashes:
            train_text = train_df[train_df['_hash'] == h]['text'].iloc[0]
            test_text = test_df[test_df['_hash'] == h]['text'].iloc[0]
            print(f"   - Train: {train_text[:80]}...")
            print(f"     Test:  {test_text[:80]}...")
            print()
    else:
        print(f"✅ Train/Test overlap: 0 (CLEAN)")
    
    # Val/Test overlap
    if len(overlap_val_test) > 0:
        print(f"❌ LEAKAGE DETECTED: Val/Test overlap = {len(overlap_val_test):,} samples")
        issues_found = True
        
        # Show examples
        print(f"\n   Example overlapping texts:")
        sample_hashes = list(overlap_val_test)[:3]
        for h in sample_hashes:
            val_text = val_df[val_df['_hash'] == h]['text'].iloc[0]
            test_text = test_df[test_df['_hash'] == h]['text'].iloc[0]
            print(f"   - Val:  {val_text[:80]}...")
            print(f"     Test: {test_text[:80]}...")
            print()
    else:
        print(f"✅ Val/Test overlap: 0 (CLEAN)")
    
    print(f"\n{'=' * 70}")
    
    if issues_found:
        print("❌ DATA LEAKAGE DETECTED")
        print("\n⚠️  CRITICAL: Cannot claim high accuracy until leakage is fixed")
        print("\nRecommended actions:")
        print("1. Modify 03_build_splits.py to use hash-based deduplication:")
        print("   - Compute hash(text) for all samples")
        print("   - Group by hash, keep only one sample per hash")
        print("   - Then do stratified split")
        print("2. Re-run training scripts 04 and 05")
        print("3. Expect accuracy to drop (70-90% is normal and trustworthy)")
        return False
    else:
        print("✅ NO DATA LEAKAGE DETECTED")
        print("\n🎉 Splits are clean - observed metrics are trustworthy")
        print("\nNext steps:")
        print("- Update documentation to report verified metrics")
        print("- Run OOD evaluation on real unseen documents")
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify no data leakage in train/val/test splits")
    parser.add_argument(
        '--splits-dir',
        default='requirement_analyzer/models/task_gen/splits',
        help='Path to splits directory'
    )
    
    args = parser.parse_args()
    
    success = verify_splits(args.splits_dir)
    sys.exit(0 if success else 1)
