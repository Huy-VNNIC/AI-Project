# Tools Directory

Thư mục này chứa các Python utility scripts và tools hỗ trợ cho dự án.

## Danh sách Tools

### Demo Scripts
- `demo.py` - Demo script cơ bản
- `demo_infrastructure.py` - Demo infrastructure
- `demo_task_generation.py` - Demo task generation
- `simple_demo.py` - Demo đơn giản
- `quick_demo.py` - Quick demo

### Testing Scripts
- `test_*.py` - Các file test khác nhau
- `simple_test.py` - Test đơn giản

### Model Scripts
- `cocomo_ii_predictor.py` - Module dự đoán COCOMO II
- `model_retrainer.py` - Huấn luyện lại models
- `train_loc_models.py` - Huấn luyện LOC models

### Fix Scripts
- `fix_*.py` - Các scripts sửa lỗi và điều chỉnh
- `adjust_model_coefficients.py` - Điều chỉnh hệ số model
- `apply_weight_integration.py` - Áp dụng tích hợp weights

### Service Scripts
- `run_estimation_service.py` - Service ước lượng nỗ lực
- `feedback_api.py` - API cho hệ thống feedback
- `feedback_collector.py` - Thu thập feedback

### Configuration Scripts
- `config_task_gen_template.py` - Template cấu hình task generation
- `create_sample_models.py` - Tạo sample models
- `packages.py` - Quản lý packages

### Analysis Scripts
- `check_prescoring.py` - Kiểm tra prescoring
- `debug_entities.py` - Debug entities
- `visualize_models_python.py` - Visualize models

### Utility Scripts
- `init_nltk.py` - Khởi tạo NLTK
- `scheduled_retraining.py` - Tự động huấn luyện lại
- `upload_to_space.py` - Upload lên Space
- `run_matlab_visualizations.py` - Chạy MATLAB visualizations

### Frontend Scripts
- `fix_frontend_display.js` - Fix frontend display

## Sử dụng

Chạy các scripts từ thư mục gốc của dự án:
```bash
python tools/[script-name].py
```

Hoặc với module:
```bash
python -m tools.[script-name]
```
