# 🚀 Running the Unified Test & Task Generation System

## Quick Start

### Single Command Start (Recommended)
```bash
cd /home/dtu/AI-Project/AI-Project
bash START_BOTH_SYSTEMS.sh
```

This will:
- ✅ Activate virtual environment
- ✅ Stop any existing processes on port 8000
- ✅ Start Unified System (Requirement Analyzer + Test Generator) on http://localhost:8000
- ✅ Automatically open unified UI

### Manual Start
```bash
cd /home/dtu/AI-Project/AI-Project
source .venv/bin/activate
python -m requirement_analyzer.api
```

---

## 📱 Access Points

| System | URL | Purpose |
|--------|-----|---------|
| **Unified UI** | http://localhost:8000 | Single interface for all tools |
| **API Docs** | http://localhost:8000/docs | Complete API documentation |
| **Dashboard** | http://localhost:8000/dashboard | Dashboard view |
| **Task Generation** | http://localhost:8000/task-generation | Task generation interface |

---

## 🧪 API Endpoints

### Task & Requirement Analysis
- `POST /api/v3/generate` - Generate tasks and test cases from requirements
- `POST /api/tasks/generate` - Generate tasks
- `GET /health` - Health check

### Test Case Generation (Integrated)
- `POST /api/v2/test-generation/generate-test-cases` - Generate test cases
- `POST /api/v2/test-generation/generate-from-tasks` - Generate from tasks
- `POST /api/v2/test-generation/export/{format}` - Export tests
- `GET /api/v2/test-generation/health` - Test generation health

### Unified API (New)
- `GET /api/unified/health` - Check system health
- `POST /api/unified/generate` - Generate using both systems
- `GET /api/unified/status` - System status

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────┐
│     Unified Web Interface (Port 8000)            │
│    (templates/unified_ui.html)                   │
│                                                 │
│  ┌─────────────┬─────────────────────┐         │
│  │  Analyzer   │  Test Generator      │         │
│  │  (Left)     │  (Right)             │         │
│  └─────────────┴─────────────────────┘         │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────▼────────────┐
        │  Main System API    │
        │  Port 8000          │
        │                     │
        │  - Requirement      │
        │    Analysis         │
        │  - Task Gen         │
        │  - Test Gen         │
        │  - Models & NLP     │
        └─────────────────────┘
```

---

## 🎯 Features

✅ **Single System** - Only port 8000 to manage
✅ **Integrated Test Generation** - Built-in to main system
✅ **Side-by-side Interface** - Compare analyzer vs test generation
✅ **No Icons** - Clean, text-only interface
✅ **Dark/Light Theme** - Toggle anytime
✅ **Real-time Health Monitoring** - Auto-updates
✅ **RESTful APIs** - Easy integration
✅ **Production Ready** - Full ML models integrated

---

## 📝 Testing the System

1. **Start the system:**
   ```bash
   bash START_BOTH_SYSTEMS.sh
   ```

2. **Open the unified UI:**
   ```
   http://localhost:8000
   ```

3. **Test Left Panel (Requirement Analysis):**
   - Enter: `Users should be able to register with email`
   - Click: `Analyze Requirements`
   - View results

4. **Test Right Panel (Test Generation):**
   - Enter: `System must validate password strength`
   - Click: `Generate Test Cases`
   - View test cases

5. **Check Results:**
   - Switch between result tabs
   - View JSON output
   - Copy results if needed

---

## 🛑 Stopping the System

### Using Script:
Press `Ctrl+C` in the terminal

### Force Kill:
```bash
lsof -ti:8000 | xargs kill -9
```

---

## 📚 Example Requirements

### Example 1: Authentication
```
Users can login with email and password
System must validate email format before assignment
Password must be at least 8 characters
Account locks after 5 failed attempts
```

### Example 2: Payment Processing
```
System processes payments securely
Invalid cards are rejected
Payment amount validation required
Duplicate transactions prevention
```

### Example 3: User Registration
```
Users can create accounts with email
Email confirmation required
Password strength validation
Duplicate email prevention
```

---

## 🔧 Troubleshooting

### Port 8000 Already in Use
```bash
lsof -ti:8000 | xargs kill -9
```

### Virtual Environment Error
```bash
cd /home/dtu/AI-Project/AI-Project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Can't Access http://localhost:8000
1. Check system is running:
   ```bash
   ps aux | grep requirement_analyzer
   ```

2. Check port is listening:
   ```bash
   lsof -i :8000
   ```

3. Restart the system:
   ```bash
   bash START_BOTH_SYSTEMS.sh
   ```

---

## 💡 Tips

✨ Everything runs on **port 8000** - simpler!
✨ Test Generation is **integrated** - no separate API needed
✨ Both tools work from **single interface** - faster workflow
✨ **Full API access** - build on top if needed
✨ All models **pre-loaded** - instant responses

---

## 📍 File Locations

| File | Location | Purpose |
|------|----------|---------|
| Startup Script | `/START_BOTH_SYSTEMS.sh` | Execute to start system |
| Unified UI | `/templates/unified_ui.html` | Main interface |
| Main API | `/app/main.py` | Core API server |
| Router Bridge | `/app/routers/unified.py` | API integration |
| Setup Guide | `/RUNNING_BOTH_SYSTEMS.md` | This file |
| Test Guide | `/TESTING_GUIDE.md` | Testing instructions |
| Overview | `/BOTH_SYSTEMS_SETUP.md` | System overview |

---

## ✅ Verification

After starting, you should see:

```
╔═══════════════════════════════════════════════════════════════╗
║                   ✅ SYSTEM STARTED                           ║
╚═══════════════════════════════════════════════════════════════╝

📱 Access the system:
  Unified Web Interface:  http://localhost:8000
  API Documentation:      http://localhost:8000/docs
  Dashboard:              http://localhost:8000/dashboard

Process ID:
  Main System: XXXXX

To stop the system, press Ctrl+C
```

---

**Ready to use! 🚀**

