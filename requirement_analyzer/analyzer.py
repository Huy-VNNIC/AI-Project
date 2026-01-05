"""
Module phân tích tài liệu requirements để trích xuất các đặc tả kỹ thuật
"""

import re
import nltk
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import joblib
import os

# Download NLTK resources if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Load spaCy model for NER - with fallback
nlp = None
try:
    nlp = spacy.load("en_core_web_sm")
    print("Loaded spaCy model: en_core_web_sm")
except OSError:
    try:
        # Try to download and load
        os.system("python -m spacy download en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
        print("Downloaded and loaded spaCy model: en_core_web_sm")
    except:
        # If all fails, create a basic tokenizer
        try:
            nlp = spacy.blank("en")
            print("Using blank English spaCy model (no NER)")
        except:
            nlp = None
            print("Warning: spaCy not available, using basic text processing")

def safe_nlp_process(text):
    """Safely process text with spaCy or return a mock object"""
    if nlp is not None:
        try:
            return nlp(text)
        except Exception as e:
            print(f"Warning: spaCy processing failed: {e}")
            # Fall back to mock object
            pass
    
    # Return a mock object with minimal functionality
    class MockDoc:
        def __init__(self, text):
            self.text = text
            self.ents = []  # No entities
            self._ = {}     # No custom attributes
        
        def __iter__(self):
            # Return word tokens
            try:
                return iter(word_tokenize(text))
            except:
                return iter(text.split())
    
    return MockDoc(text)

class RequirementAnalyzer:
    """
    Phân tích tài liệu requirements để trích xuất các thông tin cần thiết
    cho việc ước lượng nỗ lực phần mềm
    """
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(max_features=1000)
        
        # Add recursion depth tracking to prevent infinite loops
        self._recursion_depth = 0
        self._max_recursion_depth = 3
        
        # Cache for already computed features to avoid recursion
        self._features_cache = {}
        
        # Mở rộng từ điển các từ khóa cho các loại yêu cầu khác nhau
        self.requirement_keywords = {
            'functional': [
                'shall', 'must', 'will', 'should', 'function', 'feature', 'capability',
                'allow', 'enable', 'provide', 'support', 'perform', 'display', 'generate', 
                'create', 'update', 'delete', 'validate', 'authenticate', 'authorize',
                'user can', 'system will', 'application should', 'able to', 'implement'
            ],
            'non_functional': [
                'performance', 'reliability', 'usability', 'security', 'maintainability', 
                'scalability', 'availability', 'portability', 'efficiency', 'compatibility',
                'response time', 'throughput', 'user-friendly', 'secure', 'robust',
                'fast', 'easy to use', 'accessible', 'accurate', 'consistent',
                'compliant', 'interoperable', 'testable', 'modifiable', 'installable'
            ],
            'interface': [
                'interface', 'api', 'ui', 'user interface', 'web', 'mobile', 'connect', 'integration',
                'screen', 'page', 'form', 'dialog', 'menu', 'button', 'field', 'endpoint',
                'rest', 'soap', 'json', 'xml', 'http', 'url', 'uri', 'link', 'view',
                'dashboard', 'report', 'chart', 'graph', 'display', 'render', 'interact'
            ],
            'data': [
                'database', 'data', 'storage', 'record', 'file', 'format', 'schema', 'table',
                'query', 'sql', 'nosql', 'document', 'collection', 'entity', 'attribute',
                'primary key', 'foreign key', 'index', 'transaction', 'crud', 'store',
                'retrieve', 'backup', 'archive', 'encrypt', 'decrypt', 'field', 'column'
            ],
            'security': [
                'authentication', 'authorization', 'encrypt', 'secure', 'permission', 'access control',
                'login', 'logout', 'password', 'credential', 'token', 'jwt', 'oauth',
                'sso', 'role', 'privilege', 'permission', 'protect', 'firewall', 'ssl',
                'tls', 'https', 'certificate', 'vulnerability', 'threat', 'attack'
            ],
            'performance': [
                'response time', 'throughput', 'latency', 'speed', 'fast', 'performance', 'load',
                'concurrent', 'simultaneous', 'users', 'scalable', 'efficient', 'optimize',
                'benchmark', 'memory', 'cpu', 'resource', 'bottleneck', 'timeout', 'cache'
            ]
        }
        
        # Patterns để phát hiện các yêu cầu về kích thước và độ phức tạp
        self.size_patterns = [
            r'(\d+)\s*(kloc|loc|lines of code)',
            r'code\s*size\s*:\s*(\d+)',
            r'size\s*:\s*(\d+)',
            r'approximately\s*(\d+)\s*lines',
            r'about\s*(\d+)\s*(kloc|loc)',
            r'(\d+)[k]?\s*lines',
            r'(\d+)\s*thousand\s*lines',
            r'code\s*base\s*of\s*(\d+)'
        ]
        
        self.complexity_patterns = [
            r'(high|medium|low)\s*complexity',
            r'complexity\s*:\s*(high|medium|low)',
            r'(complex|simple|moderate)\s*system',
            r'(complex|simple|moderate)\s*implementation',
            r'(difficult|easy|moderate)\s*to\s*implement',
            r'(challenging|straightforward|intermediate)\s*development',
            r'(high|medium|low)\s*technical\s*difficulty',
            r'technically\s*(complex|simple|moderate)'
        ]
        
        # Patterns để phát hiện các yêu cầu về tài nguyên và ràng buộc
        self.resource_patterns = [
            r'(\d+)\s*developers',
            r'team\s*size\s*:\s*(\d+)',
            r'(\d+)\s*team\s*members',
            r'budget\s*:\s*(\d+)',
            r'(\d+)\s*developers?',
            r'team\s*of\s*(\d+)',
            r'development\s*team\s*of\s*(\d+)',
            r'(\d+)\s*person\s*team',
            r'(\d+)\s*programmers?',
            r'(\d+)\s*engineers?'
        ]
        
        self.time_constraint_patterns = [
            r'deadline\s*:\s*(\d+)\s*(months|weeks|days)',
            r'complete\s*within\s*(\d+)\s*(months|weeks|days)',
            r'time\s*frame\s*:\s*(\d+)\s*(months|weeks|days)',
            r'duration\s*:\s*(\d+)\s*(months|weeks|days)',
            r'finish\s*in\s*(\d+)\s*(months|weeks|days)',
            r'(\d+)\s*(month|week|day)\s*project',
            r'project\s*duration\s*of\s*(\d+)\s*(months|weeks|days)',
            r'timeline\s*of\s*(\d+)\s*(months|weeks|days)',
            r'deliver\s*in\s*(\d+)\s*(months|weeks|days)',
            r'project\s*will\s*last\s*(\d+)\s*(months|weeks|days)'
        ]
        
        # Danh sách các công nghệ/ngôn ngữ lập trình để phát hiện
        self.technologies = [
            'java', 'python', 'javascript', 'typescript', 'c#', 'c++', 'go', 'rust', 'php',
            'ruby', 'swift', 'kotlin', 'flutter', 'react', 'angular', 'vue', 'node.js',
            'express', 'django', 'flask', 'spring', 'hibernate', 'asp.net', '.net',
            'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'redis', 'cassandra',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
            'html', 'css', 'bootstrap', 'tailwind', 'jquery', 'rest', 'graphql', 'soap',
            'microservices', 'serverless', 'blockchain', 'ai', 'ml', 'nlp', 'iot'
        ]
        
        # Keywords để phân tích mức độ ưu tiên và quan trọng
        self.priority_keywords = {
            'critical': [
                'critical', 'must have', 'essential', 'mandatory', 'required', 'vital', 
                'crucial', 'urgent', 'emergency', 'high priority', 'mission critical',
                'core', 'fundamental', 'baseline', 'minimum viable', 'mvp',
                'cannot work without', 'system failure', 'blocking', 'showstopper',
                'quan trọng nhất', 'bắt buộc', 'thiết yếu', 'cốt lõi', 'cấp thiết'
            ],
            'high': [
                'important', 'high', 'priority', 'significant', 'major', 'key',
                'primary', 'main', 'principal', 'substantial', 'considerable',
                'should have', 'strongly recommended', 'highly desirable',
                'business critical', 'customer facing', 'revenue impact',
                'quan trọng', 'ưu tiên cao', 'chính', 'đáng kể'
            ],
            'medium': [
                'moderate', 'medium', 'normal', 'standard', 'average', 'typical',
                'could have', 'nice to have', 'useful', 'beneficial', 'helpful',
                'enhancement', 'improvement', 'optimization', 'convenience',
                'trung bình', 'bình thường', 'hữu ích', 'cải tiến'
            ],
            'low': [
                'low', 'minor', 'optional', 'future', 'later', 'eventual', 'wish list',
                'would be nice', 'if time allows', 'bonus', 'extra', 'additional',
                'cosmetic', 'polish', 'refinement', 'luxury',
                'thấp', 'tùy chọn', 'sau này', 'bổ sung'
            ]
        }
        
        # Keywords để phân tích tác động nghiệp vụ
        self.business_impact_keywords = {
            'high_impact': [
                'revenue', 'profit', 'cost saving', 'efficiency', 'productivity',
                'customer satisfaction', 'user experience', 'competitive advantage',
                'market share', 'business growth', 'roi', 'return on investment',
                'compliance', 'regulation', 'legal requirement', 'audit',
                'doanh thu', 'lợi nhuận', 'hiệu quả', 'khách hàng', 'cạnh tranh'
            ],
            'medium_impact': [
                'process improvement', 'workflow', 'automation', 'integration',
                'reporting', 'analytics', 'monitoring', 'maintenance',
                'scalability', 'performance', 'reliability', 'availability',
                'cải tiến quy trình', 'tự động hóa', 'báo cáo', 'hiệu suất'
            ],
            'low_impact': [
                'documentation', 'training', 'user interface', 'convenience',
                'aesthetic', 'branding', 'styling', 'layout', 'design',
                'tài liệu', 'đào tạo', 'giao diện', 'thẩm mỹ', 'thiết kế'
            ]
        }
        
        # Keywords để phân tích độ phức tạp kỹ thuật
        self.technical_complexity_keywords = {
            'high_complexity': [
                'machine learning', 'artificial intelligence', 'algorithm', 'optimization',
                'real-time', 'distributed', 'microservices', 'blockchain', 'encryption',
                'high availability', 'fault tolerance', 'load balancing', 'clustering',
                'big data', 'data mining', 'analytics', 'integration', 'migration',
                'thuật toán', 'học máy', 'trí tuệ nhân tạo', 'thời gian thực'
            ],
            'medium_complexity': [
                'database', 'api', 'web service', 'authentication', 'authorization',
                'notification', 'email', 'file upload', 'search', 'filtering',
                'crud', 'form validation', 'data validation', 'reporting',
                'cơ sở dữ liệu', 'dịch vụ web', 'xác thực', 'tìm kiếm'
            ],
            'low_complexity': [
                'display', 'show', 'list', 'view', 'static', 'simple form',
                'text input', 'dropdown', 'checkbox', 'radio button', 'link',
                'navigation', 'menu', 'basic ui', 'layout', 'styling',
                'hiển thị', 'danh sách', 'xem', 'đơn giản', 'giao diện cơ bản'
            ]
        }
    
    def _safe_execute_with_recursion_check(self, func, text, default_value, cache_key=None):
        """
        Safely execute a function with recursion depth tracking and caching.
        """
        # Check cache first
        if cache_key and cache_key in self._features_cache:
            return self._features_cache[cache_key]
        
        # Check recursion depth
        if self._recursion_depth >= self._max_recursion_depth:
            print(f"Maximum recursion depth reached, returning default value")
            return default_value
        
        try:
            self._recursion_depth += 1
            result = func(text)
            
            # Cache result
            if cache_key:
                self._features_cache[cache_key] = result
                
            return result
        except Exception as e:
            print(f"Error in function: {e}")
            return default_value
        finally:
            self._recursion_depth -= 1
    
    def preprocess_text(self, text):
        """
        Tiền xử lý văn bản: Chuyển thành chữ thường, xóa ký tự đặc biệt,
        loại bỏ stopwords, lemmatization
        """
        # Chuyển thành chữ thường
        text = text.lower()
        
        # Xóa ký tự đặc biệt
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize
        words = word_tokenize(text)
        
        # Loại bỏ stopwords và lemmatization
        words = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words]
        
        return ' '.join(words)
    
    def extract_requirements(self, text):
        """
        Trích xuất các yêu cầu từ văn bản
        """
        # Phân đoạn văn bản thành các câu
        sentences = sent_tokenize(text)
        
        requirements = []
        for i, sentence in enumerate(sentences):
            # Kiểm tra xem câu có chứa các từ khóa yêu cầu không
            if any(keyword in sentence.lower() for keyword in 
                   ['shall', 'must', 'will', 'should', 'needs to', 'required to', 'has to',
                   'feature', 'function', 'ability', 'capability', 'can', 'allow', 'enable',
                   'provide', 'support', 'implement', 'develop', 'create', 'build', 'design']):
                
                # Phân tích đầy đủ requirement
                priority = self._analyze_priority(sentence)
                business_impact = self._analyze_business_impact(sentence)
                technical_complexity = self._analyze_technical_complexity(sentence)
                score = self._calculate_requirement_score(priority, business_impact, technical_complexity)
                
                requirements.append({
                    'id': f'REQ-{i+1}',
                    'text': sentence,
                    'type': self._classify_requirement(sentence),
                    'priority': priority,
                    'business_impact': business_impact,
                    'technical_complexity': technical_complexity,
                    'score': score
                })
            elif len(sentence.split()) > 5 and self._contains_verb_noun_pair(sentence):
                # Phát hiện câu có cấu trúc động từ-danh từ có thể là yêu cầu
                priority = self._analyze_priority(sentence)
                business_impact = self._analyze_business_impact(sentence)
                technical_complexity = self._analyze_technical_complexity(sentence)
                score = self._calculate_requirement_score(priority, business_impact, technical_complexity)
                
                requirements.append({
                    'id': f'REQ-{i+1}',
                    'text': sentence,
                    'type': self._classify_requirement(sentence),
                    'priority': priority,
                    'business_impact': business_impact,
                    'technical_complexity': technical_complexity,
                    'score': score
                })
        
        # Nếu không tìm thấy yêu cầu nào, thử phương pháp khác
        if not requirements and len(sentences) > 0:
            # Xử lý văn bản không theo cấu trúc truyền thống
            for i, sentence in enumerate(sentences):
                if len(sentence.split()) > 8:  # Câu đủ dài
                    doc = safe_nlp_process(sentence)
                    # Kiểm tra xem câu có chứa động từ hành động
                    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
                    if any(v in ['develop', 'create', 'build', 'implement', 'design', 'add', 'make', 
                               'provide', 'enable', 'support', 'allow'] for v in verbs):
                        
                        priority = self._analyze_priority(sentence)
                        business_impact = self._analyze_business_impact(sentence)
                        technical_complexity = self._analyze_technical_complexity(sentence)
                        score = self._calculate_requirement_score(priority, business_impact, technical_complexity)
                        
                        requirements.append({
                            'id': f'REQ-{i+1}',
                            'text': sentence,
                            'type': self._classify_requirement(sentence),
                            'priority': priority,
                            'business_impact': business_impact,
                            'technical_complexity': technical_complexity,
                            'score': score
                        })
        
        # Nếu vẫn không tìm thấy, coi mỗi câu là một yêu cầu
        if not requirements and len(sentences) > 0:
            for i, sentence in enumerate(sentences):
                if len(sentence.split()) > 5:  # Chỉ lấy câu có ý nghĩa
                    priority = self._analyze_priority(sentence)
                    business_impact = self._analyze_business_impact(sentence)
                    technical_complexity = self._analyze_technical_complexity(sentence)
                    score = self._calculate_requirement_score(priority, business_impact, technical_complexity)
                    
                    requirements.append({
                        'id': f'REQ-{i+1}',
                        'text': sentence,
                        'type': 'general',
                        'priority': priority,
                        'business_impact': business_impact,
                        'technical_complexity': technical_complexity,
                        'score': score
                    })
        
        # Sắp xếp requirements theo độ ưu tiên và điểm số
        requirements.sort(key=lambda x: (
            {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x.get('priority', 'medium'), 2),
            x.get('score', 0)
        ), reverse=True)
        
        return requirements
    
    def _contains_verb_noun_pair(self, sentence):
        """Kiểm tra xem câu có chứa cặp động từ-danh từ không"""
        doc = safe_nlp_process(sentence)
        has_verb = False
        has_noun = False
        
        for token in doc:
            if token.pos_ == "VERB":
                has_verb = True
            if token.pos_ == "NOUN" or token.pos_ == "PROPN":
                has_noun = True
                
        return has_verb and has_noun

    def _analyze_priority(self, requirement):
        """
        Phân tích mức độ ưu tiên của requirement
        """
        req_lower = requirement.lower()
        priority_scores = {}
        
        # Tính điểm cho từng mức độ ưu tiên
        for priority_level, keywords in self.priority_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in req_lower:
                    # Điểm cao hơn cho từ khóa dài hơn (cụ thể hơn)
                    score += len(keyword.split()) * 2
            priority_scores[priority_level] = score
        
        # Phân tích thêm dựa trên cấu trúc câu
        if any(word in req_lower for word in ['shall', 'must', 'required']):
            priority_scores['critical'] += 3
        elif any(word in req_lower for word in ['should', 'ought to']):
            priority_scores['high'] += 2
        elif any(word in req_lower for word in ['may', 'could', 'might']):
            priority_scores['medium'] += 1
            
        # Tìm mức độ ưu tiên cao nhất
        if not any(priority_scores.values()):
            return 'medium'  # Mặc định
            
        return max(priority_scores.items(), key=lambda x: x[1])[0]
    
    def _analyze_business_impact(self, requirement):
        """
        Phân tích tác động nghiệp vụ của requirement
        """
        req_lower = requirement.lower()
        impact_scores = {}
        
        for impact_level, keywords in self.business_impact_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in req_lower:
                    score += len(keyword.split())
            impact_scores[impact_level] = score
            
        if not any(impact_scores.values()):
            return 'medium_impact'
            
        return max(impact_scores.items(), key=lambda x: x[1])[0]
    
    def _analyze_technical_complexity(self, requirement):
        """
        Phân tích độ phức tạp kỹ thuật của requirement
        """
        req_lower = requirement.lower()
        complexity_scores = {}
        
        for complexity_level, keywords in self.technical_complexity_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in req_lower:
                    score += len(keyword.split())
            complexity_scores[complexity_level] = score
            
        if not any(complexity_scores.values()):
            return 'medium_complexity'
            
        return max(complexity_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_requirement_score(self, priority, business_impact, technical_complexity):
        """
        Tính điểm tổng hợp cho requirement dựa trên các yếu tố
        """
        priority_weights = {
            'critical': 10,
            'high': 7,
            'medium': 4,
            'low': 1
        }
        
        impact_weights = {
            'high_impact': 8,
            'medium_impact': 5,
            'low_impact': 2
        }
        
        complexity_weights = {
            'high_complexity': 8,
            'medium_complexity': 5,
            'low_complexity': 2
        }
        
        total_score = (
            priority_weights.get(priority, 4) * 0.4 +
            impact_weights.get(business_impact, 5) * 0.35 +
            complexity_weights.get(technical_complexity, 5) * 0.25
        )
        
        return round(total_score, 2)

    def _classify_requirement(self, requirement):
        """
        Phân loại yêu cầu thành các loại khác nhau
        """
        requirement_lower = requirement.lower()
        
        # Kiểm tra các từ khóa trong requirement
        max_score = 0
        best_type = 'general'
        
        for req_type, keywords in self.requirement_keywords.items():
            score = sum(1 for keyword in keywords if keyword in requirement_lower)
            if score > max_score:
                max_score = score
                best_type = req_type
        
        # Thêm phân tích ngữ nghĩa
        doc = safe_nlp_process(requirement)
        
        # Phát hiện yêu cầu bảo mật
        security_terms = ['secure', 'security', 'protect', 'safe', 'encrypt', 'authorization', 'authentication',
                         'login', 'password', 'bảo mật', 'đăng nhập', 'mật khẩu', 'an toàn']
        if any(term in requirement_lower for term in security_terms):
            if max_score < 2 or best_type == 'general':
                best_type = 'security'
        
        # Phát hiện yêu cầu giao diện
        interface_terms = ['interface', 'ui', 'screen', 'display', 'view', 'button', 'form', 'menu',
                         'giao diện', 'màn hình', 'hiển thị', 'nút', 'biểu mẫu', 'đẹp']
        if any(term in requirement_lower for term in interface_terms):
            if max_score < 2 or best_type == 'general':
                best_type = 'interface'
        
        # Phát hiện yêu cầu dữ liệu
        data_terms = ['database', 'data', 'storage', 'store', 'save', 'retrieve', 'record',
                     'cơ sở dữ liệu', 'dữ liệu', 'lưu trữ', 'lưu', 'truy xuất']
        if any(term in requirement_lower for term in data_terms):
            if max_score < 2 or best_type == 'general':
                best_type = 'data'
        
        # Phát hiện yêu cầu hiệu suất
        performance_terms = ['fast', 'performance', 'quick', 'efficient', 'responsive', 'real-time', 'latency',
                           'nhanh', 'hiệu suất', 'phản hồi', 'thời gian thực']
        if any(term in requirement_lower for term in performance_terms):
            if max_score < 2 or best_type == 'general':
                best_type = 'performance'
        
        # Nếu không tìm thấy loại cụ thể và có hành động, coi như là yêu cầu chức năng
        if best_type == 'general':
            action_terms = ['create', 'update', 'delete', 'view', 'display', 'generate', 'process', 'handle', 'manage',
                          'tạo', 'cập nhật', 'xóa', 'xem', 'hiển thị', 'tạo ra', 'xử lý', 'quản lý']
            if any(term in requirement_lower for term in action_terms):
                best_type = 'functional'
        
        return best_type
    
    def extract_loc_parameters(self, text):
        """
        Trích xuất các tham số liên quan đến LOC từ văn bản
        
        Args:
            text (str): Văn bản cần phân tích
            
        Returns:
            dict: Các tham số LOC được trích xuất
        """
        params = {}
        text_lower = text.lower()
        
        # Tìm giá trị KLOC/LOC
        loc_found = False
        for pattern in self.size_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                loc_found = True
                for match in matches:
                    if isinstance(match, tuple):
                        size = match[0]
                        unit = match[1] if len(match) > 1 else ""
                    else:
                        size = match
                        unit = ""
                        
                    try:
                        size_value = float(size)
                        # Chuyển đổi đơn vị
                        if "k" in unit or "thousand" in text_lower:
                            params['kloc'] = size_value
                        else:
                            params['loc'] = size_value * 1000 if size_value < 100 else size_value
                            params['kloc'] = params['loc'] / 1000
                    except:
                        continue
                        
                break  # Dừng sau khi tìm thấy giá trị đầu tiên
        
        # Nếu không tìm thấy LOC rõ ràng, ước lượng từ mô tả dự án
        if not loc_found:
            # Ước lượng dựa trên độ dài văn bản và số lượng yêu cầu
            requirements = self.extract_requirements(text)
            req_count = len(requirements)
            
            # Dự án nhỏ (1-5 kloc), trung bình (5-15 kloc), lớn (15+ kloc)
            if req_count < 5:
                params['kloc'] = 3.0  # Dự án nhỏ
            elif req_count < 15:
                params['kloc'] = 8.0  # Dự án trung bình
            else:
                params['kloc'] = 15.0 + (req_count - 15) * 0.5  # Dự án lớn
            
            # Điều chỉnh dựa trên phát hiện công nghệ và độ phức tạp
            tech_count = 0
            for tech in self.technologies:
                if tech.lower() in text_lower:
                    tech_count += 1
                    
            if tech_count > 5:
                params['kloc'] *= 1.2  # Nhiều công nghệ = dự án phức tạp hơn
        
        # Tìm mức độ phức tạp
        complexity = 1.0  # Mặc định: trung bình
        for pattern in self.complexity_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        comp_level = match[0].lower()
                    else:
                        comp_level = match.lower()
                    
                    if any(term in comp_level for term in ['high', 'complex', 'difficult', 'challenging']):
                        complexity = 1.5  # Cao
                    elif any(term in comp_level for term in ['low', 'simple', 'easy', 'straightforward']):
                        complexity = 0.8  # Thấp
                        
                break
                
        params['complexity'] = complexity
        
        # Tìm số lượng developers
        for pattern in self.resource_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                for match in matches:
                    try:
                        if isinstance(match, tuple):
                            dev_count = int(match[0])
                        else:
                            dev_count = int(match)
                        params['developers'] = dev_count
                    except:
                        continue
                break
        
        # Nếu không có thông tin về developers, ước lượng từ KLOC
        if 'developers' not in params and 'kloc' in params:
            kloc = params['kloc']
            if kloc < 5:
                params['developers'] = 3
            elif kloc < 10:
                params['developers'] = 5
            else:
                params['developers'] = 8 + int(kloc / 10)
        
        # Phát hiện kinh nghiệm đội ngũ
        experience_terms = {
            'high': ['experienced', 'expert', 'senior', 'proficient', 'skilled', 'veteran', 'kinh nghiệm cao'],
            'low': ['junior', 'new', 'inexperienced', 'learning', 'trainee', 'beginner', 'intern', 'mới', 'ít kinh nghiệm']
        }
        
        experience = 1.0  # Mặc định: trung bình
        for level, terms in experience_terms.items():
            if any(term in text_lower for term in terms):
                if level == 'high':
                    experience = 1.3
                else:
                    experience = 0.7
                break
                
        params['experience'] = experience
        
        # Phát hiện điểm số công nghệ
        tech_score = 1.0  # Mặc định: trung bình
        tech_mentions = 0
        modern_techs = ['cloud', 'microservices', 'container', 'serverless', 'devops', 'ci/cd', 'machine learning',
                      'artificial intelligence', 'blockchain', 'iot', 'big data']
                      
        for tech in modern_techs:
            if tech in text_lower:
                tech_mentions += 1
                
        if tech_mentions >= 3:
            tech_score = 1.3  # Cao
        elif tech_mentions == 0:
            tech_score = 0.8  # Thấp
            
        params['tech_score'] = tech_score
        
        return params
    
    def extract_features(self, text):
        """
        Trích xuất các đặc trưng từ văn bản để sử dụng cho mô hình ước lượng
        """
        # Use caching to prevent recursion
        cache_key = f"extract_features_{hash(text)}"
        if cache_key in self._features_cache:
            return self._features_cache[cache_key]
            
        # Check recursion depth
        if self._recursion_depth >= self._max_recursion_depth:
            print("Maximum recursion depth reached in extract_features, returning default values")
            return {
                'complexity': 1.0,
                'developers': 3,
                'functional_reqs': 5,
                'non_functional_reqs': 3,
                'num_requirements': 8,
                'size': 5.0,
                'reliability': 1.0,
                'has_performance_requirements': False,
                'has_interface_requirements': False,
                'tech_score': 1.0
            }
        
        try:
            self._recursion_depth += 1
            
            preprocessed_text = self.preprocess_text(text)
            doc = safe_nlp_process(text)
            
            # Simple requirement counting without calling extract_requirements to avoid recursion
            functional_keywords = ['shall', 'must', 'will', 'should', 'function', 'feature']
            non_functional_keywords = ['performance', 'security', 'usability', 'reliability']
            
            functional_reqs = sum(1 for keyword in functional_keywords if keyword in text.lower())
            non_functional_reqs = sum(1 for keyword in non_functional_keywords if keyword in text.lower())
            num_requirements = max(3, functional_reqs + non_functional_reqs)
            
            # Đếm số thực thể được đề cập
            entities = []
            try:
                entities = [ent.text for ent in doc.ents]
            except:
                entities = []
            num_entities = len(set(entities)) if entities else 3  # Loại bỏ trùng lặp
        
            # Phát hiện các công nghệ được đề cập
            technologies_mentioned = set()
            for tech in self.technologies:
                if tech.lower() in text.lower():
                    technologies_mentioned.add(tech)
            num_technologies = len(technologies_mentioned)
            
            # Tìm các con số về kích thước, độ phức tạp
            size_matches = []
            for pattern in self.size_patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    size_matches.extend(matches)
            
            # Ước tính kích thước từ các con số tìm được
            size = 0
            if size_matches:
                # Lấy số đầu tiên tìm được
                size_str = size_matches[0]
                if isinstance(size_str, tuple):
                    size_str = size_str[0]
                try:
                    size = float(size_str)
                    # Kiểm tra nếu là KLOC hay LOC
                    if any(pattern in text.lower() for pattern in ['kloc', 'thousand', 'k lines']):
                        pass  # Giữ nguyên vì đã là KLOC
                    elif any(pattern in text.lower() for pattern in ['loc', 'lines']):
                        size = size / 1000  # Chuyển LOC sang KLOC
                except:
                    size = 0
            
            # Ước tính độ phức tạp
            complexity = 1.0  # Mặc định là trung bình
            for pattern in self.complexity_patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    complexity_str = matches[0]
                    if isinstance(complexity_str, tuple):
                        complexity_str = complexity_str[0]
                    
                    if complexity_str in ['high', 'complex', 'difficult', 'challenging']:
                        complexity = 1.3
                        break
                    elif complexity_str in ['medium', 'moderate', 'intermediate']:
                        complexity = 1.0
                        break
                    elif complexity_str in ['low', 'simple', 'easy', 'straightforward']:
                        complexity = 0.7
                        break
            
            # Phân tích độ phức tạp dựa trên cấu trúc văn bản (simple assessment)
            word_count = len(text.split())
            if word_count > 1000:
                text_complexity = 1.2
            elif word_count > 500:
                text_complexity = 1.0
            else:
                text_complexity = 0.8
            complexity = max(complexity, text_complexity)
            
            # Tính độ phức tạp dựa trên số yêu cầu và mối quan hệ giữa chúng
            if num_requirements > 30:
                complexity = max(complexity, 1.2)
            elif num_requirements > 15:
                complexity = max(complexity, 1.0)
            
            # Phân tích các yếu tố khác (simple keyword-based analysis)
            has_security_requirements = 'security' in text.lower() or 'authentication' in text.lower()
            has_performance_requirements = any(term in text.lower() for term in ['performance', 'fast', 'responsive'])
            has_interface_requirements = any(term in text.lower() for term in ['interface', 'ui', 'ux', 'screen'])
            has_data_requirements = any(term in text.lower() for term in ['database', 'data', 'storage'])
            
            # Ước tính độ tin cậy cần thiết
            reliability = 1.0
            if has_security_requirements:
                reliability = 1.15
            elif has_performance_requirements and has_data_requirements:
                reliability = 1.1
            
            # Nếu không tìm thấy kích thước, ước tính từ các yếu tố khác
            if size == 0:
                # Ước tính kích thước từ số yêu cầu
                if num_requirements > 0:
                    size = num_requirements * 0.5  # Giả sử mỗi yêu cầu tương đương với 0.5 KLOC
                else:
                    # Ước tính từ độ dài văn bản và số công nghệ
                    word_count = len(text.split())
                    size = (word_count / 200) * (1 + num_technologies / 10)
                
                # Điều chỉnh theo độ phức tạp
                size = size * complexity
            
            # Đảm bảo kích thước tối thiểu và hợp lý
            size = max(0.5, min(size, 100))  # Giới hạn từ 0.5 đến 100 KLOC
            
            # Trả về đặc trưng
            features = {
                'size': size,
                'complexity': complexity,
                'reliability': reliability,
                'num_requirements': num_requirements,
                'functional_reqs': functional_reqs,
                'non_functional_reqs': non_functional_reqs,
                'has_security_requirements': has_security_requirements,
                'has_performance_requirements': has_performance_requirements,
                'has_interface_requirements': has_interface_requirements,
                'has_data_requirements': has_data_requirements,
                'entities': num_entities,
                'technologies': list(technologies_mentioned),
                'num_technologies': num_technologies,
                'developers': max(2, min(10, int(size * 2))),  # Estimate team size
                'tech_score': 1.0 + (num_technologies * 0.1)  # Technology complexity score
            }
            
            # Cache the result
            self._features_cache[cache_key] = features
            return features
            
        except Exception as e:
            print(f"Error in extract_features: {e}")
            return {
                'complexity': 1.0,
                'developers': 3,
                'functional_reqs': 5,
                'non_functional_reqs': 3,
                'num_requirements': 8,
                'size': 5.0,
                'reliability': 1.0,
                'has_performance_requirements': False,
                'has_interface_requirements': False,
                'tech_score': 1.0
            }
        finally:
            self._recursion_depth -= 1
        
        return features
    
    def extract_cocomo_parameters(self, text):
        """
        Trích xuất các tham số cho mô hình COCOMO II
        """
        # Use safe execution to avoid recursion
        cache_key = f"cocomo_params_{hash(text)}"
        if cache_key in self._features_cache:
            return self._features_cache[cache_key]
            
        if self._recursion_depth >= self._max_recursion_depth:
            print("Maximum recursion depth reached in extract_cocomo_parameters")
            return {'size': 5.0, 'eaf': 1.0}
        
        try:
            self._recursion_depth += 1
            
            # Simple parameter extraction without calling extract_features
            # Basic size estimation from text
            word_count = len(text.split())
            size = max(1.0, word_count / 200)  # Simple KLOC estimation
            
            # Basic complexity assessment
            complexity = 1.0
            if any(word in text.lower() for word in ['complex', 'difficult', 'advanced']):
                complexity = 1.3
            elif any(word in text.lower() for word in ['simple', 'basic', 'easy']):
                complexity = 0.8
                
            reliability = 1.0
            if any(word in text.lower() for word in ['security', 'critical', 'reliable']):
                reliability = 1.15
                
            # Basic requirement type detection
            has_performance_requirements = any(word in text.lower() for word in ['performance', 'fast', 'speed'])
            has_interface_requirements = any(word in text.lower() for word in ['interface', 'ui', 'screen'])
            
            # Chuyển đổi các đặc trưng thành tham số COCOMO II
            cocomo_params = {
                'size': size,
                'reliability': reliability,
                'complexity': complexity,
                'documentation': 1.0,  # Mặc định
                'reuse': 0.0,  # Mặc định
                'eaf': reliability * complexity  # Effort Adjustment Factor
            }
            
            # Ước tính các hệ số điều chỉnh khác
            if has_performance_requirements:
                cocomo_params['time_constraint'] = 1.1
            else:
                cocomo_params['time_constraint'] = 1.0
                
            if has_interface_requirements:
                cocomo_params['platform_volatility'] = 1.1
            else:
                cocomo_params['platform_volatility'] = 1.0
            
            # Các hệ số khác mặc định là 1.0
            cocomo_params['storage_constraint'] = 1.0
            cocomo_params['personnel_capability'] = 1.0
            cocomo_params['personnel_experience'] = 1.0
            cocomo_params['tool_experience'] = 1.0
            cocomo_params['language_experience'] = 1.0
            cocomo_params['team_cohesion'] = 1.0
            cocomo_params['process_maturity'] = 1.0
            
            # Cache the result
            self._features_cache[cache_key] = cocomo_params
            return cocomo_params
            
        except Exception as e:
            print(f"Error in extract_cocomo_parameters: {e}")
            return {'size': 5.0, 'eaf': 1.0}
        finally:
            self._recursion_depth -= 1
    
    def extract_function_points_parameters(self, text):
        """
        Trích xuất các tham số cho mô hình Function Points
        """
        cache_key = f"fp_params_{hash(text)}"
        if cache_key in self._features_cache:
            return self._features_cache[cache_key]
            
        if self._recursion_depth >= self._max_recursion_depth:
            print("Maximum recursion depth reached in extract_function_points_parameters")
            return {
                'external_inputs': 3, 'external_outputs': 2,
                'external_inquiries': 2, 'internal_files': 1,
                'external_files': 1, 'complexity_multiplier': 1.0
            }
            
        try:
            self._recursion_depth += 1
            
            doc = safe_nlp_process(text)
            
            # Simple requirement counting
            functional_keywords = ['input', 'output', 'form', 'report', 'query', 'search']
            functional_count = sum(1 for keyword in functional_keywords if keyword in text.lower())
            
            # Đếm số interface được đề cập
            interfaces = 0
            try:
                for ent in doc.ents:
                    if hasattr(ent, 'label_') and (ent.label_ == 'ORG' or 'interface' in ent.text.lower() or 'api' in ent.text.lower()):
                        interfaces += 1
            except:
                interfaces = text.lower().count('interface') + text.lower().count('api')
            
            # Ước tính số lượng input, output, query, file
            if functional_count > 0:
                # Phân bổ các yêu cầu chức năng vào các thành phần FP
                inputs = max(1, int(functional_count * 0.3))
                outputs = max(1, int(functional_count * 0.25))
                queries = max(1, int(functional_count * 0.2))
                files = max(1, int(functional_count * 0.15))
            else:
                # Giá trị mặc định
                inputs = 3
                outputs = 2
                queries = 2
                files = 1
            
            # Ước tính complexity multiplier từ text
            complexity_indicators = ['complex', 'complicated', 'advanced', 'sophisticated', 'intricate']
            simple_indicators = ['simple', 'basic', 'straightforward', 'easy']
            
            complexity_count = sum(1 for word in complexity_indicators if word in text.lower())
            simple_count = sum(1 for word in simple_indicators if word in text.lower())
            
            # Tính complexity multiplier dựa trên indicators
            if complexity_count > simple_count:
                complexity_multiplier = 1.2 + (complexity_count * 0.1)
            elif simple_count > complexity_count:
                complexity_multiplier = 0.8 + (simple_count * 0.05)
            else:
                complexity_multiplier = 1.0
            
            # Giới hạn complexity multiplier trong khoảng hợp lý
            complexity_multiplier = max(0.5, min(2.0, complexity_multiplier))
            
            # Tạo tham số Function Points
            fp_params = {
                'external_inputs': inputs,
                'external_outputs': outputs,
                'external_inquiries': queries,
                'internal_files': files,
                'external_files': interfaces,
                'complexity_multiplier': complexity_multiplier
            }
            
            return fp_params
            
        except Exception as e:
            print(f"Error in extract_function_points_parameters: {e}")
            return {
                'external_inputs': 3, 'external_outputs': 2,
                'external_inquiries': 2, 'internal_files': 1,
                'external_files': 1, 'complexity_multiplier': 1.0
            }
        finally:
            self._recursion_depth -= 1
    
    def extract_use_case_points_parameters(self, text):
        """
        Trích xuất các tham số cho mô hình Use Case Points
        """
        features = self.extract_features(text)
        
        # Đếm số actor được đề cập
        doc = safe_nlp_process(text)
        actors = []
        for ent in doc.ents:
            if ent.label_ == 'PERSON' or ent.label_ == 'ORG':
                actors.append(ent.text)
        
        # Loại bỏ các actor trùng lặp
        actors = list(set(actors))
        num_actors = len(actors)
        
        # Ước tính số lượng use case từ các yêu cầu chức năng
        num_use_cases = features['functional_reqs']
        
        # Phân loại actor và use case theo độ phức tạp
        if num_actors > 0:
            simple_actors = max(1, int(num_actors * 0.4))
            average_actors = max(1, int(num_actors * 0.4))
            complex_actors = max(0, num_actors - simple_actors - average_actors)
        else:
            # Giá trị mặc định
            simple_actors = 1
            average_actors = 1
            complex_actors = 0
        
        if num_use_cases > 0:
            simple_use_cases = max(1, int(num_use_cases * 0.3))
            average_use_cases = max(1, int(num_use_cases * 0.5))
            complex_use_cases = max(0, num_use_cases - simple_use_cases - average_use_cases)
        else:
            # Giá trị mặc định
            simple_use_cases = 1
            average_use_cases = 2
            complex_use_cases = 0
        
        # Ước tính Technical Complexity Factor và Environmental Factor
        tcf = 0.6 + (0.01 * 30)  # Giả sử giá trị trung bình
        ecf = 1.4 - (0.03 * 9)   # Giả sử giá trị trung bình
        
        # Ảnh hưởng của các yêu cầu phi chức năng
        if features['has_security_requirements']:
            tcf += 0.05
        if features['has_performance_requirements']:
            tcf += 0.05
        if features['has_interface_requirements']:
            tcf += 0.03
        
        # Tạo tham số Use Case Points
        ucp_params = {
            'simple_actors': simple_actors,
            'average_actors': average_actors,
            'complex_actors': complex_actors,
            'simple_use_cases': simple_use_cases,
            'average_use_cases': average_use_cases,
            'complex_use_cases': complex_use_cases,
            'technical_factors': tcf,
            'environmental_factors': ecf
        }
        
        return ucp_params

    def extract_loc_parameters(self, text):
        """
        Trích xuất tham số cho mô hình Lines of Code (LOC)
        
        Args:
            text (str): Văn bản yêu cầu
            
        Returns:
            dict: Tham số cho mô hình LOC
        """
        # Trích xuất kích thước LOC từ văn bản
        loc = self._extract_numeric_feature(text, self.size_patterns, default=None)
        
        # Nếu không tìm thấy số LOC trực tiếp, ước tính từ các thông tin khác
        if loc is None:
            # Đếm số lượng yêu cầu chức năng và phi chức năng
            features = self.extract_features(text)
            functional_reqs = features.get('functional_reqs', 0)
            non_functional_reqs = features.get('non_functional_reqs', 0)
            
            # Mức độ phức tạp ảnh hưởng đến số dòng mã trên mỗi yêu cầu
            complexity = features.get('complexity', 1.0)
            
            # Ước tính cơ bản: Mỗi yêu cầu chức năng = ~500 LOC, phi chức năng = ~200 LOC
            # Điều chỉnh theo độ phức tạp
            loc_estimate = (functional_reqs * 500 * complexity) + (non_functional_reqs * 200)
            
            # Chuyển LOC sang KLOC
            loc = loc_estimate / 1000
        else:
            # Chuyển LOC sang KLOC nếu đã tìm thấy
            # Kiểm tra nếu giá trị đã là KLOC hay không
            if loc < 1000:  # Nếu giá trị nhỏ, giả định là KLOC
                pass
            else:  # Nếu lớn, chuyển LOC sang KLOC
                loc = loc / 1000
        
        # Đảm bảo giá trị hợp lý
        loc = max(0.1, min(loc, 10000.0))
        
        # Trích xuất các thông số bổ sung cho mô hình LOC
        
        # Số lượng lập trình viên (developers)
        developers = self._extract_numeric_feature(text, 
            [r'(\d+)\s*developers', r'team\s*size\s*:\s*(\d+)', r'(\d+)\s*team\s*members',
             r'team\s*of\s*(\d+)', r'(\d+)\s*programmers', r'(\d+)\s*engineers',
             r'(\d+)\s*person\s*team'], 
            default=3)
        
        # Trích xuất độ phức tạp
        features = self.extract_features(text)
        complexity = features.get('complexity', 1.0)
        
        # Trích xuất mức độ kinh nghiệm của đội
        experience_patterns = [
            r'(high|medium|low)\s*experience',
            r'experience\s*level\s*:\s*(high|medium|low)',
            r'(experienced|intermediate|inexperienced)\s*team',
            r'team\s*with\s*(high|medium|low)\s*experience',
            r'(senior|mid-level|junior)\s*developers'
        ]
        
        experience_text = self._extract_text_feature(text, experience_patterns, default='medium')
        
        # Chuyển đổi văn bản thành giá trị số
        if experience_text in ['high', 'experienced', 'senior']:
            experience = 1.2
        elif experience_text in ['medium', 'intermediate', 'mid-level']:
            experience = 1.0
        else:  # low, inexperienced, junior
            experience = 0.8
        
        # Tính toán điểm số ngôn ngữ và công nghệ
        tech_score = 1.0
        
        # Kiểm tra các từ khóa công nghệ phức tạp
        complex_tech = ['machine learning', 'ai', 'blockchain', 'microservices', 
                      'distributed', 'real-time', 'high-performance', 'cloud native']
        
        for tech in complex_tech:
            if tech in text.lower():
                tech_score *= 1.15  # Tăng 15% cho mỗi công nghệ phức tạp
        
        # Giới hạn giá trị hợp lý
        tech_score = min(tech_score, 2.0)
        
        # Cập nhật độ phức tạp với công nghệ
        complexity = complexity * tech_score
        
        # Điều chỉnh kinh nghiệm dựa trên văn bản
        if 'extensive experience' in text.lower() or 'many years experience' in text.lower():
            experience *= 1.2
        elif 'little experience' in text.lower() or 'new technology' in text.lower():
            experience *= 0.8
            
        return {
            'kloc': loc,  # Nghìn dòng mã
            'loc': loc * 1000,  # Dòng mã
            'complexity': complexity,  # Độ phức tạp
            'developers': developers,  # Số lượng lập trình viên
            'experience': experience,  # Kinh nghiệm đội ngũ
            'tech_score': tech_score  # Điểm công nghệ
        }
    
    def extract_machine_learning_features(self, text):
        """
        Trích xuất các đặc trưng cho mô hình máy học từ văn bản yêu cầu
        
        Args:
            text (str): Văn bản yêu cầu
            
        Returns:
            dict: Các đặc trưng đã trích xuất
        """
        features = {}
        
        # Phân tích văn bản
        doc = safe_nlp_process(text)
        sentences = list(doc.sents)
        
        # Trích xuất thông tin số lượng nhà phát triển
        developers = self._extract_numeric_feature(text, 
            [r'(\d+)\s*developers', r'team\s*size\s*:\s*(\d+)', r'(\d+)\s*team\s*members',
             r'team\s*of\s*(\d+)', r'(\d+)\s*programmers', r'(\d+)\s*engineers',
             r'(\d+)\s*person\s*team'], 
            default=3)
        features['developers'] = developers
        
        # Trích xuất kinh nghiệm của nhóm phát triển
        team_exp_patterns = [
            r'team\s*experience\s*:\s*(high|medium|low)',
            r'(experienced|inexperienced)\s*team',
            r'team\s*with\s*(high|medium|low)\s*experience',
            r'(senior|junior|mid-level)\s*developers',
            r'developers\s*with\s*(extensive|moderate|limited)\s*experience',
            r'team\s*with\s*(many|some|few)\s*years\s*of\s*experience'
        ]
        
        team_exp_text = self._extract_text_feature(text, team_exp_patterns, default='medium')
        
        # Map từ ngữ sang giá trị số
        exp_mapping = {
            'high': 5, 'medium': 3, 'low': 1,
            'experienced': 5, 'inexperienced': 1,
            'senior': 5, 'mid-level': 3, 'junior': 1,
            'extensive': 5, 'moderate': 3, 'limited': 1,
            'many': 5, 'some': 3, 'few': 1
        }
        
        team_exp = exp_mapping.get(team_exp_text.lower(), 3)
        features['team_exp'] = team_exp
        
        # Trích xuất kinh nghiệm của quản lý
        manager_exp_patterns = [
            r'manager\s*experience\s*:\s*(high|medium|low)',
            r'(experienced|inexperienced)\s*manager',
            r'manager\s*with\s*(high|medium|low)\s*experience',
            r'(senior|junior|mid-level)\s*project\s*manager',
            r'project\s*manager\s*with\s*(extensive|moderate|limited)\s*experience',
            r'(experienced|capable|novice)\s*leadership'
        ]
        
        manager_exp_text = self._extract_text_feature(text, manager_exp_patterns, default='medium')
        manager_exp = exp_mapping.get(manager_exp_text.lower(), 3)
        features['manager_exp'] = manager_exp
        
        # Ước lượng kích thước dự án từ văn bản
        size = self._extract_project_size(text)
        features['size'] = size
        
        # Tính toán các tham số bổ sung
        features['kloc_per_dev'] = size / max(developers, 1)
        
        # Ước lượng thời gian
        time_months = self._extract_numeric_feature(text, 
            [r'(\d+)\s*months', r'timeline\s*:\s*(\d+)', r'duration\s*:\s*(\d+)\s*months',
             r'project\s*duration\s*of\s*(\d+)\s*months', r'complete\s*in\s*(\d+)\s*months',
             r'deliver\s*in\s*(\d+)\s*months', r'project\s*will\s*last\s*(\d+)\s*months'], 
            default=6)
        
        # Chuyển đổi tuần/ngày sang tháng nếu cần
        weeks_match = re.search(r'(\d+)\s*weeks', text, re.IGNORECASE)
        if weeks_match and not re.search(r'\d+\s*months', text, re.IGNORECASE):
            weeks = float(weeks_match.group(1))
            time_months = weeks / 4.33  # 4.33 tuần = 1 tháng
        
        days_match = re.search(r'(\d+)\s*days', text, re.IGNORECASE)
        if days_match and not (re.search(r'\d+\s*months', text, re.IGNORECASE) or re.search(r'\d+\s*weeks', text, re.IGNORECASE)):
            days = float(days_match.group(1))
            time_months = days / 30  # 30 ngày = 1 tháng
            
        features['time_months'] = time_months
        features['kloc_per_month'] = size / max(time_months, 1)
        
        # Ước lượng điểm chức năng (Function Points)
        fp_params = self.extract_function_points_parameters(text)
        
        # Tính tổng điểm chức năng chưa điều chỉnh
        unadjusted_fp = (
            (fp_params['external_inputs'] * 4) +
            (fp_params['external_outputs'] * 5) +
            (fp_params['external_inquiries'] * 4) +
            (fp_params['internal_files'] * 10) +
            (fp_params['external_files'] * 7)
        )
        
        features['points_non_adjust'] = unadjusted_fp
        features['adjustment'] = fp_params['complexity_multiplier']
        
        # Ước lượng số lượng giao dịch từ văn bản
        transactions = self._count_transactions(text)
        features['transactions'] = transactions
        
        # Ước lượng số lượng thực thể dữ liệu
        entities = self._count_entities(text)
        features['entities'] = entities
        
        # Tính toán tỷ lệ FP/month và FP/dev
        fp = features['points_non_adjust']
        features['fp_per_month'] = fp / max(time_months, 1)
        features['fp_per_dev'] = fp / max(developers, 1)
        
        # Xác định schema (phương pháp ước lượng chính)
        schema_patterns = [
            r'schema\s*:\s*(LOC|FP|UCP)',
            r'estimation\s*using\s*(LOC|FP|UCP)',
            r'based\s*on\s*(LOC|FP|UCP)'
        ]
        
        schema_text = self._extract_text_feature(text, schema_patterns, default='FP')
        schema_mapping = {'LOC': 0, 'FP': 1, 'UCP': 2}
        features['schema'] = schema_mapping.get(schema_text.upper(), 1)
        
        return features
    
    def _extract_numeric_feature(self, text, patterns, default=0):
        """Trích xuất đặc trưng số từ văn bản sử dụng các mẫu regex"""
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0])
                except (ValueError, TypeError):
                    # Nếu matches[0] là tuple, lấy phần tử đầu tiên
                    if isinstance(matches[0], tuple) and len(matches[0]) > 0:
                        try:
                            return float(matches[0][0])
                        except (ValueError, TypeError):
                            pass
        return default
    
    def _extract_text_feature(self, text, patterns, default=''):
        """Trích xuất đặc trưng văn bản từ văn bản sử dụng các mẫu regex"""
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple) and len(matches[0]) > 0:
                    return matches[0][1]
                return matches[0]
        return default
    
    def _extract_project_size(self, text):
        """Ước lượng kích thước dự án (KLOC) từ văn bản"""
        # In ra để debug
        print(f"Extracting project size from: {text}")
        
        # Tìm số dòng mã rõ ràng
        size = 0
        
        # Kiểm tra các mẫu KLOC
        kloc_patterns = [
            r'(\d+)[.,]?\d*[\s]*kloc',
            r'(\d+)[.,]?\d*[\s]*k[\s]*loc',
            r'(\d+)[.,]?\d*[\s]*k[\s]*lines[\s]*of[\s]*code',
            r'(\d+)[.,]?\d*[\s]*thousand[\s]*lines[\s]*of[\s]*code',
            r'(\d+)[.,]?\d*[\s]*k[\s]*sloc',
            r'size[\s]*:[\s]*(\d+)[.,]?\d*[\s]*k',
            r'approximately[\s]*(\d+)[.,]?\d*[\s]*k[\s]*lines'
        ]
        
        for pattern in kloc_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    size = float(matches[0])
                    print(f"Found KLOC size: {size}")
                    return size
                except (ValueError, TypeError):
                    if isinstance(matches[0], tuple) and len(matches[0]) > 0:
                        try:
                            size = float(matches[0][0])
                            print(f"Found KLOC size (from tuple): {size}")
                            return size
                        except (ValueError, TypeError):
                            pass
        
        # Tìm số dòng mã (LOC, không phải KLOC)
        loc_patterns = [
            r'(\d+)[.,]?\d*[\s]*loc',
            r'(\d+)[.,]?\d*[\s]*lines[\s]*of[\s]*code',
            r'(\d+)[.,]?\d*[\s]*lines',
            r'(\d+)[.,]?\d*[\s]*sloc',
            r'code[\s]*size[\s]*:[\s]*(\d+)[.,]?\d*',
            r'approximately[\s]*(\d+)[.,]?\d*[\s]*lines',
            r'about[\s]*(\d+)[.,]?\d*[\s]*lines',
            r'will[\s]*be[\s]*(\d+)[.,]?\d*[\s]*lines',
            r'project[\s]*of[\s]*(\d+)[.,]?\d*[\s]*lines',
            r'(\d+)[.,]?\d*[\s]*dòng[\s]*mã',
            r'(\d+)[.,]?\d*[\s]*dòng[\s]*code'
        ]
        
        for pattern in loc_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    loc = float(matches[0])
                    print(f"Found LOC size: {loc}")
                    return loc / 1000.0  # Chuyển LOC sang KLOC
                except (ValueError, TypeError):
                    if isinstance(matches[0], tuple) and len(matches[0]) > 0:
                        try:
                            loc = float(matches[0][0])
                            print(f"Found LOC size (from tuple): {loc}")
                            return loc / 1000.0
                        except (ValueError, TypeError):
                            pass
        
        # Phân tích sự phức tạp của yêu cầu để ước tính kích thước
        complexity_score = self._assess_text_complexity(text)
        
        # Đếm số yêu cầu và số thực thể nghiệp vụ
        requirements = self.extract_requirements(text)
        num_requirements = len(requirements)
        entities = self._count_entities(text)
        
        # Đếm số tính năng và mô-đun được đề cập
        feature_count = 0
        module_count = 0
        
        # Tính năng có thể được đề cập trực tiếp
        feature_patterns = [
            r'feature[s]?[\s:]+([^.,;]+)',
            r'tính năng[\s:]+([^.,;]+)',
            r'chức năng[\s:]+([^.,;]+)'
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, text.lower())
            feature_count += len(matches)
        
        # Hoặc đếm số mục có dấu bullet/số
        bullet_pattern = r'[-•*]\s+([^.,;]+)'
        number_pattern = r'\d+\.\s+([^.,;]+)'
        
        bullet_matches = re.findall(bullet_pattern, text)
        number_matches = re.findall(number_pattern, text)
        
        implicit_features = bullet_matches + number_matches
        feature_count += len(implicit_features)
        
        # Tìm các công nghệ phức tạp
        complex_techs = ['ai', 'machine learning', 'blockchain', 'distributed', 
                       'microservices', 'real-time', 'cloud', 'mobile', 
                       'đám mây', 'di động', 'thời gian thực', 'học máy']
        
        tech_complexity = 1.0
        for tech in complex_techs:
            if tech in text.lower():
                tech_complexity *= 1.2
                print(f"Found complex technology: {tech}")
        
        # Kiểm tra các từ khóa chỉ ra độ phức tạp
        if any(term in text.lower() for term in ['complex', 'complicated', 'sophisticated', 'advanced', 'phức tạp', 'cao cấp']):
            complexity_score *= 1.3
            print("Found complexity indicators in text")
        
        # Tính toán ước lượng kích thước dựa trên phân tích
        if num_requirements > 0:
            # Có yêu cầu rõ ràng
            req_based_size = num_requirements * 0.7 * tech_complexity * complexity_score / 3.0
            print(f"Size based on requirements: {req_based_size}")
        else:
            req_based_size = 1.0 * tech_complexity
        
        if feature_count > 0:
            # Có các tính năng rõ ràng
            feature_based_size = feature_count * 1.2 * tech_complexity * complexity_score / 3.0
            print(f"Size based on features: {feature_based_size}")
        else:
            feature_based_size = 1.5 * tech_complexity
        
        # Kích thước dựa trên độ phức tạp của văn bản
        text_complexity_size = complexity_score * 1.5 * tech_complexity
        print(f"Size based on text complexity: {text_complexity_size}")
        
        # Kích thước dựa trên số thực thể
        entity_based_size = entities * 0.8 * tech_complexity
        print(f"Size based on entities: {entity_based_size}")
        
        # Lấy giá trị lớn nhất trong các ước lượng
        size = max(req_based_size, feature_based_size, text_complexity_size, entity_based_size)
        
        # Đảm bảo kích thước tối thiểu là 1 KLOC
        size = max(1.0, size)
        
        print(f"Final estimated size: {size} KLOC")
        return size
    
    def _assess_text_complexity(self, text):
        """Đánh giá độ phức tạp của văn bản yêu cầu"""
        # Đếm số từ kỹ thuật
        technical_terms = [
            'database', 'api', 'interface', 'algorithm', 'security', 'authentication', 
            'encryption', 'cloud', 'distributed', 'microservices', 'scalable', 'performance', 
            'latency', 'concurrency', 'parallel', 'optimization', 'architecture', 'design pattern',
            'framework', 'integration', 'middleware', 'backend', 'frontend', 'full-stack',
            'container', 'orchestration', 'virtualization', 'serverless', 'oauth', 'token',
            'cryptography', 'blockchain', 'machine learning', 'artificial intelligence',
            'data mining', 'data analytics', 'deep learning', 'neural network', 'streaming',
            'real-time', 'asynchronous', 'synchronous', 'cache', 'pipeline', 'dependency',
            'injection', 'service', 'component', 'repository', 'repository pattern', 'orm'
        ]
        
        # Tìm các từ kỹ thuật trong văn bản
        tech_terms_found = set()
        for term in technical_terms:
            if term in text.lower():
                tech_terms_found.add(term)
        
        tech_count = len(tech_terms_found)
        
        # Đếm số câu phức tạp
        doc = safe_nlp_process(text)
        
        # Câu phức tạp: câu dài hoặc có nhiều mệnh đề
        complex_sentences = 0
        total_sentences = 0
        
        for sent in doc.sents:
            total_sentences += 1
            
            # Câu dài (>20 từ)
            if len(sent) > 20:
                complex_sentences += 1
                continue
                
            # Câu có nhiều danh từ và động từ
            noun_count = sum(1 for token in sent if token.pos_ in ["NOUN", "PROPN"])
            verb_count = sum(1 for token in sent if token.pos_ == "VERB")
            
            if noun_count >= 4 and verb_count >= 2:
                complex_sentences += 1
                continue
                
            # Câu có các kết nối logic phức tạp
            if any(token.text.lower() in ["if", "while", "unless", "although", "however", "nevertheless", 
                                       "therefore", "thus", "consequently", "whereas"] 
                  for token in sent):
                complex_sentences += 1
        
        # Tính tỷ lệ câu phức tạp
        complexity_ratio = complex_sentences / max(1, total_sentences)
        
        # Phân tích các công nghệ và framework được đề cập
        complex_tech_keywords = ["distributed", "microservices", "blockchain", "ai", "machine learning", 
                              "neural network", "real-time", "high-availability", "fault-tolerant",
                              "load balancing", "scalable", "cloud-native", "containerized"]
        
        complex_tech_count = sum(1 for term in complex_tech_keywords if term in text.lower())
        
        # Tính điểm phức tạp từ 1.0 đến 3.0
        tech_score = min(1.5, tech_count / 15)
        sentence_score = min(1.0, complexity_ratio * 2)
        complex_tech_score = min(0.5, complex_tech_count / 5)
        
        complexity = 1.0 + tech_score + sentence_score + complex_tech_score
        return min(3.0, complexity)  # Giới hạn tối đa là 3.0
    
    def _count_transactions(self, text):
        """Ước lượng số lượng giao dịch từ văn bản"""
        # Tìm kiếm các hành động CRUD trong văn bản
        crud_terms = [
            'create', 'read', 'update', 'delete', 'add', 'edit', 'remove', 
            'insert', 'select', 'query', 'modify', 'save', 'load', 'store',
            'retrieve', 'search', 'find', 'get', 'post', 'put', 'patch',
            'submit', 'upload', 'download', 'import', 'export', 'register',
            'login', 'logout', 'authenticate', 'authorize', 'validate'
        ]
        
        # Đếm các động từ hành động
        doc = safe_nlp_process(text)
        action_verbs = set()
        
        for token in doc:
            if token.pos_ == "VERB" and token.lemma_.lower() in crud_terms:
                action_verbs.add(token.lemma_.lower())
        
        crud_count = len(action_verbs)
        
        # Đếm số endpoint API/database được đề cập
        api_terms = ['api', 'endpoint', 'service', 'request', 'response', 'url', 'uri', 'route']
        api_count = sum(1 for term in api_terms if term in text.lower())
        
        # Đếm số thực thể nghiệp vụ
        business_entities = self._count_entities(text)
        
        # Đếm số tính năng người dùng
        user_features = sum(1 for term in ['user can', 'allow user', 'enable user', 'user should', 'user will'] 
                         if term in text.lower())
        
        # Kết hợp các yếu tố, với mức tối thiểu là 5
        return max(5, crud_count + (api_count / 2) + business_entities + user_features)
    
    def _count_entities(self, text):
        """Ước lượng số lượng thực thể dữ liệu từ văn bản"""
        # Sử dụng spaCy để trích xuất thực thể có tên
        doc = safe_nlp_process(text)
        named_entities = set([ent.text.lower() for ent in doc.ents])
        
        # Tìm các thực thể dữ liệu tiềm năng từ các danh từ
        potential_entities = set()
        for token in doc:
            if token.pos_ == "NOUN" and len(token.text) > 3 and token.text.lower() not in self.stop_words:
                # Kiểm tra xem danh từ này có phải là một thực thể dữ liệu không
                if any(token.text.lower() in sent.text.lower() for sent in doc.sents 
                      if any(data_term in sent.text.lower() for data_term in 
                           ['store', 'save', 'database', 'record', 'data', 'entity', 'object', 'class'])):
                    potential_entities.add(token.text.lower())
        
        # Tìm các từ liên quan đến thực thể dữ liệu
        data_terms = [
            'table', 'entity', 'object', 'class', 'model', 'record', 'document', 
            'collection', 'schema', 'database', 'data', 'structure', 'type',
            'information', 'attribute', 'property', 'field', 'column', 'relation'
        ]
        
        data_mentions = set()
        for term in data_terms:
            if term in text.lower():
                # Tìm các danh từ gần với từ dữ liệu này
                for sent in doc.sents:
                    if term in sent.text.lower():
                        for token in sent:
                            if token.pos_ == "NOUN" and token.text.lower() != term and len(token.text) > 3:
                                data_mentions.add(token.text.lower())
        
        # Kết hợp các thực thể tìm được
        all_entities = named_entities.union(potential_entities).union(data_mentions)
        
        # Lọc bỏ các từ thông dụng hoặc không liên quan
        common_words = ['system', 'application', 'software', 'platform', 'service', 'user', 'admin', 'manager']
        filtered_entities = set([e for e in all_entities if e not in common_words])
        
        # Kết hợp số thực thể, với mức tối thiểu là 3
        return max(3, len(filtered_entities))
        
    def extract_parameters(self, text):
        """
        Trích xuất các tham số từ văn bản yêu cầu để sử dụng cho việc ước lượng nỗ lực
        
        Args:
            text (str): Văn bản yêu cầu
            
        Returns:
            dict: Các tham số đã trích xuất cho việc ước lượng
        """
        # Phân tích toàn bộ tài liệu yêu cầu
        params = self.analyze_requirements_document(text)
        
        # Trích xuất thêm thông tin về mức độ phức tạp
        doc = safe_nlp_process(text)
        complexity_words = ['complex', 'complicated', 'difficult', 'advanced', 'sophisticated',
                          'phức tạp', 'khó', 'cao cấp', 'tiên tiến', 'phức hợp']
                          
        complexity_level = 1.0  # Mặc định: Trung bình
        for word in complexity_words:
            if word in text.lower():
                complexity_level = 1.5  # Cao
                break
                
        simplicity_words = ['simple', 'easy', 'straightforward', 'basic', 'fundamental',
                          'đơn giản', 'cơ bản', 'dễ dàng', 'đơn giản']
                          
        for word in simplicity_words:
            if word in text.lower():
                complexity_level = 0.8  # Thấp
                break
                
        # Trích xuất thông tin về độ tin cậy cần thiết
        reliability_words = ['reliable', 'robust', 'stable', 'secure', 'safe', 'critical',
                          'đáng tin cậy', 'ổn định', 'an toàn', 'bảo mật', 'quan trọng']
                          
        reliability = 1.0  # Mặc định: Trung bình
        for word in reliability_words:
            if word in text.lower():
                reliability = 1.2  # Cao
                break
                
        # Cập nhật các tham số
        params['complexity'] = complexity_level
        params['reliability'] = reliability
        
        # Trích xuất các tham số LOC nếu chưa có
        if 'loc_linear' not in params or 'loc_random_forest' not in params:
            loc_params = self.extract_loc_parameters(text)
            params['loc_linear'] = loc_params
            params['loc_random_forest'] = loc_params
            
        return params
    
    def analyze_requirements_document(self, text):
        """
        Phân tích toàn bộ tài liệu yêu cầu và trích xuất tất cả thông tin cần thiết
        """
        try:
            # Đảm bảo văn bản hợp lệ
            if text is None:
                text = "Empty requirement document"
            elif not isinstance(text, str):
                text = str(text)
            
            # Đảm bảo độ dài tối thiểu để xử lý
            if len(text.strip()) < 10:
                text = text + "\nDefault software project with standard requirements."
            
            # Trích xuất các tham số cho từng mô hình
            try:
                cocomo_params = self.extract_cocomo_parameters(text)
            except Exception as e:
                print(f"Error extracting COCOMO parameters: {e}")
                cocomo_params = {'size': 5.0, 'eaf': 1.0}
            
            try:
                fp_params = self.extract_function_points_parameters(text)
            except Exception as e:
                print(f"Error extracting Function Points parameters: {e}")
                fp_params = {
                    'external_inputs': 3, 'external_outputs': 2,
                    'external_inquiries': 2, 'internal_files': 1,
                    'external_files': 1, 'complexity_multiplier': 1.0
                }
            
            try:
                ucp_params = self.extract_use_case_points_parameters(text)
            except Exception as e:
                print(f"Error extracting Use Case Points parameters: {e}")
                ucp_params = {
                    'simple_actors': 2, 'average_actors': 1, 'complex_actors': 1,
                    'simple_uc': 3, 'average_uc': 2, 'complex_uc': 1,
                    'complexity_factor': 1.0
                }
            
            # Trích xuất đặc trưng cho mô hình máy học
            try:
                ml_features = self.extract_machine_learning_features(text)
            except Exception as e:
                print(f"Error extracting ML features: {e}")
                ml_features = {}
            
            # Trích xuất yêu cầu
            try:
                requirements = self.extract_requirements(text)
            except Exception as e:
                print(f"Error extracting requirements: {e}")
                requirements = []
            
            # Trích xuất đặc trưng
            try:
                features = self.extract_features(text)
            except Exception as e:
                print(f"Error extracting features: {e}")
                features = {
                    'complexity': 1.0, 'developers': 3,
                    'functional_reqs': 5, 'non_functional_reqs': 3,
                    'num_requirements': 8
                }
                
            # Trích xuất tham số LOC
            try:
                loc_params = self.extract_loc_parameters(text)
            except Exception as e:
                print(f"Error extracting LOC parameters: {e}")
                loc_params = {'kloc': 5.0}
            
            # Tạo dictionary chứa tất cả thông tin
            all_params = {
                'cocomo': cocomo_params,
                'function_points': fp_params,
                'use_case_points': ucp_params,
                'loc_linear': loc_params,
                'loc_random_forest': loc_params,
                'ml_features': ml_features,
                'requirements': requirements,
                'features': features
            }
            
            return all_params
            
        except Exception as e:
            print(f"Error in analyze_requirements_document: {e}")
            # Trả về cấu trúc dữ liệu mặc định để đảm bảo API không bị lỗi
            return {
                'cocomo': {'size': 5.0, 'eaf': 1.0},
                'loc_linear': {'kloc': 5.0},
                'loc_random_forest': {'kloc': 5.0},
                'function_points': {
                    'external_inputs': 3, 'external_outputs': 2,
                    'external_inquiries': 2, 'internal_files': 1,
                    'external_files': 1, 'complexity_multiplier': 1.0
                },
                'use_case_points': {
                    'simple_actors': 2, 'average_actors': 1, 'complex_actors': 1,
                    'simple_uc': 3, 'average_uc': 2, 'complex_uc': 1,
                    'complexity_factor': 1.0
                },
                'ml_features': {},
                'requirements': [],
                'features': {
                    'complexity': 1.0, 'developers': 3,
                    'functional_reqs': 5, 'non_functional_reqs': 3,
                    'num_requirements': 8
                }
            }
