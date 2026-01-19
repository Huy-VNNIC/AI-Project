#!/usr/bin/env python3
"""
Quick demo script to test task generation pipeline
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

def demo_basic():
    """Demo basic task generation"""
    print("="*80)
    print("🎯 DEMO: Basic Task Generation")
    print("="*80)
    
    # Sample requirement document
    sample_doc = """
# E-commerce Platform Requirements

## User Management
The system shall allow users to register with email and password.
The application must authenticate users securely using JWT tokens.
Users should be able to update their profile information.

## Product Catalog
The system shall display products with images, prices, and descriptions.
The interface must support product search with filters.
Products shall be organized by categories.

## Shopping Cart
The application must allow users to add products to cart.
The system should calculate total price including taxes.
Users can remove items from cart.

## Payment Processing
The system shall integrate with payment gateway for secure transactions.
All payment data must be encrypted in transit and at rest.
The application should send order confirmation emails.
"""
    
    print(f"\n📄 Sample document ({len(sample_doc)} chars)")
    print(sample_doc[:200] + "...\n")
    
    # Initialize pipeline
    print("🔧 Initializing task generation pipeline...")
    try:
        from requirement_analyzer.task_gen import get_pipeline
        
        pipeline = get_pipeline()
        print("✓ Pipeline loaded\n")
    except Exception as e:
        print(f"❌ Error loading pipeline: {e}")
        print("\n⚠️  Please train models first:")
        print("   cd scripts/task_generation")
        print("   ./train_all.sh")
        return
    
    # Generate tasks
    print("🚀 Generating tasks...")
    try:
        response = pipeline.generate_tasks(
            text=sample_doc,
            max_tasks=20,
            epic_name="E-commerce Platform v2.0"
        )
        
        print(f"\n✅ Generation complete!")
        print(f"   Processing time: {response.processing_time:.2f}s")
        print(f"   Total tasks: {response.total_tasks}")
        print(f"   Avg confidence: {response.stats.get('avg_confidence', 0):.3f}")
        
        # Print distribution
        print(f"\n📊 Distribution:")
        print(f"   Type: {response.stats.get('type_distribution', {})}")
        print(f"   Priority: {response.stats.get('priority_distribution', {})}")
        print(f"   Role: {response.stats.get('role_distribution', {})}")
        
        # Print sample tasks
        print(f"\n📋 Sample Tasks (showing 5/{len(response.tasks)}):\n")
        
        for i, task in enumerate(response.tasks[:5], 1):
            print(f"{i}. [{task.type}/{task.priority}] {task.title}")
            print(f"   Role: {task.role}")
            print(f"   Description: {task.description[:100]}...")
            print(f"   Acceptance Criteria ({len(task.acceptance_criteria)}):")
            for ac in task.acceptance_criteria[:3]:
                print(f"     • {ac}")
            print(f"   Confidence: {task.confidence:.3f}")
            print()
        
        # Export to JSON
        output_file = PROJECT_ROOT / "demo_tasks.json"
        import json
        with open(output_file, 'w') as f:
            json.dump(response.dict(), f, indent=2, default=str)
        print(f"💾 Full output saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error generating tasks: {e}")
        import traceback
        traceback.print_exc()


def demo_with_estimation():
    """Demo task generation + effort estimation"""
    print("\n" + "="*80)
    print("🎯 DEMO: Task Generation + Effort Estimation")
    print("="*80)
    
    sample_doc = """
The mobile banking application must support biometric authentication.
The system shall encrypt all data in transit using TLS 1.3.
Users should be able to transfer funds between accounts.
The application must display transaction history with filters.
The system should send push notifications for important events.
"""
    
    print(f"\n📄 Sample requirements")
    
    try:
        from requirement_analyzer.task_gen import get_pipeline
        from requirement_analyzer.estimator import EffortEstimator
        
        pipeline = get_pipeline()
        estimator = EffortEstimator()
        
        # Generate tasks
        print("🚀 Generating tasks...")
        response = pipeline.generate_tasks(
            text=sample_doc,
            max_tasks=10,
            epic_name="Mobile Banking v3.0"
        )
        
        print(f"✓ Generated {response.total_tasks} tasks")
        
        # Estimate effort
        print("\n📊 Estimating effort...")
        estimation = estimator.estimate_from_requirements(sample_doc)
        
        print(f"\n💰 Effort Estimation:")
        print(f"   Total effort: {estimation.get('total_effort_hours', 0):.1f} hours")
        print(f"   Duration: {estimation.get('duration_months', 0):.1f} months")
        print(f"   Team size: {estimation.get('team_size', 0):.1f} people")
        
        # Allocate story points (simple version)
        total_hours = estimation.get('total_effort_hours', 100)
        hours_per_task = total_hours / len(response.tasks) if response.tasks else 8
        
        print(f"\n📈 Story Points Allocation:")
        for task in response.tasks[:5]:
            # Simple mapping
            if hours_per_task <= 4:
                points = 1
            elif hours_per_task <= 8:
                points = 2
            elif hours_per_task <= 16:
                points = 3
            elif hours_per_task <= 24:
                points = 5
            else:
                points = 8
            
            print(f"   {task.title[:60]:<60} → {points} points")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo"""
    print("\n" + "="*80)
    print("🎬 TASK GENERATION DEMO")
    print("="*80)
    
    # Check if models exist
    models_dir = PROJECT_ROOT / 'models' / 'task_gen'
    
    if not models_dir.exists():
        print(f"\n⚠️  Models directory not found: {models_dir}")
        print("\n📚 Please train models first:")
        print("   1. Process dataset:")
        print("      python scripts/task_generation/01_scan_dataset.py")
        print("      python scripts/task_generation/02_build_parquet.py")
        print("      python scripts/task_generation/03_build_splits.py")
        print("\n   2. Train models:")
        print("      python scripts/task_generation/04_train_requirement_detector.py")
        print("      python scripts/task_generation/05_train_enrichers.py")
        print("\n   Or run all at once:")
        print("      cd scripts/task_generation")
        print("      ./train_all.sh")
        return
    
    # Run demos
    try:
        demo_basic()
        print("\n" + "="*80 + "\n")
        demo_with_estimation()
    except KeyboardInterrupt:
        print("\n\n⏸️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ Demo complete!")
    print("="*80)


if __name__ == "__main__":
    main()
