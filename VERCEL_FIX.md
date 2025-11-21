# Fix: Environment Variable Error in Vercel

## The Problem
You're getting this error:
```
Environment Variable "NEXT_PUBLIC_API_URL" references Secret "api_url", which does not exist.
```

This means you (or Vercel) tried to set an environment variable that references a secret using the `@api_url` syntax, but the secret doesn't exist.

## Solution

### Option 1: Remove the Environment Variable (Do This First)

1. **Go to your Vercel project dashboard**
2. **Click on your project**
3. **Go to Settings → Environment Variables**
4. **Find `NEXT_PUBLIC_API_URL`** in the list
5. **Click the "..." menu** next to it → **Delete it**
6. **Redeploy your project**

### Option 2: Set a Temporary Value (If you need it)

If you want to keep the variable for now (before deploying backend):

1. **Go to Settings → Environment Variables**
2. **Edit `NEXT_PUBLIC_API_URL`**
3. **Set the value to**: `http://localhost:8000` (temporary, for now)
   - **DO NOT use** `@api_url` or any secret syntax
   - Just put a plain URL or leave it empty
4. **Click Save**
5. **Redeploy**

### Option 3: Create the Secret (Not Recommended Now)

Only if you actually want to use secrets:
1. Go to **Settings → Environment Variables**
2. Click **"Add Secret"**
3. Create a secret named `api_url` with your backend URL
4. Then set `NEXT_PUBLIC_API_URL` to `@api_url`

**But this is unnecessary** - you can just set the environment variable directly.

---

## Correct Way to Set Environment Variables in Vercel

For Next.js projects, set environment variables **directly in Vercel dashboard**:

1. Go to **Settings → Environment Variables**
2. Click **"Add New"**
3. **Key**: `NEXT_PUBLIC_API_URL`
4. **Value**: Your actual backend URL (e.g., `https://your-backend.up.railway.app`)
5. **Environments**: Select Production, Preview, Development (or just Production)
6. **Click "Save"**

**Don't use `@secret_name` syntax** unless you've created a secret first.

---

## After Fixing

Once you remove or fix the environment variable:
1. The deployment error will disappear
2. Your frontend will deploy successfully
3. After deploying backend, come back and add the real `NEXT_PUBLIC_API_URL` value

---

## Quick Fix Right Now

**Simplest solution**: Just delete the `NEXT_PUBLIC_API_URL` environment variable from Vercel dashboard. Your app will still work because the code has a fallback (`http://localhost:8000`), and you can add it back later when you have the backend URL.

