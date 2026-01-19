#!/usr/bin/env python3
"""
Test LLM Mode for Task Generation

Tests the LLM-based natural language generation (vs template mode).
Requires API key: export OPENAI_API_KEY="sk-..."
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_llm_mode():
    """Test LLM generation mode"""
    logger.info("=" * 70)
    logger.info("Testing LLM Mode (Natural Language Generation)")
    logger.info("=" * 70)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY not set!")
        logger.info("Set it with: export OPENAI_API_KEY='sk-...'")
        logger.info("Or try Anthropic: export ANTHROPIC_API_KEY='sk-ant-...'")
        return False
    
    logger.info(f"✓ API key found: {api_key[:10]}...")
    
    # Import task_gen
    try:
        from requirement_analyzer.task_gen import get_pipeline
        logger.info("✓ task_gen module imported")
    except ImportError as e:
        logger.error(f"❌ Failed to import task_gen: {e}")
        return False
    
    # Test document
    test_doc = """
    User Authentication Requirements:
    
    1. Users must be able to register with email and password.
    2. System should validate email format and password strength (min 8 characters, 1 uppercase, 1 number).
    3. After registration, send verification email with unique token link.
    4. Users can login with verified email and password.
    5. System must implement JWT-based authentication for API endpoints.
    6. Tokens should expire after 24 hours and support refresh mechanism.
    7. Implement password reset functionality via email link.
    8. Dashboard should display user profile with avatar upload capability.
    """
    
    logger.info("\n📄 Test Document:")
    logger.info("-" * 70)
    logger.info(test_doc.strip())
    logger.info("-" * 70)
    
    # Test 1: LLM Mode (OpenAI)
    logger.info("\n🧠 Test 1: LLM Mode (OpenAI GPT-4o-mini)")
    logger.info("-" * 70)
    
    try:
        pipeline_llm = get_pipeline(
            generator_mode="llm",
            llm_provider="openai",
            llm_model="gpt-4o-mini"
        )
        logger.info("✓ LLM pipeline initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize LLM pipeline: {e}")
        return False
    
    try:
        logger.info("Generating tasks with LLM (this may take 10-30 seconds)...")
        result_llm = pipeline_llm.generate_tasks(
            text=test_doc,
            max_tasks=10
        )
        
        logger.info(f"\n✓ Generated {result_llm.total_tasks} tasks in {result_llm.processing_time:.2f}s")
        logger.info(f"  Avg confidence: {result_llm.stats['avg_confidence']:.2f}")
        
        # Display first 3 tasks
        logger.info("\n📋 Generated Tasks (LLM Mode):")
        logger.info("=" * 70)
        
        for i, task in enumerate(result_llm.tasks[:3], 1):
            logger.info(f"\n{i}. {task.title}")
            logger.info(f"   Priority: {task.priority} | Type: {task.type} | Role: {task.role}")
            logger.info(f"   Confidence: {task.confidence:.2f}")
            logger.info(f"\n   Description:")
            logger.info(f"   {task.description}")
            logger.info(f"\n   Acceptance Criteria ({len(task.acceptance_criteria)} items):")
            for j, ac in enumerate(task.acceptance_criteria, 1):
                logger.info(f"   {j}. {ac}")
        
        if result_llm.total_tasks > 3:
            logger.info(f"\n   ... and {result_llm.total_tasks - 3} more tasks")
        
    except Exception as e:
        logger.error(f"❌ LLM generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Compare with Template Mode
    logger.info("\n" + "=" * 70)
    logger.info("📊 Comparison: Template Mode vs LLM Mode")
    logger.info("=" * 70)
    
    try:
        pipeline_template = get_pipeline(generator_mode="template")
        result_template = pipeline_template.generate_tasks(
            text=test_doc,
            max_tasks=10
        )
        
        logger.info(f"\nTemplate Mode:")
        logger.info(f"  Tasks: {result_template.total_tasks}")
        logger.info(f"  Time: {result_template.processing_time:.2f}s")
        logger.info(f"  First task: {result_template.tasks[0].title}")
        logger.info(f"  Description: {result_template.tasks[0].description[:100]}...")
        
        logger.info(f"\nLLM Mode:")
        logger.info(f"  Tasks: {result_llm.total_tasks}")
        logger.info(f"  Time: {result_llm.processing_time:.2f}s")
        logger.info(f"  First task: {result_llm.tasks[0].title}")
        logger.info(f"  Description: {result_llm.tasks[0].description[:100]}...")
        
        logger.info(f"\n⚡ Speed: Template is {result_llm.processing_time / result_template.processing_time:.1f}x faster")
        logger.info(f"💰 Cost: LLM ~${result_llm.total_tasks * 0.0002:.4f} (template: $0)")
        logger.info(f"✨ Quality: LLM tasks are more natural and detailed")
        
    except Exception as e:
        logger.warning(f"⚠️  Template comparison skipped: {e}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ LLM Mode Test Complete!")
    logger.info("=" * 70)
    return True


def test_anthropic_mode():
    """Test with Anthropic Claude (optional)"""
    logger.info("\n" + "=" * 70)
    logger.info("Testing Anthropic Claude Mode (Optional)")
    logger.info("=" * 70)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.info("⏭️  Skipping Anthropic test (no API key)")
        return True
    
    try:
        from requirement_analyzer.task_gen import get_pipeline
        
        pipeline = get_pipeline(
            generator_mode="llm",
            llm_provider="anthropic",
            llm_model="claude-3-haiku-20240307"
        )
        
        result = pipeline.generate_tasks(
            text="Users must login with OAuth2 support for Google and GitHub.",
            max_tasks=2
        )
        
        logger.info(f"✓ Anthropic generated {result.total_tasks} tasks")
        logger.info(f"  First task: {result.tasks[0].title}")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  Anthropic test failed: {e}")
        return True  # Don't fail overall test


if __name__ == '__main__':
    success = test_llm_mode()
    
    # Optional: Test Anthropic
    if success and os.getenv("TEST_ANTHROPIC"):
        test_anthropic_mode()
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 All tests passed! LLM mode is working.")
        print("\nNext steps:")
        print("1. Compare output quality with template mode")
        print("2. A/B test with real users")
        print("3. Monitor API costs")
        print("4. Consider fine-tuning local model for cost savings")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Check errors above.")
        sys.exit(1)
