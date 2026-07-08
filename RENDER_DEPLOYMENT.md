# Render Deployment Guide

## Prerequisites
- GitHub repository configured (✅ Done)
- Private repository (optional but recommended for data security)
- Render account: https://render.com

---

## Step 1: Connect GitHub to Render

1. Go to https://render.com
2. Sign up or log in with GitHub
3. Click **"New +"** → **"Web Service"**
4. Select your repository: `api_laudos`
5. Click **"Connect"**

---

## Step 2: Configure the Service

**Basic Settings:**
```
Name: api-laudos
Environment: Docker
Region: Use closest to your data
```

**Build & Deploy:**
```
Build Command: (leave empty - uses Dockerfile)
Start Command: (leave empty - Dockerfile CMD)
```

---

## Step 3: Add Data File

### Option A: Upload via Render Dashboard (Free, easy)

1. In Render dashboard, go to **"Files"** section
2. Click **"Add File"**
3. Select `laudos_completos.xlsx` from your computer
4. Render will store it in `/var/data/laudos_completos.xlsx`

### Option B: Use S3/Cloud Storage (Scalable, recommended for production)

1. Upload `laudos_completos.xlsx` to AWS S3 or similar
2. Create a pre-signed URL or public URL
3. In Render environment variables, add:
```
LAUDOS_DATA_FILE=https://your-bucket.s3.amazonaws.com/laudos_completos.xlsx
```

---

## Step 4: Add Environment Variables

In Render dashboard → **"Environment"**:

```
PYTHONUNBUFFERED=1
PORT=8000
LAUDOS_DATA_FILE=/var/data/laudos_completos.xlsx

# Optional
LOG_LEVEL=info
ENVIRONMENT=production
```

---

## Step 5: Deploy

Click **"Deploy"** button. Render will:
1. Clone your repository
2. Build the Docker image
3. Start the container
4. Run health checks

Deployment takes ~2-5 minutes. You'll see logs in real-time.

---

## Accessing Your API

After deployment completes:

- **API Base URL:** `https://api-laudos.onrender.com`
- **Swagger UI:** `https://api-laudos.onrender.com/docs`
- **ReDoc:** `https://api-laudos.onrender.com/redoc`
- **Health Check:** `https://api-laudos.onrender.com/health`

---

## Monitoring & Logs

In Render dashboard:
- **Logs:** Real-time output from your service
- **Metrics:** CPU, memory, request rate
- **Deployments:** History of all deployments

---

## Troubleshooting

### Build fails
```
Check Logs → Look for Python/dependency errors
Solution: Verify requirements.txt is correct
```

### Container crashes
```
Check Logs → Look for data file not found errors
Solution: Ensure laudos_completos.xlsx is uploaded or URL is correct
```

### High memory usage
```
Increase plan to "Pro" or use database instead of Excel
```

---

## Updating Your API

1. Push changes to GitHub:
```bash
git add .
git commit -m "Update API"
git push origin main
```

2. Render automatically redeploys on push to `main` branch

---

## Custom Domain

1. In Render dashboard → **"Settings"**
2. Add your custom domain (e.g., `api.yourdomain.com`)
3. Update DNS records as instructed by Render

---

## Auto-deploy on GitHub Push

Already configured! Render watches your `main` branch and auto-deploys on every push.

To disable: Settings → Build & Deploy → disable "Auto-Deploy"

---

## Next Steps

- Monitor first deployment in logs
- Test endpoints at `/docs`
- Configure CI/CD pipeline (GitHub Actions)
- Set up monitoring/alerts
- Plan database migration (Excel → PostgreSQL)
