#!/usr/bin/env python3
"""
Quick demo script to test task generation pipeline
Run this after training models to verify everything works
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from requirement_analyzer.task_gen import get_pipeline


def main():
    """Demo task generation"""
    
    # Sample requirement document
    sample_doc = """
# E-Commerce Platform Requirements

## User Authentication
The system must support user registration with email verification.
Users shall be able to login using email and password.
The application should implement two-factor authentication for enhanced security.
All user passwords must be encrypted using bcrypt with salt.

## Product Management
The platform needs to display products with images, descriptions, and pricing.
Users can search products by name, category, or price range.
The system should support product filtering and sorting.
Product inventory must be updated in real-time after each purchase.

## Shopping Cart
Users shall be able to add products to shopping cart.
The cart should persist across sessions.
The system must calculate total price including taxes and shipping.
Users can modify quantities or remove items from cart.

## Payment Processing
The application should integrate with multiple payment gateways.
All payment data must be encrypted and PCI-DSS compliant.
The system needs to send payment confirmation emails.
Failed payments must be logged for analysis.

## Order Management
The system shall generate unique order numbers for each transaction.
Users can track order status in real-time.
The platform needs to support order cancellation within 24 hours.
Order history should be accessible to users at any time.

## Performance Requirements
The system should handle 1000 concurrent users.
Page load time must be under 2 seconds.
Database queries should be optimized with proper indexing.

## Security Requirements
The platform must implement role-based access control.
All API endpoints should require authentication tokens.
Security audit logs must capture all critical operations.
The system needs to protect against SQL injection and XSS attacks.
"""

    print("="*80)
    print("🚀 TASK GENERATION DEMO")
    print("="*80)
    
    # Initialize pipeline
    print("\n📦 Loading pipeline...")
    try:
        pipeline = get_pipeline()
        print("✓ Pipeline loaded successfully")
    except Exception as e:
        print(f"❌ Error loading pipeline: {e}")
        print("\n💡 Make sure you have trained models first:")
        print("   python scripts/task_generation/04_train_requirement_detector.py")
        print("   python scripts/task_generation/05_train_enrichers.py")
        return
    
    # Generate tasks
    print(f"\n📝 Generating tasks from sample document...")
    print(f"   Document length: {len(sample_doc)} characters")
    
    try:
        response = pipeline.generate_tasks(
            text=sample_doc,
            max_tasks=20,
            epic_name="E-Commerce Platform MVP"
        )
        
        print(f"\n✅ Task generation completed!")
        print(f"   Processing time: {response.processing_time:.2f}s")
        print(f"   Generated tasks: {response.total_tasks}")
        print(f"   Avg confidence: {response.stats['avg_confidence']:.3f}")
        
        # Display tasks
        print("\n" + "="*80)
        print("📋 GENERATED TASKS")
        print("="*80)
        
        for i, task in enumerate(response.tasks, 1):
            print(f"\n{i}. {task.title}")
            print(f"   Type: {task.type} | Priority: {task.priority} | Role: {task.role}")
            print(f"   Domain: {task.domain} | Confidence: {task.confidence:.2f}")
            print(f"   Description: {task.description[:100]}...")
            print(f"   Acceptance Criteria ({len(task.acceptance_criteria)}):")
            for j, ac in enumerate(task.acceptance_criteria[:3], 1):
                print(f"      {j}. {ac}")
            if len(task.acceptance_criteria) > 3:
                print(f"      ... and {len(task.acceptance_criteria) - 3} more")
        
        # Display statistics
        print("\n" + "="*80)
        print("📊 STATISTICS")
        print("="*80)
        
        print("\n🏷️  Type Distribution:")
        for type_name, count in sorted(response.stats['type_distribution'].items(), key=lambda x: x[1], reverse=True):
            pct = count / response.total_tasks * 100
            print(f"   {type_name:20s}: {count:3d} ({pct:5.1f}%)")
        
        print("\n🎯 Priority Distribution:")
        for priority, count in sorted(response.stats['priority_distribution'].items(), key=lambda x: x[1], reverse=True):
            pct = count / response.total_tasks * 100
            print(f"   {priority:20s}: {count:3d} ({pct:5.1f}%)")
        
        print("\n👥 Role Distribution:")
        for role, count in sorted(response.stats['role_distribution'].items(), key=lambda x: x[1], reverse=True):
            pct = count / response.total_tasks * 100
            print(f"   {role:20s}: {count:3d} ({pct:5.1f}%)")
        
        print("\n🏢 Domain Distribution:")
        for domain, count in sorted(response.stats['domain_distribution'].items(), key=lambda x: x[1], reverse=True):
            pct = count / response.total_tasks * 100
            print(f"   {domain:20s}: {count:3d} ({pct:5.1f}%)")
        
        # Export to JSON (optional)
        import json
        output_file = PROJECT_ROOT / "demo_tasks_output.json"
        with open(output_file, 'w') as f:
            json.dump(response.dict(), f, indent=2, default=str)
        print(f"\n💾 Tasks exported to: {output_file}")
        
        print("\n" + "="*80)
        print("✅ DEMO COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during task generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
