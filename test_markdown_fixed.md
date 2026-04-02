# Healthcare System Requirements (Hệ Thống Y Tế)

## User Stories & Features

### 1. Patient Registration Module
This module handles all patient registration and intake processes.

- The system must allow patients to register online for medical appointments
- Hệ thống phải quản lý hồ sơ bệnh nhân với thông tin cá nhân đầy đủ
- Hệ thống phải tạo số thứ tự khám tự động

### 2. Appointment Management
Manage doctor's schedules and patient appointments.

- Hệ thống phải quản lý lịch làm việc của bác sĩ theo ca và phòng khám
- Hệ thống phải cho phép đặt lịch hẹn trước 30 ngày
- Hệ thống phải gửi SMS/email nhắc nhở trước giờ khám

### 3. Medical Examination
Doctors examine patients and record findings.

- Hệ thống phải tích hợp với thiết bị đo sinh hiệu (huyết áp, nhịp tim, nhiệt độ)
- Hệ thống phải cảnh báo dị ứng thuốc khi tiếp nhận
- Hệ thống phải cảnh báo tương tác thuốc nguy hiểm

### 4. Laboratory Testing
Manage lab tests and results.

- Hệ thống phải quản lý phiếu chỉ định xét nghiệm
- Hệ thống phải theo dõi trạng thái mẫu xét nghiệm
- Hệ thống phải cho phép bác sĩ xem kết quả xét nghiệm online

### 5. Image Diagnosis (PACS)
Handle medical imaging and DICOM standards.

- Hệ thống phải quản lý chỉ định chụp X-quang, CT, MRI, siêu âm
- Hệ thsimulator phải tích hợp với hệ thống PACS lưu ảnh y khoa
- Hệ thống phải lưu trữ ảnh theo chuẩn DICOM

### 6. Pharmacy Management
Control drug inventory and dispensing.

- Hệ thống phải quản lý kho thuốc với tồn kho và hạn sử dụng
- Hệ thống phải cảnh báo thuốc sắp hết hạn hoặc hết tồn kho
- Hệ thống phải bán thuốc theo đơn và kiểm tra đơn hợp lệ

### 7. Inpatient Management
Manage patient hospitalizations.

- Hệ thống phải quản lý nhập viện với phân giường bệnh
- Hệ thống phải theo dõi tình trạng giường bệnh
- Hệ thống phải quản lý dinh dưỡng và chế độ ăn của bệnh nhân

### 8. Billing & Payment
Handle hospital invoicing and payments.

- Hệ thống phải tính toán viện phí bao gồm khám, thuốc, xét nghiệm, nội trú
- Hệ thống phải xuất hóa đơn điện tử theo quy định
- Hệ thống phải xử lý thanh toán qua BHYT và thanh toán tự nguyện

### 9. Reporting & Analytics
Generate hospital reports and statistics.

- Hệ thống phải báo cáo doanh thu theo khoa, dịch vụ, thời gian
- Hệ thống phải thống kê số lượt khám theo chuyên khoa
- Hệ thống phải xuất báo cáo theo quy định của Bộ Y tế

## Non-Functional Requirements

### Performance
- The system must handle concurrent sessions
- Database backup must run every 4 hours
- Hệ thống phải xử lý 500 lượt khám đồng thời

### Security & Compliance
- Encrypt all patient data according to HIPAA standards
- Kiểm soát truy cập dựa trên vai trò (RBAC)
- Mã hóa dữ liệu bệnh nhân theo HIPAA
- Tuân thủ Luật An toàn Thông tin cá nhân
