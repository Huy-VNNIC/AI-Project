# V2 Requirements Engineering Pipeline - Evaluation Report

Generated: 2026-01-27 01:20:36

## Executive Summary

- **Total Requirements Processed:** 100
- **Total User Stories Generated:** 484
- **Total Subtasks Generated:** 1456
- **Total Gaps Detected:** 282
- **Average INVEST Score:** 24.16/30
- **Processing Time:** 0.05s
- **Success Rate:** 100.0%

## Detailed Metrics

### Requirement Processing

- Avg stories per requirement: 4.84
- Avg subtasks per requirement: 14.56
- Avg gaps per requirement: 2.82

### Gap Analysis

- Critical gaps: 4
- High severity gaps: 93

### Gap Type Distribution

- ambiguity: 91
- missing_nfr: 84
- missing_actor: 75
- missing_error_handling: 14
- missing_data_validation: 5
- missing_object: 5
- missing_security: 4
- missing_integration: 4

### INVEST Score Distribution

- Excellent (25-30): 132
- Good (20-24): 352
- Fair (15-19): 0
- Poor (<15): 0

## Sample Outputs

### Sample 1: REQ001

**Original:** - Phát triển hệ thống quản lý khách sạn toàn diện để tự động hóa các quy trình...

**Refinement:**
- Title: Quản lý khách sạn toàn diện để
- User Story: Là một Quản lý, tôi muốn quản lý khách sạn toàn diện để tự động hóa các quy trình, để tự động hóa các quy trình.
- AC Count: 2
- NFRs: 0

**Gaps Detected:** 2
- [Low] ambiguity: Chỉ có 2 AC (khuyến nghị 3-8)...
- [Low] missing_nfr: Không có yêu cầu phi chức năng (NFR)...

**Slicing:** 5 stories, 15 subtasks
- Slice S1 (workflow): 2 stories
- Slice S2 (data): 3 stories

**Quality Metrics:**
- Refinement Score: 0.45
- Gap Coverage: 0.40
- Avg INVEST: 24.00
- Processing Time: 0.00s

---

### Sample 2: REQ002

**Original:** - Cải thiện trải nghiệm khách hàng thông qua giao diện đặt phòng và quản lý đơn giản...

**Refinement:**
- Title: Quản lý đơn giản
- User Story: Là một Quản lý, tôi muốn quản lý đơn giản, Cải thiện trải nghiệm khách hàng thông qua giao diện đặt phòng và quản lý đơn gi.
- AC Count: 2
- NFRs: 1

**Gaps Detected:** 1
- [Low] ambiguity: Chỉ có 2 AC (khuyến nghị 3-8)...

**Slicing:** 7 stories, 21 subtasks
- Slice S1 (workflow): 2 stories
- Slice S2 (role): 2 stories
- Slice S3 (data): 3 stories

**Quality Metrics:**
- Refinement Score: 0.70
- Gap Coverage: 0.20
- Avg INVEST: 24.00
- Processing Time: 0.00s

---

### Sample 3: REQ003

**Original:** - Tối ưu hóa hiệu suất quản lý và tăng doanh thu...

**Refinement:**
- Title: Quản lý và tăng doanh thu
- User Story: Là một Quản lý, tôi muốn quản lý và tăng doanh thu, tăng doanh thu.
- AC Count: 2
- NFRs: 1

**Gaps Detected:** 1
- [Low] ambiguity: Chỉ có 2 AC (khuyến nghị 3-8)...

**Slicing:** 5 stories, 15 subtasks
- Slice S1 (workflow): 2 stories
- Slice S2 (data): 3 stories

**Quality Metrics:**
- Refinement Score: 0.70
- Gap Coverage: 0.20
- Avg INVEST: 24.00
- Processing Time: 0.00s

---

## Traceability Sample

**REQ001 Traceability:**

- Stories: REQ001_ST01, REQ001_ST02, REQ001_ST03, REQ001_ST04, REQ001_ST05
- Tasks: REQ001_ST01 → REQ001_ST01_T01,REQ001_ST01_T02,REQ001_ST01_T03

## Recommendations

⚠️  **HIGH PRIORITY:** 4 critical gaps detected. Review with Product Owner immediately.

✅ Pipeline executed successfully. All requirements processed with full traceability.

