"""
Configuration constants for Rule-Based Test Case Generator
"""

# NLP Config
SPACY_MODEL = "en_core_web_sm"
MIN_REQUIREMENT_LENGTH = 10  # minimum characters
MAX_REQUIREMENT_LENGTH = 1000

# Synonym mapping for normalization
SYNONYM_MAP = {
    # Login/Authentication
    "sign in": "login",
    "sign up": "signup",
    "authenticate": "login",
    "log in": "login",
    "register": "signup",
    "create account": "signup",
    "enter credentials": "login",
    
    # Save/Store
    "save": "store",
    "persist": "store",
    "commit": "store",
    "write": "store",
    
    # Delete/Remove
    "delete": "remove",
    "erase": "remove",
    "destroy": "remove",
    "drop": "remove",
    
    # Display/Show
    "display": "show",
    "present": "show",
    "render": "show",
    "output": "show",
    
    # Verify/Validate/Check
    "verify": "validate",
    "check": "validate",
    "confirm": "validate",
    "ensure": "validate",
}

# Security-related actions that trigger security tests
SECURITY_ACTIONS = [
    "login", "authenticate", "authorize", "validate", "check",
    "verify", "encrypt", "decrypt", "hash", "sign", "access"
]

# Domain keywords for automatic categorization
DOMAIN_KEYWORDS = {
    "hotel": ["room", "booking", "check-in", "check-out", "reservation", "guest", "phòng", "đặt"],
    "banking": ["account", "transfer", "transaction", "balance", "deposit", "withdraw", "ngân hàng", "chuyển"],
    "ecommerce": ["product", "cart", "order", "payment", "checkout", "inventory", "shop", "mua"],
    "healthcare": ["patient", "doctor", "appointment", "prescription", "medical", "diagnosis", "bệnh nhân"],
}

# Test priority mapping
PRIORITY_MAPPING = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}

# Test type definitions
TEST_TYPES = {
    "positive": "Happy path - valid inputs",
    "negative": "Invalid inputs - expect failure",
    "edge_case": "Boundary values",
    "security": "Security-related tests",
    "performance": "Performance/load tests",
}

# Boundary value examples
BOUNDARY_VALUES = {
    "email": ["test@example.com", "invalid_email", "", "test@", "@example.com"],
    "password": ["Pass123!", "", "12345", "a" * 256],
    "phone": ["0123456789", "", "abc", "+1234567890"],
    "age": [0, -1, 1000, 18, 65],
    "quantity": [0, -1, 1, 999999],
}

# Conditional keywords
CONDITIONAL_KEYWORDS = ["if", "when", "unless", "provided", "given", "provided that"]

# Expected result keywords
EXPECTED_KEYWORDS = [
    "system should", "should", "must", "will", "displays", "shows",
    "returns", "sends", "creates", "updates", "deletes", "saves"
]
