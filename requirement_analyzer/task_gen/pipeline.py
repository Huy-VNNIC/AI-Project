"""
Task Generation Pipeline - Main Orchestrator
Combines all components into end-to-end pipeline
"""
import time
from pathlib import Path
from typing import List, Dict, Optional
import logging

from .schemas import GeneratedTask, TaskGenerationRequest, TaskGenerationResponse
from .segmenter import get_segmenter, Sentence
from .req_detector import get_detector
from .enrichers import get_enrichment_pipeline
from .generator_templates import get_generator
from .generator_llm import get_llm_generator
from .generator_model_based import ModelBasedTaskGenerator
from .postprocess import get_postprocessor

logger = logging.getLogger(__name__)


class TaskGenerationPipeline:
    """
    End-to-end pipeline for task generation
    
    Pipeline stages:
    1. Segment document into sentences
    2. Filter requirements using detector
    3. Enrich with labels (type/priority/domain/role)
    4. Generate tasks using templates
    5. Post-process (dedupe, filter)
    """
    
    def __init__(
        self, 
        model_dir: Optional[Path] = None,
        generator_mode: str = "template",  # "template", "llm", or "model"
        llm_provider: Optional[str] = None,  # For LLM mode: "openai", "anthropic"
        llm_model: Optional[str] = None,  # For LLM mode
        llm_api_key: Optional[str] = None  # For LLM mode
    ):
        """
        Initialize pipeline
        
        Args:
            model_dir: Path to trained models directory
            generator_mode: "template" (default), "llm", or "model" (trained ML models)
            llm_provider: LLM provider (if mode=llm): "openai" or "anthropic"
            llm_model: LLM model name (e.g., "gpt-4o-mini")
            llm_api_key: LLM API key (or use env var)
        """
        if model_dir is None:
            # Import config to get correct path
            from .config import MODEL_DIR
            model_dir = MODEL_DIR
        
        self.model_dir = Path(model_dir)
        self.generator_mode = generator_mode
        
        # Resolve models path (all trained models should be in model_dir)
        models_path = self.model_dir
        
        # If model_dir has a 'models' subdirectory, use it
        if (self.model_dir / 'models').exists():
            models_path = self.model_dir / 'models'
        
        # Verify at least one model file exists
        test_file = models_path / 'requirement_detector_model.joblib'
        if not test_file.exists():
            logger.warning(f"Models not found at {models_path}")
        else:
            logger.info(f"Using models from: {models_path}")
        
        # Initialize components (all use same models path)
        self.segmenter = get_segmenter()
        self.detector = get_detector(models_path)
        self.enricher = get_enrichment_pipeline(models_path)
        
        # Initialize generator based on mode
        if generator_mode == "llm":
            if not llm_provider:
                llm_provider = "openai"
            if not llm_model:
                llm_model = "gpt-4o-mini" if llm_provider == "openai" else "claude-3-haiku-20240307"
            
            logger.info(f"Using LLM generator: {llm_provider}/{llm_model}")
            self.generator = get_llm_generator(
                provider=llm_provider,
                model=llm_model,
                api_key=llm_api_key
            )
        elif generator_mode == "model":
            logger.info("Using trained model-based generator (no API required)")
            try:
                self.generator = ModelBasedTaskGenerator(model_dir=models_path)
                logger.info(f"✅ ModelBasedTaskGenerator initialized: {type(self.generator).__name__}")
            except Exception as e:
                logger.exception(f"❌ Model generator init failed, falling back to template: {e}")
                self.generator = get_generator()
                self.generator_mode = "template"  # Update mode to reflect fallback
        else:
            logger.info("Using template generator")
            self.generator = get_generator()
        
        self.postprocessor = get_postprocessor()
        
        logger.info(f"✓ Task generation pipeline initialized (mode={generator_mode})")
    
    def generate_tasks(
        self,
        text: str,
        max_tasks: int = 50,
        requirement_threshold: float = 0.5,
        epic_name: Optional[str] = None,
        domain_hint: Optional[str] = None
    ) -> TaskGenerationResponse:
        """
        Generate tasks from requirement document
        
        Args:
            text: Requirement document text
            max_tasks: Maximum number of tasks to generate
            requirement_threshold: Confidence threshold for requirement detection
            epic_name: Optional epic/project name
            domain_hint: Optional domain hint (overrides ML prediction)
        
        Returns:
            TaskGenerationResponse with generated tasks
        """
        start_time = time.time()
        
        logger.info(f"🚀 Starting task generation pipeline")
        logger.info(f"   Input length: {len(text)} characters")
        logger.info(f"   Max tasks: {max_tasks}")
        
        # Stage 1: Segmentation
        logger.info("📄 Stage 1: Segmenting document...")
        sections, sentences = self.segmenter.segment(text)
        logger.info(f"   Extracted {len(sentences)} sentences from {len(sections)} sections")
        
        if not sentences:
            logger.warning("No sentences extracted from document")
            return self._empty_response(time.time() - start_time)
        
        # Stage 2: Requirement Detection
        logger.info("🔍 Stage 2: Detecting requirements...")
        sentence_texts = [s.text for s in sentences]
        detection_results = self.detector.detect(
            sentence_texts,
            threshold=requirement_threshold
        )
        
        # Filter to requirements only
        requirement_sentences = []
        requirement_confidences = []
        
        for sentence, (is_req, confidence) in zip(sentences, detection_results):
            if is_req:
                requirement_sentences.append(sentence)
                requirement_confidences.append(confidence)
        
        logger.info(f"   Found {len(requirement_sentences)} requirements "
                   f"(filtered {len(sentences) - len(requirement_sentences)} non-requirements)")
        
        if not requirement_sentences:
            logger.warning("No requirements detected in document")
            return self._empty_response(time.time() - start_time)
        
        # Limit to max_tasks at detection stage
        if len(requirement_sentences) > max_tasks:
            # Sort by confidence and take top max_tasks
            sorted_pairs = sorted(
                zip(requirement_sentences, requirement_confidences),
                key=lambda x: x[1],
                reverse=True
            )
            requirement_sentences = [s for s, _ in sorted_pairs[:max_tasks]]
            requirement_confidences = [c for _, c in sorted_pairs[:max_tasks]]
            logger.info(f"   Limited to top {max_tasks} requirements by confidence")
        
        # Stage 3: Enrichment (type, priority, domain, role)
        logger.info("🏷️  Stage 3: Enriching requirements with labels...")
        req_texts = [s.text for s in requirement_sentences]
        enrichment_results = self.enricher.enrich(req_texts)
        
        # Apply domain hint if provided
        if domain_hint:
            for result in enrichment_results:
                result['domain'] = domain_hint
        
        # Combine detection confidence with enrichment confidence
        for i, det_conf in enumerate(requirement_confidences):
            enrichment_results[i]['confidence'] = min(
                det_conf,
                enrichment_results[i]['confidence']
            )
        
        logger.info(f"   Enriched {len(enrichment_results)} requirements")
        
        # Log distribution
        type_dist = {}
        for result in enrichment_results:
            t = result['type']
            type_dist[t] = type_dist.get(t, 0) + 1
        logger.info(f"   Type distribution: {type_dist}")
        
        # Stage 4: Task Generation
        logger.info("⚙️  Stage 4: Generating tasks...")
        tasks = self.generator.generate_batch(
            requirement_sentences,
            enrichment_results,
            epic_name=epic_name
        )
        logger.info(f"   Generated {len(tasks)} tasks")
        
        # Stage 5: Post-processing
        logger.info("🧹 Stage 5: Post-processing tasks...")
        tasks = self.postprocessor.process(tasks)
        logger.info(f"   Final task count: {len(tasks)}")
        
        # Build response
        processing_time = time.time() - start_time
        
        response = TaskGenerationResponse(
            tasks=tasks,
            total_tasks=len(tasks),
            stats={},  # Auto-computed by pydantic validator
            processing_time=processing_time,
            mode=self.generator_mode  # Use actual mode, not hardcoded
        )
        
        logger.info(f"✅ Task generation complete in {processing_time:.2f}s")
        logger.info(f"   Generated {len(tasks)} tasks")
        logger.info(f"   Avg confidence: {response.stats['avg_confidence']:.3f}")
        
        return response
    
    def generate_from_sentences(
        self,
        sentences: List[str],
        epic_name: Optional[str] = None
    ) -> List[GeneratedTask]:
        """
        Generate tasks from pre-segmented sentences
        (Useful when sentences are already extracted externally)
        """
        # Convert to Sentence objects
        sentence_objs = [
            Sentence(text=s, section=None, offset_start=0, offset_end=len(s))
            for s in sentences
        ]
        
        # Detect requirements
        detection_results = self.detector.detect(sentences)
        req_sentences = [s for s, (is_req, _) in zip(sentence_objs, detection_results) if is_req]
        
        if not req_sentences:
            return []
        
        # Enrich
        req_texts = [s.text for s in req_sentences]
        enrichment_results = self.enricher.enrich(req_texts)
        
        # Generate
        tasks = self.generator.generate_batch(req_sentences, enrichment_results, epic_name)
        
        # Post-process
        tasks = self.postprocessor.process(tasks)
        
        return tasks
    
    def _empty_response(self, processing_time: float) -> TaskGenerationResponse:
        """Create empty response when no tasks generated"""
        return TaskGenerationResponse(
            tasks=[],
            total_tasks=0,
            stats={},
            processing_time=processing_time,
            mode='template'
        )


# Singleton
_pipeline = None
_pipeline_params = None

def get_pipeline(
    model_dir: Optional[Path] = None,
    generator_mode: str = "template",
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
    llm_api_key: Optional[str] = None
) -> TaskGenerationPipeline:
    """
    Get singleton pipeline
    
    Args:
        model_dir: Path to trained models
        generator_mode: "template" or "llm"
        llm_provider: LLM provider (if mode=llm)
        llm_model: LLM model name (if mode=llm)
        llm_api_key: LLM API key (if mode=llm)
    """
    global _pipeline, _pipeline_params
    
    current_params = (model_dir, generator_mode, llm_provider, llm_model)
    
    if _pipeline is None or _pipeline_params != current_params:
        _pipeline = TaskGenerationPipeline(
            model_dir=model_dir,
            generator_mode=generator_mode,
            llm_provider=llm_provider,
            llm_model=llm_model,
            llm_api_key=llm_api_key
        )
        _pipeline_params = current_params
    
    return _pipeline
