# 🚂 Railway Configuration - Exact Steps

## The Error You're Seeing
"Error creating build plan with Railpack" - Railway can't detect your Python project.

## ✅ Solution: Configure in Railway Dashboard

### **Step 1: Push Your Code (Do This First!)**

```bash
git push origin main
```

This will trigger a new deployment with the configuration files.

---

### **Step 2: Open Railway Dashboard**

1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Click on your project
3. Click on the **service** (e.g., "ai_assistant")

---

### **Step 3: Go to Settings Tab**

Look for tabs at the top:
- **Deployments** (currently selected, showing the error)
- **Variables** 
- **Metrics**
- **Settings** ← **Click this one!**

---

### **Step 4: Set Root Directory**

1. In **Settings** tab, scroll down
2. Find **"Root Directory"** section
3. You'll see it might be empty or set to `/` or `.`
4. Click **"Edit"** or **"Change"** button
5. **Delete** whatever is there
6. Type exactly: `backend` (no slash, no period, just the word)
7. Click **"Save"** or press Enter

✅ **Expected Result**: Root Directory should now show `backend`

---

### **Step 5: Set Start Command**

1. Still in **Settings** tab, scroll down
2. Find **"Start Command"** or **"Deploy"** section
3. You might see a field that says:
   - Empty, or
   - Something like `python -m app.main`, or
   - Default Railway commands

4. Click **"Edit"** or **"Change"** button
5. **Delete** whatever is there
6. Copy and paste this exactly:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
7. Click **"Save"**

✅ **Expected Result**: Start Command should now show `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

### **Step 6: Verify Settings**

Your **Settings** tab should now show:
```
Root Directory: backend
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

### **Step 7: Add Environment Variables**

1. Go to **"Variables"** tab (next to Settings)
2. Click **"+ New Variable"** button
3. Add these one by one:

   **Variable 1:**
   - Key: `GROQ_API_KEY`
   - Value: (paste your actual Groq API key)
   - Click **"Add"**

   **Variable 2:**
   - Key: `ALLOWED_ORIGINS`
   - Value: `https://your-frontend.vercel.app,http://localhost:3000`
     (Replace `your-frontend.vercel.app` with your actual Vercel URL)
   - Click **"Add"**

---

### **Step 8: Add PostgreSQL Database**

1. In your Railway project (not in service settings)
2. Click **"+ New"** button (usually top right or in sidebar)
3. Select **"Database"**
4. Click **"Add PostgreSQL"**
5. Railway will automatically:
   - Create the database
   - Add environment variables (POSTGRES_HOST, POSTGRES_DB, etc.)
   - Link it to your service

✅ You'll see new variables appear in your **Variables** tab automatically

---

### **Step 9: Redeploy**

After saving settings, Railway should auto-redeploy. If not:

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** button (usually top right)
3. Select **"Redeploy"** from the dropdown
4. Wait for deployment to complete

---

## 🎯 Quick Checklist

Before redeploying, make sure:
- [ ] Root Directory = `backend` ✓
- [ ] Start Command = `uvicorn app.main:app --host 0.0.0.0 --port $PORT` ✓
- [ ] `GROQ_API_KEY` environment variable added ✓
- [ ] `ALLOWED_ORIGINS` environment variable added ✓
- [ ] PostgreSQL database added ✓
- [ ] Code pushed to GitHub (`git push`) ✓

---

## 📸 What You Should See

### **Settings Tab (After Configuration):**
```
Service Settings
─────────────────────────────────
Root Directory: backend
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
─────────────────────────────────
```

### **Variables Tab (After Adding):**
```
Environment Variables
─────────────────────────────────
GROQ_API_KEY = ********
ALLOWED_ORIGINS = https://your-app.vercel.app,http://localhost:3000
POSTGRES_HOST = ******** (auto-added)
POSTGRES_DB = ******** (auto-added)
... (other PostgreSQL vars)
─────────────────────────────────
```

---

## ❓ Still Not Working?

If deployment still fails after these steps:

1. **Check deployment logs**: Click "View logs" on the failed deployment
2. **Verify Root Directory**: Must be exactly `backend` (not `/backend` or `./backend`)
3. **Verify Start Command**: Copy it exactly as shown above
4. **Check Python version**: Railway should auto-detect Python 3.11+

---

## 🎉 After Successful Deployment

Once deployment succeeds:
1. Your backend URL will be: `https://your-service-name.up.railway.app`
2. Copy this URL
3. Go to Vercel dashboard → Your project → Settings → Environment Variables
4. Update `NEXT_PUBLIC_API_URL` with your Railway URL
5. Redeploy frontend

