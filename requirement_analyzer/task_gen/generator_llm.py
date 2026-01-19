"""
LLM-based Task Generator (No Templates)
Uses structured LLM prompting to generate natural task descriptions
"""
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
import time

from .schemas import GeneratedTask, TaskSource
from .segmenter import Sentence

logger = logging.getLogger(__name__)


class LLMTaskGenerator:
    """
    Generate tasks using LLM with structured JSON output
    No templates - LLM writes naturally following schema
    """
    
    def __init__(
        self,
        provider: str = "openai",  # or "anthropic", "local"
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.3,
        max_retries: int = 2
    ):
        """
        Initialize LLM generator
        
        Args:
            provider: LLM provider (openai, anthropic, local)
            model: Model name
            api_key: API key (or None to use env var)
            temperature: Generation temperature (0.3 = more consistent)
            max_retries: Max retries for failed generations
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        
        # Initialize client
        self.client = None
        self._init_client(api_key)
        
        logger.info(f"✓ LLM Task Generator initialized ({provider}/{model})")
    
    def _init_client(self, api_key: Optional[str]):
        """Initialize LLM client based on provider"""
        if self.provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
                logger.info("✓ OpenAI client initialized")
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
                raise
        
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
                logger.info("✓ Anthropic client initialized")
            except ImportError:
                logger.error("anthropic package not installed. Run: pip install anthropic")
                raise
        
        elif self.provider == "local":
            # For local LLMs (transformers, llama.cpp, etc.)
            logger.warning("Local LLM provider not fully implemented yet")
            # TODO: Implement local LLM support
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def generate(
        self,
        sentence: Sentence,
        labels: Dict[str, any],
        epic_name: Optional[str] = None,
        context_sentences: Optional[List[str]] = None
    ) -> GeneratedTask:
        """
        Generate a task from requirement sentence using LLM
        
        Args:
            sentence: Sentence object with requirement text
            labels: Dict with type, priority, domain, role, confidence
            epic_name: Optional epic/project name
            context_sentences: Optional surrounding sentences for context
        
        Returns:
            GeneratedTask object
        """
        # Build prompt
        prompt = self._build_prompt(sentence, labels, context_sentences)
        
        # Call LLM with retries
        task_json = None
        for attempt in range(self.max_retries + 1):
            try:
                task_json = self._call_llm(prompt)
                
                # Validate and parse
                task = self._parse_and_validate(task_json, sentence, labels, epic_name)
                return task
                
            except Exception as e:
                logger.warning(f"LLM generation attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    # Fallback: return minimal task
                    logger.error("All LLM attempts failed, returning fallback task")
                    return self._create_fallback_task(sentence, labels, epic_name)
        
        return self._create_fallback_task(sentence, labels, epic_name)
    
    def _build_prompt(
        self,
        sentence: Sentence,
        labels: Dict[str, any],
        context_sentences: Optional[List[str]] = None
    ) -> str:
        """Build structured prompt for LLM"""
        
        # Add context if available
        context_section = ""
        if context_sentences:
            context_section = f"\n\nContext (surrounding sentences):\n" + "\n".join(
                f"- {s}" for s in context_sentences[:3]
            )
        
        prompt = f"""You are a senior Business Analyst and Engineering Lead.
Your job is to convert ONE software requirement sentence into ONE Jira-ready task object.
You MUST return VALID JSON only (no markdown, no explanation, no extra text).

Requirement sentence:
"{sentence.text}"

Predicted labels (use these as strong hints):
- type: {labels.get('type', 'functional')}  (functional|security|interface|data|performance|integration|other)
- priority: {labels.get('priority', 'Medium')}  (Low|Medium|High|Critical)
- domain: {labels.get('domain', 'general')}  (ecommerce|iot|healthcare|education|finance|general|...)
- suggested_role: {labels.get('role', 'Backend')}  (Backend|Frontend|QA|DevOps|BA|Security){context_section}

CRITICAL REQUIREMENTS:
1) Write in natural, professional English like a real Jira ticket written by humans
2) Title must be:
   - Action-oriented (start with verb: Implement, Create, Setup, Configure, etc.)
   - Specific and concise (<= 12 words)
   - NOT generic ("Implement functionality")
   
3) Description must:
   - Restate the requirement in your own words (do NOT copy verbatim)
   - Include why this matters (business value if implied)
   - Mention technical approach if clear from requirement
   - Be 2-4 sentences, professional tone
   
4) Acceptance Criteria must be:
   - Specific, measurable, testable
   - 3-6 items (not too many, not too few)
   - Written as "Given/When/Then" OR bullet assertions
   - NOT generic ("code follows standards" unless truly relevant)
   - Cover functional correctness, edge cases, and verification
   
5) Role assignment:
   - interface/ui/frontend keywords -> Frontend
   - security/auth/encrypt keywords -> Security
   - data/database/storage keywords -> Backend or Data
   - api/server/business logic -> Backend
   - test/validation keywords -> QA
   - deploy/infrastructure keywords -> DevOps
   
6) Labels: include domain, type, and 1-3 short descriptive tags inferred from text

7) Confidence: float 0.0-1.0 based on:
   - How clear and specific the requirement is
   - How well it maps to task components
   - Use 0.7-0.9 for clear requirements, 0.5-0.7 for vague ones

JSON SCHEMA (return EXACTLY this structure, no extra fields):
{{
  "title": "string (action-oriented, specific, <= 12 words)",
  "description": "string (2-4 sentences, natural language)",
  "acceptance_criteria": ["string", "string", ...],  // 3-6 items
  "type": "string",  // use predicted type
  "priority": "string",  // use predicted priority
  "domain": "string",  // use predicted domain
  "role": "string",  // Backend|Frontend|QA|DevOps|BA|Security
  "labels": ["string", ...],  // 2-5 tags
  "confidence": number  // 0.0-1.0
}}

Now generate the JSON. Return ONLY valid JSON, nothing else:"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> Dict:
        """Call LLM and return parsed JSON"""
        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.provider == "local":
            return self._call_local(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _call_openai(self, prompt: str) -> Dict:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional software task generator. You always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"}  # Force JSON output
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _call_anthropic(self, prompt: str) -> Dict:
        """Call Anthropic API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=self.temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        
        # Extract JSON (Anthropic doesn't guarantee JSON-only response)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        return json.loads(content.strip())
    
    def _call_local(self, prompt: str) -> Dict:
        """Call local LLM (placeholder)"""
        # TODO: Implement local LLM support
        raise NotImplementedError("Local LLM not implemented yet")
    
    def _parse_and_validate(
        self,
        task_json: Dict,
        sentence: Sentence,
        labels: Dict,
        epic_name: Optional[str]
    ) -> GeneratedTask:
        """Parse and validate LLM output into GeneratedTask"""
        
        # Extract fields with fallbacks
        title = task_json.get('title', 'Implement requirement')
        description = task_json.get('description', sentence.text)
        acceptance_criteria = task_json.get('acceptance_criteria', [])
        
        # Ensure AC is a list
        if isinstance(acceptance_criteria, str):
            acceptance_criteria = [acceptance_criteria]
        
        # Validate and clean
        title = title.strip()[:100]  # Limit length
        
        if not acceptance_criteria:
            acceptance_criteria = ['Requirement is implemented as specified']
        
        # Create source metadata
        source = TaskSource(
            sentence=sentence.text,
            section=sentence.section,
            doc_offset=[sentence.offset_start, sentence.offset_end],
            line_number=sentence.line_number
        )
        
        # Build task
        task = GeneratedTask(
            epic=epic_name,
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria[:7],  # Limit to 7
            type=task_json.get('type', labels.get('type', 'functional')),
            priority=task_json.get('priority', labels.get('priority', 'Medium')),
            domain=task_json.get('domain', labels.get('domain', 'general')),
            role=task_json.get('role', labels.get('role', 'Backend')),
            labels=task_json.get('labels', [])[:5],  # Limit to 5
            confidence=float(task_json.get('confidence', labels.get('confidence', 0.7))),
            source=source
        )
        
        return task
    
    def _create_fallback_task(
        self,
        sentence: Sentence,
        labels: Dict,
        epic_name: Optional[str]
    ) -> GeneratedTask:
        """Create a basic fallback task when LLM fails"""
        
        source = TaskSource(
            sentence=sentence.text,
            section=sentence.section,
            doc_offset=[sentence.offset_start, sentence.offset_end],
            line_number=sentence.line_number
        )
        
        # Extract first verb + object as title
        words = sentence.text.split()[:10]
        title = ' '.join(words)
        
        task = GeneratedTask(
            epic=epic_name,
            title=f"Implement: {title[:80]}",
            description=f"Requirement: {sentence.text}",
            acceptance_criteria=[
                "Functionality is implemented as described",
                "Edge cases are handled appropriately",
                "Testing confirms requirements are met"
            ],
            type=labels.get('type', 'functional'),
            priority=labels.get('priority', 'Medium'),
            domain=labels.get('domain', 'general'),
            role=labels.get('role', 'Backend'),
            confidence=0.5,  # Low confidence for fallback
            source=source
        )
        
        return task
    
    def generate_batch(
        self,
        sentences: List[Sentence],
        labels_list: List[Dict[str, any]],
        epic_name: Optional[str] = None,
        show_progress: bool = True
    ) -> List[GeneratedTask]:
        """Generate tasks for a batch of sentences"""
        tasks = []
        
        total = len(sentences)
        for i, (sentence, labels) in enumerate(zip(sentences, labels_list)):
            if show_progress and (i + 1) % 5 == 0:
                logger.info(f"  Generating task {i+1}/{total}...")
            
            try:
                task = self.generate(sentence, labels, epic_name)
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error generating task {i+1}: {e}")
                # Create fallback
                fallback = self._create_fallback_task(sentence, labels, epic_name)
                tasks.append(fallback)
            
            # Rate limiting (optional)
            time.sleep(0.1)  # Small delay to avoid rate limits
        
        return tasks


# Factory function
def get_llm_generator(
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    **kwargs
) -> LLMTaskGenerator:
    """
    Get LLM task generator
    
    Args:
        provider: 'openai', 'anthropic', or 'local'
        model: Model name (e.g., 'gpt-4o-mini', 'claude-3-haiku-20240307')
        api_key: API key (or use env variable)
        **kwargs: Additional generator parameters
    """
    return LLMTaskGenerator(
        provider=provider,
        model=model,
        api_key=api_key,
        **kwargs
    )
