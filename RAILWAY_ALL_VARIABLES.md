# 🔐 Complete Railway Environment Variables List

## ✅ Copy-Paste Ready Variables for Railway

Use these **exact values** in Railway's Variables tab. Click **"+ New Variable"** for each one.

---

## 📋 Required Variables

### 1. **GROQ_API_KEY**
```
YOUR_GROQ_API_KEY_HERE
```
*(Get your API key from: https://console.groq.com/keys)*

### 2. **ALLOWED_ORIGINS**
```
https://ai-assistant-lake.vercel.app,http://localhost:3000
```
*(Note: Added localhost for local development)*

### 3. **CHROMA_PERSIST_DIR**
```
./data/chroma_db
```

### 4. **POSTGRES_CONNECTION_STRING**
```
postgresql://neondb_owner:npg_zvs0cJiabI5u@ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

---

## 🗄️ PostgreSQL Individual Variables (Required by config.py)

Your `config.py` needs these individual variables extracted from your connection string:

### 5. **DATABASE_URL**
```
postgresql://neondb_owner:npg_zvs0cJiabI5u@ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech:5432/neondb
```

### 6. **POSTGRES_HOST**
```
ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech
```

### 7. **POSTGRES_PORT**
```
5432
```

### 8. **POSTGRES_DB**
```
neondb
```

### 9. **POSTGRES_USER**
```
neondb_owner
```

### 10. **POSTGRES_PASSWORD**
```
npg_zvs0cJiabI5u
```

---

## 📝 Quick Add Format for Railway

Copy each line and add as a new variable in Railway:

```
Key: GROQ_API_KEY
Value: YOUR_GROQ_API_KEY_HERE (get from https://console.groq.com/keys)

Key: ALLOWED_ORIGINS
Value: https://ai-assistant-lake.vercel.app,http://localhost:3000

Key: CHROMA_PERSIST_DIR
Value: ./data/chroma_db

Key: POSTGRES_CONNECTION_STRING
Value: postgresql://neondb_owner:npg_zvs0cJiabI5u@ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require

Key: DATABASE_URL
Value: postgresql://neondb_owner:npg_zvs0cJiabI5u@ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech:5432/neondb

Key: POSTGRES_HOST
Value: ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech

Key: POSTGRES_PORT
Value: 5432

Key: POSTGRES_DB
Value: neondb

Key: POSTGRES_USER
Value: neondb_owner

Key: POSTGRES_PASSWORD
Value: npg_zvs0cJiabI5u
```

---

## ✅ Checklist

Add these variables in Railway (Variables tab):

- [ ] `GROQ_API_KEY` = `YOUR_GROQ_API_KEY_HERE` (get from https://console.groq.com/keys)
- [ ] `ALLOWED_ORIGINS` = `https://ai-assistant-lake.vercel.app,http://localhost:3000`
- [ ] `CHROMA_PERSIST_DIR` = `./data/chroma_db`
- [ ] `POSTGRES_CONNECTION_STRING` = `postgresql://neondb_owner:npg_zvs0cJiabI5u@ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
- [ ] `DATABASE_URL` = `postgresql://neondb_owner:npg_zvs0cJiabI5u@ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech:5432/neondb`
- [ ] `POSTGRES_HOST` = `ep-solitary-scene-afxw92h9-pooler.c-2.us-west-2.aws.neon.tech`
- [ ] `POSTGRES_PORT` = `5432`
- [ ] `POSTGRES_DB` = `neondb`
- [ ] `POSTGRES_USER` = `neondb_owner`
- [ ] `POSTGRES_PASSWORD` = `npg_zvs0cJiabI5u`

---

## 🚨 Important Notes

1. **ALLOWED_ORIGINS**: I removed the trailing slash and added `http://localhost:3000` for local development
2. **DATABASE_URL**: Added port `:5432` to the connection string format
3. **All PostgreSQL variables**: These are required because your `config.py` Settings class expects them individually

---

## 🔄 After Adding All Variables

1. Railway will automatically redeploy
2. Check the deployment logs
3. The error should be resolved! ✅

