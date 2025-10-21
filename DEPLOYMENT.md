# 🚀 Deployment Guide

This guide will help you deploy **Extractify** to production using free hosting services.

## 📋 Architecture

- **Frontend**: Deployed on **Vercel** (React/Vite)
- **Backend**: Deployed on **Render** (FastAPI)
- **Database**: Local JSON files (data/pages.jsonl, data/entities.json)

---

## 🔧 Step 1: Deploy Backend to Render

### 1.1 Sign Up for Render
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account

### 1.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `Extractify-The-Coding-Penguins-Deviathon-2025`
3. Configure the service:
   - **Name**: `extractify-backend`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: Leave empty (project root)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**:
     ```bash
     uvicorn api.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free

### 1.3 Add Environment Variables (Optional)
In Render dashboard, add these environment variables:
- `PYTHON_VERSION`: `3.11.6`
- `CP_IGNORE_ROBOTS`: `0`
- `CP_REQUEST_DELAY_MS`: `300`
- `CP_TIMEOUT_SEC`: `25`
- `CP_MAX_RETRIES`: `2`

### 1.4 Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Your backend will be available at: `https://extractify-backend.onrender.com`
4. Test health check: `https://extractify-backend.onrender.com/api/health`

---

## 🌐 Step 2: Deploy Frontend to Vercel

### 2.1 Sign Up for Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with your GitHub account

### 2.2 Import Project
1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository: `Extractify-The-Coding-Penguins-Deviathon-2025`
3. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `ui`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### 2.3 Add Environment Variables
In Vercel project settings → Environment Variables, add:
- **Key**: `VITE_API_URL`
- **Value**: `https://extractify-backend.onrender.com`
- **Environment**: Production

### 2.4 Deploy
1. Click **"Deploy"**
2. Wait for deployment (2-3 minutes)
3. Your frontend will be available at: `https://extractify-xxx.vercel.app`

---

## ✅ Step 3: Verify Deployment

### 3.1 Test Backend
```bash
# Health check
curl https://extractify-backend.onrender.com/api/health

# Expected response:
{
  "status": "ok",
  "app": "Extractify — Entity Extractor",
  "pages_file_present": false,
  "entities_file_present": false
}
```

Also check the root and docs:

```bash
# Landing page (should render a simple HTML with links)
curl -I https://extractify-backend.onrender.com/

# API docs (Swagger UI)
open https://extractify-backend.onrender.com/docs
```

### 3.2 Test Frontend
1. Open your Vercel URL: `https://extractify-xxx.vercel.app`
2. Check that API status shows "API Online" (green badge)
3. Navigate to Crawl Settings and try a small crawl (10-20 pages)

If your frontend Root Directory is set to `ui` (recommended), ensure a `vercel.json` exists inside the `ui/` folder (already added in this repo). This enables a rewrite so relative `/api/*` requests proxy to the Render backend.

Quick proxy check:

```bash
curl https://extractify-xxx.vercel.app/api/health
# Should return the same JSON as the backend health endpoint.
```

---

## ⚙️ Step 4: Configuration

### 4.1 Update Frontend API URL (if needed)
If your backend URL is different, update `ui/src/lib/api.ts`:
```typescript
const raw = (import.meta.env.VITE_API_URL as string | undefined)?.trim() ||
            "https://YOUR-BACKEND-URL.onrender.com";
```

### 4.2 Custom Domain (Optional)
- **Vercel**: Add custom domain in project settings
- **Render**: Add custom domain in service settings

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Build fails with "spaCy model not found"
- **Solution**: Ensure build command includes: `python -m spacy download en_core_web_sm`

**Problem**: "Out of memory" error
- **Solution**: Free tier has 512MB RAM. Reduce crawl size or upgrade to paid plan.

**Problem**: Service sleeps after 15 minutes
- **Solution**: This is normal for free tier. First request will wake it up (cold start ~30s).

**Problem**: Root URL (`/`) returns 404
- **Solution**: The backend now includes a landing page at `/` with links to `/docs` and `/api/health`. Redeploy if you don't see it yet.

**Problem**: 502 on `POST /api/crawl-and-extract`
- **Cause**: Cold start or transient proxy error during background task startup.
- **Solution**: Warm the service with a GET to `/api/health` first, then retry with a tiny job:
  ```bash
  curl -X POST https://extractify-backend.onrender.com/api/crawl-and-extract \
    -H "Content-Type: application/json" \
    -d '{"domain":"https://example.com","keywords":[],"max_pages":1,"max_depth":1}'
  ```
  Check progress via `/api/results`.

### Frontend Issues

**Problem**: "API Offline" status
- **Solution**: 
  1. Check backend is running: `https://extractify-backend.onrender.com/api/health`
  2. Verify `VITE_API_URL` environment variable in Vercel
  3. If using relative `/api/*` calls, ensure `ui/vercel.json` exists and the Vercel Project Root Directory is set to `ui` so rewrites apply.
  4. Check CORS settings in `api/main.py`

**Problem**: `https://your-frontend.vercel.app/api/health` returns 404 NOT_FOUND (rewrites not applied)
- **Cause**: Vercel treats any top-level `api/` folder as Serverless Functions. If your project root is the repo root, Vercel will see the backend folder `api/` (FastAPI code) and shadow your rewrites, so `/api/*` routes won’t be proxied.
- **Fix Option A (recommended)**: In Vercel → Project Settings → General, set **Root Directory** to `ui` (monorepo style). Redeploy. The `ui/vercel.json` rewrites will now apply and `/api/*` will proxy to Render.
- **Fix Option B (code-only)**: Keep root directory at repository root but add a `.vercelignore` file that excludes the backend and non-UI files from the deployment. This repo includes one already:
  ```
  *
  !.vercelignore
  !vercel.json
  !README.md
  !LICENSE
  !DEPLOYMENT.md
  !ui/**
  api/**
  crawler/**
  extractor/**
  data/**
  requirements.txt
  render.yaml
  ```
  After pushing, redeploy the frontend in Vercel and re-check: `https://your-frontend.vercel.app/api/health` should now return the backend JSON.

**Problem**: Build fails
- **Solution**: Ensure `ui/package.json` has correct build script:
  ```json
  "scripts": {
    "build": "vite build"
  }
  ```

---

## 💡 Optimization Tips

### Reduce Memory Usage
1. Use smaller crawl limits (10-50 pages instead of 150)
2. Reduce max depth (1-2 instead of 3-5)
3. Clear data files regularly

### Improve Performance
1. Enable Vercel Edge Functions for faster API responses
2. Use Render paid plan for persistent instance (no cold starts)
3. Add Redis cache for frequent queries

---

## 📊 Monitoring

### Render Dashboard
- View logs: Backend service → Logs tab
- Check metrics: Backend service → Metrics tab
- Monitor uptime: Free tier has 99% uptime SLA

### Vercel Dashboard
- View deployments: Project → Deployments
- Check analytics: Project → Analytics (pro plan)
- Monitor performance: Project → Speed Insights

---

## 🔄 Continuous Deployment

Both Render and Vercel auto-deploy on git push:

```bash
# Make changes to your code
git add .
git commit -m "Your changes"
git push origin main

# Render and Vercel will automatically deploy the updates!
```

---

## 💰 Cost Estimates

### Free Tier Limits
- **Render**: 
  - 512MB RAM
  - 0.1 CPU
  - Sleeps after 15 min inactivity
  - 750 hours/month
  
- **Vercel**:
  - 100GB bandwidth/month
  - Unlimited websites
  - Serverless functions: 100GB-Hrs

### Upgrade Options
If you need more resources:
- **Render Starter**: $7/month (512MB RAM, no sleep)
- **Vercel Pro**: $20/month (more bandwidth, analytics)

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)

---

## 🎉 Success!

Your Extractify project is now deployed and accessible worldwide! 🌍

- **Frontend**: https://extractify-xxx.vercel.app
- **Backend API**: https://extractify-backend.onrender.com
- **API Docs**: https://extractify-backend.onrender.com/docs

Share your project with the world! 🚀
