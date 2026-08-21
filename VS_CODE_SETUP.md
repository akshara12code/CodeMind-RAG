# How to Run Codebase RAG in VS Code

Complete step-by-step guide to get the project running locally.

## ⚡ Quick Start (5 minutes)

### 1. Install Prerequisites

**On Mac/Linux:**
```bash
# Python 3.11+
python3 --version

# Node.js 18+
node --version
npm --version
```

**On Windows:**
- Download Python 3.11+ from [python.org](https://python.org)
- Download Node.js 18+ from [nodejs.org](https://nodejs.org)
- Install both with default settings

### 2. Clone/Setup Project

```bash
# Create project directory
mkdir codebase-rag
cd codebase-rag

# Copy all the files we created into this directory
# (or clone from GitHub if you set up a repo)
```

### 3. Open in VS Code

```bash
code .
```

---

## 🔧 Backend Setup (FastAPI)

### Step 1: Create Python Virtual Environment

**In VS Code Terminal:**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal.

### Step 2: Create requirements.txt

Create a file `backend/requirements.txt`:

```txt
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database & Storage
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0

# Embeddings & Search
sentence-transformers==2.2.2
qdrant-client==2.4.0
rank-bm25==0.2.2
numpy==1.24.3

# LLM & API
openai==1.3.0
anthropic==0.7.8
httpx==0.25.1

# Parsing & Processing
tree-sitter==0.20.4
aiofiles==23.2.1
python-multipart==0.0.6

# Utils
tiktoken==0.5.1
python-dateutil==2.8.2
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will take 2-3 minutes. Watch for any errors.

### Step 4: Create .env file

Create `backend/.env`:

```env
# FastAPI
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database (optional - uses mock DB for demo)
DATABASE_URL=postgresql://user:password@localhost:5432/codebase_rag

# Vector Store
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Embeddings
EMBEDDING_MODEL=sentence-transformers/code-bge-base-en-v1
EMBEDDING_DIMENSION=768

# LLM - Choose one
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo

# Or use Anthropic instead:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-api-key-here
# ANTHROPIC_MODEL=claude-3-opus-20240229
```

**Note:** For demo purposes, you can skip real API keys - the app has mock responses.

### Step 5: Run Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ **Backend is running!** Visit http://localhost:8000 in browser to see API docs.

---

## 🎨 Frontend Setup (React)

### Step 1: Open New Terminal in VS Code

Press `Ctrl+Shift+` (backtick) to open another terminal while backend runs.

### Step 2: Navigate to Frontend

```bash
cd frontend
```

### Step 3: Create package.json

Create `frontend/package.json`:

```json
{
  "name": "codebase-rag-frontend",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.292.0",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.5",
    "postcss": "^8.4.31",
    "autoprefixer": "^10.4.16"
  }
}
```

### Step 4: Install Dependencies

```bash
npm install
```

This will take 2-5 minutes.

### Step 5: Create Vite Config

Create `frontend/vite.config.js`:

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### Step 6: Create Tailwind Config

Create `frontend/tailwind.config.js`:

```js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### Step 7: Create PostCSS Config

Create `frontend/postcss.config.js`:

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### Step 8: Create CSS File

Create `frontend/src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Source Sans Pro',
    sans-serif;
}
```

### Step 9: Create main.tsx

Create `frontend/src/main.tsx`:

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### Step 10: Create HTML Entry Point

Create `frontend/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Codebase RAG - AI Developer Assistant</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### Step 11: Create TypeScript Config

Create `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForEnumMembers": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "resolveJsonModule": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

Create `frontend/tsconfig.node.json`:

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

### Step 12: Run Frontend

```bash
npm run dev
```

You should see:
```
VITE v5.0.0  ready in 234 ms

➜  Local:   http://localhost:5173/
```

✅ **Frontend is running!** Visit http://localhost:5173 in browser.

---

## 🎮 Project Structure in VS Code

Your folder structure should look like:

```
codebase-rag/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── repositories.py
│   │   │   ├── search.py
│   │   │   ├── evaluation.py
│   │   │   ├── rag_trace.py
│   │   │   └── health.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── models.py
│   │   ├── retrieval/
│   │   │   ├── hybrid_retriever.py
│   │   │   └── query_processor.py
│   │   ├── context/
│   │   │   └── context_assembler.py
│   │   ├── generation/
│   │   │   └── llm_provider.py
│   │   ├── evaluation/
│   │   │   └── rag_evaluator.py
│   │   └── infrastructure/
│   │       └── database.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   └── EvaluationDashboard.tsx
│   │   ├── components/
│   │   │   └── RAGInspector.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── tsconfig.json
│
├── ARCHITECTURE.md
├── README.md
├── IMPLEMENTATION_GUIDE.md
└── QUICK_START.md
```

---

## 🌐 Access the Application

### Backend (API)

- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Frontend (UI)

- **Application**: http://localhost:5173
- **Landing Page**: Shows hero section with CTAs
- **Dashboard**: Chat interface (click "Get Started")
- **Evaluation**: Metrics dashboard (from Dashboard page)

---

## 🎯 Test the Application

### 1. Navigate to Landing Page

```
http://localhost:5173
```

You should see:
- ✓ NEXUS logo
- ✓ "Understand Any Codebase" headline
- ✓ Blue "Get Started" button
- ✓ Feature highlights
- ✓ Preview mockup

### 2. Click "Get Started"

Goes to Dashboard with:
- ✓ Left sidebar (repos, chat history)
- ✓ Main chat area
- ✓ Input box
- ✓ RAG Inspector toggle

### 3. Type a Question

```
Where is authentication implemented?
```

Should see:
- ✓ Your message appears in chat
- ✓ AI response appears with sample code
- ✓ Source citations show files and line numbers
- ✓ Click on citations to view code in right panel

### 4. Toggle RAG Inspector

Click **"RAG Inspector"** button to see:
- ✓ Query Processing stage
- ✓ Vector Search results
- ✓ BM25 Search results
- ✓ Result Fusion (RRF)
- ✓ Reranking stage
- ✓ Final context
- ✓ LLM Generation

### 5. Go to Evaluation Dashboard

Click **"Evaluation"** button to see:
- ✓ Metrics cards (Recall@5, Precision@5, etc.)
- ✓ Strategy comparison chart
- ✓ Query type breakdown
- ✓ Generation quality metrics
- ✓ Latency breakdown

---

## 🐛 Debugging Tips

### In VS Code

**Add breakpoints:**
1. Backend: Click line number in Python files to set breakpoint
2. Frontend: Open DevTools (F12) → Sources tab → set breakpoint

**Debug Terminal:**
```bash
# Backend with debugging
python -m pdb -m uvicorn app.main:app --reload
```

**Frontend Debugging:**
- Open DevTools (F12)
- Console tab → see React errors
- Network tab → see API calls to backend
- React Developer Tools extension (recommended)

### Common Issues

**Issue: "ModuleNotFoundError: No module named 'fastapi'"**
```bash
# Solution: Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate      # Windows
```

**Issue: "npm ERR! 404 Not Found"**
```bash
# Solution: Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue: "Port 8000 already in use"**
```bash
# Solution: Use different port
python -m uvicorn app.main:app --port 8001 --reload
```

**Issue: "Port 5173 already in use"**
```bash
# Solution: Vite will auto-increment to 5174, 5175, etc.
# Or kill the process:
# Mac/Linux:
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**Issue: CORS errors in browser console**
```
Access to XMLHttpRequest blocked by CORS policy
```
✓ This is expected in mock mode
✓ Backend proxy in vite.config.js will handle it

---

## 📊 Monitoring

### Terminal Logs

**Backend Terminal:**
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO: Processing query for repository: sample-repo
INFO: Retrieved 3 chunks
INFO: Query completed in 350ms
```

**Frontend Terminal:**
```
VITE v5.0.0  ready in 234 ms
➜  Local:   http://localhost:5173/
➜  press h to show help
```

### Check API Health

In browser console:
```javascript
fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)
```

Should return:
```json
{ "status": "healthy", "version": "1.0.0" }
```

---

## 🚀 Next Steps

### 1. Explore the Code

**Backend:**
- `backend/app/api/chat.py` - Main chat endpoint
- `backend/app/retrieval/hybrid_retriever.py` - Retrieval pipeline
- `backend/app/retrieval/query_processor.py` - Query understanding

**Frontend:**
- `frontend/src/pages/Dashboard.tsx` - Main UI
- `frontend/src/components/RAGInspector.tsx` - Debugger
- `frontend/src/pages/EvaluationDashboard.tsx` - Metrics

### 2. Test the RAG Pipeline

The mock backend returns sample data. To integrate real data:

1. Connect to real embeddings service (Qdrant)
2. Set up PostgreSQL database
3. Add actual code parsing (tree-sitter)
4. Connect OpenAI/Anthropic API

### 3. Customize

**Colors:**
- Primary: `#00C8FF` (neon blue)
- Background: `#050505` (near-black)
- Edit in Tailwind utility classes

**Prompts:**
- System prompt in `backend/app/context/context_assembler.py`
- Modify to change LLM behavior

**Metrics:**
- Benchmark queries in `backend/app/evaluation/rag_evaluator.py`
- Add your own evaluation dataset

---

## ✅ Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Virtual environment created and activated
- [ ] Backend dependencies installed (requirements.txt)
- [ ] Frontend dependencies installed (npm install)
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Landing page loads at http://localhost:5173
- [ ] Can navigate to Dashboard
- [ ] Can type messages and see responses
- [ ] RAG Inspector button toggles pipeline view
- [ ] Can view Evaluation Dashboard

---

## 📞 Troubleshooting

**Still having issues?**

1. Check terminal for error messages
2. Verify ports aren't blocked: `lsof -i :8000` (backend), `lsof -i :5173` (frontend)
3. Clear caches: `rm -rf __pycache__` (backend), `rm -rf node_modules` (frontend)
4. Restart both services
5. Check .env file has correct settings

---

**You're all set! Start hacking and exploring the RAG pipeline.** 🚀
