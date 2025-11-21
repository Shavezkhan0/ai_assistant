# ✅ Railway Environment Variables - Step by Step

Based on Railway's **"Suggested Variables"** section, here's exactly what to do:

---

## 📋 Railway Suggested Variables

Railway found these variables in your source code:
1. ✅ `POSTGRES_CONNECTION_STRING` - Already has a value (from Neon database)
2. ✅ `CHROMA_PERSIST_DIR` - Already has value `./data/chroma_db`
3. ⚠️ `ALLOWED_ORIGINS` - Needs a value

---

## 🎯 What To Do

### **Step 1: Accept Suggested Variables**

Railway already detected and filled in the values:

1. **POSTGRES_CONNECTION_STRING**: 
   - ✅ Value is already there: `postgresql+psycopg://neondb_owner:npg_zvs0cJiabl5u@ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
   - **Click the "Add" button** to accept this variable

2. **CHROMA_PERSIST_DIR**: 
   - ✅ Value is already there: `./data/chroma_db`
   - **Click the "Add" button** to accept this variable

3. **ALLOWED_ORIGINS**: 
   - ⚠️ Needs a value
   - **Click in the value field** and type:
     ```
     http://localhost:3000
     ```
   - Or if you have deployed frontend:
     ```
     https://your-frontend.vercel.app,http://localhost:3000
     ```
   - Then **click "Add"**

---

### **Step 2: Add Required Variable (Not Suggested)**

Railway didn't detect `GROQ_API_KEY`, but it's required:

1. Click **"+ New Variable"** button (purple button at top)
2. **Key**: `GROQ_API_KEY`
3. **Value**: Paste your Groq API key
   - Get it from: https://console.groq.com/keys
   - Or check your local `backend/.env` file
4. **Environment**: Select Production (or All)
5. Click **"Add"**

---

## ✅ Complete Checklist

**From Suggested Variables (Click "Add" button):**
- [ ] `POSTGRES_CONNECTION_STRING` - Already has value ✅
- [ ] `CHROMA_PERSIST_DIR` - Already has value `./data/chroma_db` ✅
- [ ] `ALLOWED_ORIGINS` - Add value: `http://localhost:3000` (or your Vercel URL)

**Manually Add:**
- [ ] `GROQ_API_KEY` - Your Groq API key (required!)

---

## 📸 Visual Guide

In Railway's "Suggested Variables" section:

```
┌─────────────────────────────────────────────┐
│ Suggested Variables                         │
│ We found these variables in your source code│
├─────────────────────────────────────────────┤
│ POSTGRES_CONNECTION_STRING                  │
│ [Value filled]              [{}] [X]        │
│                                             │
│ CHROMA_PERSIST_DIR                          │
│ [./data/chroma_db]          [{}] [X]        │
│                                             │
│ ALLOWED_ORIGINS                             │
│ [VALUE or ${{REF}}]         [{}] [X]        │ ← Type value here!
│                                             │
│                            [✓ Add]          │ ← Click this!
└─────────────────────────────────────────────┘
```

---

## 🔧 After Adding Variables

1. **Click "Add" button** at bottom of Suggested Variables section
2. **Add `GROQ_API_KEY`** manually using "+ New Variable"
3. Railway will **automatically redeploy** your service
4. Go to **"Deployments"** tab to watch the deployment
5. Check logs to ensure everything works

---

## 💡 Important Notes

### **POSTGRES_CONNECTION_STRING:**
- This is from your **Neon database** (Neon.tech)
- The connection string is already correct ✅
- Just click "Add" to accept it

### **CHROMA_PERSIST_DIR:**
- Value `./data/chroma_db` is correct ✅
- This tells ChromaDB where to store vector data
- Just click "Add" to accept it

### **ALLOWED_ORIGINS:**
- This controls which domains can access your API (CORS)
- For now, use: `http://localhost:3000`
- After deploying frontend, update to: `https://your-app.vercel.app,http://localhost:3000`

### **GROQ_API_KEY:**
- This is required for your LLM/AI features
- Get it from: https://console.groq.com/keys
- Make sure it starts with `gsk_`

---

## 🎯 Summary

**Quick Steps:**
1. ✅ Accept `POSTGRES_CONNECTION_STRING` (already has value)
2. ✅ Accept `CHROMA_PERSIST_DIR` (already has value)
3. ✅ Set `ALLOWED_ORIGINS` to `http://localhost:3000` (type the value)
4. ✅ Click **"Add"** button to add all suggested variables
5. ✅ Manually add `GROQ_API_KEY` using "+ New Variable"

After this, your backend should deploy successfully! 🚀

