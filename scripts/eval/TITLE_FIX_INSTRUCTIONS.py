"""
TITLE QUALITY IMPROVEMENT FIX
Apply ONLY if pilot scores show avg_title_clarity < 3.0

This fix improves title generation by:
1. Using ROOT verb + direct object from dependency parse
2. Skipping generic suffixes (capability/functionality/feature)
3. Prioritizing longer, more specific noun phrases
4. Better handling of verb-object word order

Expected impact: Generic titles 60% → ~30%
"""

# ============================================================================
# BACKUP current generator_model_based.py BEFORE applying!
# ============================================================================

# To apply this fix:
# 1. Run pilot scoring first
# 2. If score_title_clarity < 3.0, apply changes below
# 3. Re-generate OOD with: python scripts/eval/01_generate_ood_outputs.py ...
# 4. Re-score pilot to verify improvement

# ============================================================================
# CHANGES TO: requirement_analyzer/task_gen/generator_model_based.py
# ============================================================================

"""
CHANGE 1: Improve extract_entities() to include dependency parse info
Location: Around line 148

ADD this method:
"""

def extract_entities_enhanced(self, text: str) -> Dict[str, Any]:
    """Extract entities with dependency parse for better title generation"""
    if not self.nlp:
        return self.extract_entities(text)  # Fallback
    
    doc = self.nlp(text.lower())
    
    # Basic extraction
    verbs = [token.lemma_ for token in doc if token.pos_ == 'VERB']
    nouns = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    objects = [chunk.text for chunk in doc.noun_chunks]
    
    # Enhanced: ROOT verb + direct object
    root_verb = None
    direct_object = None
    
    for token in doc:
        if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
            root_verb = token.lemma_
            # Find direct object of ROOT
            for child in token.children:
                if child.dep_ in ('dobj', 'obj', 'pobj'):
                    # Get full noun phrase containing this object
                    for chunk in doc.noun_chunks:
                        if child in chunk:
                            direct_object = chunk.text
                            break
                    if direct_object:
                        break
    
    return {
        'verbs': verbs[:3],
        'nouns': nouns[:5],
        'objects': objects[:5],  # Increase to 5 for more options
        'root_verb': root_verb,
        'direct_object': direct_object
    }


"""
CHANGE 2: Improve generate_title() with better logic
Location: Around line 171

REPLACE generate_title() method with:
"""

def generate_title(self, text: str, req_type: str, entities: Dict) -> str:
    """Generate natural title (improved version)"""
    import re
    
    # Modal verbs to skip
    MODAL_VERBS = {'need', 'must', 'should', 'shall', 'may', 'can', 'will', 'would', 'could'}
    
    # Generic terms to avoid
    GENERIC_OBJECTS = {'system', 'application', 'platform', 'feature', 'functionality',
                      'solution', 'tool', 'module', 'service', 'capability', 'product',
                      'users', 'user'}
    
    # Generic suffixes to avoid
    GENERIC_SUFFIXES = ['capability', 'functionality', 'feature']
    
    # 1. Extract action verb
    action = None
    
    # Try ROOT verb from enhanced extraction
    if entities.get('root_verb'):
        action = entities['root_verb']
    # Try modal pattern "be able to [verb]"
    elif match := re.search(r'(?:shall|must|should|may|can)\s+be\s+able\s+to\s+(\w+)', text, re.I):
        action = match.group(1).lower()
    # Try first non-modal verb
    elif entities.get('verbs'):
        for verb in entities['verbs']:
            if verb.lower() not in MODAL_VERBS:
                action = verb
                break
    
    if not action:
        action = 'support'  # Final fallback
    
    # 2. Extract object phrase
    obj = None
    
    # Try direct object from ROOT verb
    if entities.get('direct_object'):
        candidate = entities['direct_object']
        words = candidate.split()
        # Skip if entirely generic
        if not all(w.lower() in GENERIC_OBJECTS for w in words):
            obj = candidate
    
    # Fallback: find best noun phrase from objects list
    if not obj and entities.get('objects'):
        candidates = []
        for candidate in entities['objects']:
            words = candidate.split()
            if not words:
                continue
            # Skip if contains generic words AND is short (< 3 words)
            if any(w.lower() in GENERIC_OBJECTS for w in words) and len(words) < 3:
                continue
            # Score by length (longer = more specific)
            candidates.append((len(words), candidate))
        
        if candidates:
            # Pick longest
            obj = max(candidates, key=lambda x: x[0])[1]
    
    if not obj:
        obj = 'feature'  # Final fallback
    
    # 3. Construct title (simple format, avoid generic suffixes)
    title = f"{action.capitalize()} {obj}"
    
    # Remove generic suffixes if present
    for suffix in GENERIC_SUFFIXES:
        if title.lower().endswith(suffix):
            title = title[:-(len(suffix)+1)].strip()  # +1 for space
            break
    
    return title


"""
CHANGE 3: Update call sites to use enhanced extraction
Location: Around lines 321, 409 (in generate_* methods)

REPLACE:
    entities = self.extract_entities(sentence.text)

WITH:
    entities = self.extract_entities_enhanced(sentence.text)
"""

# ============================================================================
# TESTING AFTER APPLYING
# ============================================================================

"""
1. Test with sample requirements:

python -c "
from requirement_analyzer.task_gen.pipeline import TaskGenerationPipeline

test_reqs = [
    'The system must verify user identity through two-factor authentication',
    'Users should be able to transfer funds between their accounts',
    'Doctors must be able to prescribe medications electronically',
]

pipeline = TaskGenerationPipeline(model_dir='requirement_analyzer/models/task_gen/models', generator_mode='model')

for req in test_reqs:
    result = pipeline.generate_tasks(text=req, max_tasks=1)
    if result.tasks:
        print(f'Req: {req[:50]}...')
        print(f'Title: {result.tasks[0].title}')
        print()
"

Expected improvements:
- "Verify the system" → "Verify user identity"
- "Transfer their accounts functionality" → "Transfer funds"
- Should generate task for "be able to prescribe"

2. Re-run OOD generation:

python scripts/eval/01_generate_ood_outputs.py \
  scripts/eval/ood_requirements_filled.csv \
  scripts/eval/ood_generated_v4.csv --mode model

3. Compare v3 vs v4:

python scripts/eval/compare_v2_v3.py  # Adapt for v3 vs v4

4. Extract new pilot and pre-score:

python scripts/eval/extract_pilot_sample.py \
  scripts/eval/ood_generated_v4.csv \
  scripts/eval/ood_pilot_v4.csv 50 42

python scripts/eval/prescore_ood.py \
  scripts/eval/ood_pilot_v4.csv \
  scripts/eval/ood_pilot_v4_prescored.csv

Expected: Generic titles drop from 60% to ~30%
"""

print(__doc__)
