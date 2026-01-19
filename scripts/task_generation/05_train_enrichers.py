"""
Script 5: Train Enrichment Classifiers (type, priority, domain)
Multi-class classification for labeling requirements
"""
import os
import sys
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


class EnricherTrainer:
    """Train multi-class classifiers for type/priority/domain"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.models = {}  # {label_name: (vectorizer, model)}
        self.metrics = {}
        self.label_encodings = {}
    
    def train_all(
        self,
        train_file,
        val_file,
        test_file,
        labels_to_train=['type', 'priority', 'domain']
    ):
        """Train all enrichment classifiers"""
        print("="*80)
        print("🎯 TRAINING ENRICHMENT CLASSIFIERS")
        print("="*80)
        
        # Load data
        print("\n📂 Loading data...")
        train_df = pd.read_parquet(train_file)
        val_df = pd.read_parquet(val_file)
        test_df = pd.read_parquet(test_file)
        
        # Filter to only requirements
        train_df = train_df[train_df['is_requirement'] == 1].copy()
        val_df = val_df[val_df['is_requirement'] == 1].copy()
        test_df = test_df[test_df['is_requirement'] == 1].copy()
        
        print(f"   Train: {len(train_df):,} requirements")
        print(f"   Val:   {len(val_df):,} requirements")
        print(f"   Test:  {len(test_df):,} requirements")
        
        # Train each classifier
        for label_name in labels_to_train:
            print(f"\n{'='*80}")
            print(f"🏷️  Training {label_name.upper()} classifier")
            print(f"{'='*80}")
            
            self._train_single_classifier(
                label_name,
                train_df,
                val_df,
                test_df
            )
        
        # Save summary
        self._save_summary()
        
        print("\n" + "="*80)
        print("✅ ALL CLASSIFIERS TRAINED")
        print("="*80)
        
        return self.metrics
    
    def _train_single_classifier(
        self,
        label_name,
        train_df,
        val_df,
        test_df
    ):
        """Train a single multi-class classifier"""
        
        # Prepare data
        X_train, y_train, classes = self._prepare_data(train_df, label_name)
        X_val, y_val, _ = self._prepare_data(val_df, label_name, classes)
        X_test, y_test, _ = self._prepare_data(test_df, label_name, classes)
        
        if len(classes) < 2:
            print(f"   ⚠️  Skipping {label_name}: only {len(classes)} class(es) found")
            return
        
        print(f"\n📊 Class distribution (train):")
        train_dist = pd.Series(y_train).value_counts()
        for cls, count in train_dist.items():
            print(f"   {cls}: {count:,} ({count/len(y_train):.1%})")
        
        print(f"\n   Total classes: {len(classes)}")
        
        # Train vectorizer
        print(f"\n🔧 Training TF-IDF vectorizer...")
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
            strip_accents='unicode',
            lowercase=True,
            stop_words='english'
        )
        
        X_train_vec = vectorizer.fit_transform(X_train)
        X_val_vec = vectorizer.transform(X_val)
        X_test_vec = vectorizer.transform(X_test)
        
        print(f"   Feature space: {X_train_vec.shape[1]:,} features")
        
        # Train model
        print(f"\n🏋️  Training Logistic Regression...")
        model = LogisticRegression(
            penalty='l2',
            C=1.0,
            class_weight='balanced',
            max_iter=1000,
            multi_class='multinomial',
            solver='lbfgs',
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        
        model.fit(X_train_vec, y_train)
        print(f"   ✓ Training complete")
        
        # Evaluate
        print(f"\n📈 Evaluating...")
        
        y_train_pred = model.predict(X_train_vec)
        y_val_pred = model.predict(X_val_vec)
        y_test_pred = model.predict(X_test_vec)
        
        # Get probabilities for confidence scores
        y_train_proba = model.predict_proba(X_train_vec)
        y_val_proba = model.predict_proba(X_val_vec)
        y_test_proba = model.predict_proba(X_test_vec)
        
        # Compute metrics
        self.metrics[label_name] = {
            'train': self._compute_metrics(y_train, y_train_pred, classes),
            'val': self._compute_metrics(y_val, y_val_pred, classes),
            'test': self._compute_metrics(y_test, y_test_pred, classes)
        }
        
        # Print classification reports
        print(f"\n📋 Classification Report (Test):")
        print(classification_report(y_test, y_test_pred, zero_division=0))
        
        # Store model
        self.models[label_name] = (vectorizer, model)
        self.label_encodings[label_name] = classes
        
        # Save individual model
        self._save_model(label_name, vectorizer, model, classes)
        
        # Plot confusion matrix
        self._plot_confusion_matrix(y_test, y_test_pred, classes, label_name)
    
    def _prepare_data(self, df, label_name, classes=None):
        """Prepare data for training"""
        # Get text
        X = df['text'].fillna('').astype(str)
        
        # Get labels
        y = df[label_name].fillna('unknown').astype(str)
        
        # Get unique classes
        if classes is None:
            classes = sorted(y.unique())
        
        # Filter to known classes
        valid_mask = y.isin(classes)
        X = X[valid_mask]
        y = y[valid_mask]
        
        return X.tolist(), y.tolist(), classes
    
    def _compute_metrics(self, y_true, y_pred, classes):
        """Compute metrics"""
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'macro_f1': float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
            'weighted_f1': float(f1_score(y_true, y_pred, average='weighted', zero_division=0)),
            'num_classes': len(classes)
        }
        return metrics
    
    def _save_model(self, label_name, vectorizer, model, classes):
        """Save individual model"""
        # Save vectorizer
        vec_path = self.output_dir / f'{label_name}_vectorizer.joblib'
        joblib.dump(vectorizer, vec_path, compress=3)
        
        # Save model
        model_path = self.output_dir / f'{label_name}_model.joblib'
        joblib.dump(model, model_path, compress=3)
        
        # Save classes
        classes_path = self.output_dir / f'{label_name}_classes.json'
        with open(classes_path, 'w') as f:
            json.dump(classes, f, indent=2)
        
        print(f"\n💾 Saved {label_name} model:")
        print(f"   Vectorizer: {vec_path.name}")
        print(f"   Model: {model_path.name}")
        print(f"   Classes: {classes_path.name}")
    
    def _plot_confusion_matrix(self, y_true, y_pred, classes, label_name):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred, labels=classes)
        
        # If too many classes, show only top confusion
        if len(classes) > 15:
            print(f"   ⚠️  Too many classes ({len(classes)}) - skipping confusion matrix plot")
            return
        
        plt.figure(figsize=(max(10, len(classes)), max(8, len(classes) * 0.8)))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=classes,
            yticklabels=classes,
            cbar_kws={'label': 'Count'}
        )
        plt.title(f'Confusion Matrix - {label_name.upper()}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        plot_path = self.output_dir / f'{label_name}_confusion_matrix.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"   ✓ Confusion matrix: {plot_path.name}")
        plt.close()
    
    def _save_summary(self):
        """Save training summary"""
        summary = {
            'trained_at': datetime.now().isoformat(),
            'models': list(self.models.keys()),
            'metrics': self.metrics,
            'label_encodings': self.label_encodings
        }
        
        summary_path = self.output_dir / 'enrichers_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Summary saved: {summary_path}")
        
        # Print summary table
        print("\n" + "="*80)
        print("📊 TRAINING SUMMARY")
        print("="*80)
        print(f"\n{'Model':<15} {'Classes':<10} {'Test Acc':<12} {'Test Macro-F1':<15} {'Test Weighted-F1':<15}")
        print("-" * 80)
        
        for model_name in self.metrics.keys():
            test_metrics = self.metrics[model_name]['test']
            print(f"{model_name:<15} "
                  f"{test_metrics['num_classes']:<10} "
                  f"{test_metrics['accuracy']:.4f}      "
                  f"{test_metrics['macro_f1']:.4f}          "
                  f"{test_metrics['weighted_f1']:.4f}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train enrichment classifiers')
    parser.add_argument('--data-dir', type=str, default='data/splits',
                       help='Directory with train/val/test parquet files')
    parser.add_argument('--output-dir', type=str, default='models/task_gen',
                       help='Output directory for models')
    parser.add_argument('--labels', type=str, nargs='+',
                       default=['type', 'priority', 'domain'],
                       help='Labels to train classifiers for')
    
    args = parser.parse_args()
    
    data_dir = PROJECT_ROOT / args.data_dir
    train_file = data_dir / 'train.parquet'
    val_file = data_dir / 'val.parquet'
    test_file = data_dir / 'test.parquet'
    
    # Check files exist
    for f in [train_file, val_file, test_file]:
        if not f.exists():
            print(f"❌ File not found: {f}")
            print("   Please run 03_build_splits.py first")
            sys.exit(1)
    
    output_dir = PROJECT_ROOT / args.output_dir
    
    trainer = EnricherTrainer(output_dir)
    metrics = trainer.train_all(
        train_file, val_file, test_file,
        labels_to_train=args.labels
    )
    
    print("\n✅ Training complete!")


if __name__ == "__main__":
    main()
