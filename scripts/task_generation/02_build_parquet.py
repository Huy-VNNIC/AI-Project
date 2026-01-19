"""
Script 2: Clean và convert dataset sang Parquet format để training nhanh
Xử lý streaming để không tràn RAM
"""
import os
import sys
import glob
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


class DatasetCleaner:
    """Clean và chuẩn hóa dataset, sau đó lưu thành parquet"""
    
    def __init__(self, input_path, output_path):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            'total_input': 0,
            'total_output': 0,
            'dropped_missing_text': 0,
            'dropped_duplicates': 0,
            'dropped_too_short': 0,
            'dropped_too_long': 0,
            'normalized_labels': {}
        }
        
        # Label normalization maps
        self.label_maps = {
            'type': {},
            'priority': {
                'none': 'None',
                'low': 'Low',
                'medium': 'Medium',
                'high': 'High'
            },
            'domain': {},
            'is_requirement': {
                0: 0,
                1: 1,
                '0': 0,
                '1': 1,
                'false': 0,
                'true': 1
            }
        }
        
    def process(self, chunksize=10000, min_length=10, max_length=1000):
        """Process all CSV files và convert sang parquet"""
        print(f"🧹 Cleaning dataset: {self.input_path}")
        print(f"📦 Output to: {self.output_path}")
        
        csv_files = sorted(glob.glob(str(self.input_path / "chunk_*.csv")))
        print(f"📁 Found {len(csv_files)} CSV files")
        
        # Process in batches and write to parquet
        all_chunks = []
        seen_texts = set()
        
        for file_idx, csv_file in enumerate(csv_files):
            print(f"\n📄 Processing file {file_idx + 1}/{len(csv_files)}: {Path(csv_file).name}")
            
            try:
                for chunk_idx, chunk in enumerate(pd.read_csv(csv_file, chunksize=chunksize)):
                    cleaned_chunk = self._clean_chunk(chunk, seen_texts, min_length, max_length)
                    
                    if not cleaned_chunk.empty:
                        all_chunks.append(cleaned_chunk)
                    
                    # Write intermediate parquet if accumulated too much
                    if len(all_chunks) >= 100:
                        self._write_intermediate(all_chunks, file_idx, chunk_idx)
                        all_chunks = []
                    
                    if (chunk_idx + 1) % 10 == 0:
                        print(f"  ✓ Processed {(chunk_idx + 1) * chunksize} rows")
                        
            except Exception as e:
                print(f"  ❌ Error processing {csv_file}: {e}")
                continue
        
        # Write remaining chunks
        if all_chunks:
            self._write_final(all_chunks)
        
        # Save label maps
        self._save_label_maps()
        
        # Print summary
        self._print_summary()
        
        return self.stats
    
    def _clean_chunk(self, chunk, seen_texts, min_length, max_length):
        """Clean a single chunk"""
        original_size = len(chunk)
        self.stats['total_input'] += original_size
        
        # Required columns
        required_cols = ['text', 'is_requirement', 'type', 'priority', 'domain']
        for col in required_cols:
            if col not in chunk.columns:
                chunk[col] = None
        
        # 1. Drop rows with missing text
        before = len(chunk)
        chunk = chunk.dropna(subset=['text'])
        chunk = chunk[chunk['text'].str.strip() != '']
        self.stats['dropped_missing_text'] += before - len(chunk)
        
        if chunk.empty:
            return chunk
        
        # 2. Normalize text
        chunk['text'] = chunk['text'].astype(str).str.strip()
        
        # 3. Filter by length
        text_lengths = chunk['text'].str.len()
        
        before = len(chunk)
        chunk = chunk[text_lengths >= min_length]
        self.stats['dropped_too_short'] += before - len(chunk)
        
        before = len(chunk)
        chunk = chunk[text_lengths <= max_length]
        self.stats['dropped_too_long'] += before - len(chunk)
        
        if chunk.empty:
            return chunk
        
        # 4. Remove duplicates (global)
        before = len(chunk)
        chunk['_text_lower'] = chunk['text'].str.lower()
        chunk = chunk[~chunk['_text_lower'].isin(seen_texts)]
        seen_texts.update(chunk['_text_lower'].tolist())
        chunk = chunk.drop(columns=['_text_lower'])
        self.stats['dropped_duplicates'] += before - len(chunk)
        
        if chunk.empty:
            return chunk
        
        # 5. Normalize labels
        chunk = self._normalize_labels(chunk)
        
        # 6. Add metadata
        chunk['text_length'] = chunk['text'].str.len()
        chunk['word_count'] = chunk['text'].str.split().str.len()
        
        self.stats['total_output'] += len(chunk)
        
        return chunk
    
    def _normalize_labels(self, chunk):
        """Normalize label values"""
        # is_requirement
        if 'is_requirement' in chunk.columns:
            chunk['is_requirement'] = chunk['is_requirement'].map(
                lambda x: self.label_maps['is_requirement'].get(str(x).lower(), x)
            )
            chunk['is_requirement'] = pd.to_numeric(chunk['is_requirement'], errors='coerce')
            chunk['is_requirement'] = chunk['is_requirement'].fillna(0).astype(int)
        
        # priority
        if 'priority' in chunk.columns:
            chunk['priority'] = chunk['priority'].fillna('None')
            chunk['priority'] = chunk['priority'].astype(str).str.strip().str.capitalize()
            # Map variations
            priority_map = {
                'None': 'None', 'none': 'None',
                'Low': 'Low', 'low': 'Low', 'l': 'Low',
                'Medium': 'Medium', 'medium': 'Medium', 'med': 'Medium', 'm': 'Medium',
                'High': 'High', 'high': 'High', 'h': 'High'
            }
            chunk['priority'] = chunk['priority'].map(lambda x: priority_map.get(x, 'None'))
        
        # type - keep as is but strip whitespace
        if 'type' in chunk.columns:
            chunk['type'] = chunk['type'].fillna('unknown')
            chunk['type'] = chunk['type'].astype(str).str.strip().str.lower()
        
        # domain - keep as is but strip whitespace
        if 'domain' in chunk.columns:
            chunk['domain'] = chunk['domain'].fillna('general')
            chunk['domain'] = chunk['domain'].astype(str).str.strip().str.lower()
        
        return chunk
    
    def _write_intermediate(self, chunks, file_idx, chunk_idx):
        """Write intermediate parquet file"""
        if not chunks:
            return
        
        df = pd.concat(chunks, ignore_index=True)
        output_file = self.output_path / f"intermediate_{file_idx}_{chunk_idx}.parquet"
        df.to_parquet(output_file, index=False, engine='pyarrow', compression='snappy')
        print(f"  💾 Wrote intermediate file: {output_file.name} ({len(df)} rows)")
    
    def _write_final(self, chunks):
        """Combine all intermediate files into final parquet"""
        print("\n📦 Combining all data into final parquet files...")
        
        # Combine remaining chunks
        if chunks:
            df = pd.concat(chunks, ignore_index=True)
            temp_file = self.output_path / "temp_final.parquet"
            df.to_parquet(temp_file, index=False, engine='pyarrow', compression='snappy')
        
        # Load all intermediate files
        all_parquet_files = list(self.output_path.glob("*.parquet"))
        
        if not all_parquet_files:
            print("⚠️  No data to combine!")
            return
        
        print(f"📊 Combining {len(all_parquet_files)} parquet files...")
        
        dfs = []
        for pq_file in all_parquet_files:
            try:
                df = pd.read_parquet(pq_file)
                dfs.append(df)
            except Exception as e:
                print(f"  ⚠️  Error reading {pq_file}: {e}")
        
        if not dfs:
            print("❌ No valid data found!")
            return
        
        # Combine all
        final_df = pd.concat(dfs, ignore_index=True)
        
        # Final deduplication
        print(f"  🔍 Final deduplication check...")
        before = len(final_df)
        final_df = final_df.drop_duplicates(subset=['text'], keep='first')
        after = len(final_df)
        if before > after:
            print(f"  ✓ Removed {before - after} duplicates in final merge")
            self.stats['dropped_duplicates'] += before - after
        
        # Write final cleaned parquet
        output_file = self.output_path / "clean_full.parquet"
        final_df.to_parquet(output_file, index=False, engine='pyarrow', compression='snappy')
        print(f"\n✅ Final dataset saved: {output_file}")
        print(f"   Total rows: {len(final_df):,}")
        
        # Also write split by is_requirement for easier access
        if 'is_requirement' in final_df.columns:
            req_df = final_df[final_df['is_requirement'] == 1]
            non_req_df = final_df[final_df['is_requirement'] == 0]
            
            req_file = self.output_path / "clean_requirements.parquet"
            non_req_file = self.output_path / "clean_non_requirements.parquet"
            
            req_df.to_parquet(req_file, index=False, engine='pyarrow', compression='snappy')
            non_req_df.to_parquet(non_req_file, index=False, engine='pyarrow', compression='snappy')
            
            print(f"   Requirements: {len(req_df):,} rows -> {req_file.name}")
            print(f"   Non-requirements: {len(non_req_df):,} rows -> {non_req_file.name}")
        
        # Clean up intermediate files
        print("\n🗑️  Cleaning up intermediate files...")
        for pq_file in all_parquet_files:
            if pq_file.name.startswith('intermediate_') or pq_file.name.startswith('temp_'):
                pq_file.unlink()
        print("  ✓ Cleanup complete")
    
    def _save_label_maps(self):
        """Save label mappings for reference"""
        # Load a sample to get actual unique values
        sample_file = self.output_path / "clean_full.parquet"
        if sample_file.exists():
            df = pd.read_parquet(sample_file)
            
            self.label_maps['type'] = {v: v for v in df['type'].unique() if pd.notna(v)}
            self.label_maps['domain'] = {v: v for v in df['domain'].unique() if pd.notna(v)}
            self.label_maps['priority'] = {v: v for v in df['priority'].unique() if pd.notna(v)}
        
        output_file = self.output_path / "label_maps.json"
        with open(output_file, 'w') as f:
            json.dump(self.label_maps, f, indent=2, default=str)
        print(f"\n💾 Label maps saved to: {output_file}")
    
    def _print_summary(self):
        """Print cleaning summary"""
        print("\n" + "="*80)
        print("📊 CLEANING SUMMARY")
        print("="*80)
        print(f"Total input rows:        {self.stats['total_input']:,}")
        print(f"Total output rows:       {self.stats['total_output']:,}")
        print(f"Retention rate:          {self.stats['total_output']/self.stats['total_input']*100:.2f}%")
        print(f"\nDropped statistics:")
        print(f"  Missing text:          {self.stats['dropped_missing_text']:,}")
        print(f"  Duplicates:            {self.stats['dropped_duplicates']:,}")
        print(f"  Too short:             {self.stats['dropped_too_short']:,}")
        print(f"  Too long:              {self.stats['dropped_too_long']:,}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean dataset and convert to parquet')
    parser.add_argument('--input', type=str,
                       default='requirement_analyzer/dataset_large_1m',
                       help='Input dataset folder')
    parser.add_argument('--output', type=str,
                       default='data/processed',
                       help='Output folder for parquet files')
    parser.add_argument('--chunksize', type=int, default=10000,
                       help='Chunk size for processing')
    parser.add_argument('--min-length', type=int, default=10,
                       help='Minimum text length')
    parser.add_argument('--max-length', type=int, default=1000,
                       help='Maximum text length')
    
    args = parser.parse_args()
    
    input_path = PROJECT_ROOT / args.input
    output_path = PROJECT_ROOT / args.output
    
    if not input_path.exists():
        print(f"❌ Input path not found: {input_path}")
        sys.exit(1)
    
    cleaner = DatasetCleaner(input_path, output_path)
    cleaner.process(
        chunksize=args.chunksize,
        min_length=args.min_length,
        max_length=args.max_length
    )
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
