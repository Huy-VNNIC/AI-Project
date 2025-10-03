"""
Module for advanced requirement analysis using machine learning to extract 
software specification details for effort estimation
"""

import re
import nltk
import numpy as np
import pandas as pd
import spacy
import joblib
import os
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK resources if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class MLRequirementAnalyzer:
    """
    Advanced requirement analyzer that uses machine learning to extract
    information needed for software effort estimation
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the ML-based requirement analyzer
        
        Args:
            model_path (str): Path to pre-trained models directory
        """
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(max_features=1000)
        
        # Initialize transformer models for advanced NLP tasks
        try:
            # For relevance classification
            self.relevance_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            self.relevance_model = AutoModel.from_pretrained("distilbert-base-uncased")
            
            # For requirement classification
            self.req_classifier = pipeline("zero-shot-classification")
            
            # For complexity assessment
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            
            # Named entity recognition for technical terms
            self.ner_pipeline = pipeline("ner")
        except Exception as e:
            print(f"Error loading transformer models: {e}")
            print("Falling back to traditional NLP methods")
            
        # Load pre-trained models if provided
        if model_path:
            try:
                self.relevance_classifier = joblib.load(os.path.join(model_path, 'relevance_model.pkl'))
                self.req_type_classifier = joblib.load(os.path.join(model_path, 'req_type_model.pkl'))
                self.complexity_model = joblib.load(os.path.join(model_path, 'complexity_model.pkl'))
                print("Loaded pre-trained models successfully")
            except Exception as e:
                print(f"Error loading pre-trained models: {e}")
                print("Models will be trained when needed")
    
    def train_relevance_model(self, data_paths):
        """
        Train a model to classify requirements as relevant or irrelevant
        
        Args:
            data_paths (list): Paths to datasets with labeled requirements
            
        Returns:
            model: Trained classifier model
        """
        # Collect training data from ARFF files
        X = []
        y = []
        
        for path in data_paths:
            if path.endswith('.arff'):
                # Process ARFF files
                with open(path, 'r') as f:
                    lines = f.readlines()
                
                data_section = False
                for line in lines:
                    if line.strip() == '@data':
                        data_section = True
                        continue
                    
                    if data_section and line.strip():
                        # Extract requirement and label
                        parts = line.strip().split('","')
                        if len(parts) >= 4:
                            requirement = parts[0].replace('"', '')
                            label = parts[3].replace('"', '')
                            
                            X.append(requirement)
                            y.append(1 if label == 'relevant' else 0)
            
            elif path.endswith('.csv'):
                # Process CSV files
                df = pd.read_csv(path)
                if 'Requirement' in df.columns and 'Class' in df.columns:
                    for _, row in df.iterrows():
                        X.append(row['Requirement'])
                        # For DOSSPRE datasets, consider all requirements relevant
                        # but with different classifications
                        y.append(1)  
        
        # Preprocess text data
        X_processed = [self.preprocess_text(text) for text in X]
        
        # Convert to TF-IDF features
        X_tfidf = self.vectorizer.fit_transform(X_processed)
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X_tfidf, y, test_size=0.2, random_state=42
        )
        
        # Train a Random Forest classifier
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = clf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        
        print(f"Relevance Model Accuracy: {accuracy:.4f}")
        print("Classification Report:")
        print(report)
        
        # Save model
        self.relevance_classifier = clf
        joblib.dump(clf, 'relevance_model.pkl')
        
        return clf
    
    def train_requirement_type_model(self, data_paths):
        """
        Train a model to classify requirements into different types
        
        Args:
            data_paths (list): Paths to datasets with labeled requirements
            
        Returns:
            model: Trained classifier model
        """
        # Collect training data from CSV files
        X = []
        y = []
        
        for path in data_paths:
            if path.endswith('.csv'):
                df = pd.read_csv(path)
                if 'Requirement' in df.columns and 'Class' in df.columns:
                    for _, row in df.iterrows():
                        X.append(row['Requirement'])
                        y.append(row['Class'])
        
        # Get unique classes
        classes = list(set(y))
        
        # Create label encoder
        label_map = {label: i for i, label in enumerate(classes)}
        y_encoded = [label_map[label] for label in y]
        
        # Preprocess text data
        X_processed = [self.preprocess_text(text) for text in X]
        
        # Convert to TF-IDF features
        X_tfidf = self.vectorizer.fit_transform(X_processed)
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X_tfidf, y_encoded, test_size=0.2, random_state=42
        )
        
        # Train a Random Forest classifier
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = clf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Requirement Type Model Accuracy: {accuracy:.4f}")
        
        # Save model and label map
        self.req_type_classifier = clf
        self.label_map = label_map
        self.inv_label_map = {v: k for k, v in label_map.items()}
        
        joblib.dump(clf, 'req_type_model.pkl')
        joblib.dump(label_map, 'label_map.pkl')
        
        return clf
    
    def preprocess_text(self, text):
        """
        Preprocess text for ML model input
        
        Args:
            text (str): Input text
            
        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize
        words = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        words = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words]
        
        return ' '.join(words)
    
    def extract_requirements(self, text):
        """
        Extract requirements from text using NLP techniques
        
        Args:
            text (str): Input requirements document
            
        Returns:
            list: List of extracted requirements with metadata
        """
        # Split text into sentences
        sentences = sent_tokenize(text)
        
        requirements = []
        for i, sentence in enumerate(sentences):
            # Skip very short sentences
            if len(sentence.split()) < 5:
                continue
                
            # Check if sentence is a requirement
            if hasattr(self, 'relevance_classifier'):
                # Use trained model if available
                sentence_processed = self.preprocess_text(sentence)
                sentence_vector = self.vectorizer.transform([sentence_processed])
                is_relevant = self.relevance_classifier.predict(sentence_vector)[0] == 1
            else:
                # Use rule-based fallback
                is_relevant = self._is_requirement_sentence(sentence)
            
            if is_relevant:
                # Classify requirement type
                if hasattr(self, 'req_type_classifier'):
                    # Use trained model if available
                    sentence_processed = self.preprocess_text(sentence)
                    sentence_vector = self.vectorizer.transform([sentence_processed])
                    type_id = self.req_type_classifier.predict(sentence_vector)[0]
                    req_type = self.inv_label_map[type_id]
                else:
                    # Use zero-shot classification with transformers
                    try:
                        result = self.req_classifier(
                            sentence, 
                            candidate_labels=["functional", "security", "performance", "usability", "interface", "data"]
                        )
                        req_type = result['labels'][0]
                    except:
                        # Fallback to rule-based classification
                        req_type = self._classify_requirement_rule_based(sentence)
                
                # Add to requirements list
                requirements.append({
                    'id': f'REQ-{i+1}',
                    'text': sentence,
                    'type': req_type,
                    'complexity': self._assess_complexity(sentence)
                })
        
        return requirements
    
    def _is_requirement_sentence(self, sentence):
        """
        Check if a sentence is likely to be a requirement using rule-based approach
        
        Args:
            sentence (str): Input sentence
            
        Returns:
            bool: True if the sentence is likely a requirement
        """
        sentence_lower = sentence.lower()
        
        # Check for requirement keywords
        requirement_indicators = [
            'shall', 'must', 'will', 'should', 'needs to', 'required to', 'has to',
            'can', 'allow', 'enable', 'provide', 'support', 'implement', 'develop'
        ]
        
        if any(indicator in sentence_lower for indicator in requirement_indicators):
            return True
            
        # Check for verb-noun structure using spaCy
        doc = nlp(sentence)
        has_verb = any(token.pos_ == "VERB" for token in doc)
        has_noun = any(token.pos_ == "NOUN" for token in doc)
        
        # Sentences with both verbs and nouns and at least 7 words are likely requirements
        if has_verb and has_noun and len(sentence.split()) >= 7:
            return True
            
        return False
    
    def _classify_requirement_rule_based(self, sentence):
        """
        Classify requirement type using rule-based approach
        
        Args:
            sentence (str): Input requirement sentence
            
        Returns:
            str: Requirement type
        """
        sentence_lower = sentence.lower()
        
        # Define keyword dictionaries for each requirement type
        type_keywords = {
            'functional': [
                'shall', 'must', 'will', 'function', 'feature', 'capability',
                'allow', 'enable', 'provide', 'perform', 'display', 'generate', 
                'create', 'update', 'delete', 'validate'
            ],
            'security': [
                'secure', 'authentication', 'authorization', 'encrypt', 'decrypt',
                'password', 'login', 'access control', 'confidential', 'integrity',
                'permission', 'protect', 'vulnerability'
            ],
            'performance': [
                'performance', 'speed', 'fast', 'efficient', 'response time',
                'throughput', 'latency', 'resource', 'memory', 'cpu', 'load',
                'concurrent', 'simultaneous'
            ],
            'usability': [
                'user-friendly', 'easy to use', 'intuitive', 'accessible',
                'usability', 'user interface', 'ux', 'ui', 'user experience',
                'learn', 'simple', 'clear', 'help', 'guide', 'tutorial'
            ],
            'interface': [
                'interface', 'api', 'ui', 'connect', 'integration', 'communicate',
                'interact', 'screen', 'form', 'dialog', 'menu', 'button', 'endpoint'
            ],
            'data': [
                'database', 'data', 'storage', 'record', 'file', 'format', 'schema',
                'query', 'table', 'document', 'collection', 'backup', 'archive'
            ]
        }
        
        # Count keywords for each type
        scores = {req_type: 0 for req_type in type_keywords.keys()}
        
        for req_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in sentence_lower:
                    scores[req_type] += 1
        
        # Return the type with the highest score
        max_score = 0
        best_type = 'functional'  # Default
        
        for req_type, score in scores.items():
            if score > max_score:
                max_score = score
                best_type = req_type
        
        return best_type
    
    def _assess_complexity(self, sentence):
        """
        Assess the complexity of a requirement
        
        Args:
            sentence (str): Input requirement sentence
            
        Returns:
            float: Complexity score (1.0-3.0)
        """
        # Try using sentiment analysis to gauge complexity
        try:
            result = self.sentiment_analyzer(sentence)
            # More negative sentiment often correlates with more complex requirements
            sentiment_score = result[0]['score']
            if result[0]['label'] == 'NEGATIVE':
                complexity_from_sentiment = 2.0 + sentiment_score
            else:
                complexity_from_sentiment = 2.0 - sentiment_score
        except:
            complexity_from_sentiment = 2.0  # Default medium complexity
        
        # Analyze sentence structure
        doc = nlp(sentence)
        
        # Count technical terms and entities
        technical_terms = len([token for token in doc if token.pos_ == "NOUN" and len(token.text) > 4])
        entities = len(doc.ents)
        
        # Count complex words (longer than 8 characters)
        complex_words = len([token for token in doc if len(token.text) > 8])
        
        # Sentence length factor (longer sentences tend to be more complex)
        length_factor = min(1.0, len(sentence.split()) / 30)
        
        # Calculate complexity score (1.0 - 3.0 range)
        structure_complexity = 1.0 + (0.1 * technical_terms) + (0.1 * entities) + (0.05 * complex_words) + length_factor
        structure_complexity = min(3.0, structure_complexity)
        
        # Combine sentiment-based and structure-based complexity
        complexity = (complexity_from_sentiment + structure_complexity) / 2
        
        return round(min(3.0, complexity), 1)
    
    def extract_features(self, text):
        """
        Extract features from requirements text for effort estimation
        
        Args:
            text (str): Input requirements document
            
        Returns:
            dict: Extracted features
        """
        # Extract requirements
        requirements = self.extract_requirements(text)
        
        # Basic metrics
        num_requirements = len(requirements)
        requirement_types = [req['type'] for req in requirements]
        requirement_complexities = [req['complexity'] for req in requirements]
        
        # Count requirements by type
        type_counts = {}
        for req_type in set(requirement_types):
            type_counts[f'{req_type}_reqs'] = requirement_types.count(req_type)
        
        # Calculate average complexity
        avg_complexity = sum(requirement_complexities) / max(1, len(requirement_complexities))
        
        # Extract entities and technical terms
        doc = nlp(text)
        entities = [ent.text for ent in doc.ents]
        num_entities = len(set(entities))
        
        # Detect technologies mentioned
        technology_keywords = [
            'java', 'python', 'javascript', 'typescript', 'c#', 'c++', 'go', 'rust', 'php',
            'ruby', 'swift', 'kotlin', 'flutter', 'react', 'angular', 'vue', 'node.js',
            'express', 'django', 'flask', 'spring', 'hibernate', 'asp.net', '.net',
            'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'redis', 'cassandra',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
            'html', 'css', 'bootstrap', 'tailwind', 'jquery', 'rest', 'graphql', 'soap',
            'microservices', 'serverless', 'blockchain', 'ai', 'ml', 'nlp', 'iot'
        ]
        
        technologies_mentioned = set()
        for tech in technology_keywords:
            if tech.lower() in text.lower():
                technologies_mentioned.add(tech)
        
        # Estimate project size
        size = self._estimate_project_size(text, requirements)
        
        # Combine all features
        features = {
            'num_requirements': num_requirements,
            'avg_complexity': avg_complexity,
            'size': size,
            'num_entities': num_entities,
            'num_technologies': len(technologies_mentioned),
            'technologies': list(technologies_mentioned)
        }
        
        # Add type counts
        features.update(type_counts)
        
        return features
    
    def _estimate_project_size(self, text, requirements):
        """
        Estimate project size based on requirements
        
        Args:
            text (str): Full requirements document
            requirements (list): Extracted requirements
            
        Returns:
            float: Estimated size in KLOC
        """
        # Look for explicit size mentions
        size_patterns = [
            r'(\d+)\s*(kloc|k loc|ksloc|k sloc)',
            r'(\d+)\s*thousand\s*(loc|lines|sloc)',
            r'(\d+)k\s*(loc|lines|sloc)',
            r'size\s*:\s*(\d+)\s*k'
        ]
        
        for pattern in size_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    if isinstance(matches[0], tuple):
                        size = float(matches[0][0])
                    else:
                        size = float(matches[0])
                    return size  # Already in KLOC
                except (ValueError, IndexError):
                    pass
        
        # If no explicit size, estimate based on requirements
        num_reqs = len(requirements)
        avg_complexity = sum(req['complexity'] for req in requirements) / max(1, len(requirements))
        
        # Formula: base size per requirement * number of requirements * complexity factor
        estimated_size = 0.05 * num_reqs * avg_complexity
        
        # Adjust based on requirement types
        req_types = [req['type'] for req in requirements]
        
        # Data and security requirements typically need more code
        data_security_factor = 1.0 + (0.2 * (req_types.count('data') + req_types.count('security'))) / max(1, num_reqs)
        
        return round(estimated_size * data_security_factor, 2)
    
    def extract_cocomo_parameters(self, text):
        """
        Extract COCOMO II model parameters from requirements text
        
        Args:
            text (str): Input requirements document
            
        Returns:
            dict: COCOMO II parameters
        """
        features = self.extract_features(text)
        
        # Map features to COCOMO II parameters
        cocomo_params = {
            'size': features['size'],  # KLOC
            'reliability': self._derive_reliability(text, features),
            'complexity': features['avg_complexity'] / 3.0,  # Scale to 0-1 range
            'documentation': self._derive_documentation_factor(text),
            'reuse': self._derive_reuse_factor(text)
        }
        
        # Environmental factors
        if 'security_reqs' in features and features['security_reqs'] > 0:
            cocomo_params['security_factor'] = 1.1
        else:
            cocomo_params['security_factor'] = 1.0
            
        if 'performance_reqs' in features and features['performance_reqs'] > 0:
            cocomo_params['time_constraint'] = 1.1
        else:
            cocomo_params['time_constraint'] = 1.0
            
        if 'interface_reqs' in features and features['interface_reqs'] > 0:
            cocomo_params['platform_volatility'] = 1.1
        else:
            cocomo_params['platform_volatility'] = 1.0
        
        # Personnel factors (default to nominal)
        cocomo_params['personnel_capability'] = 1.0
        cocomo_params['personnel_experience'] = 1.0
        cocomo_params['tool_experience'] = 1.0
        cocomo_params['language_experience'] = 1.0
        cocomo_params['team_cohesion'] = 1.0
        cocomo_params['process_maturity'] = 1.0
        
        return cocomo_params
    
    def _derive_reliability(self, text, features):
        """
        Derive reliability requirement factor from text
        
        Args:
            text (str): Requirements text
            features (dict): Extracted features
            
        Returns:
            float: Reliability factor (0.75-1.4)
        """
        reliability_keywords = [
            'reliability', 'stable', 'robust', 'failover', 'recovery',
            'high availability', 'fault tolerance', 'error handling',
            'backup', 'redundancy', 'critical', 'mission critical'
        ]
        
        reliability_score = 0
        for keyword in reliability_keywords:
            if keyword in text.lower():
                reliability_score += 1
        
        # Scale to COCOMO range (0.75 - 1.4)
        scaled_score = 0.75 + (reliability_score / 10) * 0.65
        return min(1.4, scaled_score)
    
    def _derive_documentation_factor(self, text):
        """
        Derive documentation requirements factor
        
        Args:
            text (str): Requirements text
            
        Returns:
            float: Documentation factor (0.8-1.2)
        """
        doc_keywords = [
            'documentation', 'document', 'manual', 'help', 'guide',
            'user manual', 'technical documentation', 'api documentation'
        ]
        
        doc_score = 0
        for keyword in doc_keywords:
            if keyword in text.lower():
                doc_score += 1
        
        # Scale to range (0.8 - 1.2)
        scaled_score = 0.8 + (doc_score / 8) * 0.4
        return min(1.2, scaled_score)
    
    def _derive_reuse_factor(self, text):
        """
        Derive code reuse factor
        
        Args:
            text (str): Requirements text
            
        Returns:
            float: Reuse factor (0.0-1.0)
        """
        reuse_keywords = [
            'reuse', 'library', 'framework', 'component', 'existing code',
            'third-party', 'open source', 'package', 'module', 'api'
        ]
        
        reuse_score = 0
        for keyword in reuse_keywords:
            if keyword in text.lower():
                reuse_score += 1
        
        # Scale to range (0.0 - 0.5)
        scaled_score = min(0.5, (reuse_score / 10) * 0.5)
        return scaled_score
    
    def extract_function_points_parameters(self, text):
        """
        Extract Function Points analysis parameters
        
        Args:
            text (str): Requirements text
            
        Returns:
            dict: Function Points parameters
        """
        # Extract requirements
        requirements = self.extract_requirements(text)
        
        # Count by type
        functional_reqs = [req for req in requirements if req['type'] == 'functional']
        interface_reqs = [req for req in requirements if req['type'] == 'interface']
        data_reqs = [req for req in requirements if req['type'] == 'data']
        
        # Estimate Function Point components
        num_functional = len(functional_reqs)
        
        # External Inputs (EI)
        inputs = max(1, int(num_functional * 0.3))
        
        # External Outputs (EO)
        outputs = max(1, int(num_functional * 0.25))
        
        # External Inquiries (EQ)
        queries = max(1, int(num_functional * 0.2))
        
        # Internal Logical Files (ILF)
        internal_files = max(1, len(data_reqs))
        
        # External Interface Files (EIF)
        external_interfaces = max(1, len(interface_reqs))
        
        # Complexity factor from overall requirements
        avg_complexity = sum(req['complexity'] for req in requirements) / max(1, len(requirements))
        complexity_factor = avg_complexity / 2.0  # Scale to 0.5-1.5 range
        
        # Function Point parameters
        fp_params = {
            'external_inputs': inputs,
            'external_outputs': outputs,
            'external_inquiries': queries,
            'internal_files': internal_files,
            'external_files': external_interfaces,
            'complexity_multiplier': complexity_factor
        }
        
        return fp_params
    
    def extract_use_case_points_parameters(self, text):
        """
        Extract Use Case Points analysis parameters
        
        Args:
            text (str): Requirements text
            
        Returns:
            dict: Use Case Points parameters
        """
        # Extract requirements and identify actors and use cases
        requirements = self.extract_requirements(text)
        
        # Identify actors from text using NER
        doc = nlp(text)
        actors = set()
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG"]:
                actors.add(ent.text.lower())
        
        # Add common system actors
        common_actors = ["user", "admin", "system", "customer", "manager", "employee"]
        for actor in common_actors:
            if actor in text.lower():
                actors.add(actor)
        
        # Classify actors by complexity
        simple_actors = 0
        average_actors = 0
        complex_actors = 0
        
        for actor in actors:
            # Simple actors typically interact through API
            if "api" in text.lower() or "service" in text.lower():
                simple_actors += 1
            # Complex actors are typically humans with complex UI
            elif actor in ["user", "admin", "customer", "manager", "employee"]:
                complex_actors += 1
            # Average actors are everything else
            else:
                average_actors += 1
        
        # Identify use cases from functional requirements
        functional_reqs = [req for req in requirements if req['type'] == 'functional']
        
        # Classify use cases by complexity based on requirement complexity
        simple_use_cases = 0
        average_use_cases = 0
        complex_use_cases = 0
        
        for req in functional_reqs:
            if req['complexity'] < 1.5:
                simple_use_cases += 1
            elif req['complexity'] < 2.5:
                average_use_cases += 1
            else:
                complex_use_cases += 1
        
        # Technical Complexity Factor (TCF)
        technical_factors = self._derive_technical_factors(text)
        
        # Environmental Complexity Factor (ECF)
        environmental_factors = self._derive_environmental_factors(text)
        
        # Use Case Points parameters
        ucp_params = {
            'simple_actors': simple_actors,
            'average_actors': average_actors,
            'complex_actors': complex_actors,
            'simple_use_cases': simple_use_cases,
            'average_use_cases': average_use_cases,
            'complex_use_cases': complex_use_cases,
            'technical_factors': technical_factors,
            'environmental_factors': environmental_factors
        }
        
        return ucp_params
    
    def _derive_technical_factors(self, text):
        """
        Derive technical complexity factors for Use Case Points
        
        Args:
            text (str): Requirements text
            
        Returns:
            float: Technical complexity factor
        """
        # Define technical factors and their weights
        technical_factors = {
            'distributed_system': 2.0,
            'performance': 1.0,
            'end_user_efficiency': 1.0,
            'complex_processing': 1.0,
            'reusable_code': 1.0,
            'easy_to_install': 0.5,
            'easy_to_use': 0.5,
            'portable': 2.0,
            'easy_to_change': 1.0,
            'concurrent': 1.0,
            'security': 1.0,
            'third_party_access': 1.0,
            'special_training': 1.0
        }
        
        # Keywords for each factor
        factor_keywords = {
            'distributed_system': ['distributed', 'client-server', 'multi-tier', 'cloud', 'microservices'],
            'performance': ['performance', 'fast', 'speed', 'efficient', 'response time', 'throughput'],
            'end_user_efficiency': ['user-friendly', 'intuitive', 'easy to use', 'efficiency'],
            'complex_processing': ['complex', 'algorithm', 'calculation', 'processing', 'analysis'],
            'reusable_code': ['reuse', 'component', 'module', 'library', 'framework'],
            'easy_to_install': ['install', 'deployment', 'setup', 'configuration'],
            'easy_to_use': ['usability', 'user experience', 'ux', 'interface'],
            'portable': ['portable', 'cross-platform', 'platform-independent', 'multiple platforms'],
            'easy_to_change': ['maintenance', 'change', 'update', 'modify', 'flexible'],
            'concurrent': ['concurrent', 'parallel', 'simultaneous', 'multi-user', 'multi-threaded'],
            'security': ['secure', 'security', 'authentication', 'authorization', 'encryption'],
            'third_party_access': ['third-party', 'external', 'api', 'integration'],
            'special_training': ['training', 'learn', 'skill', 'knowledge', 'expertise']
        }
        
        # Calculate factor values
        factor_values = {}
        text_lower = text.lower()
        
        for factor, keywords in factor_keywords.items():
            # Check for keywords in text
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            # Convert to 0-5 scale
            factor_values[factor] = min(5, score)
        
        # Calculate TCF using formula: 0.6 + (0.01 * Sum(weight * value))
        sum_weighted_factors = sum(technical_factors[factor] * factor_values.get(factor, 0) for factor in technical_factors)
        tcf = 0.6 + (0.01 * sum_weighted_factors)
        
        return tcf
    
    def _derive_environmental_factors(self, text):
        """
        Derive environmental factors for Use Case Points
        
        Args:
            text (str): Requirements text
            
        Returns:
            float: Environmental factor
        """
        # Define environmental factors and their weights
        environmental_factors = {
            'familiar_with_process': 1.5,
            'application_experience': 0.5,
            'oop_experience': 1.0,
            'lead_analyst_capability': 0.5,
            'motivation': 1.0,
            'stable_requirements': 2.0,
            'part_time_workers': -1.0,
            'difficult_language': -1.0
        }
        
        # Set default values (moderate experience/capability)
        factor_values = {
            'familiar_with_process': 3,
            'application_experience': 3,
            'oop_experience': 3,
            'lead_analyst_capability': 3,
            'motivation': 3,
            'stable_requirements': 3,
            'part_time_workers': 3,
            'difficult_language': 3
        }
        
        # Update based on text content
        text_lower = text.lower()
        
        # Check for indicators of experience level
        experience_keywords = ['experienced', 'skilled', 'expert', 'proficient']
        inexperience_keywords = ['inexperienced', 'new', 'learning', 'junior']
        
        if any(keyword in text_lower for keyword in experience_keywords):
            factor_values['application_experience'] = 4
            factor_values['oop_experience'] = 4
            factor_values['lead_analyst_capability'] = 4
        
        if any(keyword in text_lower for keyword in inexperience_keywords):
            factor_values['application_experience'] = 2
            factor_values['oop_experience'] = 2
            factor_values['lead_analyst_capability'] = 2
        
        # Check for indicators of stable requirements
        stable_keywords = ['stable', 'fixed', 'clear', 'well-defined']
        unstable_keywords = ['changing', 'evolving', 'unclear', 'undefined', 'fluid']
        
        if any(keyword in text_lower for keyword in stable_keywords):
            factor_values['stable_requirements'] = 4
        
        if any(keyword in text_lower for keyword in unstable_keywords):
            factor_values['stable_requirements'] = 2
        
        # Calculate EF using formula: 1.4 + (-0.03 * Sum(weight * value))
        sum_weighted_factors = sum(environmental_factors[factor] * factor_values.get(factor, 3) for factor in environmental_factors)
        ef = 1.4 + (-0.03 * sum_weighted_factors)
        
        return ef
    
    def extract_machine_learning_features(self, text):
        """
        Extract features for machine learning-based effort estimation
        
        Args:
            text (str): Requirements document
            
        Returns:
            dict: Features for ML models
        """
        # Basic features
        features = self.extract_features(text)
        
        # COCOMO parameters
        cocomo_params = self.extract_cocomo_parameters(text)
        
        # Function Point parameters
        fp_params = self.extract_function_points_parameters(text)
        
        # Use Case Point parameters
        ucp_params = self.extract_use_case_points_parameters(text)
        
        # Additional linguistic features
        doc = nlp(text)
        
        # Count verbs, nouns, adjectives (indicators of complexity)
        num_verbs = len([token for token in doc if token.pos_ == "VERB"])
        num_nouns = len([token for token in doc if token.pos_ == "NOUN"])
        num_adjectives = len([token for token in doc if token.pos_ == "ADJ"])
        
        # Readability metrics (more complex text often indicates more complex software)
        num_words = len([token for token in doc if not token.is_punct and not token.is_space])
        num_sentences = len(list(doc.sents))
        avg_sentence_length = num_words / max(1, num_sentences)
        
        # Combine all features for ML model
        ml_features = {
            # Basic metrics
            'num_requirements': features['num_requirements'],
            'avg_complexity': features['avg_complexity'],
            'num_entities': features['num_entities'],
            'num_technologies': features['num_technologies'],
            
            # COCOMO parameters
            'size_kloc': cocomo_params['size'],
            'reliability': cocomo_params['reliability'],
            'complexity': cocomo_params['complexity'],
            
            # Function Points metrics
            'external_inputs': fp_params['external_inputs'],
            'external_outputs': fp_params['external_outputs'],
            'external_inquiries': fp_params['external_inquiries'],
            'internal_files': fp_params['internal_files'],
            'external_files': fp_params['external_files'],
            'fp_complexity': fp_params['complexity_multiplier'],
            
            # Use Case Points metrics
            'simple_actors': ucp_params['simple_actors'],
            'average_actors': ucp_params['average_actors'],
            'complex_actors': ucp_params['complex_actors'],
            'simple_use_cases': ucp_params['simple_use_cases'],
            'average_use_cases': ucp_params['average_use_cases'],
            'complex_use_cases': ucp_params['complex_use_cases'],
            'technical_factors': ucp_params['technical_factors'],
            'environmental_factors': ucp_params['environmental_factors'],
            
            # Linguistic features
            'num_verbs': num_verbs,
            'num_nouns': num_nouns,
            'num_adjectives': num_adjectives,
            'avg_sentence_length': avg_sentence_length,
            'text_length': len(text)
        }
        
        return ml_features
    
    def analyze_requirements_document(self, text):
        """
        Comprehensive analysis of a requirements document
        
        Args:
            text (str): Requirements document
            
        Returns:
            dict: Complete analysis results
        """
        # Extract all features
        features = self.extract_features(text)
        cocomo_params = self.extract_cocomo_parameters(text)
        fp_params = self.extract_function_points_parameters(text)
        ucp_params = self.extract_use_case_points_parameters(text)
        ml_features = self.extract_machine_learning_features(text)
        
        # Extract requirements
        requirements = self.extract_requirements(text)
        
        # Create LOC model parameters based on cocomo_params
        loc_params = {
            'kloc': cocomo_params['size'],
            'complexity': cocomo_params['complexity'],
            'tech_score': 1.0 + (0.1 * len(features.get('technologies', []))/10),
            'experience': 1.0
        }
        
        # Comprehensive analysis results
        analysis = {
            'requirements': requirements,
            'summary': {
                'total_requirements': len(requirements),
                'by_type': {
                    'functional': sum(1 for req in requirements if req['type'] == 'functional'),
                    'security': sum(1 for req in requirements if req['type'] == 'security'),
                    'performance': sum(1 for req in requirements if req['type'] == 'performance'),
                    'usability': sum(1 for req in requirements if req['type'] == 'usability'),
                    'interface': sum(1 for req in requirements if req['type'] == 'interface'),
                    'data': sum(1 for req in requirements if req['type'] == 'data')
                },
                'avg_complexity': sum(req['complexity'] for req in requirements) / max(1, len(requirements)),
                'size_estimate_kloc': cocomo_params['size'],
                'technologies_detected': features.get('technologies', [])
            },
            'effort_estimation_parameters': {
                'cocomo': cocomo_params,
                'function_points': fp_params,
                'use_case_points': ucp_params,
                'loc_linear': loc_params.copy(),
                'loc_random_forest': loc_params.copy()
            },
            'ml_features': ml_features
        }
        
        return analysis
