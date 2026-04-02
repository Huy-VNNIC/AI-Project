"""
Report Generator with Charts and Visualizations
Tạo báo cáo chuyên nghiệp với biểu đồ, thống kê chi tiết
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np


class ReportGenerator:
    """Generate professional reports with visualizations"""
    
    def __init__(self, test_data: Dict[str, Any]):
        """
        Args:
            test_data: Output from AITestCaseGeneratorV3.generate()
        """
        self.test_data = test_data
        self.detailed = test_data.get('detailed', [])
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.colors = {
            'critical': '#FF6B6B',
            'high': '#FFA500',
            'medium': '#FFD700',
            'happy': '#4CAF50',
            'negative': '#FF6B6B',
            'equivalence': '#2196F3',
            'state': '#9C27B0',
            'boundary': '#FF9800'
        }
    
    def generate_html_report(self) -> str:
        """Generate interactive HTML report with embedded charts"""
        html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Case Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #0f766e 0%, #06b6d4 50%, #0369a1 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .timestamp {{
            font-size: 12px;
            opacity: 0.8;
            margin-top: 10px;
        }}
        .content {{
            padding: 40px;
        }}
        .section {{
            margin-bottom: 40px;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 20px;
            background: #f9f9f9;
        }}
        .section h2 {{
            color: #0369a1;
            margin-bottom: 20px;
            font-size: 24px;
            border-bottom: 3px solid #0369a1;
            padding-bottom: 10px;
        }}
        .section h3 {{
            color: #333;
            margin-top: 20px;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-box {{
            background: white;
            border-left: 5px solid #0369a1;
            padding: 20px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-box .number {{
            font-size: 32px;
            font-weight: bold;
            color: #0369a1;
        }}
        .stat-box .label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .chart-container {{
            position: relative;
            width: 100%;
            height: 300px;
            margin-bottom: 20px;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .table th {{
            background: #0369a1;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        .table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        .table tr:hover {{
            background: #f5f5f5;
        }}
        .priority-critical {{ background: #ffebee; color: #c62828; }}
        .priority-high {{ background: #fff3e0; color: #e65100; }}
        .priority-medium {{ background: #fffde7; color: #f57f17; }}
        .confidence-high {{ color: #2e7d32; font-weight: bold; }}
        .confidence-medium {{ color: #f57c00; font-weight: bold; }}
        .confidence-low {{ color: #d32f2f; font-weight: bold; }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f9f9f9;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 12px;
        }}
        .requirement-breakdown {{
            background: white;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #0369a1;
        }}
        .requirement-breakdown .req-id {{
            font-weight: bold;
            color: #0369a1;
            margin-bottom: 5px;
        }}
        .requirement-breakdown .req-text {{
            color: #333;
            margin-bottom: 10px;
        }}
        .test-type-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin: 2px;
            font-weight: 600;
        }}
        .badge-happy {{ background: #c8e6c9; color: #2e7d32; }}
        .badge-negative {{ background: #ffccbc; color: #d84315; }}
        .badge-equivalence {{ background: #bbdefb; color: #1565c0; }}
        .badge-state {{ background: #e1bee7; color: #6a1b9a; }}
        .badge-boundary {{ background: #ffe0b2; color: #e65100; }}
        .page-break {{
            page-break-after: always;
            margin-top: 40px;
            margin-bottom: 40px;
            border: none;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
            .page-break {{ page-break-after: always; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header_html()}
        <div class="content">
            {self._generate_overview_html()}
            {self._generate_charts_html()}
            {self._generate_distribution_html()}
            {self._generate_requirement_breakdown_html()}
            {self._generate_quality_metrics_html()}
        </div>
        {self._generate_footer_html()}
    </div>
</body>
</html>
"""
        return html
    
    def _generate_header_html(self) -> str:
        """Generate report header"""
        return f"""
        <div class="header">
            <h1>📊 Test Case Analysis Report</h1>
            <p>AI-Generated Test Cases với NLP Analysis</p>
            <p class="timestamp">Ngày tạo: {self.timestamp}</p>
        </div>
"""
    
    def _generate_overview_html(self) -> str:
        """Generate overview statistics"""
        total_reqs = len(self.detailed)
        total_tests = sum(r.get('test_cases_count', 0) for r in self.detailed)
        avg_confidence = self.test_data.get('avg_nlp_confidence', 0)
        
        return f"""
        <div class="section">
            <h2>📈 Tổng Quan</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="number">{total_reqs}</div>
                    <div class="label">Requirements</div>
                </div>
                <div class="stat-box">
                    <div class="number">{total_tests}</div>
                    <div class="label">Test Cases</div>
                </div>
                <div class="stat-box">
                    <div class="number">{avg_confidence:.1%}</div>
                    <div class="label">NLP Confidence</div>
                </div>
                <div class="stat-box">
                    <div class="number">{total_tests/total_reqs if total_reqs > 0 else 0:.1f}</div>
                    <div class="label">Test/Requirement</div>
                </div>
            </div>
        </div>
"""
    
    def _generate_charts_html(self) -> str:
        """Generate chart containers"""
        return """
        <div class="section">
            <h2>📊 Biểu Đồ Phân Tích</h2>
            
            <h3>1. Phân Bố Loại Test Case</h3>
            <div class="chart-container">
                <canvas id="testTypeChart"></canvas>
            </div>
            
            <h3>2. Phân Bố Mức Độ Priority</h3>
            <div class="chart-container">
                <canvas id="priorityChart"></canvas>
            </div>
            
            <h3>3. Phân Bố Độ Tin Cậy</h3>
            <div class="chart-container">
                <canvas id="confidenceChart"></canvas>
            </div>
            
            <h3>4. Trend Độ Tin Cậy theo Requirement</h3>
            <div class="chart-container">
                <canvas id="trendChart"></canvas>
            </div>
        </div>
        
        <script>
            {self._generate_chart_scripts()}
        </script>
"""
    
    def _generate_chart_scripts(self) -> str:
        """Generate Chart.js script data"""
        # Collect statistics
        test_type_count = {}
        priority_count = {}
        confidence_values = []
        
        for req in self.detailed:
            for tc in req.get('test_cases', []):
                tc_type = tc.get('type', 'other')
                test_type_count[tc_type] = test_type_count.get(tc_type, 0) + 1
                
                priority = tc.get('priority', 'MEDIUM')
                priority_count[priority] = priority_count.get(priority, 0) + 1
                
                confidence = float(tc.get('confidence', 0.85))
                confidence_values.append(confidence)
        
        # Prepare data for charts
        test_types = list(test_type_count.keys())
        test_type_values = list(test_type_count.values())
        
        priorities = list(priority_count.keys())
        priority_values = list(priority_count.values())
        
        confidence_bins = [0.0, 0.0, 0.0, 0.0]  # <70%, 70-80%, 80-90%, >90%
        for conf in confidence_values:
            if conf < 0.7:
                confidence_bins[0] += 1
            elif conf < 0.8:
                confidence_bins[1] += 1
            elif conf < 0.9:
                confidence_bins[2] += 1
            else:
                confidence_bins[3] += 1
        
        req_ids = [r.get('requirement_id', f"REQ-{i}") for i, r in enumerate(self.detailed)]
        req_confidences = [r.get('nlp_confidence', 0) for r in self.detailed]
        
        return f"""
            // Test Type Distribution
            const testTypeCtx = document.getElementById('testTypeChart').getContext('2d');
            new Chart(testTypeCtx, {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(test_types)},
                    datasets: [{{
                        data: {json.dumps(test_type_values)},
                        backgroundColor: [
                            '#4CAF50', '#FF6B6B', '#2196F3', '#9C27B0', '#FF9800'
                        ],
                        borderColor: 'white',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'bottom' }}
                    }}
                }}
            }});
            
            // Priority Distribution
            const priorityCtx = document.getElementById('priorityChart').getContext('2d');
            new Chart(priorityCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(priorities)},
                    datasets: [{{
                        label: 'Số lượng Test Cases',
                        data: {json.dumps(priority_values)},
                        backgroundColor: ['#FF6B6B', '#FFA500', '#FFD700'],
                        borderRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: true }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});
            
            // Confidence Distribution
            const confidenceCtx = document.getElementById('confidenceChart').getContext('2d');
            new Chart(confidenceCtx, {{
                type: 'bar',
                data: {{
                    labels: ['< 70%', '70-80%', '80-90%', '> 90%'],
                    datasets: [{{
                        label: 'Số lượng Test Cases',
                        data: {json.dumps(confidence_bins)},
                        backgroundColor: ['#FF6B6B', '#FFA500', '#FFD700', '#4CAF50'],
                        borderRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});
            
            // Confidence Trend
            const trendCtx = document.getElementById('trendChart').getContext('2d');
            new Chart(trendCtx, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(req_ids[:20])},  // First 20 requirements
                    datasets: [{{
                        label: 'NLP Confidence',
                        data: {json.dumps(req_confidences[:20])},
                        borderColor: '#0369a1',
                        backgroundColor: 'rgba(3, 105, 161, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#0369a1',
                        pointBorderColor: 'white',
                        pointBorderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: true }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 1,
                            ticks: {{
                                format: {{ style: 'percent' }}
                            }}
                        }}
                    }}
                }}
            }});
        """
    
    def _generate_distribution_html(self) -> str:
        """Generate distribution tables"""
        # Count test types
        type_counts = {}
        for req in self.detailed:
            for tc in req.get('test_cases', []):
                tc_type = tc.get('type', 'other')
                type_counts[tc_type] = type_counts.get(tc_type, 0) + 1
        
        type_rows = "".join([
            f'<tr><td>{t}</td><td>{c}</td><td>{c/sum(type_counts.values())*100:.1f}%</td></tr>'
            for t, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        ])
        
        return f"""
        <div class="section">
            <h2>📋 Phân Tích Chi Tiết</h2>
            
            <h3>Phân Bố Loại Test Case</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Loại Test</th>
                        <th>Số Lượng</th>
                        <th>Tỷ Lệ %</th>
                    </tr>
                </thead>
                <tbody>
                    {type_rows}
                </tbody>
            </table>
        </div>
"""
    
    def _generate_requirement_breakdown_html(self) -> str:
        """Generate detailed requirement breakdown"""
        requirement_rows = ""
        
        for req in self.detailed:
            req_id = req.get('requirement_id', 'UNKNOWN')
            req_text = req.get('requirement', '')[:100]
            test_count = req.get('test_cases_count', 0)
            confidence = req.get('nlp_confidence', 0)
            
            confidenceclass = 'confidence-high' if confidence >= 0.85 else ('confidence-medium' if confidence >= 0.75 else 'confidence-low')
            
            # Count test types for this requirement
            test_types_html = ""
            if req.get('test_cases'):
                type_map = {}
                for tc in req['test_cases']:
                    tc_type = tc.get('type', 'other')
                    type_map[tc_type] = type_map.get(tc_type, 0) + 1
                
                badge_map = {
                    'happy_path': 'badge-happy',
                    'negative': 'badge-negative',
                    'equivalence_partition': 'badge-equivalence',
                    'state_transition': 'badge-state',
                    'boundary_value': 'badge-boundary'
                }
                
                for tc_type, count in sorted(type_map.items()):
                    badge_class = badge_map.get(tc_type, '')
                    test_types_html += f'<span class="test-type-badge {badge_class}">{tc_type}: {count}</span>'
            
            requirement_rows += f"""
            <div class="requirement-breakdown">
                <div class="req-id">{req_id}</div>
                <div class="req-text">{req_text}...</div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        {test_types_html}
                    </div>
                    <div style="text-align: right;">
                        <span style="margin-right: 20px;">Test Cases: <strong>{test_count}</strong></span>
                        <span class="{confidenceclass}">Confidence: {confidence:.1%}</span>
                    </div>
                </div>
            </div>
"""
        
        return f"""
        <div class="section">
            <h2>📝 Chi Tiết Từng Requirement</h2>
            {requirement_rows}
        </div>
"""
    
    def _generate_quality_metrics_html(self) -> str:
        """Generate quality metrics"""
        total_tests = sum(r.get('test_cases_count', 0) for r in self.detailed)
        avg_confidence = self.test_data.get('avg_nlp_confidence', 0)
        
        # Calculate coverage
        happy_tests = sum(len([tc for tc in r.get('test_cases', []) if tc.get('type') == 'happy_path']) for r in self.detailed)
        negative_tests = sum(len([tc for tc in r.get('test_cases', []) if tc.get('type') == 'negative']) for r in self.detailed)
        
        return f"""
        <div class="section">
            <h2>✅ Chỉ Số Chất Lượng</h2>
            <table class="table">
                <tr>
                    <th>Chỉ Số</th>
                    <th>Giá Trị</th>
                    <th>Đánh Giá</th>
                </tr>
                <tr>
                    <td>Độ Tin Cậy NLP</td>
                    <td><strong>{avg_confidence:.1%}</strong></td>
                    <td>{'✓ Tốt (>85%)' if avg_confidence >= 0.85 else '⚠ Trung Bình' if avg_confidence >= 0.75 else '✗ Cần Cải Thiện'}</td>
                </tr>
                <tr>
                    <td>Test Happy Path</td>
                    <td><strong>{happy_tests}</strong> ({happy_tests/total_tests*100:.1f}%)</td>
                    <td>{'✓ Tốt (>10%)' if happy_tests/total_tests > 0.1 else '⚠ Cần Thêm'}</td>
                </tr>
                <tr>
                    <td>Test Negative</td>
                    <td><strong>{negative_tests}</strong> ({negative_tests/total_tests*100:.1f}%)</td>
                    <td>{'✓ Tốt (>20%)' if negative_tests/total_tests > 0.2 else '⚠ Cần Thêm'}</td>
                </tr>
                <tr>
                    <td>Tổng Test Cases</td>
                    <td><strong>{total_tests}</strong></td>
                    <td>{'✓ Đầy Đủ (>100)' if total_tests > 100 else '⚠ Cần Thêm'}</td>
                </tr>
            </table>
        </div>
"""
    
    def _generate_footer_html(self) -> str:
        """Generate report footer"""
        return f"""
        <div class="footer">
            <p>Generated by AI Test Case Generator v3 | {self.timestamp}</p>
            <p>© 2026 AI-Project. All Rights Reserved.</p>
        </div>
"""
    
    def generate_pdf_report(self) -> bytes:
        """Generate PDF report with charts"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            # Create PDF
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0369a1'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("📊 Test Case Analysis Report", title_style))
            story.append(Paragraph(f"Generated: {self.timestamp}", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Overview Stats
            story.append(Paragraph("📈 Tổng Quan", styles['Heading2']))
            total_reqs = len(self.detailed)
            total_tests = sum(r.get('test_cases_count', 0) for r in self.detailed)
            avg_confidence = self.test_data.get('avg_nlp_confidence', 0)
            
            overview_data = [
                ['Chỉ Số', 'Giá Trị'],
                ['Requirements', str(total_reqs)],
                ['Test Cases', str(total_tests)],
                ['NLP Confidence', f'{avg_confidence:.1%}'],
                ['Test/Requirement', f'{total_tests/total_reqs if total_reqs > 0 else 0:.1f}']
            ]
            
            overview_table = Table(overview_data)
            overview_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0369a1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white])
            ]))
            story.append(overview_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Test Type Distribution
            story.append(PageBreak())
            story.append(Paragraph("📋 Phân Tích Chi Tiết", styles['Heading2']))
            
            type_counts = {}
            for req in self.detailed:
                for tc in req.get('test_cases', []):
                    tc_type = tc.get('type', 'other')
                    type_counts[tc_type] = type_counts.get(tc_type, 0) + 1
            
            type_data = [['Loại Test', 'Số Lượng', 'Tỷ Lệ %']]
            for t, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                type_data.append([t, str(c), f'{c/sum(type_counts.values())*100:.1f}%'])
            
            type_table = Table(type_data)
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0369a1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white])
            ]))
            story.append(type_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Requirement Breakdown
            story.append(Paragraph("📝 Chi Tiết Requirement", styles['Heading3']))
            for req in self.detailed[:10]:  # First 10 requirements
                req_id = req.get('requirement_id', 'UNKNOWN')
                req_text = req.get('requirement', '')[:80]
                confidence = req.get('nlp_confidence', 0)
                test_count = req.get('test_cases_count', 0)
                
                story.append(Paragraph(
                    f"<b>{req_id}</b> - {req_text}... (Confidence: {confidence:.1%}, Tests: {test_count})",
                    styles['Normal']
                ))
            
            # Build PDF
            doc.build(story)
            return pdf_buffer.getvalue()
        
        except ImportError:
            return b"PDF library not installed. Install reportlab: pip install reportlab"
    
    def export_statistics_json(self) -> str:
        """Export statistics as JSON for dashboard/analytics"""
        stats = {
            "timestamp": self.timestamp,
            "total_requirements": len(self.detailed),
            "total_test_cases": sum(r.get('test_cases_count', 0) for r in self.detailed),
            "average_confidence": self.test_data.get('avg_nlp_confidence', 0),
            "test_type_distribution": {},
            "priority_distribution": {},
            "confidence_distribution": self._calculate_confidence_distribution(),
            "quality_score": self._calculate_quality_score(),
            "recommendations": self._generate_recommendations()
        }
        
        # Count by type and priority
        for req in self.detailed:
            for tc in req.get('test_cases', []):
                tc_type = tc.get('type', 'other')
                stats['test_type_distribution'][tc_type] = stats['test_type_distribution'].get(tc_type, 0) + 1
                
                priority = tc.get('priority', 'MEDIUM')
                stats['priority_distribution'][priority] = stats['priority_distribution'].get(priority, 0) + 1
        
        return json.dumps(stats, indent=2, ensure_ascii=False)
    
    def _calculate_confidence_distribution(self) -> Dict[str, int]:
        """Calculate confidence distribution"""
        distribution = {
            "very_low": 0,  # < 70%
            "low": 0,       # 70-80%
            "medium": 0,    # 80-90%
            "high": 0       # > 90%
        }
        
        for req in self.detailed:
            confidence = req.get('nlp_confidence', 0)
            if confidence < 0.7:
                distribution['very_low'] += 1
            elif confidence < 0.8:
                distribution['low'] += 1
            elif confidence < 0.9:
                distribution['medium'] += 1
            else:
                distribution['high'] += 1
        
        return distribution
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score (0-100)"""
        total_tests = sum(r.get('test_cases_count', 0) for r in self.detailed)
        avg_confidence = self.test_data.get('avg_nlp_confidence', 0)
        
        # Count diverse test types
        test_types = set()
        for req in self.detailed:
            for tc in req.get('test_cases', []):
                test_types.add(tc.get('type', 'other'))
        
        test_diversity = len(test_types) / 5 * 20  # max 20 points
        confidence_score = avg_confidence * 60  # 60 points
        coverage_score = min(total_tests / 100 * 20, 20)  # 20 points for >100 tests
        
        return min(test_diversity + confidence_score + coverage_score, 100)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        total_tests = sum(r.get('test_cases_count', 0) for r in self.detailed)
        avg_confidence = self.test_data.get('avg_nlp_confidence', 0)
        
        if avg_confidence < 0.75:
            recommendations.append("⚠️ Độ tin cậy NLP thấp - Hãy làm rõ requirements")
        
        if total_tests < 50:
            recommendations.append("⚠️ Số test cases ít - Nên tăng complexity requirements")
        
        # Check test type diversity
        test_types = set()
        for req in self.detailed:
            for tc in req.get('test_cases', []):
                test_types.add(tc.get('type', 'other'))
        
        if len(test_types) < 3:
            recommendations.append("⚠️ Thiếu diversity trong test types - Nên thêm negative/boundary tests")
        
        if len(recommendations) == 0:
            recommendations.append("✓ Chất lượng test case tốt - Sẵn sàng triển khai")
        
        return recommendations
