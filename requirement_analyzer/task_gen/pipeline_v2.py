"""
V2 Pipeline Orchestrator
=========================

Orchestrates the complete V2 Requirements Engineering pipeline:
Stage 0: Extract & Normalize (from V1)
Stage 1: Refinement (User Story + AC)
Stage 2: Gap Detection (Rule-based + LLM)
Stage 3: Smart Slicing + INVEST Scoring
Stage 4: Enhanced Task Generation

Includes Quality Gates and Traceability.
"""
import time
from typing import List, Dict, Any
from requirement_analyzer.task_gen.schemas_v2 import (
    Requirement,
    RequirementV2Output,
    BatchV2Output,
    Traceability,
    QualityMetrics
)
from requirement_analyzer.task_gen.refinement import RequirementRefiner
from requirement_analyzer.task_gen.gap_detector import GapDetector
from requirement_analyzer.task_gen.slicer import SmartSlicer


class V2Pipeline:
    """V2 Requirements Engineering Pipeline"""
    
    def __init__(self):
        """Initialize pipeline components"""
        self.refiner = RequirementRefiner()
        self.gap_detector = GapDetector()
        self.slicer = SmartSlicer()
    
    def process_single_requirement(self, requirement: Requirement) -> RequirementV2Output:
        """
        Process a single requirement through V2 pipeline
        
        Args:
            requirement: Raw requirement
            
        Returns:
            RequirementV2Output with all stages completed
        """
        start_time = time.time()
        
        # Quality Gate 1: Schema validation (already done by Pydantic)
        
        # Stage 1: Refinement
        print(f"  [Stage 1] Refining {requirement.requirement_id}...")
        refinement = self.refiner.refine(requirement)
        
        # Stage 2: Gap Detection
        print(f"  [Stage 2] Detecting gaps in {requirement.requirement_id}...")
        gap_report = self.gap_detector.detect_gaps(requirement, refinement)
        
        # Quality Gate 2: Check critical gaps
        if gap_report.critical_count > 0:
            print(f"  ⚠️  Found {gap_report.critical_count} CRITICAL gaps - flagged for review")
        
        # Stage 3: Smart Slicing + INVEST
        print(f"  [Stage 3] Slicing {requirement.requirement_id} into stories...")
        slicing = self.slicer.slice_requirement(refinement)
        
        # Quality Gate 3: Check INVEST scores
        low_invest_count = sum(
            1 for slice_obj in slicing.slices
            for story in slice_obj.stories
            if story.invest_score.total < 20
        )
        if low_invest_count > 0:
            print(f"  ⚠️  {low_invest_count} stories have low INVEST scores")
        
        # Build Traceability
        traceability = self._build_traceability(requirement, refinement, slicing, gap_report)
        
        # Calculate Quality Metrics
        processing_time = time.time() - start_time
        quality_metrics = self._calculate_quality_metrics(
            refinement,
            gap_report,
            slicing,
            processing_time
        )
        
        print(f"  ✅ Completed {requirement.requirement_id} in {processing_time:.2f}s")
        print(f"     └─ {slicing.total_stories} stories, {slicing.total_subtasks} subtasks, {gap_report.total_gaps} gaps")
        
        return RequirementV2Output(
            requirement_id=requirement.requirement_id,
            original_requirement=requirement.original_text,
            domain=requirement.domain or "unknown",
            language=requirement.language,
            refinement=refinement,
            gap_report=gap_report,
            slicing=slicing,
            traceability=traceability,
            quality_metrics=quality_metrics
        )
    
    def process_batch(self, requirements: List[Requirement]) -> BatchV2Output:
        """
        Process batch of requirements through V2 pipeline
        
        Args:
            requirements: List of raw requirements
            
        Returns:
            BatchV2Output with summary statistics
        """
        print(f"\n{'='*70}")
        print(f"V2 Pipeline: Processing {len(requirements)} requirements")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        outputs = []
        
        for idx, requirement in enumerate(requirements, 1):
            print(f"[{idx}/{len(requirements)}] Processing {requirement.requirement_id}...")
            try:
                output = self.process_single_requirement(requirement)
                outputs.append(output)
            except Exception as e:
                print(f"  ❌ Error processing {requirement.requirement_id}: {e}")
                continue
        
        processing_time = time.time() - start_time
        
        # Calculate summary statistics
        total_stories = sum(o.slicing.total_stories for o in outputs)
        total_subtasks = sum(o.slicing.total_subtasks for o in outputs)
        total_gaps = sum(o.gap_report.total_gaps for o in outputs)
        
        # Calculate average INVEST score
        all_invest_scores = [
            story.invest_score.total
            for o in outputs
            for slice_obj in o.slicing.slices
            for story in slice_obj.stories
        ]
        avg_invest_score = sum(all_invest_scores) / len(all_invest_scores) if all_invest_scores else 0
        
        # Summary
        summary = {
            "processing_time_seconds": processing_time,
            "success_rate": len(outputs) / len(requirements) * 100,
            "avg_stories_per_requirement": total_stories / len(outputs) if outputs else 0,
            "avg_subtasks_per_requirement": total_subtasks / len(outputs) if outputs else 0,
            "avg_gaps_per_requirement": total_gaps / len(outputs) if outputs else 0,
            "avg_invest_score": avg_invest_score,
            "critical_gaps_count": sum(o.gap_report.critical_count for o in outputs),
            "high_gaps_count": sum(o.gap_report.high_count for o in outputs),
        }
        
        print(f"\n{'='*70}")
        print(f"V2 Pipeline: Completed in {processing_time:.2f}s")
        print(f"{'='*70}")
        print(f"  Requirements: {len(requirements)} → {len(outputs)} processed ({summary['success_rate']:.1f}%)")
        print(f"  Stories: {total_stories} ({summary['avg_stories_per_requirement']:.1f} per req)")
        print(f"  Subtasks: {total_subtasks} ({summary['avg_subtasks_per_requirement']:.1f} per req)")
        print(f"  Gaps: {total_gaps} ({summary['avg_gaps_per_requirement']:.1f} per req)")
        print(f"  INVEST Score: {avg_invest_score:.1f}/30 average")
        print(f"  Critical Gaps: {summary['critical_gaps_count']}")
        print(f"{'='*70}\n")
        
        return BatchV2Output(
            requirements=outputs,
            total_requirements=len(outputs),
            total_stories=total_stories,
            total_subtasks=total_subtasks,
            total_gaps=total_gaps,
            avg_invest_score=avg_invest_score,
            processing_time_seconds=processing_time,
            summary=summary
        )
    
    def _build_traceability(
        self,
        requirement: Requirement,
        refinement: Any,
        slicing: Any,
        gap_report: Any
    ) -> Traceability:
        """Build traceability links"""
        
        # Requirement → Stories
        requirement_to_stories = [
            story.story_id
            for slice_obj in slicing.slices
            for story in slice_obj.stories
        ]
        
        # Story → Tasks
        story_to_tasks = [
            f"{story.story_id} → {','.join(t.task_id for t in story.subtasks)}"
            for slice_obj in slicing.slices
            for story in slice_obj.stories
        ]
        
        # Gaps → Stories (gaps that led to new stories)
        gaps_to_stories = []
        if gap_report.total_gaps > 0:
            # Simple heuristic: map critical gaps to stories
            for gap in gap_report.gaps:
                if gap.severity.value in ["Critical", "High"]:
                    # Link to first story (simplified)
                    if requirement_to_stories:
                        gaps_to_stories.append(f"{gap.gap_id} → {requirement_to_stories[0]}")
        
        return Traceability(
            requirement_to_stories=requirement_to_stories,
            story_to_tasks=story_to_tasks,
            gaps_to_stories=gaps_to_stories
        )
    
    def _calculate_quality_metrics(
        self,
        refinement: Any,
        gap_report: Any,
        slicing: Any,
        processing_time: float
    ) -> QualityMetrics:
        """Calculate quality metrics"""
        
        # Refinement score (based on AC count and NFRs)
        ac_score = min(len(refinement.acceptance_criteria) / 5, 1.0)  # Target: 5 AC
        nfr_score = 1.0 if refinement.non_functional_requirements else 0.5
        refinement_score = (ac_score + nfr_score) / 2
        
        # Gap coverage (based on gap count)
        gap_coverage = min(gap_report.total_gaps / 5, 1.0)  # Target: 5+ gaps detected
        
        # Average INVEST score
        all_invest_scores = [
            story.invest_score.total
            for slice_obj in slicing.slices
            for story in slice_obj.stories
        ]
        invest_avg_score = sum(all_invest_scores) / len(all_invest_scores) if all_invest_scores else 0
        
        return QualityMetrics(
            schema_valid=True,
            refinement_score=refinement_score,
            gap_coverage=gap_coverage,
            invest_avg_score=invest_avg_score,
            processing_time_seconds=processing_time
        )
