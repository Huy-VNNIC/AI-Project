# Database Schema Documentation

> **Last Updated:** April 2, 2026  
> **Version:** 1.0  
> **Audience:** Database administrators, backend developers, architects

## Table of Contents

1. [Design Overview](#design-overview)
2. [Entity Relationship Diagram](#entity-relationship-diagram)
3. [Table Definitions](#table-definitions)
4. [Indexes](#indexes)
5. [Relationships](#relationships)
6. [Data Integrity](#data-integrity)
7. [Migration Guide](#migration-guide)
8. [Backup & Recovery](#backup--recovery)

---

## Design Overview

### Architecture

```
Requirements Storage
    ↓
NLP Analysis Results
    ↓
Test Case Generation
    ↓
Results Storage & Export
```

### Design Principles

- **Normalization:** 3NF normalized schema
- **Integrity:** Foreign key constraints
- **Audit:** Timestamp tracking for all records
- **Performance:** Strategic indexing
- **Scalability:** Designed for 1M+ requirements

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│         REQUIREMENTS                │
├─────────────────────────────────────┤
│ PK: requirement_id (INT)            │
│ ForeignKeys: project_id, user_id    │
│ Columns:                            │
│  - text (TEXT)                      │
│  - category (VARCHAR)               │
│  - nlp_confidence (FLOAT)           │
│  - created_at (TIMESTAMP)           │
│  - status (ENUM)                    │
└────────────┬────────────────────────┘
             │ 1:N
             │
┌────────────▼────────────────────────┐
│        TEST_CASES                   │
├─────────────────────────────────────┤
│ PK: test_case_id (INT)              │
│ FK: requirement_id → REQUIREMENTS   │
│ Columns:                            │
│  - title (VARCHAR)                  │
│  - scenario_type (VARCHAR)          │
│  - priority (ENUM)                  │
│  - effort_hours (FLOAT)             │
│  - generated_at (TIMESTAMP)         │
└────────────┬────────────────────────┘
             │ 1:N
             │
┌────────────▼────────────────────────┐
│       TEST_STEPS                    │
├─────────────────────────────────────┤
│ PK: step_id (INT)                   │
│ FK: test_case_id → TEST_CASES       │
│ Columns:                            │
│  - step_number (INT)                │
│  - action (TEXT)                    │
│  - expected_result (TEXT)           │
└─────────────────────────────────────┘
```

---

## Table Definitions

### 1. REQUIREMENTS Table

**Purpose:** Store parsed requirements and metadata

```sql
CREATE TABLE requirements (
    -- Primary Key
    requirement_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Foreign Keys
    project_id INT NOT NULL,
    file_id BIGINT,
    created_by INT,
    
    -- Core Data
    text TEXT NOT NULL COLLATE utf8mb4_unicode_ci,
    category VARCHAR(100),
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    
    -- NLP Analysis
    nlp_confidence FLOAT CHECK (nlp_confidence >= 0 AND nlp_confidence <= 1),
    parsed_entities JSON,
    
    -- Content Analysis
    word_count INT GENERATED ALWAYS AS (CHAR_LENGTH(text) - CHAR_LENGTH(REPLACE(text, ' ', '')) + 1) STORED,
    character_count INT GENERATED ALWAYS AS (CHAR_LENGTH(text)) STORED,
    
    -- Status
    status ENUM('new', 'analyzed', 'failed', 'archived') DEFAULT 'new',
    requires_review BOOLEAN DEFAULT false,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Search
    FULLTEXT INDEX idx_ft_text (text),
    
    -- Performance
    INDEX idx_project_status (project_id, status),
    INDEX idx_nlp_confidence (nlp_confidence),
    INDEX idx_created_at (created_at DESC)
);
```

**Column Descriptions:**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| requirement_id | BIGINT | Unique identifier | 1001 |
| project_id | INT | References project | 5 |
| text | TEXT | Requirement text | "User can log in..." |
| nlp_confidence | FLOAT | NLP parse confidence 0-1 | 0.92 |
| word_count | INT | Number of words (generated) | 8 |
| status | ENUM | Processing status | 'analyzed' |
| created_at | TIMESTAMP | Creation time | 2026-04-02 10:30:45 |

### 2. TEST_CASES Table

**Purpose:** Store generated test cases with metadata

```sql
CREATE TABLE test_cases (
    -- Primary Key
    test_case_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Foreign Key
    requirement_id BIGINT NOT NULL,
    
    -- Test Case Data
    title VARCHAR(255) NOT NULL,
    description TEXT,
    scenario_type VARCHAR(50),  -- 'happy_path', 'negative', 'boundary', etc.
    
    -- Scenario
    preconditions TEXT,
    expected_results TEXT,
    
    -- Classification
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    category VARCHAR(100),
    
    -- Estimation
    estimated_effort_hours DECIMAL(8, 2),
    
    -- Quality Metrics
    confidence FLOAT,
    automation_feasibility FLOAT,  -- 0-1 score
    
    -- Status
    status ENUM('generated', 'reviewed', 'approved', 'failed') DEFAULT 'generated',
    test_id VARCHAR(50) UNIQUE,  -- External test ID if linked
    
    -- Audit
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by INT,
    approved_at TIMESTAMP NULL,
    
    -- Relationships
    FOREIGN KEY (requirement_id) REFERENCES requirements(requirement_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Indexes
    INDEX idx_requirement (requirement_id),
    INDEX idx_priority (priority),
    INDEX idx_status (status),
    INDEX idx_confidence (confidence DESC),
    INDEX idx_created (generated_at DESC)
);
```

**Column Descriptions:**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| test_case_id | BIGINT | Unique test ID | 50001 |
| requirement_id | BIGINT | Parent requirement | 1001 |
| title | VARCHAR | Test case title | "Log in with valid credentials" |
| scenario_type | VARCHAR | Test scenario type | "happy_path" |
| priority | ENUM | Test priority | "high" |
| estimated_effort_hours | DECIMAL | Estimated effort | 2.5 |
| confidence | FLOAT | Generation confidence | 0.88 |

### 3. TEST_STEPS Table

**Purpose:** Store individual test steps within test cases

```sql
CREATE TABLE test_steps (
    -- Primary Key
    step_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Foreign Key
    test_case_id BIGINT NOT NULL,
    
    -- Step Data
    step_number INT NOT NULL,  -- Order of execution
    action TEXT NOT NULL,      -- What to do
    expected_result TEXT NOT NULL,  -- What should happen
    
    -- Metadata
    input_data JSON,  -- Optional test data
    validation_rules JSON,  -- How to validate
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    FOREIGN KEY (test_case_id) REFERENCES test_cases(test_case_id) ON DELETE CASCADE,
    UNIQUE KEY uk_test_case_step (test_case_id, step_number),
    
    -- Indexes
    INDEX idx_test_case (test_case_id)
);
```

**Column Descriptions:**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| step_id | BIGINT | Unique step ID | 200001 |
| test_case_id | BIGINT | Parent test case | 50001 |
| step_number | INT | Execution order | 1 |
| action | TEXT | Action to perform | "Enter email 'user@test.com'" |
| expected_result | TEXT | Expected outcome | "Email field populated" |

### 4. PROJECTS Table (Supporting)

**Purpose:** Group requirements and test cases by project

```sql
CREATE TABLE projects (
    project_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('active', 'archived') DEFAULT 'active'
);
```

### 5. FILES Table (Supporting)

**Purpose:** Track uploaded files

```sql
CREATE TABLE files (
    file_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type ENUM('txt', 'csv', 'md', 'docx') NOT NULL,
    file_size BIGINT,
    requirements_count INT,
    uploaded_by INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    INDEX idx_project (project_id),
    INDEX idx_uploaded (uploaded_at DESC)
);
```

---

## Indexes

### Performance Indexes

```sql
-- Full-text search on requirement text
CREATE FULLTEXT INDEX idx_ft_requirements_text 
  ON requirements(text);

-- NLP Confidence filtering (common query)
CREATE INDEX idx_requirements_confidence 
  ON requirements(nlp_confidence DESC, created_at);

-- Project-Status common query
CREATE INDEX idx_requirements_project_status 
  ON requirements(project_id, status);

-- Test case priority filtering
CREATE INDEX idx_testcases_priority 
  ON test_cases(priority DESC, estimated_effort_hours);

-- Time-based queries
CREATE INDEX idx_requirements_created 
  ON requirements(created_at DESC);

CREATE INDEX idx_testcases_generated 
  ON test_cases(generated_at DESC);
```

### Query Optimization Examples

**Slow Query (without index):**
```sql
-- Table scan for requirements with high confidence
SELECT * FROM requirements 
WHERE nlp_confidence > 0.75 
AND project_id = 5;
```

**Fast Query (with index):**
```sql
-- Uses idx_requirements_project_status
SELECT * FROM requirements 
WHERE project_id = 5 
AND nlp_confidence > 0.75;
```

---

## Relationships

### One-to-Many: Requirements → Test Cases

```
1 Requirement → N Test Cases
Example: "User can log in" → 
  - TC-1: Happy path login
  - TC-2: Invalid password
  - TC-3: Missing email
  - TC-4: SQL injection attempt
```

### One-to-Many: Test Cases → Test Steps

```
1 Test Case → N Test Steps
Example: "Log in with valid credentials" →
  Step 1: Navigate to login page
  Step 2: Enter email
  Step 3: Enter password
  Step 4: Click sign in
  Step 5: Verify dashboard
```

### Many-to-One: Requirements → Projects

```
Multiple Requirements → 1 Project
Example: Project "E-Commerce"
  - REQ-1: User registration
  - REQ-2: Payment processing
  - REQ-3: Order tracking
  - REQ-n: ...
```

### Cascade Rules

```
DELETE project → DELETE all requirements, test_cases, test_steps
DELETE requirement → DELETE all related test_cases and test_steps
DELETE test_case → DELETE all related test_steps

IMPORTANT: Always back up before cascading deletes!
```

---

## Data Integrity

### Primary Key Constraints

```sql
-- Auto-incrementing primary keys for all tables
ALTER TABLE requirements AUTO_INCREMENT = 1000;
ALTER TABLE test_cases AUTO_INCREMENT = 50000;
ALTER TABLE test_steps AUTO_INCREMENT = 200000;
```

### Foreign Key Constraints

```sql
-- Ensure data consistency
ALTER TABLE test_cases 
ADD CONSTRAINT fk_testcases_requirement
FOREIGN KEY (requirement_id) REFERENCES requirements(requirement_id)
ON DELETE CASCADE  -- Delete test cases if requirement deleted
ON UPDATE CASCADE;
```

### Check Constraints

```sql
-- NLP Confidence must be 0-1
ALTER TABLE requirements
ADD CONSTRAINT chk_nlp_confidence
CHECK (nlp_confidence >= 0 AND nlp_confidence <= 1);

-- Word count must be positive
ALTER TABLE requirements
ADD CONSTRAINT chk_word_count
CHECK (word_count > 0);

-- Effort hours must be positive
ALTER TABLE test_cases
ADD CONSTRAINT chk_effort_hours
CHECK (estimated_effort_hours > 0);
```

### Unique Constraints

```sql
-- Test ID must be unique
ALTER TABLE test_cases
ADD CONSTRAINT uk_test_id UNIQUE (test_id);

-- File name unique per project
ALTER TABLE files
ADD CONSTRAINT uk_project_filename UNIQUE (project_id, filename);
```

---

## Migration Guide

### Create Schema from Scratch

```bash
# 1. Create database
mysql -u root -p
CREATE DATABASE test_generation;
USE test_generation;

# 2. Run schema script
mysql -u root -p test_generation < schema.sql

# 3. Verify tables
SHOW TABLES;
DESCRIBE requirements;
```

### Add New Column

```sql
-- Before deployment
ALTER TABLE requirements 
ADD COLUMN risk_level ENUM('low', 'medium', 'high') DEFAULT 'medium'
AFTER priority;

-- Create index on new column
CREATE INDEX idx_risk_level ON requirements(risk_level);

-- Test queries before production cutover
SELECT * FROM requirements WHERE risk_level = 'high';
```

### Migrate Data

```sql
-- Migrate from old table to new table
INSERT INTO requirements_new 
SELECT *, DEFAULT FROM requirements_old;

-- Verify counts match
SELECT COUNT(*) FROM requirements_old;
SELECT COUNT(*) FROM requirements_new;

-- Switch tables (after verification)
RENAME TABLE requirements TO requirements_backup;
RENAME TABLE requirements_new TO requirements;
```

---

## Backup & Recovery

### Backup Strategy

```bash
# Full backup (daily)
mysqldump -u root -p test_generation > backup_$(date +%Y%m%d).sql

# Incremental backup (binary logs)
# Enable in my.cnf: log-bin = mysql-bin

# Backup to cloud
aws s3 cp backup_20260402.sql s3://backups/test_generation/
```

### Recovery Procedures

**Full Restore:**
```bash
mysql -u root -p test_generation < backup_20260402.sql
```

**Point-in-Time Recovery:**
```bash
# Using binary logs
mysqlbinlog mysql-bin.* | mysql -u root -p
```

**Verify Recovery:**
```sql
-- Check data integrity
SELECT COUNT(*) FROM requirements;
SELECT COUNT(*) FROM test_cases;
SELECT COUNT(*) FROM test_steps;

-- Verify relationships
SELECT r.requirement_id, COUNT(t.test_case_id) as test_count
FROM requirements r
LEFT JOIN test_cases t ON r.requirement_id = t.requirement_id
GROUP BY r.requirement_id;
```

---

## Sample Queries

### Find requirements by confidence

```sql
SELECT requirement_id, text, nlp_confidence
FROM requirements
WHERE nlp_confidence >= 0.75
ORDER BY nlp_confidence DESC
LIMIT 20;
```

### Get test cases for requirement

```sql
SELECT tc.test_case_id, tc.title, tc.priority, ts.step_number, ts.action
FROM test_cases tc
LEFT JOIN test_steps ts ON tc.test_case_id = ts.test_case_id
WHERE tc.requirement_id = 1001
ORDER BY ts.step_number;
```

### Find requirements needing review

```sql
SELECT requirement_id, text, nlp_confidence
FROM requirements
WHERE requires_review = true
ORDER BY created_at DESC;
```

### Calculate effort by project

```sql
SELECT 
  p.name,
  COUNT(DISTINCT r.requirement_id) as requirement_count,
  COUNT(DISTINCT tc.test_case_id) as test_case_count,
  SUM(tc.estimated_effort_hours) as total_effort
FROM projects p
LEFT JOIN requirements r ON p.project_id = r.project_id
LEFT JOIN test_cases tc ON r.requirement_id = tc.requirement_id
GROUP BY p.name;
```

---

## Support

- 📊 See [SYSTEM_UPGRADE_PHASE2.md](SYSTEM_UPGRADE_PHASE2.md) for architecture
- 🔍 See [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) for data issues
- 📈 See [PERFORMANCE_TUNING_GUIDE.md](PERFORMANCE_TUNING_GUIDE.md) for optimization

---

*Last updated: April 2, 2026*
