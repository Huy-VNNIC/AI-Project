"""
Script 1: Scan toàn bộ dataset để phân tích cấu trúc và chất lượng dữ liệu
Không load hết vào RAM - streaming processing
"""
import os
import sys
import glob
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

class DatasetScanner:
    """Scanner để phân tích dataset lớn mà không load hết vào RAM"""
    
    def __init__(self, dataset_path):
        self.dataset_path = Path(dataset_path)
        self.stats = {
            'total_rows': 0,
            'total_files': 0,
            'is_requirement': Counter(),
            'type': Counter(),
            'priority': Counter(),
            'domain': Counter(),
            'text_lengths': [],
            'missing_values': {
                'text': 0,
                'is_requirement': 0,
                'type': 0,
                'priority': 0,
                'domain': 0
            },
            'duplicates': set(),
            'duplicate_count': 0,
            'sample_requirements': [],
            'sample_non_requirements': []
        }
        
    def scan(self, chunksize=10000, max_text_length_samples=10000):
        """Scan toàn bộ dataset theo chunks"""
        print(f"🔍 Scanning dataset: {self.dataset_path}")
        
        csv_files = sorted(glob.glob(str(self.dataset_path / "chunk_*.csv")))
        self.stats['total_files'] = len(csv_files)
        
        print(f"📁 Found {len(csv_files)} CSV files")
        
        for file_idx, csv_file in enumerate(csv_files):
            print(f"\n📄 Processing file {file_idx + 1}/{len(csv_files)}: {Path(csv_file).name}")
            
            try:
                # Read in chunks to avoid memory issues
                for chunk_idx, chunk in enumerate(pd.read_csv(csv_file, chunksize=chunksize)):
                    self._process_chunk(chunk, max_text_length_samples)
                    
                    if (chunk_idx + 1) % 10 == 0:
                        print(f"  ✓ Processed {(chunk_idx + 1) * chunksize} rows from this file")
                        
            except Exception as e:
                print(f"  ❌ Error reading {csv_file}: {e}")
                continue
        
        # Calculate final statistics
        self._finalize_stats()
        
        print("\n" + "="*80)
        print("✅ Scan completed!")
        print("="*80)
        
        return self.stats
    
    def _process_chunk(self, chunk, max_text_length_samples):
        """Process a single chunk of data"""
        chunk_size = len(chunk)
        self.stats['total_rows'] += chunk_size
        
        # Check for required columns
        required_cols = ['text', 'is_requirement', 'type', 'priority', 'domain']
        missing_cols = [col for col in required_cols if col not in chunk.columns]
        if missing_cols:
            print(f"  ⚠️  Missing columns: {missing_cols}")
            return
        
        # Count missing values
        for col in required_cols:
            self.stats['missing_values'][col] += chunk[col].isna().sum()
        
        # Filter out rows with missing text
        chunk = chunk.dropna(subset=['text'])
        
        # Count distributions
        for col in ['is_requirement', 'type', 'priority', 'domain']:
            if col in chunk.columns:
                self.stats[col].update(chunk[col].value_counts().to_dict())
        
        # Sample text lengths (don't store all to save memory)
        if len(self.stats['text_lengths']) < max_text_length_samples:
            lengths = chunk['text'].astype(str).str.len().tolist()
            self.stats['text_lengths'].extend(lengths[:max_text_length_samples - len(self.stats['text_lengths'])])
        
        # Track duplicates using hash
        for text in chunk['text'].dropna():
            text_hash = hash(str(text))
            if text_hash in self.stats['duplicates']:
                self.stats['duplicate_count'] += 1
            else:
                self.stats['duplicates'].add(text_hash)
        
        # Collect samples
        if len(self.stats['sample_requirements']) < 50:
            req_samples = chunk[chunk['is_requirement'] == 1].head(10)
            for _, row in req_samples.iterrows():
                self.stats['sample_requirements'].append({
                    'text': row['text'],
                    'type': row.get('type', 'unknown'),
                    'priority': row.get('priority', 'unknown'),
                    'domain': row.get('domain', 'unknown')
                })
        
        if len(self.stats['sample_non_requirements']) < 50:
            non_req_samples = chunk[chunk['is_requirement'] == 0].head(10)
            for _, row in non_req_samples.iterrows():
                self.stats['sample_non_requirements'].append({
                    'text': row['text'],
                    'type': row.get('type', 'unknown'),
                    'domain': row.get('domain', 'unknown')
                })
    
    def _finalize_stats(self):
        """Calculate final statistics"""
        # Calculate text length statistics
        if self.stats['text_lengths']:
            self.stats['text_length_stats'] = {
                'min': int(np.min(self.stats['text_lengths'])),
                'max': int(np.max(self.stats['text_lengths'])),
                'mean': float(np.mean(self.stats['text_lengths'])),
                'median': float(np.median(self.stats['text_lengths'])),
                'std': float(np.std(self.stats['text_lengths']))
            }
        
        # Remove the large set from stats
        del self.stats['duplicates']
        
        # Convert Counters to dicts for JSON serialization
        self.stats['is_requirement'] = dict(self.stats['is_requirement'])
        self.stats['type'] = dict(self.stats['type'])
        self.stats['priority'] = dict(self.stats['priority'])
        self.stats['domain'] = dict(self.stats['domain'])
    
    def print_summary(self):
        """Print a human-readable summary"""
        print("\n" + "="*80)
        print("📊 DATASET SUMMARY")
        print("="*80)
        
        print(f"\n📈 OVERALL STATISTICS")
        print(f"  Total files:     {self.stats['total_files']}")
        print(f"  Total rows:      {self.stats['total_rows']:,}")
        print(f"  Duplicates:      {self.stats['duplicate_count']:,} ({self.stats['duplicate_count']/self.stats['total_rows']*100:.2f}%)")
        
        print(f"\n❌ MISSING VALUES")
        for col, count in self.stats['missing_values'].items():
            pct = count / self.stats['total_rows'] * 100 if self.stats['total_rows'] > 0 else 0
            print(f"  {col:20s}: {count:8,} ({pct:5.2f}%)")
        
        print(f"\n📏 TEXT LENGTH STATISTICS")
        if 'text_length_stats' in self.stats:
            for key, value in self.stats['text_length_stats'].items():
                print(f"  {key:10s}: {value:10.2f}")
        
        print(f"\n✅ IS_REQUIREMENT DISTRIBUTION")
        total_valid = sum(self.stats['is_requirement'].values())
        for key, count in sorted(self.stats['is_requirement'].items()):
            pct = count / total_valid * 100 if total_valid > 0 else 0
            print(f"  {key}: {count:8,} ({pct:5.2f}%)")
        
        print(f"\n📋 TYPE DISTRIBUTION")
        for key, count in sorted(self.stats['type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {key:20s}: {count:8,}")
        
        print(f"\n🎯 PRIORITY DISTRIBUTION")
        for key, count in sorted(self.stats['priority'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {key:20s}: {count:8,}")
        
        print(f"\n🏢 DOMAIN DISTRIBUTION")
        for key, count in sorted(self.stats['domain'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {key:20s}: {count:8,}")
        
        print(f"\n📝 SAMPLE REQUIREMENTS (showing {min(5, len(self.stats['sample_requirements']))}):")
        for i, sample in enumerate(self.stats['sample_requirements'][:5], 1):
            print(f"\n  {i}. [{sample['type']}/{sample['priority']}/{sample['domain']}]")
            print(f"     {sample['text'][:100]}...")
        
        print(f"\n🚫 SAMPLE NON-REQUIREMENTS (showing {min(5, len(self.stats['sample_non_requirements']))}):")
        for i, sample in enumerate(self.stats['sample_non_requirements'][:5], 1):
            print(f"\n  {i}. [{sample['type']}/{sample['domain']}]")
            print(f"     {sample['text'][:100]}...")
    
    def save_report(self, output_path):
        """Save detailed report to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save JSON report
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)
        print(f"\n💾 JSON report saved to: {json_path}")
        
        # Save markdown report
        md_path = output_path.with_suffix('.md')
        with open(md_path, 'w') as f:
            f.write(self._generate_markdown_report())
        print(f"💾 Markdown report saved to: {md_path}")
    
    def _generate_markdown_report(self):
        """Generate a markdown report"""
        md = []
        md.append("# Dataset Quality Report")
        md.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"\nDataset: `{self.dataset_path}`")
        
        md.append("\n## Overall Statistics")
        md.append(f"- **Total files**: {self.stats['total_files']}")
        md.append(f"- **Total rows**: {self.stats['total_rows']:,}")
        md.append(f"- **Duplicates**: {self.stats['duplicate_count']:,} ({self.stats['duplicate_count']/self.stats['total_rows']*100:.2f}%)")
        
        md.append("\n## Missing Values")
        md.append("| Column | Count | Percentage |")
        md.append("|--------|-------|------------|")
        for col, count in self.stats['missing_values'].items():
            pct = count / self.stats['total_rows'] * 100 if self.stats['total_rows'] > 0 else 0
            md.append(f"| {col} | {count:,} | {pct:.2f}% |")
        
        md.append("\n## Text Length Statistics")
        if 'text_length_stats' in self.stats:
            md.append("| Metric | Value |")
            md.append("|--------|-------|")
            for key, value in self.stats['text_length_stats'].items():
                md.append(f"| {key.capitalize()} | {value:.2f} |")
        
        md.append("\n## Label Distributions")
        
        md.append("\n### Is Requirement")
        md.append("| Value | Count | Percentage |")
        md.append("|-------|-------|------------|")
        total_valid = sum(self.stats['is_requirement'].values())
        for key, count in sorted(self.stats['is_requirement'].items()):
            pct = count / total_valid * 100 if total_valid > 0 else 0
            md.append(f"| {key} | {count:,} | {pct:.2f}% |")
        
        md.append("\n### Type Distribution")
        md.append("| Type | Count |")
        md.append("|------|-------|")
        for key, count in sorted(self.stats['type'].items(), key=lambda x: x[1], reverse=True)[:10]:
            md.append(f"| {key} | {count:,} |")
        
        md.append("\n### Priority Distribution")
        md.append("| Priority | Count |")
        md.append("|----------|-------|")
        for key, count in sorted(self.stats['priority'].items(), key=lambda x: x[1], reverse=True):
            md.append(f"| {key} | {count:,} |")
        
        md.append("\n### Domain Distribution")
        md.append("| Domain | Count |")
        md.append("|--------|-------|")
        for key, count in sorted(self.stats['domain'].items(), key=lambda x: x[1], reverse=True):
            md.append(f"| {key} | {count:,} |")
        
        md.append("\n## Recommendations")
        
        # Class imbalance check
        req_counts = self.stats['is_requirement']
        if 1 in req_counts and 0 in req_counts:
            req_ratio = req_counts[1] / req_counts[0]
            if req_ratio < 0.5 or req_ratio > 2.0:
                md.append(f"\n⚠️ **Class imbalance detected**: requirement vs non-requirement ratio is {req_ratio:.2f}. Consider using `class_weight='balanced'` in models.")
        
        # Missing values check
        high_missing = [col for col, count in self.stats['missing_values'].items() 
                       if count / self.stats['total_rows'] > 0.01]
        if high_missing:
            md.append(f"\n⚠️ **High missing values** in columns: {', '.join(high_missing)}. Consider imputation or filtering.")
        
        # Duplicate check
        if self.stats['duplicate_count'] / self.stats['total_rows'] > 0.05:
            md.append(f"\n⚠️ **High duplicate rate** ({self.stats['duplicate_count']/self.stats['total_rows']*100:.2f}%). Consider deduplication.")
        
        return '\n'.join(md)


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan and analyze requirement dataset')
    parser.add_argument('--dataset', type=str, 
                       default='requirement_analyzer/dataset_large_1m',
                       help='Path to dataset folder (relative to project root)')
    parser.add_argument('--output', type=str,
                       default='report/data_quality_report',
                       help='Output report path (relative to project root)')
    parser.add_argument('--chunksize', type=int, default=10000,
                       help='Chunk size for streaming processing')
    
    args = parser.parse_args()
    
    # Resolve paths
    dataset_path = PROJECT_ROOT / args.dataset
    output_path = PROJECT_ROOT / args.output
    
    if not dataset_path.exists():
        print(f"❌ Dataset path not found: {dataset_path}")
        sys.exit(1)
    
    # Run scanner
    scanner = DatasetScanner(dataset_path)
    stats = scanner.scan(chunksize=args.chunksize)
    
    # Print and save results
    scanner.print_summary()
    scanner.save_report(output_path)
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
