"""
Script 6: Generate Training Data for Seq2Seq Task Generator
Tạo synthetic tasks từ requirements để train model generation

Dataset hiện tại chỉ có: text, type, priority, domain
Cần tạo: title, description, acceptance_criteria

Strategy:
1. Dùng rule-based + NLP để extract entities
2. Generate structured tasks với variation (không template cứng)
3. Save thành training corpus cho T5/BART
"""
import os
import sys
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple
import random
import spacy
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


class TaskTrainingDataGenerator:
    """Generate training data for seq2seq task generator"""
    
    def __init__(self):
        # Load spaCy for NER and parsing
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✓ Loaded spaCy model")
        except OSError:
            print("⚠️  spaCy model not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Define variation patterns
        self.title_patterns = self._init_title_patterns()
        self.desc_patterns = self._init_desc_patterns()
        self.ac_patterns = self._init_ac_patterns()
    
    def _init_title_patterns(self) -> Dict[str, List[str]]:
        """Title generation patterns by type"""
        return {
            'functional': [
                'Implement {action} for {object}',
                'Build {object} {action} feature',
                'Create {action} capability for {object}',
                'Develop {object} {action} functionality',
                'Add {action} to {object}',
            ],
            'security': [
                'Secure {object} against {threat}',
                'Implement {action} security for {object}',
                'Add {object} protection',
                'Enforce {action} on {object}',
                'Harden {object} security',
            ],
            'interface': [
                'Design {object} interface',
                'Create UI for {action}',
                'Build {object} user interface',
                'Implement {action} screen',
                'Develop {object} UI components',
            ],
            'data': [
                'Implement {object} data management',
                'Setup {object} data storage',
                'Create {object} data model',
                'Build {object} database schema',
                'Design {object} data structure',
            ],
            'performance': [
                'Optimize {object} {action}',
                'Improve {object} performance',
                'Speed up {action}',
                'Reduce {object} latency',
                'Scale {object} for high load',
            ],
            'integration': [
                'Integrate {object} with {target}',
                'Connect {object} to {target}',
                'Setup {object} integration',
                'Build {object} connector',
                'Implement {object} API integration',
            ]
        }
    
    def _init_desc_patterns(self) -> Dict[str, List[str]]:
        """Description generation patterns"""
        return {
            'functional': [
                'The system needs to {action} {object} to support {purpose}. Users should be able to {action} {object} through the interface.',
                'We need to implement functionality that allows users to {action} {object}. This feature will enable {purpose}.',
                'The application must provide capability to {action} {object} for {purpose}. This includes proper validation and error handling.',
                'Implement feature to {action} {object} in order to {purpose}. The system should handle both success and failure scenarios.',
            ],
            'security': [
                'Security measures must be implemented to protect {object} from unauthorized {action}. This includes encryption, access control, and audit logging.',
                'The system needs to secure {object} against {threat}. Implement authentication, authorization, and data protection.',
                'Add security controls to prevent unauthorized {action} of {object}. Include role-based access and encryption.',
                'Implement comprehensive security for {object} including {action} protection and audit trails.',
            ],
            'interface': [
                'Design and implement user interface for {action}. The UI should be intuitive, responsive, and accessible.',
                'Create interface components for {object} management. Include proper form validation and user feedback.',
                'Build UI screens for {action} with focus on usability and user experience.',
                'Develop user interface that allows users to {action} {object} easily.',
            ],
            'data': [
                'Setup data storage and management for {object}. Design database schema with proper relationships and constraints.',
                'Implement data model for {object} with CRUD operations and validation.',
                'Create database structure to support {object} storage with indexing and optimization.',
                'Build data layer for {object} including persistence and retrieval operations.',
            ],
            'performance': [
                'Optimize {object} to improve {action} performance. Implement caching, indexing, and efficient algorithms.',
                'Improve system performance for {action} operations. Reduce latency and resource consumption.',
                'Scale {object} to handle high load. Implement performance optimizations and monitoring.',
                'Enhance {object} efficiency through optimization and better resource management.',
            ],
            'integration': [
                'Setup integration between {object} and {target}. Implement API calls, data mapping, and error handling.',
                'Connect {object} with external system {target}. Handle authentication, data transformation, and failures.',
                'Build integration layer for {object} to communicate with {target}.',
                'Implement connector to integrate {object} with {target} system.',
            ]
        }
    
    def _init_ac_patterns(self) -> Dict[str, List[List[str]]]:
        """Acceptance criteria patterns by type"""
        return {
            'functional': [
                [
                    'User can {action} {object} successfully through the interface',
                    'System validates all input data before processing',
                    'Appropriate success/error messages are displayed',
                    'All edge cases and error conditions are handled properly',
                    'Feature works correctly across all supported browsers/devices',
                ],
                [
                    '{Object} can be {action}ed with valid input data',
                    'Invalid inputs are rejected with clear error messages',
                    'System provides confirmation after successful {action}',
                    'Feature is accessible to authorized users only',
                    'Performance meets requirements (< 2s response time)',
                ]
            ],
            'security': [
                [
                    'Only authorized users can {action} {object}',
                    'All sensitive data is encrypted in transit and at rest',
                    'Audit logs capture all {action} operations',
                    'Role-based access control is enforced',
                    'Security vulnerabilities are addressed and tested',
                ],
                [
                    'Authentication is required before {action}',
                    'Access control prevents unauthorized operations',
                    'Encryption protects {object} data',
                    'Security events are logged and monitored',
                    'Compliance requirements are met',
                ]
            ],
            'interface': [
                [
                    'UI displays {object} information clearly and accurately',
                    'Form validation provides immediate user feedback',
                    'Interface is responsive across desktop and mobile',
                    'Accessibility standards (WCAG 2.1) are met',
                    'Loading states and error messages are user-friendly',
                ],
                [
                    'User can navigate the interface intuitively',
                    'Visual design follows style guide and brand guidelines',
                    'Interactive elements have clear affordances',
                    'Interface performs well with large datasets',
                    'Help text and tooltips guide users',
                ]
            ],
            'data': [
                [
                    'Database schema supports {object} storage requirements',
                    'CRUD operations work correctly for {object}',
                    'Data integrity constraints are enforced',
                    'Indexes optimize query performance',
                    'Backup and recovery procedures are in place',
                ],
                [
                    'Data model supports all required {object} attributes',
                    'Relationships between entities are properly defined',
                    'Data validation prevents invalid states',
                    'Migration scripts are tested and reversible',
                    'Performance testing shows acceptable query times',
                ]
            ],
            'performance': [
                [
                    'Response time is under 2 seconds for typical operations',
                    'System handles 1000 concurrent users without degradation',
                    'Resource usage (CPU, memory) is optimized',
                    'Caching reduces database load by 50%+',
                    'Load testing confirms scalability targets',
                ],
                [
                    'Page load time meets performance budget',
                    'API endpoints respond within SLA requirements',
                    'Database queries are optimized with proper indexes',
                    'Monitoring shows improved performance metrics',
                    'System scales horizontally as needed',
                ]
            ],
            'integration': [
                [
                    'API connection is established and authenticated',
                    'Data is correctly mapped between systems',
                    'Error handling covers integration failures',
                    'Retry logic handles temporary failures',
                    'Integration monitoring and logging are in place',
                ],
                [
                    'External system integration works end-to-end',
                    'Data synchronization maintains consistency',
                    'Integration handles rate limits appropriately',
                    'Fallback mechanisms handle system unavailability',
                    'Integration testing covers success and failure scenarios',
                ]
            ]
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from requirement text using spaCy"""
        doc = self.nlp(text.lower())
        
        entities = {
            'verbs': [],
            'nouns': [],
            'objects': [],
        }
        
        # Extract verbs (actions)
        for token in doc:
            if token.pos_ == 'VERB':
                entities['verbs'].append(token.lemma_)
        
        # Extract nouns (objects)
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN']:
                entities['nouns'].append(token.text)
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            entities['objects'].append(chunk.text)
        
        return entities
    
    def generate_task(
        self,
        requirement_text: str,
        req_type: str,
        priority: str,
        domain: str
    ) -> Dict:
        """Generate a task from requirement"""
        
        # Extract entities
        entities = self.extract_entities(requirement_text)
        
        # Select patterns
        title_pattern = random.choice(self.title_patterns.get(req_type, self.title_patterns['functional']))
        desc_pattern = random.choice(self.desc_patterns.get(req_type, self.desc_patterns['functional']))
        ac_list = random.choice(self.ac_patterns.get(req_type, self.ac_patterns['functional']))
        
        # Fill placeholders
        action = entities['verbs'][0] if entities['verbs'] else 'process'
        obj = entities['objects'][0] if entities['objects'] else 'data'
        purpose = f"{domain} operations"
        threat = "unauthorized access"
        target = "external system"
        
        # Generate components
        title = title_pattern.format(action=action, object=obj, threat=threat, target=target)
        description = desc_pattern.format(action=action, object=obj, purpose=purpose, threat=threat, target=target)
        
        # Generate 3-5 acceptance criteria with variation
        num_ac = random.randint(3, 5)
        acceptance_criteria = []
        for ac_pattern in ac_list[:num_ac]:
            ac = ac_pattern.format(action=action, object=obj.capitalize(), Object=obj.capitalize())
            acceptance_criteria.append(ac)
        
        task = {
            'source_requirement': requirement_text,
            'type': req_type,
            'priority': priority,
            'domain': domain,
            'title': title,
            'description': description,
            'acceptance_criteria': acceptance_criteria,
        }
        
        return task
    
    def generate_from_dataset(
        self,
        input_file: Path,
        output_file: Path,
        max_samples: int = None
    ):
        """Generate tasks from requirement dataset"""
        
        print(f"📂 Loading requirements from: {input_file}")
        df = pd.read_parquet(input_file)
        
        # Filter only requirements
        df = df[df['is_requirement'] == 1].copy()
        
        if max_samples:
            df = df.sample(n=min(max_samples, len(df)), random_state=42)
        
        print(f"   Processing {len(df):,} requirements")
        
        tasks = []
        for idx, row in df.iterrows():
            if idx % 10000 == 0 and idx > 0:
                print(f"   Processed {idx:,} / {len(df):,} ({idx/len(df)*100:.1f}%)")
            
            try:
                task = self.generate_task(
                    row['text'],
                    row['type'],
                    row['priority'],
                    row['domain']
                )
                tasks.append(task)
            except Exception as e:
                # Skip problematic rows
                continue
        
        print(f"\n✅ Generated {len(tasks):,} tasks")
        
        # Save as JSONL
        print(f"💾 Saving to: {output_file}")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            for task in tasks:
                f.write(json.dumps(task) + '\n')
        
        print(f"✅ Saved {len(tasks):,} tasks")
        
        # Save sample
        sample_file = output_file.parent / 'task_generation_samples.json'
        with open(sample_file, 'w') as f:
            json.dump(tasks[:100], f, indent=2)
        print(f"📝 Sample saved to: {sample_file}")
        
        return len(tasks)


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate task training data')
    parser.add_argument('--input', type=str, required=True,
                       help='Input parquet file with requirements')
    parser.add_argument('--output', type=str, required=True,
                       help='Output JSONL file for training')
    parser.add_argument('--max-samples', type=int, default=None,
                       help='Max samples to generate (default: all)')
    
    args = parser.parse_args()
    
    input_file = Path(args.input)
    output_file = Path(args.output)
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    generator = TaskTrainingDataGenerator()
    generator.generate_from_dataset(input_file, output_file, args.max_samples)
    
    print("\n✅ Task generation data created!")
    print("   Next steps:")
    print("   1. Review samples in task_generation_samples.json")
    print("   2. Use this data to train T5/BART model")
    print("   3. Or use as few-shot examples for better generation")


if __name__ == "__main__":
    main()
