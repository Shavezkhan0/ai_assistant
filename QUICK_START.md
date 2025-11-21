# 🚀 Quick Start - Deploy to Vercel

## Short Answer

**You only need ONE Git repository** (monorepo). You don't need separate repos for frontend and backend.

## 📝 Quick Checklist

### 1. Create GitHub Repository (5 minutes)
- [ ] Go to [GitHub](https://github.com/new)
- [ ] Create repository (e.g., `resultnotesbot-assistant`)
- [ ] **Don't** initialize with README

### 2. Push Code to GitHub (5 minutes)
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 3. Deploy Frontend on Vercel (10 minutes)
- [ ] Go to [Vercel](https://vercel.com) → Sign in with GitHub
- [ ] Click "Add New Project" → Import your repo
- [ ] Set **Root Directory** to `frontend`
- [ ] Add environment variable: `NEXT_PUBLIC_API_URL` = (leave empty for now, update after backend)
- [ ] Deploy

### 4. Deploy Backend on Railway (15 minutes)
- [ ] Go to [Railway](https://railway.app) → Sign in with GitHub
- [ ] Create project → Deploy from GitHub repo
- [ ] Set **Root Directory** to `backend`
- [ ] Add PostgreSQL database (in Railway dashboard)
- [ ] Add environment variables:
  ```
  GROQ_API_KEY=your_key
  ALLOWED_ORIGINS=https://your-frontend.vercel.app
  ```
  (Railway auto-adds PostgreSQL vars)
- [ ] Get your backend URL

### 5. Connect Frontend to Backend (2 minutes)
- [ ] Go back to Vercel
- [ ] Update `NEXT_PUBLIC_API_URL` with your Railway backend URL
- [ ] Redeploy frontend

### 6. Test
- [ ] Open your Vercel frontend URL
- [ ] Test the application

---

## 🎯 That's It!

Your frontend will be at: `https://your-project.vercel.app`  
Your backend will be at: `https://your-project.up.railway.app`

---

For detailed instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)

