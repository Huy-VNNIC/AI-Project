#!/usr/bin/env python3
"""
Quick Demo - Direct Pipeline Test
Tests task generation pipeline without needing API server
"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from requirement_analyzer.task_gen.pipeline import TaskGenerationPipeline


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def main():
    print_header("TASK GENERATION PIPELINE - QUICK DEMO")
    
    # Test document
    test_doc = """
    The system must authenticate users through email and password.
    Users should be able to reset their passwords via email verification.
    The application must support two-factor authentication using SMS or authenticator apps.
    Admin users need the ability to manage user accounts, roles, and permissions.
    The system shall log all authentication attempts for security auditing.
    """
    
    print("📝 Input Requirements:")
    print(test_doc.strip())
    
    # Initialize pipeline
    print("\n🔧 Initializing pipeline...")
    try:
        pipeline = TaskGenerationPipeline(
            model_dir="requirement_analyzer/models/task_gen/models",
            generator_mode="model"
        )
        print("   ✅ Pipeline loaded")
        print(f"   Mode: {pipeline.generator_mode}")
    except Exception as e:
        print(f"   ❌ Failed to load pipeline: {e}")
        return
    
    # Generate tasks
    print("\n🚀 Generating tasks...")
    try:
        result = pipeline.generate_tasks(
            text=test_doc,
            max_tasks=5,
            requirement_threshold=0.5
        )
        
        tasks = result.tasks
        
        print(f"   ✅ Generated {len(tasks)} tasks")
        print(f"   Mode: {result.mode}")
        print(f"   Processing time: {result.processing_time:.2f}s")
        
    except Exception as e:
        print(f"   ❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print_header("GENERATED TASKS")
    
    for idx, task in enumerate(tasks, 1):
        print(f"\n📋 Task {idx}: {task.title}")
        print(f"   Type: {task.type}")
        print(f"   Priority: {task.priority}")
        print(f"   Domain: {task.domain}")
        print(f"   Confidence: {task.confidence:.2f}")
        
        # Description (truncated)
        desc = task.description
        if desc:
            print(f"   Description: {desc[:100]}...")
        
        # Acceptance criteria
        acs = task.acceptance_criteria
        if acs:
            print(f"   Acceptance Criteria ({len(acs)}):")
            for ac in acs[:3]:  # Show first 3
                print(f"      • {ac}")
            if len(acs) > 3:
                print(f"      ... and {len(acs) - 3} more")
    
    # Summary
    print_header("SUMMARY")
    
    print(f"📊 Statistics:")
    print(f"   Total tasks generated: {len(tasks)}")
    print(f"   Processing time: {result.processing_time:.2f}s")
    print(f"   Mode: {result.mode}")
    
    # Type distribution
    types = {}
    for task in tasks:
        t = task.type
        types[t] = types.get(t, 0) + 1
    
    print(f"\n   Type distribution:")
    for t, count in types.items():
        print(f"      {t}: {count}")
    
    # Priority distribution
    priorities = {}
    for task in tasks:
        p = task.priority
        priorities[p] = priorities.get(p, 0) + 1
    
    print(f"\n   Priority distribution:")
    for p, count in priorities.items():
        print(f"      {p}: {count}")
    
    # Domain distribution
    domains = {}
    for task in tasks:
        d = task.domain
        domains[d] = domains.get(d, 0) + 1
    
    print(f"\n   Domain distribution:")
    for d, count in domains.items():
        print(f"      {d}: {count}")
    
    # Avg confidence
    confidences = [t.confidence for t in tasks]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    print(f"\n   Average confidence: {avg_conf:.2f}")
    
    print("\n✅ Demo completed successfully!\n")
    
    print("💡 Next steps:")
    print("   1. Test API: uvicorn app.main:app --port 8001")
    print("   2. Configure .env for Jira/Trello (optional)")
    print("   3. Run OOD evaluation with real requirements")
    print()


if __name__ == '__main__':
    main()
