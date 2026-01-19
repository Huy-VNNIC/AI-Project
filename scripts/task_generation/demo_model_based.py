"""
Demo: Model-Based Task Generation
NO API keys required - uses trained ML models

Compares:
- Template mode (template strings - "giả")
- Model mode (trained ML + NLP - natural)
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from requirement_analyzer.task_gen.pipeline import TaskGenerationPipeline


def main():
    """Test model-based task generation"""
    
    print("="*80)
    print("🧪 TESTING MODEL-BASED TASK GENERATION (NO API REQUIRED)")
    print("="*80)
    
    # Sample requirement document
    sample_doc = """
User Authentication Requirements

1. The system must authenticate users with email and password
2. Password must be encrypted using bcrypt
3. System should implement JWT token-based authentication
4. User dashboard must display user profile information
5. The application needs to validate email format before registration
6. System must log all authentication attempts for security audit
7. Interface should provide password reset functionality
8. The platform needs to manage user roles and permissions
9. Database must store user credentials securely
10. API endpoints should return proper error messages for invalid credentials
"""
    
    # Test Template Mode
    print("\n" + "="*80)
    print("📋 MODE 1: TEMPLATE (current - 'giả')")
    print("="*80)
    
    try:
        pipeline_template = TaskGenerationPipeline(
            model_dir=PROJECT_ROOT / 'requirement_analyzer' / 'models' / 'task_gen',
            generator_mode="template"
        )
        
        result_template = pipeline_template.generate_tasks(sample_doc, max_tasks=5)
        
        print(f"\n✅ Generated {len(result_template.tasks)} tasks\n")
        for idx, task in enumerate(result_template.tasks[:3], 1):
            print(f"Task {idx}: {task.title}")
            print(f"  Type: {task.type} | Priority: {task.priority}")
            print(f"  Description: {task.description[:100]}...")
            print(f"  AC: {len(task.acceptance_criteria)} items")
            print()
    except Exception as e:
        print(f"❌ Template mode error: {e}")
    
    # Test Model Mode
    print("\n" + "="*80)
    print("🤖 MODE 2: TRAINED MODELS (your custom trained models - natural)")
    print("="*80)
    
    try:
        pipeline_model = TaskGenerationPipeline(
            model_dir=PROJECT_ROOT / 'requirement_analyzer' / 'models' / 'task_gen',
            generator_mode="model"
        )
        
        result_model = pipeline_model.generate_tasks(sample_doc, max_tasks=10)
        
        print(f"\n✅ Generated {len(result_model.tasks)} tasks\n")
        for idx, task in enumerate(result_model.tasks[:5], 1):
            print(f"Task {idx}: {task.title}")
            print(f"  Type: {task.type} | Priority: {task.priority} | Domain: {task.domain}")
            print(f"  Description: {task.description[:120]}...")
            print(f"  Acceptance Criteria ({len(task.acceptance_criteria)} items):")
            for ac in task.acceptance_criteria[:3]:
                print(f"    - {ac}")
            print()
    except Exception as e:
        print(f"❌ Model mode error: {e}")
        import traceback
        traceback.print_exc()
    
    # Comparison
    print("\n" + "="*80)
    print("📊 COMPARISON")
    print("="*80)
    print("\n📋 Template Mode:")
    print("  ❌ Uses hardcoded template strings")
    print("  ❌ Output looks 'giả' (fake/generic)")
    print("  ✅ Fast, no dependencies")
    
    print("\n🤖 Model Mode:")
    print("  ✅ Uses YOUR trained ML models (1M dataset)")
    print("  ✅ Natural, varied output (not template)")
    print("  ✅ NO API keys required")
    print("  ✅ Learns from your data")
    print("  ✅ Can improve with more training data")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review generated tasks above")
    print("2. Compare template vs model output quality")
    print("3. If you want even better quality:")
    print("   - Generate more training data with script 06")
    print("   - Fine-tune T5/BART model for seq2seq generation")
    print("4. Use model mode in production: generator_mode='model'")


if __name__ == "__main__":
    main()
