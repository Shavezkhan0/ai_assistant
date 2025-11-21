# Deployment Guide for Vercel

This guide will help you deploy your project on Vercel.

## 📋 Project Structure

Your project has:
- **Frontend**: Next.js application (in `frontend/` folder)
- **Backend**: FastAPI application (in `backend/` folder)

## 🎯 Deployment Strategy

### Option 1: Recommended (Frontend on Vercel + Backend on Separate Service)

**Frontend on Vercel** ✅  
**Backend on Railway/Render/Fly.io** ✅

This is the **best approach** because your backend uses:
- PostgreSQL database
- ChromaDB (vector database) with persistent storage
- File uploads with persistent storage
- Long-running AI/LLM operations

Vercel serverless functions have limitations for these use cases.

---

## 🚀 Step-by-Step Deployment

### **Step 1: Create a Git Repository**

You only need **ONE Git repository** (monorepo structure). You already have this!

1. **Initialize Git** (if not already done):
   ```bash
   git init
   ```

2. **Create a GitHub repository**:
   - Go to [GitHub](https://github.com/new)
   - Create a new repository (e.g., `resultnotesbot-assistant`)
   - **Don't** initialize with README (you already have files)

3. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual values.

---

### **Step 2: Deploy Frontend on Vercel**

1. **Go to [Vercel](https://vercel.com)** and sign in with GitHub

2. **Click "Add New Project"**

3. **Import your GitHub repository**

4. **Configure the project**:
   - **Root Directory**: Set to `frontend`
     - Click "Edit" next to Root Directory
     - Type `frontend` and save

   - **Framework Preset**: Next.js (should auto-detect)

   - **Build Command**: `npm run build` (or `pnpm build` if using pnpm)

   - **Output Directory**: `.next` (default)

   - **Install Command**: `npm install` (or `pnpm install`)

5. **Environment Variables**:
   Add this environment variable:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-url.com
   ```
   (You'll get this URL after deploying the backend in Step 3)

6. **Click "Deploy"**

7. **Your frontend will be live at**: `https://your-project.vercel.app`

---

### **Step 3: Deploy Backend on Railway/Render**

Choose one platform for your backend:

#### **Option A: Railway (Recommended - Easiest)**

1. **Go to [Railway](https://railway.app)** and sign in with GitHub

2. **Create a new project** → "Deploy from GitHub repo"

3. **Select your repository**

4. **Configure**:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Railway auto-detects Python and installs dependencies

5. **Environment Variables** (Add in Railway dashboard):
   ```
   GROQ_API_KEY=your_groq_api_key
   DATABASE_URL=your_postgres_connection_string
   POSTGRES_HOST=your_postgres_host
   POSTGRES_PORT=5432
   POSTGRES_DB=your_database_name
   POSTGRES_USER=your_postgres_user
   POSTGRES_PASSWORD=your_postgres_password
   ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
   ENVIRONMENT=production
   DEBUG=false
   ```
   
   **Add PostgreSQL Database**:
   - In Railway dashboard, click "+ New" → "Database" → "Add PostgreSQL"
   - Railway will automatically create a `DATABASE_URL` environment variable

6. **Get your backend URL**:
   - Railway provides a URL like: `https://your-project.up.railway.app`
   - Copy this URL

7. **Update Frontend Environment Variable**:
   - Go back to Vercel dashboard
   - Go to your project → Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` to your Railway backend URL
   - Redeploy the frontend

#### **Option B: Render**

1. **Go to [Render](https://render.com)** and sign in

2. **Create a new Web Service** → Connect your GitHub repo

3. **Configure**:
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add PostgreSQL Database**:
   - Create a new PostgreSQL database in Render
   - Copy the connection string

5. **Environment Variables**: (Same as Railway)

6. **Get your backend URL**: `https://your-project.onrender.com`

---

### **Step 4: Configure ChromaDB for Production**

Since Vercel/Railway/Render use ephemeral file systems, you need to configure ChromaDB for cloud storage:

#### **Option A: Use ChromaDB Cloud** (Recommended)
1. Sign up at [ChromaDB Cloud](https://www.trychroma.com/)
2. Create a collection
3. Update your `backend/app/database/vector_db.py` to use ChromaDB client with cloud credentials

#### **Option B: Use External Storage**
- Store ChromaDB data in a persistent volume (Railway volumes)
- Or use a cloud storage service (AWS S3, etc.)

---

## ✅ Post-Deployment Checklist

- [ ] Frontend deployed on Vercel
- [ ] Backend deployed on Railway/Render
- [ ] Environment variables configured
- [ ] CORS configured to allow frontend domain
- [ ] Database connected and working
- [ ] API endpoints accessible
- [ ] File uploads working (if using external storage)

---

## 🔧 Troubleshooting

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` environment variable in Vercel
- Ensure CORS allows your frontend domain
- Verify backend URL is correct

### Backend deployment fails
- Check build logs for missing dependencies
- Verify all environment variables are set
- Check Python version compatibility

### Database connection issues
- Verify database credentials
- Check if database is publicly accessible (if needed)
- Ensure SSL is configured correctly

### File uploads not working
- Use external storage (S3, Cloudinary, etc.)
- Or configure persistent volumes

---

## 📝 Additional Notes

### Alternative: Deploy Backend on Vercel (Limited)

You can deploy the backend as Vercel serverless functions, but you'll face limitations:
- No persistent file storage
- ChromaDB won't persist data
- Limited execution time (10 seconds on free tier)
- Requires refactoring for serverless architecture

**Not recommended** for your current backend setup.

---

## 🆘 Need Help?

If you encounter issues:
1. Check deployment logs
2. Verify environment variables
3. Test API endpoints using Postman/curl
4. Check browser console for CORS errors

---

## 📚 Useful Links

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

