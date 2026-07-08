# Railway Deployment Guide

## Prerequisites
- GitHub repository configured (✅ Done)
- Railway account: https://railway.app
- Data file ready

---

## Step 1: Connect GitHub to Railway

1. Go to https://railway.app
2. Sign up or log in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Authorize Railway to access your GitHub
6. Select `api_laudos` repository
7. Select `main` branch

---

## Step 2: Railway Auto-detects Configuration

Railway automatically:
- Detects Python project
- Reads `Dockerfile`
- Sets up port 8000
- Configures Nixpacks

---

## Step 3: Add Environment Variables

In Railway dashboard → **"Variables"**:

```
PYTHONUNBUFFERED=1
PORT=8000
LAUDOS_DATA_FILE=/data/laudos_completos.xlsx
```

---

## Step 4: Upload Data File

### Option A: Volume Storage (Easy)

1. In Railway → **"Data"** → **"Add Volume"**
2. Name: `data`
3. Mount path: `/data`
4. Upload `laudos_completos.xlsx` via the dashboard

### Option B: Cloud Storage

```
LAUDOS_DATA_FILE=https://bucket.s3.amazonaws.com/laudos_completos.xlsx
```

---

## Step 5: Deploy

Railway automatically deploys when:
- You push to `main` branch
- You manually trigger a deploy

Watch the logs in real-time:
```
Deployment in progress...
→ Building Docker image
→ Starting container
→ Health check passed ✓
```

---

## Accessing Your API

After successful deployment:

- **API Base URL:** `https://<railway-domain>.railway.app`
- **Swagger UI:** `https://<railway-domain>.railway.app/docs`
- **ReDoc:** `https://<railway-domain>.railway.app/redoc`
- **Health:** `https://<railway-domain>.railway.app/health`

Find your domain in Railway dashboard under **"Deployment"**.

---

## Monitoring

Railway provides:
- **Logs:** Real-time application output
- **Metrics:** Response time, errors, CPU/memory
- **Deployments:** History and rollback
- **Activity:** All changes and events

---

## Custom Domain

1. In Railway → **"Settings"** → **"Domains"**
2. Add custom domain (e.g., `api.yourdomain.com`)
3. Update your DNS records

---

## Scaling

- **Pro Plan:** More resources, better performance
- **Multi-instance:** Click "Instances" to scale horizontally
- **Database:** Upgrade to PostgreSQL for production

---

## Troubleshooting

### Deployment fails
```bash
# Check logs
railway logs -f
```

### Container restarts frequently
```
Likely OOM (Out of Memory)
Solution: Upgrade Railway plan or optimize memory usage
```

### Data file not found
```
Verify LAUDOS_DATA_FILE path matches volume mount
Check volume is properly attached
```

---

## Auto-rollback

Railway keeps deployment history. If an issue occurs:
1. Go to **"Deployments"**
2. Find previous working version
3. Click **"Rollback"**

---

## PostgreSQL Integration

For production, migrate from Excel to database:

```bash
# Create PostgreSQL service in Railway
# Update connection string in app/core/config.py
# Test locally, then commit and push
```

---

## GitHub Actions Integration

Railway works seamlessly with GitHub Actions:

1. On every push to `main`:
   - GitHub Actions runs tests (`.github/workflows/ci-cd.yml`)
   - If tests pass, Railway auto-deploys
   - If tests fail, deployment blocks

---

## Cost Estimation

- **Free tier:** ~$5/month
- **Hobby plan:** $5/month
- **Usage:** Based on CPU, memory, storage

Monitor usage in Railway **"Billing"** dashboard.

---

## Next Steps

✅ API running in production  
✅ Auto-deploy on every Git push  
Next:
- [ ] Set up alerts/monitoring
- [ ] Test endpoints with real data
- [ ] Configure custom domain
- [ ] Plan database migration
- [ ] Set up CI/CD pipeline with test coverage

---

## Support

- Railway Docs: https://docs.railway.app
- Discord Community: https://discord.gg/railway
- Status: https://status.railway.app
