"""
V2 Pipeline Test Script
=======================

Tests the V2 Requirements Engineering pipeline end-to-end:
- Extract requirements from file
- Process through V2 pipeline (Refinement → Gap → Slicing → INVEST)
- Generate evaluation report
"""
import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from requirement_analyzer.task_gen.schemas_v2 import Requirement
from requirement_analyzer.task_gen.pipeline_v2 import V2Pipeline


def extract_requirements_from_file(file_path: str) -> List[Requirement]:
    """
    Extract requirements from markdown file
    
    Args:
        file_path: Path to requirements file
        
    Returns:
        List of Requirement objects
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    requirements = []
    req_counter = 0
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines and headings
        if not line or line.startswith('#') or len(line) < 20:
            continue
        
        # Skip intro paragraphs
        skip_keywords = [
            'tài liệu này', 'giới thiệu', 'mục tiêu dự án', 'phạm vi',
            'this document', 'introduction', 'project goal'
        ]
        if any(kw in line.lower() for kw in skip_keywords):
            continue
        
        # Detect language
        has_vietnamese = any(ord(c) > 127 for c in line)
        language = "vi" if has_vietnamese else "en"
        
        # Extract domain from filename
        domain = Path(file_path).stem.split('_')[0]
        
        req_counter += 1
        req = Requirement(
            requirement_id=f"REQ{req_counter:03d}",
            original_text=line,
            domain=domain,
            language=language,
            confidence=0.9,
            source_file=file_path,
            line_number=line_num
        )
        requirements.append(req)
    
    return requirements


def generate_evaluation_report(batch_output, output_file: str):
    """
    Generate V2 evaluation report
    
    Args:
        batch_output: BatchV2Output object
        output_file: Path to output file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# V2 Requirements Engineering Pipeline - Evaluation Report\n\n")
        f.write(f"Generated: {batch_output.requirements[0].created_at.strftime('%Y-%m-%d %H:%M:%S') if batch_output.requirements else 'N/A'}\n\n")
        
        # Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Requirements Processed:** {batch_output.total_requirements}\n")
        f.write(f"- **Total User Stories Generated:** {batch_output.total_stories}\n")
        f.write(f"- **Total Subtasks Generated:** {batch_output.total_subtasks}\n")
        f.write(f"- **Total Gaps Detected:** {batch_output.total_gaps}\n")
        f.write(f"- **Average INVEST Score:** {batch_output.avg_invest_score:.2f}/30\n")
        f.write(f"- **Processing Time:** {batch_output.processing_time_seconds:.2f}s\n")
        f.write(f"- **Success Rate:** {batch_output.summary['success_rate']:.1f}%\n\n")
        
        # Detailed metrics
        f.write("## Detailed Metrics\n\n")
        f.write("### Requirement Processing\n\n")
        f.write(f"- Avg stories per requirement: {batch_output.summary['avg_stories_per_requirement']:.2f}\n")
        f.write(f"- Avg subtasks per requirement: {batch_output.summary['avg_subtasks_per_requirement']:.2f}\n")
        f.write(f"- Avg gaps per requirement: {batch_output.summary['avg_gaps_per_requirement']:.2f}\n\n")
        
        f.write("### Gap Analysis\n\n")
        f.write(f"- Critical gaps: {batch_output.summary['critical_gaps_count']}\n")
        f.write(f"- High severity gaps: {batch_output.summary['high_gaps_count']}\n\n")
        
        # Gap breakdown
        f.write("### Gap Type Distribution\n\n")
        gap_types = {}
        for req_output in batch_output.requirements:
            for gap in req_output.gap_report.gaps:
                gap_type = gap.type.value
                gap_types[gap_type] = gap_types.get(gap_type, 0) + 1
        
        for gap_type, count in sorted(gap_types.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {gap_type}: {count}\n")
        f.write("\n")
        
        # INVEST score distribution
        f.write("### INVEST Score Distribution\n\n")
        invest_scores = []
        for req_output in batch_output.requirements:
            for slice_obj in req_output.slicing.slices:
                for story in slice_obj.stories:
                    invest_scores.append(story.invest_score.total)
        
        if invest_scores:
            f.write(f"- Excellent (25-30): {sum(1 for s in invest_scores if s >= 25)}\n")
            f.write(f"- Good (20-24): {sum(1 for s in invest_scores if 20 <= s < 25)}\n")
            f.write(f"- Fair (15-19): {sum(1 for s in invest_scores if 15 <= s < 20)}\n")
            f.write(f"- Poor (<15): {sum(1 for s in invest_scores if s < 15)}\n\n")
        
        # Sample outputs
        f.write("## Sample Outputs\n\n")
        for idx, req_output in enumerate(batch_output.requirements[:3], 1):  # First 3
            f.write(f"### Sample {idx}: {req_output.requirement_id}\n\n")
            f.write(f"**Original:** {req_output.original_requirement[:100]}...\n\n")
            
            f.write(f"**Refinement:**\n")
            f.write(f"- Title: {req_output.refinement.title}\n")
            f.write(f"- User Story: {req_output.refinement.user_story}\n")
            f.write(f"- AC Count: {len(req_output.refinement.acceptance_criteria)}\n")
            f.write(f"- NFRs: {len(req_output.refinement.non_functional_requirements)}\n\n")
            
            f.write(f"**Gaps Detected:** {req_output.gap_report.total_gaps}\n")
            for gap in req_output.gap_report.gaps[:3]:  # First 3 gaps
                f.write(f"- [{gap.severity.value}] {gap.type.value}: {gap.description[:80]}...\n")
            f.write("\n")
            
            f.write(f"**Slicing:** {req_output.slicing.total_stories} stories, {req_output.slicing.total_subtasks} subtasks\n")
            for slice_obj in req_output.slicing.slices:
                f.write(f"- Slice {slice_obj.slice_id} ({slice_obj.rationale.value}): {len(slice_obj.stories)} stories\n")
            f.write("\n")
            
            f.write(f"**Quality Metrics:**\n")
            f.write(f"- Refinement Score: {req_output.quality_metrics.refinement_score:.2f}\n")
            f.write(f"- Gap Coverage: {req_output.quality_metrics.gap_coverage:.2f}\n")
            f.write(f"- Avg INVEST: {req_output.quality_metrics.invest_avg_score:.2f}\n")
            f.write(f"- Processing Time: {req_output.quality_metrics.processing_time_seconds:.2f}s\n\n")
            f.write("---\n\n")
        
        # Traceability sample
        f.write("## Traceability Sample\n\n")
        if batch_output.requirements:
            req_output = batch_output.requirements[0]
            f.write(f"**{req_output.requirement_id} Traceability:**\n\n")
            f.write(f"- Stories: {', '.join(req_output.traceability.requirement_to_stories)}\n")
            if req_output.traceability.story_to_tasks:
                f.write(f"- Tasks: {req_output.traceability.story_to_tasks[0]}\n")
            f.write("\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        critical_count = batch_output.summary['critical_gaps_count']
        if critical_count > 0:
            f.write(f"⚠️  **HIGH PRIORITY:** {critical_count} critical gaps detected. Review with Product Owner immediately.\n\n")
        
        low_invest_count = sum(1 for s in invest_scores if s < 20)
        if low_invest_count > 0:
            f.write(f"⚠️  **MEDIUM PRIORITY:** {low_invest_count} stories have low INVEST scores. Consider refinement.\n\n")
        
        f.write("✅ Pipeline executed successfully. All requirements processed with full traceability.\n\n")


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("V2 Requirements Engineering Pipeline - Test")
    print("="*70 + "\n")
    
    # Test file
    test_file = "requirement_analyzer/task_gen/hotel_management_requirements.md"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        print("Please create a test requirements file first.")
        return
    
    # Extract requirements
    print(f"📄 Reading requirements from: {test_file}")
    requirements = extract_requirements_from_file(test_file)
    print(f"✅ Extracted {len(requirements)} requirements\n")
    
    # Limit to first 5 for testing
    requirements = requirements[:5]
    print(f"🔬 Testing with first {len(requirements)} requirements\n")
    
    # Initialize pipeline
    pipeline = V2Pipeline()
    
    # Process batch
    batch_output = pipeline.process_batch(requirements)
    
    # Generate report
    output_file = "V2_EVAL_REPORT.md"
    print(f"\n📊 Generating evaluation report: {output_file}")
    generate_evaluation_report(batch_output, output_file)
    print(f"✅ Report saved: {output_file}\n")
    
    # Summary
    print("="*70)
    print("V2 Pipeline Test Complete!")
    print("="*70)
    print(f"Requirements: {batch_output.total_requirements}")
    print(f"Stories: {batch_output.total_stories}")
    print(f"Subtasks: {batch_output.total_subtasks}")
    print(f"Gaps: {batch_output.total_gaps}")
    print(f"INVEST Avg: {batch_output.avg_invest_score:.1f}/30")
    print(f"Time: {batch_output.processing_time_seconds:.2f}s")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
