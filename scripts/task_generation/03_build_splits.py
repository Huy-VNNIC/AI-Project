"""
Script 3: Stratified train/val/test split
"""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


class DatasetSplitter:
    """Create stratified train/val/test splits"""
    
    def __init__(self, input_path, output_path):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def split(self, train_size=0.8, val_size=0.1, test_size=0.1, random_state=42):
        """Create stratified splits"""
        print(f"📊 Creating train/val/test splits")
        print(f"   Splits: train={train_size}, val={val_size}, test={test_size}")
        
        # Load full dataset
        input_file = self.input_path / "clean_full.parquet"
        if not input_file.exists():
            print(f"❌ Input file not found: {input_file}")
            print(f"   Please run 02_build_parquet.py first")
            sys.exit(1)
        
        print(f"📂 Loading data from: {input_file}")
        df = pd.read_parquet(input_file)
        print(f"   Loaded {len(df):,} rows")
        
        # Create stratification column (combine is_requirement + domain)
        df['_strat'] = df['is_requirement'].astype(str) + '_' + df['domain'].astype(str)
        
        print(f"\n🎯 Stratification distribution:")
        strat_counts = df['_strat'].value_counts()
        print(f"   Total unique strata: {len(strat_counts)}")
        
        # Remove rare strata (less than 3 samples) to avoid split errors
        min_samples = 3
        valid_strata = strat_counts[strat_counts >= min_samples].index
        df_stratified = df[df['_strat'].isin(valid_strata)].copy()
        
        removed = len(df) - len(df_stratified)
        if removed > 0:
            print(f"   ⚠️  Removed {removed} rows from rare strata (< {min_samples} samples)")
        
        # First split: train vs (val + test)
        X = df_stratified.drop(columns=['_strat'])
        y = df_stratified['_strat']
        
        test_val_size = val_size + test_size
        
        print(f"\n🔀 Splitting data...")
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y,
            test_size=test_val_size,
            stratify=y,
            random_state=random_state
        )
        
        # Second split: val vs test
        val_ratio = val_size / test_val_size
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=(1 - val_ratio),
            stratify=y_temp,
            random_state=random_state
        )
        
        # Save splits
        train_file = self.output_path / "train.parquet"
        val_file = self.output_path / "val.parquet"
        test_file = self.output_path / "test.parquet"
        
        X_train.to_parquet(train_file, index=False, engine='pyarrow', compression='snappy')
        X_val.to_parquet(val_file, index=False, engine='pyarrow', compression='snappy')
        X_test.to_parquet(test_file, index=False, engine='pyarrow', compression='snappy')
        
        print(f"\n✅ Splits saved:")
        print(f"   Train: {len(X_train):,} rows -> {train_file}")
        print(f"   Val:   {len(X_val):,} rows -> {val_file}")
        print(f"   Test:  {len(X_test):,} rows -> {test_file}")
        
        # Save split metadata
        metadata = {
            'total_samples': len(df),
            'stratified_samples': len(df_stratified),
            'train_size': len(X_train),
            'val_size': len(X_val),
            'test_size': len(X_test),
            'train_ratio': len(X_train) / len(df_stratified),
            'val_ratio': len(X_val) / len(df_stratified),
            'test_ratio': len(X_test) / len(df_stratified),
            'random_state': random_state,
            'stratification_column': 'is_requirement + domain'
        }
        
        # Check distributions
        print(f"\n📊 Split distributions:")
        self._print_distribution(X_train, "Train")
        self._print_distribution(X_val, "Val")
        self._print_distribution(X_test, "Test")
        
        metadata_file = self.output_path / "split_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"\n💾 Metadata saved to: {metadata_file}")
        
        return metadata
    
    def _print_distribution(self, df, split_name):
        """Print label distribution for a split"""
        print(f"\n  {split_name}:")
        if 'is_requirement' in df.columns:
            req_dist = df['is_requirement'].value_counts(normalize=True)
            print(f"    is_requirement: ", end='')
            for val, pct in req_dist.items():
                print(f"{val}={pct:.1%} ", end='')
            print()
        
        if 'priority' in df.columns:
            priority_dist = df['priority'].value_counts()
            print(f"    priority: {dict(priority_dist.head(3))}")
        
        if 'domain' in df.columns:
            domain_dist = df['domain'].value_counts()
            print(f"    domain: {dict(domain_dist.head(3))}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create train/val/test splits')
    parser.add_argument('--input', type=str,
                       default='data/processed',
                       help='Input folder with clean_full.parquet')
    parser.add_argument('--output', type=str,
                       default='data/splits',
                       help='Output folder for splits')
    parser.add_argument('--train-size', type=float, default=0.8,
                       help='Train split ratio')
    parser.add_argument('--val-size', type=float, default=0.1,
                       help='Validation split ratio')
    parser.add_argument('--test-size', type=float, default=0.1,
                       help='Test split ratio')
    parser.add_argument('--random-state', type=int, default=42,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Validate ratios
    total = args.train_size + args.val_size + args.test_size
    if not np.isclose(total, 1.0):
        print(f"❌ Split ratios must sum to 1.0 (got {total})")
        sys.exit(1)
    
    input_path = PROJECT_ROOT / args.input
    output_path = PROJECT_ROOT / args.output
    
    splitter = DatasetSplitter(input_path, output_path)
    splitter.split(
        train_size=args.train_size,
        val_size=args.val_size,
        test_size=args.test_size,
        random_state=args.random_state
    )
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
