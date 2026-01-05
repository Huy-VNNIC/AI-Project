"""
API đơn giản để kiểm tra thay đổi
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import logging

# Thiết lập logging
logging.basicConfig(
    filename='test_api_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_api')

# Thêm thư mục gốc vào đường dẫn
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from requirement_analyzer.estimator import EffortEstimator
from requirement_analyzer.ml_requirement_analyzer import MLRequirementAnalyzer

app = Flask(__name__)
CORS(app)

# Khởi tạo các thành phần
estimator = EffortEstimator()
analyzer = MLRequirementAnalyzer()

@app.route('/estimate', methods=['POST'])
def estimate():
    """API endpoint để ước lượng từ văn bản"""
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({"error": "Thiếu văn bản yêu cầu"}), 400
        
        text = data['text']
        method = data.get('method', 'weighted_average')
        
        # Phân tích yêu cầu
        logger.info(f"Đang phân tích yêu cầu: {text[:50]}...")
        analysis = analyzer.analyze_requirements_document(text)
        logger.info(f"Hoàn thành phân tích, có {len(analysis)} tham số")
        
        # Ước lượng nỗ lực
        logger.info(f"Đang ước lượng với phương thức: {method}")
        estimation = estimator._integrated_estimate(analysis, method)
        logger.info("Hoàn thành ước lượng")
        
        # Log kết quả chi tiết hơn
        log_message = "===== PHÂN TÍCH KẾT QUẢ =====\n"
        log_message += f"1. Các mô hình ước lượng: {estimation.get('model_estimates', {})}\n"
        log_message += "\n2. Tham số đầu vào:\n"
        log_message += f"  - Số tham số input: {len(analysis)}\n"
        log_message += f"  - Các loại tham số: {list(analysis.keys())}\n"
        if 'loc_linear' in analysis:
            log_message += f"  - LOC Linear params: {analysis['loc_linear']}\n"
        if 'loc_random_forest' in analysis:
            log_message += f"  - LOC Random Forest params: {analysis['loc_random_forest']}\n"
        if 'cocomo' in analysis:
            log_message += f"  - COCOMO params: {analysis['cocomo']}\n"
        
        log_message += "\n3. Kết quả đánh giá:\n"
        log_message += f"  - Total Effort: {estimation.get('total_effort', 'N/A')}\n"
        log_message += f"  - Confidence Level: {estimation.get('confidence_level', 'N/A')}\n"
        
        logger.info(log_message)
        print(log_message)
        
        return jsonify(estimation), 200
    
    except Exception as e:
        error_msg = f"Lỗi: {str(e)}"
        logger.error(error_msg)
        logger.exception("Chi tiết lỗi:")
        print(error_msg)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"API đang chạy tại http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)