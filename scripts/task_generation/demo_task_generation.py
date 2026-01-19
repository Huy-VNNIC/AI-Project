"""
Demo script for task generation
Quick test to verify the system works
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from requirement_analyzer.task_gen import get_pipeline


def demo_basic():
    """Basic demo with sample requirement document"""
    
    sample_doc = """
# E-commerce Platform Requirements

## User Management
The system must allow users to register with email and password.
Users should be able to update their profile information.
The application needs to support password reset functionality.

## Product Catalog
The system shall display products with images and descriptions.
Users can filter products by category, price range, and availability.
The platform must support product search functionality.

## Shopping Cart
Users should be able to add products to cart.
The system must calculate total price including taxes.
Cart contents should persist across sessions.

## Security
All user data must be encrypted in transit and at rest.
The system shall implement role-based access control.
Payment information must comply with PCI-DSS standards.
"""
    
    print("="*80)
    print("🚀 TASK GENERATION DEMO")
    print("="*80)
    
    # Initialize pipeline
    print("\n📦 Loading pipeline...")
    pipeline = get_pipeline()
    
    # Generate tasks
    print("\n🎯 Generating tasks from sample document...")
    response = pipeline.generate_tasks(
        text=sample_doc,
        max_tasks=20,
        epic_name="E-commerce Platform MVP"
    )
    
    # Display results
    print(f"\n✅ Generated {response.total_tasks} tasks in {response.processing_time:.2f}s")
    print(f"   Average confidence: {response.stats['avg_confidence']:.3f}")
    
    print("\n📊 Distribution:")
    print(f"   Types: {response.stats['type_distribution']}")
    print(f"   Priorities: {response.stats['priority_distribution']}")
    print(f"   Roles: {response.stats['role_distribution']}")
    
    # Show first 3 tasks
    print("\n" + "="*80)
    print("📋 SAMPLE TASKS (first 3)")
    print("="*80)
    
    for i, task in enumerate(response.tasks[:3], 1):
        print(f"\n{'─'*80}")
        print(f"Task {i}: {task.title}")
        print(f"{'─'*80}")
        print(f"Type:     {task.type}")
        print(f"Priority: {task.priority}")
        print(f"Domain:   {task.domain}")
        print(f"Role:     {task.role}")
        print(f"Points:   {task.story_points or 'N/A'}")
        print(f"\nDescription:")
        print(f"  {task.description[:200]}...")
        print(f"\nAcceptance Criteria:")
        for j, ac in enumerate(task.acceptance_criteria[:3], 1):
            print(f"  {j}. {ac}")
        if len(task.acceptance_criteria) > 3:
            print(f"  ... and {len(task.acceptance_criteria) - 3} more")
    
    print("\n" + "="*80)
    print("✅ Demo complete!")
    print("="*80)


if __name__ == "__main__":
    try:
        demo_basic()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Trained the models (run training pipeline)")
        print("  2. Installed all requirements: pip install -r requirements-task-generation.txt")
        sys.exit(1)
