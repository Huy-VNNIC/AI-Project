"""
Script 4: Train Requirement Detector (binary classifier)
Detect whether a sentence is a requirement or not
"""
import os
import sys
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_curve, auc
from sklearn.calibration import CalibratedClassifierCV
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


class RequirementDetectorTrainer:
    """Train a binary classifier to detect requirements"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.vectorizer = None
        self.model = None
        self.metrics = {}
    
    def train(
        self,
        train_file,
        val_file,
        test_file,
        model_type='sgd',
        calibrate=True
    ):
        """Train the requirement detector"""
        print("="*80)
        print("🎯 TRAINING REQUIREMENT DETECTOR")
        print("="*80)
        
        # Load data
        print("\n📂 Loading data...")
        train_df = pd.read_parquet(train_file)
        val_df = pd.read_parquet(val_file)
        test_df = pd.read_parquet(test_file)
        
        print(f"   Train: {len(train_df):,} samples")
        print(f"   Val:   {len(val_df):,} samples")
        print(f"   Test:  {len(test_df):,} samples")
        
        # Check class distribution
        print(f"\n📊 Class distribution (train):")
        train_dist = train_df['is_requirement'].value_counts(normalize=True)
        for label, ratio in train_dist.items():
            print(f"   {label}: {ratio:.2%}")
        
        # Extract features
        print(f"\n🔧 Extracting features...")
        X_train, y_train = self._prepare_data(train_df)
        X_val, y_val = self._prepare_data(val_df)
        X_test, y_test = self._prepare_data(test_df)
        
        # Train vectorizer
        print(f"   Training TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
            strip_accents='unicode',
            lowercase=True,
            stop_words='english'
        )
        
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_val_vec = self.vectorizer.transform(X_val)
        X_test_vec = self.vectorizer.transform(X_test)
        
        print(f"   Feature space: {X_train_vec.shape[1]:,} features")
        
        # Train model
        print(f"\n🏋️  Training {model_type.upper()} model...")
        
        if model_type == 'sgd':
            # SGDClassifier with log loss (gives probabilities)
            self.model = SGDClassifier(
                loss='log_loss',  # logistic regression
                penalty='l2',
                alpha=0.0001,
                max_iter=1000,
                tol=1e-3,
                class_weight='balanced',  # handle imbalance
                random_state=42,
                n_jobs=-1,
                verbose=0
            )
        elif model_type == 'logistic':
            self.model = LogisticRegression(
                penalty='l2',
                C=1.0,
                class_weight='balanced',
                max_iter=1000,
                random_state=42,
                n_jobs=-1,
                verbose=0
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        self.model.fit(X_train_vec, y_train)
        print(f"   ✓ Training complete")
        
        # Calibrate probabilities (optional but recommended)
        if calibrate:
            print(f"\n🎚️  Calibrating probabilities...")
            self.model = CalibratedClassifierCV(self.model, cv='prefit')
            self.model.fit(X_val_vec, y_val)
            print(f"   ✓ Calibration complete")
        
        # Evaluate
        print(f"\n📈 Evaluating model...")
        
        # Train performance
        y_train_pred = self.model.predict(X_train_vec)
        y_train_proba = self.model.predict_proba(X_train_vec)[:, 1]
        
        # Val performance
        y_val_pred = self.model.predict(X_val_vec)
        y_val_proba = self.model.predict_proba(X_val_vec)[:, 1]
        
        # Test performance
        y_test_pred = self.model.predict(X_test_vec)
        y_test_proba = self.model.predict_proba(X_test_vec)[:, 1]
        
        # Compute metrics
        self.metrics = {
            'train': self._compute_metrics(y_train, y_train_pred, y_train_proba),
            'val': self._compute_metrics(y_val, y_val_pred, y_val_proba),
            'test': self._compute_metrics(y_test, y_test_pred, y_test_proba)
        }
        
        # Print results
        self._print_metrics()
        
        # Save models
        self._save_models()
        
        # Plot confusion matrices
        self._plot_confusion_matrices(
            y_train, y_train_pred,
            y_val, y_val_pred,
            y_test, y_test_pred
        )
        
        # Plot PR curves
        self._plot_pr_curves(
            y_train, y_train_proba,
            y_val, y_val_proba,
            y_test, y_test_proba
        )
        
        return self.metrics
    
    def _prepare_data(self, df):
        """Prepare X and y from dataframe"""
        X = df['text'].fillna('').astype(str)
        y = df['is_requirement'].fillna(0).astype(int)
        return X, y
    
    def _compute_metrics(self, y_true, y_pred, y_proba):
        """Compute evaluation metrics"""
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, roc_auc_score, average_precision_score
        )
        
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1': float(f1_score(y_true, y_pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_true, y_proba)),
            'pr_auc': float(average_precision_score(y_true, y_proba))
        }
        
        return metrics
    
    def _print_metrics(self):
        """Print metrics summary"""
        print("\n" + "="*80)
        print("📊 EVALUATION RESULTS")
        print("="*80)
        
        for split in ['train', 'val', 'test']:
            print(f"\n{split.upper()} SET:")
            metrics = self.metrics[split]
            print(f"   Accuracy:  {metrics['accuracy']:.4f}")
            print(f"   Precision: {metrics['precision']:.4f}")
            print(f"   Recall:    {metrics['recall']:.4f}")
            print(f"   F1 Score:  {metrics['f1']:.4f}")
            print(f"   ROC AUC:   {metrics['roc_auc']:.4f}")
            print(f"   PR AUC:    {metrics['pr_auc']:.4f}")
    
    def _save_models(self):
        """Save vectorizer and model"""
        print(f"\n💾 Saving models to {self.output_dir}")
        
        # Save vectorizer
        vectorizer_path = self.output_dir / 'requirement_detector_vectorizer.joblib'
        joblib.dump(self.vectorizer, vectorizer_path, compress=3)
        print(f"   ✓ Vectorizer: {vectorizer_path.name}")
        
        # Save model
        model_path = self.output_dir / 'requirement_detector_model.joblib'
        joblib.dump(self.model, model_path, compress=3)
        print(f"   ✓ Model: {model_path.name}")
        
        # Save metrics
        metrics_path = self.output_dir / 'requirement_detector_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump({
                'metrics': self.metrics,
                'trained_at': datetime.now().isoformat(),
                'model_type': type(self.model).__name__,
                'feature_count': self.vectorizer.max_features
            }, f, indent=2)
        print(f"   ✓ Metrics: {metrics_path.name}")
    
    def _plot_confusion_matrices(self, y_train, y_train_pred, y_val, y_val_pred, y_test, y_test_pred):
        """Plot confusion matrices"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        
        for idx, (y_true, y_pred, split) in enumerate([
            (y_train, y_train_pred, 'Train'),
            (y_val, y_val_pred, 'Val'),
            (y_test, y_test_pred, 'Test')
        ]):
            cm = confusion_matrix(y_true, y_pred)
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx])
            axes[idx].set_title(f'Confusion Matrix - {split}')
            axes[idx].set_ylabel('True')
            axes[idx].set_xlabel('Predicted')
        
        plt.tight_layout()
        plot_path = self.output_dir / 'requirement_detector_confusion_matrices.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"   ✓ Confusion matrices: {plot_path.name}")
        plt.close()
    
    def _plot_pr_curves(self, y_train, y_train_proba, y_val, y_val_proba, y_test, y_test_proba):
        """Plot precision-recall curves"""
        plt.figure(figsize=(10, 6))
        
        for y_true, y_proba, split, color in [
            (y_train, y_train_proba, 'Train', 'blue'),
            (y_val, y_val_proba, 'Val', 'green'),
            (y_test, y_test_proba, 'Test', 'red')
        ]:
            precision, recall, _ = precision_recall_curve(y_true, y_proba)
            pr_auc = auc(recall, precision)
            plt.plot(recall, precision, label=f'{split} (AUC={pr_auc:.3f})', color=color)
        
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curves')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plot_path = self.output_dir / 'requirement_detector_pr_curves.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"   ✓ PR curves: {plot_path.name}")
        plt.close()


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train requirement detector')
    parser.add_argument('--data-dir', type=str, default='data/splits',
                       help='Directory with train/val/test parquet files')
    parser.add_argument('--output-dir', type=str, default='models/task_gen',
                       help='Output directory for models')
    parser.add_argument('--model-type', type=str, default='sgd',
                       choices=['sgd', 'logistic'],
                       help='Model type')
    parser.add_argument('--no-calibrate', action='store_true',
                       help='Skip probability calibration')
    
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
    
    trainer = RequirementDetectorTrainer(output_dir)
    metrics = trainer.train(
        train_file, val_file, test_file,
        model_type=args.model_type,
        calibrate=not args.no_calibrate
    )
    
    print("\n✅ Training complete!")
    print(f"   Test F1: {metrics['test']['f1']:.4f}")
    print(f"   Test PR-AUC: {metrics['test']['pr_auc']:.4f}")


if __name__ == "__main__":
    main()
