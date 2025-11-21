# Railway Backend Deployment Setup Guide

## The Problem
Railway is showing "Error creating build plan with Railpack" because it can't detect your Python project structure.

## Solution: Configure Railway Settings

### **Step 1: Create Railway Service from GitHub**

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"** or **"Add Service"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository

### **Step 2: Configure Root Directory**

After importing, Railway needs to know where your backend is:

1. Click on your **service** (e.g., "ai_assistant")
2. Go to **"Settings"** tab
3. Scroll down to **"Root Directory"**
4. Click **"Edit"** or **"Change"**
5. Enter: `backend`
6. Click **"Save"**

### **Step 3: Configure Start Command**

1. Still in **Settings** tab
2. Scroll to **"Start Command"** (or **"Deploy"** section)
3. Click **"Edit"**
4. Enter this command:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Click **"Save"**

### **Step 4: Set Build Command (Optional but Recommended)**

Railway should auto-detect Python, but if it doesn't:

1. In **Settings** tab
2. Find **"Build Command"** (if visible)
3. Enter: `pip install -r requirements.txt`
4. Click **"Save"**

### **Step 5: Add Environment Variables**

Go to **"Variables"** tab and add:

**Required:**
```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=your_postgres_connection_string (Railway auto-adds this if you add PostgreSQL)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

**PostgreSQL Variables (Railway auto-adds these when you add PostgreSQL database):**
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

### **Step 6: Add PostgreSQL Database**

1. In your Railway project dashboard
2. Click **"+ New"** button
3. Select **"Database"** → **"Add PostgreSQL"**
4. Railway will automatically:
   - Create the database
   - Add connection environment variables
   - Link it to your service

### **Step 7: Redeploy**

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** or wait for auto-redeploy after saving settings

---

## Visual Guide for Railway Dashboard

### **Settings Tab Layout:**
```
Settings
├── Service Name: ai_assistant
├── Root Directory: backend          ← Set this!
├── Build Command: pip install -r requirements.txt
├── Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT  ← Set this!
└── ...
```

### **Variables Tab:**
```
Variables
├── GROQ_API_KEY = your_key
├── ALLOWED_ORIGINS = https://your-frontend.vercel.app,http://localhost:3000
└── (PostgreSQL vars are auto-added when you add database)
```

---

## Alternative: Using Railway CLI

If the dashboard doesn't work, you can use Railway CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize in your project
cd backend
railway init

# Set root directory (already in backend folder, so no need)
# Set start command
railway variables set RAILWAY_START_COMMAND="uvicorn app.main:app --host 0.0.0.0 --port $PORT"

# Deploy
railway up
```

---

## Troubleshooting

### **If build still fails:**

1. **Check logs**: Click "View logs" in failed deployment
2. **Verify Root Directory**: Make sure it's exactly `backend` (no slash)
3. **Verify Start Command**: Should be exactly:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. **Check Python version**: Railway should auto-detect, but if not, add `runtime.txt` in backend folder

### **Common Issues:**

- **"Module not found"**: Root directory not set correctly
- **"Port binding error"**: Start command not using `$PORT` variable
- **"Build plan error"**: Root directory not set or Python not detected

---

## Quick Checklist

- [ ] Service created from GitHub repo
- [ ] **Root Directory** set to `backend`
- [ ] **Start Command** set to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] PostgreSQL database added
- [ ] Environment variables added
- [ ] Service redeployed

---

## After Deployment

Once deployed successfully:
1. Copy your Railway service URL (e.g., `https://your-project.up.railway.app`)
2. Update `NEXT_PUBLIC_API_URL` in Vercel with this URL
3. Update `ALLOWED_ORIGINS` in Railway with your Vercel frontend URL

