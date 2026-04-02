"""
Pipeline Orchestrator
Combines all components into a complete processing pipeline
"""

from typing import List, Dict, Any
from pathlib import Path

from input_processor import InputProcessor
from text_preprocessor import TextPreprocessor
from sentence_segmenter import SentenceSegmenter
from semantic_extractor import SemanticExtractor
from normalizer import Normalizer
from requirement_structurer import RequirementStructurer
from test_generator import TestGenerator
from export_handler import ExportHandler


class TestGenerationPipeline:
    """Complete test generation pipeline"""
    
    def __init__(self):
        """Initialize all components"""
        self.input_processor = InputProcessor()
        self.preprocessor = TextPreprocessor()
        self.segmenter = SentenceSegmenter()
        self.extractor = SemanticExtractor()
        self.normalizer = Normalizer()
        self.structurer = RequirementStructurer()
        self.generator = TestGenerator()
    
    def process_file(
        self,
        filepath: str,
        output_format: str = "json",
        export_path: str = None
    ) -> Dict[str, Any]:
        """
        Process a complete requirement file end-to-end
        
        Args:
            filepath: Path to input file (PDF, DOCX, TXT)
            output_format: Format for output (json, excel, csv, markdown)
            export_path: Optional path to save export
            
        Returns:
            Dict with results
        """
        print(f"\n{'='*70}")
        print(f"🚀 Processing: {filepath}")
        print('='*70)
        
        # Step 1: Extract
        print(f"\n📂 Step 1: Extracting text from {Path(filepath).name}")
        raw_text = self.input_processor.extract_text(filepath)
        print(f"   ✓ Extracted {len(raw_text)} characters")
        
        # Step 2: Preprocess
        print(f"\n🧹 Step 2: Preprocessing text")
        cleaned_text = self.preprocessor.process(raw_text)
        print(f"   ✓ Cleaned text, removed noise")
        
        # Step 3: Segment
        print(f"\n✂️ Step 3: Segmenting requirements")
        requirements = self.segmenter.segment(cleaned_text)
        print(f"   ✓ Found {len(requirements)} requirement sentences")
        
        # Step 4: Extract semantics
        print(f"\n🧠 Step 4: Extracting semantic information")
        extracted = []
        for i, req in enumerate(requirements, 1):
            try:
                ext = self.extractor.extract(req)
                extracted.append(ext)
                print(f"   ✓ [{i}/{len(requirements)}] Extracted from: {req[:50]}...")
            except Exception as e:
                print(f"   ⚠️ [{i}/{len(requirements)}] Failed: {e}")
        
        # Step 5: Normalize
        print(f"\n🔄 Step 5: Normalizing requirements")
        normalized = [self.normalizer.normalize(ext) for ext in extracted]
        print(f"   ✓ Normalized {len(normalized)} requirements")
        
        # Step 6: Structure
        print(f"\n🔧 Step 6: Structuring requirements")
        structured = self.structurer.structure_batch(normalized)
        print(f"   ✓ Structured {len(structured)} requirements")
        
        # Step 7: Generate tests
        print(f"\n🧪 Step 7: Generating test cases")
        test_cases = self.generator.generate_batch(structured)
        print(f"   ✓ Generated {len(test_cases)} test cases")
        
        # Step 8: Export
        print(f"\n📤 Step 8: Exporting in {output_format} format")
        
        results = {
            "status": "success",
            "input_file": filepath,
            "requirements": [req.to_dict() for req in structured],
            "test_cases": [tc.to_dict() for tc in test_cases],
            "summary": {
                "total_requirements": len(structured),
                "total_test_cases": len(test_cases),
                "export_format": output_format,
            }
        }
        
        # Save export if path provided
        if export_path:
            if output_format == "json":
                ExportHandler.to_json_file(test_cases, export_path)
            elif output_format == "excel":
                ExportHandler.to_excel(test_cases, export_path)
            elif output_format == "csv":
                ExportHandler.to_csv(test_cases, export_path)
            elif output_format == "markdown":
                ExportHandler.to_markdown_file(test_cases, export_path)
            
            print(f"   ✓ Exported to: {export_path}")
            results["export_file"] = export_path
        
        print(f"\n{'='*70}")
        print(f"✅ Pipeline completed successfully!")
        print(f"{'='*70}\n")
        
        return results
    
    def process_text(
        self,
        text: str,
        output_format: str = "json",
        export_path: str = None
    ) -> Dict[str, Any]:
        """
        Process requirement text directly
        
        Args:
            text: Requirement text
            output_format: Format for output
            export_path: Optional export path
            
        Returns:
            Dict with results
        """
        print(f"\n{'='*70}")
        print(f"🚀 Processing requirement text")
        print('='*70)
        
        # Step 2: Preprocess
        print(f"\n🧹 Step 1: Preprocessing text")
        cleaned_text = self.preprocessor.process(text)
        
        # Step 3: Segment
        print(f"\n✂️ Step 2: Segmenting requirements")
        requirements = self.segmenter.segment(cleaned_text)
        print(f"   ✓ Found {len(requirements)} requirement sentences")
        
        # Step 4-7: Follow same flow
        print(f"\n🧠 Step 3: Extracting semantic information")
        extracted = []
        for req in requirements:
            try:
                ext = self.extractor.extract(req)
                extracted.append(ext)
            except Exception as e:
                print(f"   ⚠️ Failed: {e}")
        
        print(f"\n🔄 Step 4: Normalizing")
        normalized = [self.normalizer.normalize(ext) for ext in extracted]
        
        print(f"\n🔧 Step 5: Structuring")
        structured = self.structurer.structure_batch(normalized)
        
        print(f"\n🧪 Step 6: Generating test cases")
        test_cases = self.generator.generate_batch(structured)
        print(f"   ✓ Generated {len(test_cases)} test cases")
        
        results = {
            "status": "success",
            "requirements": [req.to_dict() for req in structured],
            "test_cases": [tc.to_dict() for tc in test_cases],
            "summary": {
                "total_requirements": len(structured),
                "total_test_cases": len(test_cases),
            }
        }
        
        # Save export
        if export_path:
            if output_format == "json":
                ExportHandler.to_json_file(test_cases, export_path)
            elif output_format == "excel":
                ExportHandler.to_excel(test_cases, export_path)
            
            print(f"\n📤 Exported to: {export_path}")
            results["export_file"] = export_path
        
        print(f"\n{'='*70}\n")
        
        return results


# Demo
if __name__ == "__main__":
    # Create sample text file
    sample_requirements = """
    # Hotel Management System Requirements
    
    ## User Authentication
    - User must be able to login with email and password
    - System should validate email format
    - Password must be at least 8 characters
    - If login fails, display error message
    
    ## Booking Management
    - User can create new room booking with check-in and check-out dates
    - System must verify room availability
    - User can cancel existing booking
    - When user cancels, system should process refund
    
    ## Security Requirements
    - System must authenticate every request
    - XSS attacks must be prevented
    - SQL injection must be blocked
    """
    
    # Run pipeline
    pipeline = TestGenerationPipeline()
    
    # Process text
    results = pipeline.process_text(
        sample_requirements,
        output_format="json",
        export_path="/tmp/test_cases.json"
    )
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"  Requirements: {results['summary']['total_requirements']}")
    print(f"  Test Cases: {results['summary']['total_test_cases']}")
