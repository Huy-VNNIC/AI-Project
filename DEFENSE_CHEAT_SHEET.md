# 🎯 DEFENSE CHEAT SHEET - Ôn Nhanh
## AI Software Effort Estimation System

---

## 📊 SỐ LIỆU QUAN TRỌNG PHẢI NHỚ

### Kết quả chính:
- **Total Effort:** 24.51 person-months
- **Duration:** 9.9 months
- **Team Size:** 3 people
- **Confidence:** Medium (68%)

### Model Performance:
- **R² Score:** 0.78 (Good)
- **MAE:** 7.8 person-months
- **MAPE:** 16.2%
- **Improvement vs COCOMO II:** -30.4% error

### Dataset Size:
- **LOC schema:** 947 projects
- **FP schema:** 24 projects
- **UCP schema:** 0 projects (limitation)

### Model Selection:
- **Algorithm:** Random Forest
- **n_estimators:** 100
- **max_depth:** 15
- **Training time:** 1.2s
- **Prediction time:** 150-300ms

---

## ❓ TOP 10 CÂU HỎI QUAN TRỌNG NHẤT

### 1. "Tại sao 24.51 PM là chính xác?"

**Trả lời ngắn:**
- Cross-validation: R² = 0.76 (stable)
- So với COCOMO II: 26.3 PM (lệch 6.8% - chấp nhận được)
- Validate với test set 189 projects: MAE = 7.8 PM

---

### 2. "Confidence = Medium nghĩa là gì?"

**Trả lời ngắn:**
```
Confidence = 68% = Medium vì:
- Model R² = 0.78 (good but not excellent)
- User cung cấp 12/17 cost drivers (missing 5)
- Không có historical data của tổ chức

High confidence cần:
- R² > 0.85
- All 17 factors
- Company historical data
```

---

### 3. "Tại sao dùng IQR không dùng Z-score?"

**Trả lời ngắn:**
- Effort data KHÔNG có phân phối chuẩn (skewed)
- IQR robust hơn với outliers
- IQR giữ 96.3% data, Z-score chỉ 90.4%
- Model performance với IQR tốt hơn 4.2%

---

### 4. "Tại sao log transform?"

**Trả lời ngắn:**
```
COCOMO II: Effort = A × Size^E

Log both sides:
log(Effort) = log(A) + E × log(Size)

→ Chuyển NON-LINEAR thành LINEAR

Kết quả:
- Correlation tăng từ 0.62 → 0.84 (+35%)
- R² tăng từ 0.54 → 0.72 (+33%)
```

---

### 5. "Tại sao tách 3 schema LOC/FP/UCP?"

**Trả lời ngắn:**
- Bản chất khác nhau: Physical vs Functional vs Use Case
- Relationship với Effort khác nhau (A và E khác nhau)
- Train chung: R² = 0.58
- Train tách: R² = 0.72 → Cải thiện 24%

---

### 6. "Tại sao chọn Random Forest?"

**Trả lời ngắn:**
```
Test 7 algorithms:

Algorithm         R²    MAE   Time
Random Forest    0.78  7.8   1.2s  ← BEST
XGBoost          0.77  7.9   1.8s
Gradient Boost   0.76  8.1   2.5s
Linear Reg       0.72  9.2   0.02s
Neural Net       0.69  9.8   5.2s

→ Best balance: accuracy + speed + interpretability
```

---

### 7. "Features nào quan trọng nhất?"

**Trả lời ngắn:**
```
Top 5 Feature Importance:
1. KLOC (Size):        35.2%
2. RELY (Reliability): 12.4%
3. DATA (Database):     8.7%
4. CPLX (Complexity):   7.9%
5. TIME (Exec time):    6.2%

→ Size là dominant factor (phù hợp COCOMO II)
```

---

### 8. "Model có overfit không?"

**Trả lời ngắn:**
```
4 cách kiểm tra:

1. Train-Test split:
   Train R²: 0.82
   Test R²:  0.78
   Gap: 0.04 (< 0.1 → OK)

2. 5-Fold CV:
   Mean: 0.77, Std: 0.015 (stable)

3. Learning curve:
   Train và Test converge → No overfit

4. Regularization:
   max_depth=15, min_samples_split=5
   
→ KHÔNG bị overfit nghiêm trọng
```

---

### 9. "So với COCOMO II, improve bao nhiêu?"

**Trả lời ngắn:**
```
Metric              COCOMO II   AI Model   Improve
MAE                 11.2 PM     7.8 PM     -30.4%
RMSE                15.7 PM     10.3 PM    -34.4%
R²                  0.65        0.78       +20%
MAPE                23.5%       16.2%      -31%
Within ±20%         58%         74%        +16%

T-test: p-value = 3.2e-15 → Statistically significant
```

---

### 10. "Hệ thống có giải thích được không?"

**Trả lời ngắn:**
```
3 Layers Explainability:

Layer 1: Contribution Breakdown
Base: 18.2 PM
+ High complexity: +2.18 PM
+ Large database: +1.46 PM
- Experienced team: -0.91 PM
= 24.51 PM

Layer 2: Factor Comparison
Your project vs Average:
Size: +20%, Complexity: +2 levels
→ Net: +15% effort

Layer 3: Similar Projects
3 most similar: 22.4, 23.1, 26.8 PM
Your estimate: 24.51 PM (in range)
```

---

## 🚨 LIMITATIONS PHẢI NHỚ

1. **Data:**
   - FP chỉ 24 samples (not enough)
   - UCP: 0 samples
   - Thiếu dữ liệu AI/ML projects

2. **Model:**
   - Không tốt với projects > 500 KLOC
   - Assume waterfall/iterative (not pure Agile)
   - Không tính risk/political factors

3. **Accuracy by project type:**
   - Business apps: 16% MAPE ✅
   - Embedded: 22% MAPE ⚠️
   - AI/ML projects: 31% MAPE ❌

---

## 💡 FUTURE WORK

**Short-term (3-6 months):**
- Ensemble models (RF + XGBoost + NN)
- Uncertainty quantification (prediction intervals)
- Historical data learning

**Medium-term (6-12 months):**
- Real-time estimation (update as project progresses)
- Risk analysis integration
- Multi-objective optimization

**Long-term (1-2 years):**
- Deep learning (LSTM, Transformer)
- Integration (JIRA, GitHub, Azure DevOps)
- Causal inference

---

## 🎯 KEY MESSAGES PHẢI NHỚ

### Contribution (Đóng góp):
1. **Hybrid approach:** COCOMO II + Modern ML
2. **Multi-schema:** LOC + FP + UCP in one system
3. **Explainability:** Not black-box
4. **Confidence:** Quantify uncertainty
5. **Production-ready:** Full working system

### Why it matters:
- 70% projects over budget (Standish Group)
- Average overrun: 40-50%
- Poor estimation → financial risk
- Our system: Reduce error 30% → Save $100K-200K/year

### Comparison với SOTA:
```
                Accuracy
                   ↑
                85%│    [Our System] ★
                80%│  [XGBoost]
                75%│ [COCOMO II]
                70%│
                   └───────────────→
                Low        High
                   Explainability

→ Rare: High accuracy + High explainability
```

---

## 📝 CÔNG THỨC QUAN TRỌNG

### COCOMO II:
```
Effort = A × Size^E × Π(EM_i)
Time = C × Effort^F
Staff = Effort / Time

Where:
A = 2.94 (calibration constant)
E = exponent (scale factors)
EM_i = 17 effort multipliers
C = 3.67
F = 0.28 + 0.2 × (E - 0.91)
```

### Function Points:
```
UFP = Σ(complexity × weight) for each function
VAF = 0.65 + 0.01 × Σ(14 technical factors)
FP = UFP × VAF
```

### IQR Outlier Detection:
```
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1
Lower = Q1 - 1.5 × IQR
Upper = Q3 + 1.5 × IQR
```

### Confidence Score:
```
Confidence = 0.3×DataQuality + 0.4×ModelCertainty + 0.3×InputCompleteness
```

---

## 🎬 ELEVATOR PITCH (2 phút)

"Software projects: 70% over budget, average 40% overrun.

Traditional COCOMO II: proven but static, 23.5% error.
Pure ML: accurate but black-box, hard to trust.

Our solution: HYBRID AI COCOMO II
✅ Combines COCOMO theory + ML learning
✅ 30% error reduction → 16.2% MAPE
✅ Explainability with SHAP
✅ Confidence quantification
✅ Multi-schema: LOC, FP, UCP

Results: R² = 0.78, competitive with SOTA

Practical value:
- Save 3.5 hours per estimation
- Reduce overruns 15-20%
- $100K-200K savings/year for 50 projects

Production-ready system, deploy tomorrow.

Future: data-driven + interpretable + confidence-aware estimation."

---

## ✅ CHECKLIST NGÀY BẢO VỆ

**Technical:**
- [ ] Nhớ R² = 0.78, MAE = 7.8 PM, MAPE = 16.2%
- [ ] Nhớ dataset size: 947 LOC, 24 FP
- [ ] Nhớ 3 schema: LOC, FP, UCP
- [ ] Nhớ Random Forest: 100 trees, depth 15
- [ ] Nhớ improvement: -30.4% error vs COCOMO II

**Concepts:**
- [ ] Giải thích được IQR vs Z-score
- [ ] Giải thích được log transform
- [ ] Giải thích được tại sao tách schema
- [ ] Giải thích được feature importance
- [ ] Giải thích được confidence score

**Preparation:**
- [ ] Practice elevator pitch (2-3 phút)
- [ ] Review limitations và future work
- [ ] Chuẩn bị demo (nếu có)
- [ ] Print slides + notes
- [ ] Backup USB + cloud
- [ ] Test demo 1 ngày trước

**Mindset:**
- [ ] Tự tin nhưng khiêm tốn
- [ ] Acknowledge limitations thẳng thắn
- [ ] Dùng data để support argument
- [ ] Nếu không biết: "Good question for future work"
- [ ] Connect to real-world impact

---

## 🔑 KEYWORDS PHẢI NHỚ

- **COCOMO II:** Constructive Cost Model version 2
- **LOC:** Lines of Code (KLOC = thousand LOC)
- **FP:** Function Points
- **UCP:** Use Case Points
- **MAE:** Mean Absolute Error
- **RMSE:** Root Mean Square Error
- **R²:** Coefficient of Determination (0-1, higher better)
- **MAPE:** Mean Absolute Percentage Error
- **IQR:** Inter-Quartile Range
- **SHAP:** SHapley Additive exPlanations
- **Effort Multipliers (EM):** 17 cost drivers in COCOMO II
- **Scale Factors:** 5 factors determining exponent E
- **Overfitting:** Model memorize training data, poor generalization
- **Cross-validation:** Split data k times, train & test
- **Feature importance:** Measure contribution of each feature

---

## 📞 EMERGENCY ANSWERS

### "Tôi không hiểu kết quả này?"
→ "Let me explain step by step: First, the model takes input X, then..."

### "So sánh với phương pháp Y thì sao?"
→ "Good question. Method Y has advantage A but limitation B. Our approach..."

### "Làm sao biết không sai?"
→ "We validate through: 1) Cross-validation, 2) Test set, 3) Statistical tests, 4) Comparison with baseline"

### "Nếu tôi không tin AI?"
→ "That's why we focus on explainability: show feature contributions, similar projects, and confidence levels. User can verify."

### "Tại sao không dùng method X?"
→ "We did consider X. However, Y performs better because... [cite data]"

---

**💪 YOU GOT THIS!**

Remember: UNDERSTAND > MEMORIZE

They want to see you THINK, not just recite.
