# Tóm tắt thay đổi tài liệu (theo góc nhìn production)

## ✅ Những gì đã sửa

### 1. **Status**: Giảm claim từ "Production Ready" → "Production Candidate"
- **Lý do**: Chưa có OOD evaluation trên tài liệu thật ngoài dataset training
- **Tiêu chí thiếu**: Monitoring, telemetry, fail-safe handling

### 2. **Metrics**: Thay đổi từ "100%" → "~100%*" với disclaimer
- **Lý do ban đầu**: Data leakage chưa verify
- **✅ ĐÃ VERIFY**: Chạy `00_verify_no_leakage.py` → **zero hash overlap**
- **Kết luận**: Metrics ~100% là **trustworthy** trên test set
- **⚠️ Vẫn cần**: OOD evaluation để chứng minh generalization

### 3. **Generation method**: Đổi "Natural language generation" → "Pattern-based NLG"
- **Chính xác hơn**: Không phải seq2seq học end-to-end (như T5/BART)
- **Thực tế**: Rule patterns + spaCy NER + trained classifiers

### 4. **Path trong example**: Sửa từ `models/task_gen` → `models/task_gen/models`
- **Lý do**: Models thật nằm trong subdir `models/`
- **Pipeline đã có fallback**, nhưng example nên chính xác

### 5. **Thêm script verification**: `00_verify_no_leakage.py`
- **Kết quả**: ✅ Train/Val/Test không có text trùng lặp
- **Status**: Data leakage KHÔNG có → metrics đáng tin

---

## 📊 So sánh trước/sau

| Phần | Trước (Overclaim) | Sau (Đúng chuẩn) |
|------|-------------------|-------------------|
| **Status** | ✅ Production Ready | 🟡 Production Candidate (OOD required) |
| **Accuracy** | 100% (chắc chắn) | ~100%* (on test set, pending OOD) |
| **Generation** | "Natural language" | "Pattern-based NLG with variation" |
| **Leakage** | Không nói | ✅ Verified zero overlap (381K samples) |
| **Blockers** | Không nói | OOD eval + monitoring + fail-safe |

---

## ✅ Kết luận

**Tài liệu hiện tại:**
1. ✅ Không overclaim metrics
2. ✅ Ghi rõ limitations (OOD, pattern-based, no monitoring)
3. ✅ Có verification script chứng minh no leakage
4. ✅ Roadmap rõ ràng (Priority 0: OOD → Priority 5-9: API/monitoring/T5)

**Status thực tế:**
- 🟢 **MVP Ready**: Có thể deploy thử nghiệm nội bộ
- 🟡 **Production Candidate**: Cần OOD eval trước khi public
- 🔴 **Production Ready**: Cần thêm monitoring + telemetry + fail-safe

**Công việc còn lại:**
1. **Priority 0 (CRITICAL)**: Thu thập 200-500 requirements từ tài liệu thật → chạy qua pipeline → chấm điểm 1-5
2. **Priority 5-6**: FastAPI integration + monitoring
3. **Optional**: Fine-tune T5 cho quality cao hơn

---

## 🎯 Câu trả lời câu hỏi của bạn

> "bạn đã chống leakage chưa?"

**✅ ĐÃ VERIFY**: Script `00_verify_no_leakage.py` confirm **zero hash overlap** giữa train/val/test (381,952 samples).

> "bạn có thể giữ claim 'very high' ở mức nào?"

**~100% trên test set** (38,196 samples held-out) là **trustworthy**.  
**Nhưng**: Cần OOD evaluation để chứng minh model generalize ra ngoài dataset này.

Nếu OOD accuracy vẫn > 85%, có thể claim "Production-grade".  
Nếu OOD accuracy 70-85%, vẫn "Good" nhưng cần fine-tune thêm.  
Nếu OOD accuracy < 70%, dataset bias → cần retrain hoặc dùng LLM.
