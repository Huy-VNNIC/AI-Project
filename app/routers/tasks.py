"""
Task generation router - Production endpoints
/generate, /feedback, /stats
Using LLM-Free AI Pipeline (Smart NER + Domain-Specific Generators)
"""
import os
import sys
import time
import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# ✅ Use new LLM-Free adapter (no external APIs)
from requirement_analyzer.task_gen.api_adapter_llmfree import get_llmfree_adapter

router = APIRouter()

# Global adapter instance (loaded once)
_adapter = None


def get_adapter():
    """Get or create LLM-Free adapter instance"""
    global _adapter
    if _adapter is None:
        # Initialize with mock extractor (can be replaced with custom AI model later)
        _adapter = get_llmfree_adapter()
        print("✅ LLM-Free Adapter Loaded")
    return _adapter


# Request/Response models
class GenerateRequest(BaseModel):
    document_text: str = Field(..., description="Requirement document text")
    mode: Optional[str] = Field("model", description="Generation mode: template, model, or llm")
    max_tasks: Optional[int] = Field(50, ge=1, le=200, description="Maximum tasks to generate")
    requirement_threshold: Optional[float] = Field(0.5, ge=0, le=1, description="Threshold for requirement detection")
    dedupe: Optional[bool] = Field(True, description="Enable deduplication")
    epic_name: Optional[str] = Field("Generated Tasks", description="Epic name for grouping")


class TaskMetadata(BaseModel):
    mode: str
    num_sentences: int
    num_requirements: int
    num_tasks: int
    latency_ms: int
    avg_confidence: float
    quality_gates: Dict[str, int]


class GenerateResponse(BaseModel):
    tasks: List[Dict[str, Any]]
    metadata: TaskMetadata


class FeedbackRequest(BaseModel):
    task_id: Optional[str] = None
    generated_task: Dict[str, Any] = Field(..., description="Originally generated task")
    final_task: Optional[Dict[str, Any]] = Field(None, description="User-edited task")
    rating: Optional[int] = Field(None, ge=1, le=5, description="User rating 1-5")
    comment: Optional[str] = Field(None, description="User comment")
    session_id: Optional[str] = None


class StatsResponse(BaseModel):
    total_requests: int
    avg_latency_ms: float
    avg_confidence: float
    mode_distribution: Dict[str, int]
    quality_gates_summary: Dict[str, int]


# Feedback database
def get_feedback_db():
    """Get feedback database connection"""
    db_path = Path(os.getenv('FEEDBACK_DB', 'data/feedback.db'))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    
    # Create table if not exists
    conn.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            task_id TEXT,
            generated_task TEXT NOT NULL,
            final_task TEXT,
            rating INTEGER,
            comment TEXT,
            session_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS generation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            mode TEXT NOT NULL,
            num_sentences INTEGER,
            num_requirements INTEGER,
            num_tasks INTEGER,
            latency_ms INTEGER,
            avg_confidence REAL,
            quality_gates TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    return conn


@router.post("/generate")
async def generate_tasks(request: GenerateRequest):
    """
    ✅ Generate tests from requirement document using LLM-Free AI Pipeline
    
    No external APIs - uses domain-specific generators + optional custom AI model
    
    **Features:**
    - Vietnamese language support (proper tokenization)
    - Domain-specific test generation (Hotel, Banking, Healthcare, E-commerce)
    - Intelligent deduplication (0.85 semantic similarity)
    - Security test auto-generation
    - Real confidence scores (0.5-0.95) per test
    
    **Example:**
    ```json
    {
      "document_text": "Hệ thống phải cho phép đặt phòng mới...",
      "max_tasks": 50,
      "quality_threshold": 0.6
    }
    ```
    """
    start_time = time.time()
    
    try:
        # Get adapter
        adapter = get_adapter()
        
        # Generate tests using LLM-Free pipeline
        result = adapter.generate_tests(
            requirements_text=request.document_text,
            max_tests=request.max_tasks,
            quality_threshold=request.requirement_threshold,
            auto_deduplicate=request.dedupe,
            verbose=False
        )
        
        # Return full result
        return result
    
    except Exception as e:
        import traceback
        print(f"❌ Error in /generate: {str(e)}")
        traceback.print_exc()
        
        return {
            'status': 'error',
            'message': f"Generation failed: {str(e)}",
            'test_cases': [],
            'summary': {
                'requirements_processed': 0,
                'test_cases_generated': 0,
                'unique_tests_final': 0,
                'latency_ms': int((time.time() - start_time) * 1000),
                'quality_score': 0.0
            }
        }



@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback on generated task
    
    **Used for model improvement:**
    - Collect user edits to tasks
    - Track ratings and comments
    - Build training data for future improvements
    """
    try:
        conn = get_feedback_db()
        
        conn.execute('''
            INSERT INTO feedback 
            (timestamp, task_id, generated_task, final_task, rating, comment, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            feedback.task_id,
            json.dumps(feedback.generated_task),
            json.dumps(feedback.final_task) if feedback.final_task else None,
            feedback.rating,
            feedback.comment,
            feedback.session_id
        ))
        
        conn.commit()
        feedback_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        
        return {
            "status": "success",
            "feedback_id": feedback_id,
            "message": "Thank you for your feedback!"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    days: int = Query(7, ge=1, le=365, description="Number of days to look back")
):
    """
    Get generation statistics
    
    **Returns:**
    - Total requests
    - Average latency
    - Average confidence
    - Mode distribution
    - Quality gates summary
    """
    try:
        conn = get_feedback_db()
        
        # Calculate cutoff date
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get stats
        cursor = conn.execute('''
            SELECT 
                COUNT(*) as total,
                AVG(latency_ms) as avg_latency,
                AVG(avg_confidence) as avg_confidence
            FROM generation_logs
            WHERE timestamp >= ?
        ''', (cutoff,))
        
        row = cursor.fetchone()
        total_requests = row[0] or 0
        avg_latency = row[1] or 0
        avg_confidence = row[2] or 0
        
        # Mode distribution
        cursor = conn.execute('''
            SELECT mode, COUNT(*) as count
            FROM generation_logs
            WHERE timestamp >= ?
            GROUP BY mode
        ''', (cutoff,))
        
        mode_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Quality gates summary
        cursor = conn.execute('''
            SELECT quality_gates
            FROM generation_logs
            WHERE timestamp >= ? AND quality_gates IS NOT NULL
        ''', (cutoff,))
        
        quality_gates_summary = {
            'title_repairs': 0,
            'ac_dedupes': 0,
            'priority_boosts': 0
        }
        
        for row in cursor.fetchall():
            try:
                gates = json.loads(row[0])
                for key in quality_gates_summary:
                    quality_gates_summary[key] += gates.get(key, 0)
            except:
                pass
        
        conn.close()
        
        return StatsResponse(
            total_requests=total_requests,
            avg_latency_ms=avg_latency,
            avg_confidence=avg_confidence,
            mode_distribution=mode_distribution,
            quality_gates_summary=quality_gates_summary
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/feedback/export")
async def export_feedback(
    limit: int = Query(1000, ge=1, le=10000, description="Max records to export")
):
    """
    Export feedback data for analysis
    
    **Returns JSONL format** - one feedback record per line
    """
    try:
        conn = get_feedback_db()
        
        cursor = conn.execute('''
            SELECT 
                id, timestamp, task_id, generated_task, final_task, 
                rating, comment, session_id
            FROM feedback
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        feedbacks = []
        for row in cursor.fetchall():
            feedbacks.append({
                'id': row[0],
                'timestamp': row[1],
                'task_id': row[2],
                'generated_task': json.loads(row[3]) if row[3] else None,
                'final_task': json.loads(row[4]) if row[4] else None,
                'rating': row[5],
                'comment': row[6],
                'session_id': row[7]
            })
        
        conn.close()
        
        return {
            "count": len(feedbacks),
            "feedbacks": feedbacks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export feedback: {str(e)}")
