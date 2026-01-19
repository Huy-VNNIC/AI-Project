# Task Generation Configuration

# This file contains all configurable parameters for the task generation system.
# Copy this to `config_task_gen.py` and customize as needed.

# ==============================================================================
# PATHS
# ==============================================================================

# Dataset paths
DATASET_PATH = 'datasets/dataset_large_1m/'  # Or 'datasets/dataset_small_10k/'
DATASET_CHUNKS_PATTERN = 'chunk_*.csv'

# Processed data paths
PROCESSED_DATA_PATH = 'data/processed/'
CLEAN_DATA_FILE = 'clean_full.parquet'
LABEL_MAPS_FILE = 'label_maps.json'

# Split data paths
SPLITS_PATH = 'data/splits/'
TRAIN_FILE = 'train.parquet'
VAL_FILE = 'val.parquet'
TEST_FILE = 'test.parquet'

# Model paths
MODEL_PATH = 'models/task_gen/'
REQUIREMENT_DETECTOR_MODEL = 'requirement_detector_{timestamp}.joblib'
TYPE_MODEL = 'type_classifier_{timestamp}.joblib'
PRIORITY_MODEL = 'priority_classifier_{timestamp}.joblib'
DOMAIN_MODEL = 'domain_classifier_{timestamp}.joblib'

# Report paths
REPORT_PATH = 'report/'
QUALITY_REPORT_JSON = 'data_quality_report.json'
QUALITY_REPORT_MD = 'data_quality_report.md'

# ==============================================================================
# DATA PROCESSING
# ==============================================================================

# CSV reading
CSV_ENCODING = 'utf-8'
CHUNK_SIZE = 100000  # Rows per chunk (lower if OOM)

# Cleaning
DEDUPE_THRESHOLD = 0.95  # Similarity threshold for duplicate detection
TEXT_MIN_LENGTH = 10     # Min characters for valid text
TEXT_MAX_LENGTH = 5000   # Max characters (truncate if longer)

# Splitting
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1
STRATIFY_COLUMNS = ['is_requirement', 'domain']
RANDOM_STATE = 42

# ==============================================================================
# FEATURE EXTRACTION
# ==============================================================================

# TF-IDF for Requirement Detector
TFIDF_MAX_FEATURES_DETECTOR = 10000
TFIDF_NGRAM_RANGE_DETECTOR = (1, 2)  # Unigrams + bigrams
TFIDF_MIN_DF_DETECTOR = 2
TFIDF_MAX_DF_DETECTOR = 0.95

# TF-IDF for Enrichers
TFIDF_MAX_FEATURES_ENRICHER = 5000
TFIDF_NGRAM_RANGE_ENRICHER = (1, 2)
TFIDF_MIN_DF_ENRICHER = 2
TFIDF_MAX_DF_ENRICHER = 0.90

# ==============================================================================
# MODEL TRAINING
# ==============================================================================

# Requirement Detector
DETECTOR_ALGORITHM = 'sgd'  # 'sgd' or 'logistic'
DETECTOR_CLASS_WEIGHT = 'balanced'
DETECTOR_MAX_ITER = 1000
DETECTOR_LOSS = 'log_loss'  # For SGDClassifier
DETECTOR_PENALTY = 'l2'
DETECTOR_ALPHA = 0.0001

# Calibration
CALIBRATION_METHOD = 'sigmoid'  # 'sigmoid' or 'isotonic'
CALIBRATION_CV = 3

# Enrichers (Type, Priority, Domain)
ENRICHER_ALGORITHM = 'logistic'  # Always LogisticRegression for multi-class
ENRICHER_MAX_ITER = 1000
ENRICHER_CLASS_WEIGHT = 'balanced'
ENRICHER_SOLVER = 'lbfgs'
ENRICHER_MULTI_CLASS = 'multinomial'

# ==============================================================================
# INFERENCE
# ==============================================================================

# Requirement Detection
REQUIREMENT_THRESHOLD = 0.5  # Probability threshold (0-1)
REQUIREMENT_HIGH_CONF = 0.8  # High confidence threshold

# Enrichment
ENRICHER_MIN_CONFIDENCE = 0.3  # Filter predictions below this

# ==============================================================================
# TASK GENERATION
# ==============================================================================

# Segmentation
HEADING_PATTERNS = [
    r'^#{1,6}\s+',           # Markdown: # Heading
    r'^\d+\.\s+',            # Numbered: 1. Section
    r'^\d+\.\d+\s+',         # Nested: 1.1 Subsection
    r'^[A-Z\s]{5,}$',        # ALL CAPS HEADING
]
MIN_SECTION_LENGTH = 50      # Min chars for a section

# Template Generation (Mode 1)
TEMPLATE_MODE_ENABLED = True
TEMPLATE_AC_MIN = 3          # Min acceptance criteria
TEMPLATE_AC_MAX = 7          # Max acceptance criteria
TEMPLATE_TITLE_MAX_WORDS = 10
TEMPLATE_DESC_SENTENCES = (2, 4)

# LLM Generation (Mode 2)
LLM_MODE_ENABLED = False     # Set to True after implementing
LLM_PROVIDER = 'openai'      # 'openai', 'anthropic', 'google'
LLM_MODEL = 'gpt-4o-mini'    # Model name
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 1024
LLM_TIMEOUT = 30             # Seconds
LLM_MAX_CONCURRENT = 5       # Parallel requests

# Post-processing
POSTPROCESS_DEDUPE = True
POSTPROCESS_SIMILARITY_THRESHOLD = 0.85  # TF-IDF cosine similarity
POSTPROCESS_MIN_CONFIDENCE = 0.3
POSTPROCESS_MIN_TITLE_LENGTH = 10
POSTPROCESS_FILTER_PLACEHOLDERS = True
POSTPROCESS_SPLIT_COMPLEX = False  # Optional
POSTPROCESS_MERGE_RELATED = False  # Optional

# ==============================================================================
# STORY POINTS ALLOCATION
# ==============================================================================

# Fibonacci sequence for story points
FIBONACCI_POINTS = [1, 2, 3, 5, 8, 13, 21]

# Hour ranges for each Fibonacci point
HOUR_TO_POINTS_MAP = {
    (0, 4): 1,
    (4, 8): 2,
    (8, 16): 3,
    (16, 24): 5,
    (24, 40): 8,
    (40, 60): 13,
    (60, float('inf')): 21
}

# Priority weights
PRIORITY_WEIGHTS = {
    'High': 1.3,
    'Medium': 1.0,
    'Low': 0.8
}

# Type weights
TYPE_WEIGHTS = {
    'security': 1.2,
    'data': 1.1,
    'integration': 1.1,
    'performance': 1.0,
    'functional': 1.0,
    'interface': 1.0,
    'other': 1.0
}

# Role weights
ROLE_WEIGHTS = {
    'Security': 1.2,
    'DevOps': 1.1,
    'Data': 1.1,
    'Backend': 1.0,
    'QA': 1.0,
    'Frontend': 0.9,
    'BA': 0.8
}

# ==============================================================================
# ROLE ASSIGNMENT (Rule-based)
# ==============================================================================

ROLE_KEYWORDS = {
    'Backend': [
        'api', 'endpoint', 'server', 'database', 'db', 'sql', 'query',
        'authentication', 'auth', 'authorization', 'service', 'microservice',
        'integration', 'webhook', 'cron', 'batch', 'background'
    ],
    'Frontend': [
        'ui', 'interface', 'button', 'form', 'page', 'screen', 'view',
        'component', 'react', 'vue', 'angular', 'css', 'style', 'layout',
        'responsive', 'display', 'show', 'render', 'navigation'
    ],
    'QA': [
        'test', 'testing', 'validate', 'verification', 'quality',
        'bug', 'defect', 'regression', 'automation', 'selenium'
    ],
    'DevOps': [
        'deploy', 'deployment', 'ci/cd', 'docker', 'kubernetes', 'k8s',
        'infrastructure', 'monitoring', 'logging', 'backup', 'scaling',
        'performance', 'optimization', 'cache', 'redis', 'nginx'
    ],
    'Security': [
        'security', 'secure', 'encryption', 'decrypt', 'certificate',
        'vulnerability', 'audit', 'compliance', 'gdpr', 'privacy',
        'authentication', 'authorization', 'oauth', 'jwt', 'token'
    ],
    'Data': [
        'data', 'dataset', 'analytics', 'report', 'dashboard', 'metric',
        'etl', 'pipeline', 'warehouse', 'migration', 'import', 'export',
        'csv', 'json', 'xml', 'parse'
    ],
    'BA': [
        'requirement', 'specification', 'analysis', 'documentation',
        'stakeholder', 'user story', 'acceptance criteria'
    ]
}

ROLE_DEFAULT = 'Backend'

# ==============================================================================
# API CONFIGURATION
# ==============================================================================

# Endpoints
API_PREFIX = '/api/v1'
API_MAX_TASKS_DEFAULT = 50
API_MAX_TASKS_LIMIT = 500

# Rate limiting
API_RATE_LIMIT_PER_MINUTE = 100
API_RATE_LIMIT_PER_HOUR = 1000

# File upload
UPLOAD_MAX_SIZE_MB = 50
UPLOAD_ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt', '.md']

# Timeouts
API_TASK_GENERATION_TIMEOUT = 300  # 5 minutes max

# ==============================================================================
# LOGGING
# ==============================================================================

LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'logs/task_generation.log'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ==============================================================================
# MONITORING
# ==============================================================================

# Metrics to track
TRACK_PROCESSING_TIME = True
TRACK_CONFIDENCE_SCORES = True
TRACK_TASK_DISTRIBUTION = True

# Alerts (thresholds)
ALERT_ERROR_RATE = 0.05       # 5%
ALERT_LOW_CONFIDENCE = 0.5    # Avg confidence below 0.5
ALERT_PROCESSING_TIME = 10    # Seconds per document

# ==============================================================================
# FEEDBACK & LEARNING LOOP
# ==============================================================================

# Feedback collection
FEEDBACK_ENABLED = True
FEEDBACK_STORAGE = 'database'  # 'database', 'json', 'none'
FEEDBACK_DB_TABLE = 'task_feedback'

# Retraining triggers
RETRAIN_FEEDBACK_THRESHOLD = 1000  # Min feedback count
RETRAIN_IMPROVEMENT_THRESHOLD = 0.05  # Min F1 improvement (5%)
RETRAIN_SCHEDULE_DAYS = 30  # Auto-retrain every 30 days

# ==============================================================================
# EXPERIMENTAL FEATURES
# ==============================================================================

# RAG (Retrieval-Augmented Generation)
RAG_ENABLED = False
RAG_VECTOR_DB = 'chroma'  # 'chroma', 'pinecone', 'weaviate'
RAG_TOP_K = 5
RAG_SIMILARITY_THRESHOLD = 0.7

# Multi-language
MULTI_LANGUAGE_ENABLED = False
SUPPORTED_LANGUAGES = ['en']  # Add: 'vi', 'zh', 'es', etc.

# Dependency detection
DEPENDENCY_DETECTION = False
DEPENDENCY_MIN_CONFIDENCE = 0.8

# ==============================================================================
# DEBUGGING
# ==============================================================================

DEBUG_MODE = False
DEBUG_SAVE_INTERMEDIATE = False  # Save segmented, detected, enriched data
DEBUG_INTERMEDIATE_PATH = 'debug/'

# Profiling
PROFILE_PERFORMANCE = False
PROFILE_OUTPUT = 'profile_task_gen.prof'

# ==============================================================================
# USAGE EXAMPLE
# ==============================================================================

# To use this config:
# 1. Copy to `config_task_gen.py`
# 2. Customize values
# 3. Import in your code:
#
#    from config_task_gen import *
#    pipeline = get_pipeline(mode='template', config={
#        'requirement_threshold': REQUIREMENT_THRESHOLD,
#        'max_tasks': API_MAX_TASKS_DEFAULT,
#        ...
#    })
