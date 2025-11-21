# 🔐 Railway Environment Variables Setup Guide

## Step-by-Step: Adding Environment Variables in Railway

### **Step 1: Open Variables Tab**

1. In Railway dashboard, click on your **"ai_assistant"** service
2. Click on **"Variables"** tab (at the top, next to Settings/Metrics)
3. You'll see the environment variables list

---

### **Step 2: Add Required Environment Variables**

Click **"+ New Variable"** button for each variable below:

---

### **🔑 Variable 1: GROQ_API_KEY** (Required)

1. Click **"+ New Variable"** button
2. **Key**: `GROQ_API_KEY`
3. **Value**: Paste your actual Groq API key here
   - Get it from: [https://console.groq.com/keys](https://console.groq.com/keys)
   - Or check your local `.env` file in `backend/` folder
4. **Environment**: Select all (Production, Preview, Development)
   - Or just select **Production** if you only want it in production
5. Click **"Add"** or **"Save"**

✅ **Example**:
```
Key: GROQ_API_KEY
Value: gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### **🔗 Variable 2: ALLOWED_ORIGINS** (Required)

1. Click **"+ New Variable"** button again
2. **Key**: `ALLOWED_ORIGINS`
3. **Value**: Your frontend URLs (comma-separated)
   - If you haven't deployed frontend yet, use:
     ```
     http://localhost:3000
     ```
   - After frontend is deployed, update to:
     ```
     https://your-frontend.vercel.app,http://localhost:3000
     ```
   - Replace `your-frontend.vercel.app` with your actual Vercel URL
4. **Environment**: Select **Production** (or all)
5. Click **"Add"** or **"Save"**

✅ **Example** (before frontend deployed):
```
Key: ALLOWED_ORIGINS
Value: http://localhost:3000
```

✅ **Example** (after frontend deployed):
```
Key: ALLOWED_ORIGINS
Value: https://my-app.vercel.app,http://localhost:3000
```

---

### **🐘 Variable 3: PostgreSQL Database Variables** (Auto-Added)

**IMPORTANT**: These are automatically added when you add PostgreSQL database!

1. Go back to your Railway project (not the service)
2. Click **"+ New"** button (top right or sidebar)
3. Select **"Database"** → **"Add PostgreSQL"**
4. Railway will automatically:
   - Create PostgreSQL database
   - Add these variables to your service:
     - `DATABASE_URL`
     - `POSTGRES_HOST`
     - `POSTGRES_PORT`
     - `POSTGRES_DB`
     - `POSTGRES_USER`
     - `POSTGRES_PASSWORD`
     - `PGPASSWORD`
     - `PGDATABASE`
     - `PGUSER`
     - `PGHOST`
     - `PGPORT`

✅ **You don't need to add these manually!** Railway does it automatically.

---

### **📋 Additional Variables (Optional)**

Based on your `config.py`, you might also need:

#### **Variable 4: DATABASE_URL** (Usually Auto-Added)

If not auto-added by PostgreSQL:
- **Key**: `DATABASE_URL`
- **Value**: Your PostgreSQL connection string
- **Format**: `postgresql://user:password@host:port/dbname`

#### **Variable 5: ENVIRONMENT** (Optional)

1. **Key**: `ENVIRONMENT`
2. **Value**: `production`
3. Click **"Add"**

#### **Variable 6: DEBUG** (Optional)

1. **Key**: `DEBUG`
2. **Value**: `false` (for production)
3. Click **"Add"**

---

## 📸 Visual Guide

### **Variables Tab Layout:**

```
┌─────────────────────────────────────────┐
│ Variables                    [+ New]    │
├─────────────────────────────────────────┤
│ Key                    Value    ...     │
├─────────────────────────────────────────┤
│ GROQ_API_KEY          ******** [Edit]   │ ← Add this!
│ ALLOWED_ORIGINS       https://... [Edit]│ ← Add this!
│ DATABASE_URL          postgres://...    │ ← Auto-added
│ POSTGRES_HOST         ********          │ ← Auto-added
│ POSTGRES_DB           ********          │ ← Auto-added
│ ...                                     │
└─────────────────────────────────────────┘
```

---

## ✅ Complete Environment Variables Checklist

**Required Variables:**
- [ ] `GROQ_API_KEY` - Your Groq API key
- [ ] `ALLOWED_ORIGINS` - Frontend URLs (comma-separated)
- [ ] `DATABASE_URL` - Auto-added when you add PostgreSQL
- [ ] `POSTGRES_HOST` - Auto-added when you add PostgreSQL
- [ ] `POSTGRES_DB` - Auto-added when you add PostgreSQL
- [ ] `POSTGRES_USER` - Auto-added when you add PostgreSQL
- [ ] `POSTGRES_PASSWORD` - Auto-added when you add PostgreSQL

**Optional Variables:**
- [ ] `ENVIRONMENT` - Set to `production`
- [ ] `DEBUG` - Set to `false`

---

## 🔄 After Adding Variables

1. **Railway will automatically redeploy** your service with new variables
2. Go to **"Deployments"** tab to watch the deployment
3. Check deployment logs to ensure everything works

---

## 🆘 Troubleshooting

### **"Variable not found" error?**
- Make sure variable name is exactly as shown (case-sensitive)
- Verify variable is saved in Railway dashboard
- Redeploy after adding variables

### **"Database connection failed"?**
- Make sure PostgreSQL database is added to your project
- Check that `DATABASE_URL` or PostgreSQL vars are present
- Wait a few minutes after creating database for it to initialize

### **"CORS error"?**
- Check `ALLOWED_ORIGINS` includes your frontend URL
- Make sure no extra spaces in the value
- Format: `https://url1.com,https://url2.com` (comma-separated, no spaces)

---

## 💡 Quick Tips

1. **Keep secrets secure**: Never commit `.env` files or share API keys
2. **Use different values for different environments**: Railway lets you set different values for Production vs Development
3. **Update ALLOWED_ORIGINS after frontend deployment**: Come back and update this with your Vercel URL
4. **Copy values from local `.env`**: Your `backend/.env` file has the values you need (except database, which Railway provides)

---

## 🎯 Next Steps After Setting Variables

1. ✅ Verify all variables are added
2. ✅ Wait for automatic redeployment
3. ✅ Check deployment logs for success
4. ✅ Test your API endpoint: `https://your-service.up.railway.app/health`
5. ✅ Copy Railway URL for frontend configuration

