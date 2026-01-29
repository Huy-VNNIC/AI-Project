# Scripts Directory

Thư mục này chứa tất cả các shell scripts (.sh) để chạy, triển khai và thiết lập dự án.

## Danh sách Scripts

### Deployment Scripts
- `deploy.sh` - Triển khai dự án
- `deploy-production.sh` - Triển khai production
- `deploy-api-production.sh` - Triển khai API production
- `deploy_to_huggingface.sh` - Triển khai lên HuggingFace

### Service Scripts
- `run_estimation_service.sh` - Khởi động service ước lượng
- `run_api_service.sh` - Khởi động API service
- `run_api_docker.sh` - Chạy API với Docker
- `start_estimation_service.sh` - Start estimation service

### Setup Scripts
- `setup_github.sh` - Thiết lập GitHub
- `setup_multi_model.sh` - Thiết lập multi-model
- `setup_requirement_analyzer.sh` - Thiết lập requirement analyzer
- `cocomo_setup.sh` - Thiết lập COCOMO

### Training Scripts
- `retrain_models_with_feedback.sh` - Huấn luyện lại models với feedback
- `retrain_with_current_features.sh` - Huấn luyện lại với features hiện tại

### Testing Scripts
- `run_all_tests.sh` - Chạy tất cả tests
- `test_api_fixes.sh` - Test API fixes
- `test_critical_fixes.sh` - Test critical fixes
- `test_feedback_api.sh` - Test feedback API
- `test_frontend_integration.sh` - Test frontend integration
- `test_infrastructure.sh` - Test infrastructure
- `test_task_generation.sh` - Test task generation

### Management Scripts
- `manage.sh` - Quản lý dự án
- `manage-production.sh` - Quản lý production

### Demo Scripts
- `run_demos.sh` - Chạy demos
- `quickstart_task_generation.sh` - Quickstart task generation

### Git Scripts
- `commit_to_github.sh` - Commit lên GitHub
- `push_to_github.sh` - Push lên GitHub

### Other Scripts
- `fix_sklearn_version.sh` - Fix sklearn version
- `package_for_huggingface.sh` - Đóng gói cho HuggingFace

## Sử dụng

Chạy script với quyền thực thi:
```bash
chmod +x scripts/[script-name].sh
./scripts/[script-name].sh
```

Hoặc sử dụng bash trực tiếp:
```bash
bash scripts/[script-name].sh
```
