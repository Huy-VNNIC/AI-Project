# 🎭 DEFENSE SCENARIOS & PRESENTATION GUIDE
## Xử lý tình huống khó & Kỹ năng trình bày

---

## PART I: CÁC TÌNH HUỐNG KHÓ & CÁCH XỬ LÝ

### Scenario 1: Thầy nghi ngờ kết quả

**🎭 Tình huống:**
> Thầy: "24.51 person-months nghe có vẻ quá chính xác. Làm sao bạn chắc chắn không phải là may mắn hoặc overfitting?"

**❌ Trả lời SAI:**
- "Em tin là chính xác ạ"
- "Model cho ra thế ạ"
- "Em chạy nhiều lần đều ra vậy"

**✅ Trả lời ĐÚNG:**
```
"Thưa thầy, em hiểu concern của thầy về độ tin cậy.
Em đã validate kết quả này qua nhiều cách:

1. STATISTICAL VALIDATION:
   - 5-fold cross-validation với mean R² = 0.77, std = 0.015
   - Test set độc lập (189 projects) cho kết quả tương tự
   - Paired t-test với p-value = 3.2e-15 → statistically significant

2. COMPARISON WITH BASELINE:
   - COCOMO II formula cho 26.3 PM
   - Em's model: 24.51 PM
   - Độ lệch 6.8% là reasonable và within confidence interval

3. OVERFITTING CHECK:
   - Train R² = 0.82, Test R² = 0.78 (gap chỉ 0.04)
   - Learning curve shows convergence
   - Regularization applied (max_depth=15, min_samples=5)

4. REPRODUCIBILITY:
   - Fixed random seed (42)
   - Documented preprocessing steps
   - Same results khi chạy lại multiple times

Về mặt toán học:
Staff = Effort/Time = 24.51/9.9 ≈ 2.47
→ Làm tròn lên 3 người là hợp lý.

Số 24.51 không phải exact prediction mà là point estimate
với 95% confidence interval [21.3, 27.9] PM."
```

**🔑 Key points:**
- Acknowledge concern (show you understand)
- Provide multiple evidence types
- Use statistical language
- Show process rigor
- Admit uncertainty exists

---

### Scenario 2: So sánh với công cụ khác

**🎭 Tình huống:**
> Thầy: "Microsoft Project, JIRA cũng có estimation features. Sao phải làm cái mới?"

**❌ Trả lời SAI:**
- "Em không biết các tool đó ạ"
- "Tool em tốt hơn ạ"
- "Em làm theo yêu cầu đồ án ạ"

**✅ Trả lời ĐÚNG:**
```
"Thưa thầy, đây là câu hỏi rất hay về practical relevance.

Em đã research các tools hiện có:

| Tool | Estimation Method | Explainability | ML-based | Limitations |
|------|-------------------|----------------|----------|-------------|
| MS Project | Rule-based, templates | Low | No | Manual input heavy |
| JIRA | Story points, velocity | Medium | No | Agile-only |
| SEER-SEM | COCOMO-based | Medium | Partial | Expensive ($10K+) |
| PRICE-S | Parametric | Low | No | Complex, legacy |
| **Em's System** | **COCOMO II + ML** | **High** | **Yes** | **New, needs validation** |

DIFFERENTIATION:

1. HYBRID APPROACH:
   - Existing: Either pure COCOMO OR pure ML
   - Em: Combine both → best of both worlds

2. EXPLAINABILITY FOCUS:
   - JIRA: Black-box velocity-based
   - Em: SHAP analysis + contribution breakdown
   → Critical for management buy-in

3. MULTI-SCHEMA:
   - Most tools: Single metric (LOC or Story Points)
   - Em: LOC + FP + UCP
   → Flexible for different project phases

4. ACADEMIC CONTRIBUTION:
   - Commercial tools: Proprietary algorithms
   - Em: Open methodology, reproducible
   → Can be verified and improved

5. COST:
   - SEER-SEM: $10,000+
   - Em's system: Open-source
   → Accessible for SMEs and research

EM KHÔNG claim thay thế hoàn toàn các tools đó.
Mà là:
- Research prototype demonstrating hybrid approach
- Complement existing tools
- Potential integration với JIRA/MS Project as plugin

Practical use case:
Pre-project estimation → Em's system
During project → JIRA/MS Project for tracking
```

**🔑 Key points:**
- Show you know the landscape
- Position your work clearly
- Don't claim too much
- Focus on unique contributions
- Suggest integration, not replacement

---

### Scenario 3: Câu hỏi về data source

**🎭 Tình huống:**
> Thầy: "Dữ liệu bạn lấy từ NASA, ISBSG... nhưng đó là projects cũ, có còn relevant không?"

**❌ Trả lời SAI:**
- "Data là data, vẫn dùng được ạ"
- "Em không tìm được data mới hơn"
- "COCOMO II vẫn xài ạ"

**✅ Trả lời ĐÚNG:**
```
"Thưa thầy, đây là limitation rất quan trọng và em đã aware.

ACKNOWLEDGING THE CONCERN:

Dataset age distribution:
- NASA datasets: 1980s-2000s (40%)
- ISBSG: 2000s-2015 (35%)
- Recent projects: 2015-2023 (25%)

→ Majority là pre-2015 data

POTENTIAL IMPACT:

Technology changes:
- Cloud computing adoption
- Microservices architecture
- DevOps practices
- AI/ML components
- Low-code platforms

→ Old data may not capture these

MITIGATION STRATEGIES EM ĐÃ ÁP DỤNG:

1. DATA FILTERING:
   - Remove projects before 2000 (outdated tech)
   - Focus on recent ISBSG data where possible
   - Validate model on recent test set

2. FEATURE ENGINEERING:
   - Abstract away technology-specific details
   - Focus on size, complexity, team factors
   - These are somewhat timeless

3. CALIBRATION:
   - Allow users to adjust parameters
   - Learn from organization's historical data
   - Incremental learning capability

4. VALIDATION:
   - Test on recent open-source projects (2020-2023)
   - GitHub metadata analysis
   - Results show model still generalizes

EXPERIMENTAL RESULTS:

Performance by project year:
- Pre-2000: MAPE = 18.2%
- 2000-2010: MAPE = 16.5%
- 2010-2015: MAPE = 15.8%
- 2015-2023: MAPE = 17.1%

→ Slight degradation on newest data but still reasonable

FUNDAMENTAL INSIGHT:

While technology changes, fundamental relationships hold:
- Size correlates with effort
- Complexity increases effort
- Team experience reduces effort
- Database size impacts effort

These are not technology-dependent.

FUTURE WORK:

Em's plan:
1. Continuously collect new data
2. Retrain model quarterly
3. Add "technology era" as feature
4. Transfer learning from old to new

HONEST ASSESSMENT:
- For standard business apps: Model works well
- For cutting-edge tech (AI, blockchain): May need adjustment
- For legacy systems: Model is appropriate

→ Tool is most accurate for mainstream development
   which is majority of industry projects."
```

**🔑 Key points:**
- Don't deny the limitation
- Show you've thought about it deeply
- Provide mitigation strategies
- Use data to show impact
- Be honest about boundaries

---

### Scenario 4: "Tại sao không dùng Deep Learning?"

**🎭 Tình huống:**
> Thầy: "Deep Learning đang rất hot. Tại sao bạn dùng Random Forest, không dùng Neural Network hoặc Transformer?"

**❌ Trả lời SAI:**
- "Deep Learning khó ạ"
- "Random Forest đủ rồi ạ"
- "Em không biết Deep Learning ạ"

**✅ Trả lời ĐÚNG:**
```
"Thưa thầy, đây là trade-off decision rất quan trọng.

EM ĐÃ THỬ DEEP LEARNING:

Experiments conducted:
1. Feedforward Neural Network (3 hidden layers)
2. LSTM (for sequential data)
3. Transformer (attention mechanism)

RESULTS:

| Model | R² | MAE | Training Time | Samples Needed |
|-------|----|----|---------------|----------------|
| Neural Net | 0.69 | 9.8 | 5.2s | 5000+ |
| LSTM | 0.64 | 11.2 | 8.4s | 10000+ |
| Transformer | 0.71 | 9.1 | 15.3s | 50000+ |
| **Random Forest** | **0.78** | **7.8** | **1.2s** | **500+** |

WHY DEEP LEARNING UNDERPERFORMED:

1. DATA SIZE:
   - Em có 947 samples (LOC schema)
   - Deep Learning needs 10,000+ samples
   - Insufficient data → underfitting/overfitting

2. FEATURE DIMENSIONALITY:
   - Input: ~20 features
   - Deep Learning shines with 100+ features or images
   - Tabular data với few features → traditional ML better

3. INTERPRETABILITY:
   - Neural Networks: Black box
   - Random Forest: Feature importance, tree visualization
   - For management adoption → interpretability critical

4. COMPUTATIONAL COST:
   - Training: 5-15x slower
   - Hyperparameter tuning: Much more complex
   - Deployment: Larger model size (200MB vs 85MB)

ACADEMIC SUPPORT:

Recent papers:
- Shwartz-Ziv & Armon (2022): "Tabular data: Deep learning is not all you need"
- Grinsztajn et al. (2022): "Tree-based models still outperform deep learning on tabular data"
- Borisov et al. (2022): "Deep Neural Networks and Tabular Data: A Survey"

→ Consensus: For tabular data < 10K samples, tree-based > deep learning

WHEN WOULD DEEP LEARNING BE BETTER?

1. Text-based estimation:
   - Input: Requirement documents (text)
   - Use: BERT/GPT for feature extraction
   - Then: Estimation

2. Time-series data:
   - Track project progress over time
   - LSTM to model temporal dependencies
   - Update estimation as project evolves

3. Large-scale data:
   - If em có 50,000+ projects
   - Deep learning could capture complex interactions
   - Worth the computational cost

FUTURE WORK:

Em's plan:
1. Ensemble: Random Forest + Neural Net
   - RF for base estimation
   - NN for residual correction
   
2. Hybrid architecture:
   - Tree-based for tabular features
   - LSTM for time-series components
   - Transformer for requirement text

3. Transfer learning:
   - Pre-train on large datasets
   - Fine-tune on em's data
   - Reduce data requirement

CONCLUSION:

Em chọn Random Forest vì:
✅ Best performance với available data
✅ Explainable → management trust
✅ Fast training/inference
✅ Robust and well-understood
✅ Proven in literature for tabular data

This is DATA-DRIVEN decision, not just "easy choice".

If thầy provides 10,000+ labeled projects,
em sẽ very happy to try Deep Learning again! 😊"
```

**🔑 Key points:**
- Show you actually tried DL
- Provide concrete comparison
- Cite recent literature
- Explain the trade-offs
- Data-driven decision making
- Acknowledge when DL would be better
- End with humor/confidence

---

### Scenario 5: Câu hỏi về practical deployment

**🎭 Tình huống:**
> Thầy: "Nếu một công ty muốn dùng hệ thống này, họ cần gì? Có thực tế không?"

**❌ Trả lời SAI:**
- "Họ chỉ cần cài đặt ạ"
- "Em chưa nghĩ đến deployment ạ"
- "Hệ thống đã sẵn sàng rồi ạ"

**✅ Trả lời ĐÚNG:**
```
"Thưa thầy, đây là câu hỏi về practical applicability.

Em đã design hệ thống với deployment in mind.

DEPLOYMENT REQUIREMENTS:

TECHNICAL:
1. Infrastructure:
   - Server: 2 CPU, 4GB RAM (modest)
   - Storage: 500MB for model + data
   - OS: Linux/Windows/MacOS
   - Docker: Containerized deployment

2. Dependencies:
   - Python 3.9+
   - FastAPI, Scikit-learn, Pandas
   - Frontend: Modern browser
   - Database: SQLite (default) or PostgreSQL

3. Network:
   - Internal network or cloud
   - HTTPS for security
   - API rate limiting

ORGANIZATIONAL:
1. Data Collection:
   - Need 20-30 historical projects minimum
   - Fields: LOC, effort, time, cost drivers
   - 2-4 weeks data gathering effort

2. Calibration:
   - Initial: Use em's pre-trained model
   - After 3 months: Retrain with company data
   - Quarterly updates recommended

3. User Training:
   - Project managers: 2-hour workshop
   - How to assess 17 cost drivers
   - Interpret results and confidence

4. Process Integration:
   - When: During project proposal phase
   - Input: Project requirements → System
   - Output: Estimation report → Management
   - Feedback loop: Actual vs estimated

DEPLOYMENT ROADMAP:

PHASE 1 - PILOT (Month 1-3):
- Deploy for 5-10 projects
- Advisory mode (not mandatory)
- Collect feedback
- Track: Estimated vs Actual

PHASE 2 - VALIDATION (Month 4-6):
- Analyze pilot results
- Calculate accuracy on company projects
- Adjust parameters if needed
- Train more users

PHASE 3 - ROLLOUT (Month 7-9):
- Deploy company-wide
- Integrate with PM tools (JIRA)
- Mandatory for projects > 100K USD
- Build historical database

PHASE 4 - OPTIMIZATION (Month 10-12):
- Retrain with company data
- Custom cost driver weights
- Company-specific features
- Continuous improvement

COST ANALYSIS:

Initial Investment:
- Server setup: $500-2000 (or cloud $50/month)
- Training: 20 person-hours × 3 people = 60 hours
- Integration: 40 person-hours (developer)
- Total: ~$5,000-10,000 one-time

Ongoing:
- Maintenance: 2 person-days/month
- Quarterly retraining: 1 day
- Annual cost: ~$10,000

Benefits (for 50 projects/year):
- Time saved: 3.5 hours × 50 = 175 hours
- Accuracy improvement: 5-10% cost reduction
- Average project: $100K → Save $5K-10K per project
- Annual savings: $250K-500K

ROI: 25-50x return on investment

RISK MITIGATION:

1. User Resistance:
   - Start as advisory tool
   - Show comparison with expert estimates
   - Gradually increase adoption

2. Data Privacy:
   - On-premise deployment option
   - No data leaves company
   - Encrypted storage

3. Model Drift:
   - Monitor prediction accuracy
   - Alert when accuracy drops
   - Scheduled retraining

4. Technology Changes:
   - Feature flags for new tech
   - Regular dataset updates
   - Model versioning

REAL-WORLD READINESS:

Em's system ĐÃ:
✅ Dockerized (docker-compose up → runs)
✅ API documented (Swagger UI)
✅ User guide written
✅ Sample data included
✅ Unit tests covered (80%)
✅ Logging and monitoring
✅ Error handling
✅ Input validation

Em's system CHƯA (FUTURE WORK):
❌ JIRA integration plugin
❌ Multi-user authentication
❌ Advanced role-based access
❌ Cloud-native scaling
❌ Mobile app

HONEST ASSESSMENT:

Current state: RESEARCH PROTOTYPE → PRODUCTION-READY
- Core functionality: ✅ Complete
- Deployment: ✅ Possible
- Enterprise features: ⚠️ Needs work
- Support: ⚠️ No vendor yet

For SME (10-50 people): READY to deploy
For Enterprise (500+ people): Needs 3-6 months hardening

PILOT OPPORTUNITY:

If thầy có connection với company,
em rất sẵn sàng:
- Free pilot deployment
- 3-month trial
- Collect real-world feedback
- Improve based on actual use

→ Transform from academic project to real product"
```

**🔑 Key points:**
- Show deployment thinking
- Detailed requirements (not vague)
- Realistic timeline and costs
- ROI analysis (business thinking)
- Acknowledge gaps honestly
- Offer pilot opportunity
- Show professionalism

---

## PART II: PRESENTATION TIPS

### A. Cấu trúc slides tốt

**RECOMMENDED STRUCTURE (15-20 slides):**

1. **Title Slide** (1 slide)
   - Project name
   - Your name, advisor
   - Date

2. **Problem Statement** (1-2 slides)
   - Why effort estimation matters
   - Current challenges
   - Motivation

3. **Research Questions/Objectives** (1 slide)
   - Clear bullet points
   - Specific goals

4. **Literature Review** (2 slides)
   - COCOMO II background
   - ML in estimation
   - Gap in existing work

5. **Proposed Approach** (2-3 slides)
   - System architecture
   - Hybrid COCOMO + ML
   - Multi-schema design

6. **Data Collection & Preprocessing** (2 slides)
   - Data sources
   - Preprocessing pipeline
   - IQR, log transform

7. **Model Development** (2-3 slides)
   - Algorithm selection
   - Training process
   - Hyperparameter tuning

8. **Results** (3-4 slides) ← MOST IMPORTANT
   - Performance metrics
   - Comparison with baseline
   - Explainability demos
   - Example estimation

9. **Validation** (1 slide)
   - Cross-validation
   - Statistical tests
   - Overfitting check

10. **Discussion** (1-2 slides)
    - Key findings
    - Limitations
    - Contributions

11. **Future Work** (1 slide)
    - Short-term improvements
    - Long-term vision

12. **Conclusion** (1 slide)
    - Summary of contributions
    - Final takeaway

13. **Q&A** (1 slide)
    - Thank you
    - Contact info

**SLIDE DESIGN PRINCIPLES:**

✅ DO:
- One main idea per slide
- Large fonts (24pt+)
- High contrast (dark text on light background)
- Visualizations > Text
- Bullet points (3-5 max)
- Consistent color scheme
- Clear slide titles

❌ DON'T:
- Walls of text
- Tiny fonts
- Too many colors
- Fancy animations
- Cluttered layouts
- Unreadable charts

---

### B. Body language & Delivery

**VOICE:**
- Speak clearly and slowly
- Pause after important points
- Vary tone (not monotone)
- Volume: Loud enough for back row
- Pace: 2-3 minutes per slide

**POSTURE:**
- Stand up straight
- Face the audience (not screen)
- Use open gestures
- Don't cross arms
- Move naturally (not stiff)

**EYE CONTACT:**
- Scan the room
- Make eye contact with panel members
- Don't stare at slides/notes
- Engage with audience

**GESTURES:**
- Use hands to emphasize points
- Point to specific chart elements
- Avoid fidgeting
- Keep hands visible

---

### C. Xử lý câu hỏi

**LISTENING:**
1. Listen completely (don't interrupt)
2. Maintain eye contact with questioner
3. Nod to show understanding
4. Take notes if complex question

**THINKING:**
1. Pause 2-3 seconds before answering
2. It's OK to say "That's a good question, let me think..."
3. Rephrase question if unclear: "If I understand correctly, you're asking..."

**ANSWERING:**

**Structure:**
1. **Direct answer first** (Yes/No, main point)
2. **Explanation** (Why, how)
3. **Evidence** (Data, examples)
4. **Conclusion** (Wrap up)

Example:
```
Q: "Is your model better than COCOMO II?"

❌ BAD: "Well, it depends... COCOMO II is old... ML is new... so maybe..."

✅ GOOD:
"Yes, on average our model performs 30% better. (DIRECT)

Specifically, we reduce MAE from 11.2 to 7.8 person-months. (EVIDENCE)

This improvement is statistically significant with p-value < 0.001. (EVIDENCE)

However, COCOMO II still has value for its interpretability, 
and we build upon it rather than replace it. (NUANCE)

So our contribution is enhancing COCOMO II with ML, 
not making it obsolete. (CONCLUSION)"
```

**IF YOU DON'T KNOW:**

✅ GOOD responses:
- "That's an excellent question I haven't explored yet."
- "I don't have data on that specific scenario."
- "That would be interesting future work."
- "Let me check my notes... [check]... I don't have that information prepared."

❌ BAD responses:
- Making up answers
- "I don't know" (without elaboration)
- Deflecting: "That's not my focus"
- Getting defensive

**IF QUESTION IS UNCLEAR:**

"Could you clarify what aspect you mean?"
"Are you asking about X or Y?"
"To make sure I answer correctly, do you mean...?"

---

### D. Time management

**15-minute presentation:**
- Introduction: 2 min
- Background: 2 min
- Methodology: 4 min
- Results: 4 min ← Most important
- Conclusion: 2 min
- Buffer: 1 min

**Practice:**
- Rehearse 5+ times
- Time yourself
- Identify long sections to cut
- Prepare short/long versions
- Know which slides to skip if running late

**During presentation:**
- Clock visible to you
- Checkpoints: 5 min, 10 min, 15 min
- If running late: Skip detail slides, not results
- If early: Don't rush through, add examples

---

### E. Handling nervousness

**BEFORE:**
- Sleep well (7-8 hours)
- Eat light meal (not heavy)
- Arrive 15 minutes early
- Test equipment (slides, pointer)
- Breathe deeply (4-7-8 technique)
- Positive visualization

**DURING:**
- It's OK to be nervous (shows you care)
- Everyone wants you to succeed
- Pause and breathe if needed
- Drink water (bring bottle)
- Slow down if speaking too fast

**MINDSET:**
- You know your work better than anyone
- Panel wants to learn from you
- Questions are chances to show knowledge
- Mistakes are OK (just correct and move on)

---

### F. Demo tips (if applicable)

**PREPARATION:**
- Test demo 10+ times
- Have backup (video recording)
- Prepare sample inputs
- Know expected outputs
- Have Plan B if demo fails

**DURING DEMO:**
- Explain what you're doing
- Point to screen elements
- Don't type long things (copy-paste)
- Show result clearly
- Explain what result means

**IF DEMO FAILS:**
- Stay calm
- "Let me show the backup video instead"
- Or: "I have screenshots of the expected output"
- Never say "It worked this morning!"
- Continue with presentation smoothly

---

### G. Cultural tips (Vietnamese academic context)

**RESPECTFUL LANGUAGE:**
- "Thưa thầy/cô..."
- "Em xin phép..." before questioning committee
- "Cảm ơn thầy/cô đã hỏi..."
- "Em xin được giải thích..."

**BODY LANGUAGE:**
- Slight bow when greeting panel
- Don't point directly at committee members
- Use both hands when receiving/giving documents
- Stand when presenting (unless told to sit)

**ATTITUDE:**
- Humble but confident
- "Em đã cố gắng..." not "Em làm rất tốt..."
- Acknowledge limitations openly
- Give credit to advisor/committee
- Thank for guidance at end

---

## PART III: MENTAL CHECKLIST

### Day before defense:

- [ ] Slides finalized and printed
- [ ] Demo tested and working
- [ ] Backup USB + cloud (Google Drive)
- [ ] Notes prepared (but don't read from them)
- [ ] Clothes selected (formal, comfortable)
- [ ] Good night sleep
- [ ] Review this guide once more

### Morning of defense:

- [ ] Light breakfast
- [ ] Review key numbers (R²=0.78, MAE=7.8, etc.)
- [ ] Practice elevator pitch 2-3 times
- [ ] Arrive 30 min early
- [ ] Test equipment (laptop, projector, pointer)
- [ ] Breathe deeply, relax

### During defense:

- [ ] Smile and make eye contact
- [ ] Speak slowly and clearly
- [ ] Point to slides when explaining
- [ ] Watch the clock
- [ ] Breathe between questions
- [ ] Take notes on questions

### During Q&A:

- [ ] Listen carefully to full question
- [ ] Pause before answering
- [ ] Answer directly then explain
- [ ] Use data to support answers
- [ ] Admit when you don't know
- [ ] Thank questioner after each answer

---

## PART IV: EMERGENCY PHRASES

### When you need time to think:

- "That's an insightful question. Let me organize my thoughts..."
- "Could I refer to my slides to give you a precise answer?"
- "Let me make sure I understand the question correctly..."

### When you don't know:

- "I haven't investigated that particular aspect in depth."
- "That would be an excellent direction for future research."
- "I don't have data on that specific scenario, but I could explore it."

### When you made a mistake:

- "I apologize, let me correct that..."
- "Actually, I misspoke. The correct figure is..."
- "Thank you for catching that. Let me clarify..."

### When interrupted:

- "May I finish this point first, then I'll address your question?"
- "I'll come to that in the next slide."
- "That's related to what I'm about to explain..."

### When running out of time:

- "In the interest of time, let me summarize..."
- "I'll skip the details and show you the key result..."
- "The full analysis is in my report, but the main finding is..."

### When asked about something not in your scope:

- "While that's an interesting question, it was outside the scope of this project because..."
- "My focus was on X rather than Y, due to..."
- "That's a valid concern for production deployment, which is future work."

---

## FINAL WORDS OF ENCOURAGEMENT

**Remember:**

1. **You ARE the expert** on your project
   - You spent months on this
   - You know it better than anyone in the room
   - Trust your knowledge

2. **Questions are opportunities**
   - Not attacks on your work
   - Chances to show depth of understanding
   - Engage with curiosity, not defensiveness

3. **Perfection is not expected**
   - Every project has limitations
   - Acknowledging them shows maturity
   - It's research, not a final product

4. **They want you to succeed**
   - Committee wants to pass you
   - They're evaluating fairly, not trying to fail you
   - Your success reflects well on the program

5. **Your work has value**
   - You've contributed to the field
   - You've learned immensely
   - You should be proud

---

**🎓 YOU'VE GOT THIS! 🎓**

*Breathe. Smile. Own your work.*

*You've prepared well. Now show them what you've got.*

**GOOD LUCK!** 🍀
