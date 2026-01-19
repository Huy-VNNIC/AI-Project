"""
Demo LLM-based Task Generation
Shows natural task generation without templates
"""
import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from requirement_analyzer.task_gen import (
    use_llm_mode,
    get_pipeline,
    print_config
)


def main():
    """Demo LLM task generation"""
    
    print("=" * 70)
    print("LLM-BASED TASK GENERATION DEMO")
    print("=" * 70)
    print()
    
    # Sample requirement document
    req_doc = """
# E-Commerce Platform Requirements

## User Authentication
Users must be able to register with email and password. The system shall validate 
email format and password strength (min 8 chars, 1 uppercase, 1 number, 1 special char).
Users can reset password via email link.

## Product Catalog
The system should display products with images, prices, and descriptions. 
Users can filter products by category, price range, and rating.
Search functionality must support autocomplete suggestions.

## Shopping Cart
Users can add products to cart. Cart persists across sessions. 
Calculate total with tax and shipping. Display real-time inventory status.

## Checkout Process
Support multiple payment methods: credit card, PayPal, bank transfer.
Order confirmation sent via email with tracking number.
Users can review order history in their account dashboard.

## Security
All payment data must be encrypted using PCI-DSS compliant standards.
Implement rate limiting to prevent brute force attacks.
Session tokens expire after 30 minutes of inactivity.
    """
    
    print("📄 Sample requirement document:")
    print("-" * 70)
    print(req_doc[:300] + "...")
    print("-" * 70)
    print()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ERROR: No API key found!")
        print()
        print("Set one of these environment variables:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print()
        print("Or use .env file:")
        print("  echo 'OPENAI_API_KEY=your-key' > .env")
        print()
        return
    
    # Initialize LLM pipeline
    print("🤖 Initializing LLM pipeline...")
    print()
    
    try:
        # Switch to LLM mode
        use_llm_mode(provider="openai", model="gpt-4o-mini")
        
        # Print config
        print_config()
        print()
        
        # Initialize pipeline
        pipeline = get_pipeline(
            generator_mode="llm",
            llm_provider="openai",
            llm_model="gpt-4o-mini"
        )
        
        print("✓ Pipeline ready")
        print()
        
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        print()
        print("Make sure you have installed:")
        print("  pip install openai anthropic")
        return
    
    # Generate tasks
    print("🚀 Generating tasks (this may take 30-60 seconds)...")
    print()
    
    try:
        response = pipeline.generate_tasks(
            text=req_doc,
            epic_name="E-Commerce Platform MVP",
            requirement_threshold=0.5,
            max_tasks=20
        )
        
        print(f"✓ Generated {response.total_tasks} tasks in {response.processing_time:.1f}s")
        print()
        
    except Exception as e:
        print(f"❌ Task generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display tasks
    print("=" * 70)
    print("GENERATED TASKS")
    print("=" * 70)
    print()
    
    for i, task in enumerate(response.tasks, 1):
        print(f"[{i}] {task.title}")
        print(f"    Type: {task.type} | Priority: {task.priority} | Role: {task.role}")
        print(f"    Confidence: {task.confidence:.2f}")
        print()
        print(f"    Description:")
        print(f"    {task.description}")
        print()
        print(f"    Acceptance Criteria ({len(task.acceptance_criteria)} items):")
        for j, ac in enumerate(task.acceptance_criteria, 1):
            print(f"      {j}. {ac}")
        print()
        print(f"    Source: \"{task.source.sentence[:80]}...\"")
        print()
        print("-" * 70)
        print()
    
    # Show stats
    print("=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print()
    print(f"Total tasks generated: {response.total_tasks}")
    print(f"Processing time: {response.processing_time:.2f}s")
    print(f"Average time per task: {response.processing_time / max(response.total_tasks, 1):.2f}s")
    print()
    
    # Type distribution
    type_dist = {}
    for task in response.tasks:
        type_dist[task.type] = type_dist.get(task.type, 0) + 1
    
    print("Task types:")
    for task_type, count in sorted(type_dist.items(), key=lambda x: -x[1]):
        print(f"  {task_type:15} : {count:2} tasks")
    print()
    
    # Priority distribution
    prio_dist = {}
    for task in response.tasks:
        prio_dist[task.priority] = prio_dist.get(task.priority, 0) + 1
    
    print("Priorities:")
    for prio, count in sorted(prio_dist.items(), key=lambda x: ['Low', 'Medium', 'High', 'Critical'].index(x[0]) if x[0] in ['Low', 'Medium', 'High', 'Critical'] else 999):
        print(f"  {prio:10} : {count:2} tasks")
    print()
    
    # Save to JSON
    output_file = Path(__file__).parent / "demo_llm_tasks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        import json
        json.dump(
            {
                "epic": "E-Commerce Platform MVP",
                "total_tasks": response.total_tasks,
                "processing_time": response.processing_time,
                "generator_mode": "llm",
                "tasks": [
                    {
                        "id": i,
                        "title": task.title,
                        "description": task.description,
                        "acceptance_criteria": task.acceptance_criteria,
                        "type": task.type,
                        "priority": task.priority,
                        "domain": task.domain,
                        "role": task.role,
                        "labels": task.labels,
                        "confidence": task.confidence,
                        "story_points": task.story_points,
                        "source_sentence": task.source.sentence
                    }
                    for i, task in enumerate(response.tasks, 1)
                ]
            },
            f,
            indent=2,
            ensure_ascii=False
        )
    
    print(f"✓ Saved to: {output_file}")
    print()
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
