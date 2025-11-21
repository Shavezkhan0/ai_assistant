# 🚨 URGENT: Fix Railway Build Failure

## The Problem
Railway shows: **"Railpack could not determine how to build the app"**

This happens because Railway is looking at the **root directory** instead of the **backend folder**.

## ✅ THE FIX: Set Root Directory in Railway Dashboard

### **Step 1: Open Railway Service Settings**

1. In your Railway dashboard
2. Click on **"ai_assistant"** service (the one that failed)
3. Click on **"Settings"** tab (at the top, next to Variables/Metrics)

### **Step 2: Set Root Directory**

1. Scroll down in Settings
2. Find **"Root Directory"** section
3. You'll see it's probably **empty** or set to `/`
4. Click **"Edit"** or **"Change"** button
5. **Type exactly**: `backend` (just the word, no slashes)
6. Click **"Save"** or press Enter

✅ **IMPORTANT**: After setting this, Railway will:
- Look for `requirements.txt` in `backend/` folder ✅
- Look for `Procfile` in `backend/` folder ✅
- Look for `runtime.txt` in `backend/` folder ✅
- Detect Python automatically ✅

### **Step 3: Verify Start Command**

1. Still in **Settings** tab
2. Scroll to **"Start Command"** section
3. It should show: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. If it's empty or different, click **"Edit"** and set it to:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Click **"Save"**

### **Step 4: Railway Will Auto-Redeploy**

After saving Root Directory, Railway will:
- Automatically trigger a new deployment
- Now detect Python from `backend/requirements.txt`
- Use `backend/Procfile` for the start command
- Build successfully ✅

---

## 🎯 What You Should See

### **Before Fix:**
```
Settings Tab:
├── Root Directory: (empty or "/")
├── Start Command: (empty or wrong)
└── Build fails: "Could not determine how to build"
```

### **After Fix:**
```
Settings Tab:
├── Root Directory: backend ✅
├── Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT ✅
└── Build succeeds! ✅
```

---

## 📸 Visual Guide

When you click on **Settings** tab, you should see something like:

```
┌─────────────────────────────────────┐
│ Settings                            │
├─────────────────────────────────────┤
│ Service Name: ai_assistant          │
│                                     │
│ Root Directory: [backend] [Edit]   │ ← Set this!
│                                     │
│ Start Command: [uvicorn...] [Edit] │ ← Verify this!
│                                     │
│ ...                                 │
└─────────────────────────────────────┘
```

---

## ⚡ Quick Checklist

Before clicking Redeploy, make sure:
- [ ] **Root Directory** = `backend` (exactly this word)
- [ ] **Start Command** = `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Saved both settings

---

## 🔄 After Saving Settings

1. Railway will automatically start a new deployment
2. Go to **"Deployments"** tab to watch the progress
3. This time it should:
   - ✅ Detect Python
   - ✅ Install dependencies from `backend/requirements.txt`
   - ✅ Use the Procfile start command
   - ✅ Deploy successfully!

---

## ❓ Still Not Working?

If it still fails after setting Root Directory:

1. **Check deployment logs** - Click on the new deployment → "Build Logs"
2. **Verify files exist** - Make sure `backend/requirements.txt` exists in your GitHub repo
3. **Push latest code** - Run `git push origin main` to ensure Railway has all files

---

## 💡 Why This Fixes It

- **Before**: Railway looks at root → sees `frontend/` and `backend/` → confused ❌
- **After**: Railway looks at `backend/` → sees `requirements.txt`, `Procfile` → detects Python ✅

**The Root Directory setting tells Railway: "This is where my app code is!"**

