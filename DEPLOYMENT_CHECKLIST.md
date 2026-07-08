# Deployment Checklist

## ✅ Code Quality & Testing

- [ ] All 20 tests passing locally: `pytest tests/ -v`
- [ ] Code formatted consistently
- [ ] No hardcoded secrets or credentials
- [ ] Environment variables documented in `.env.example`

## ✅ Docker & Container

- [ ] Dockerfile builds successfully: `docker build -t api_laudos .`
- [ ] Container runs locally: `docker run -p 8000:8000 api_laudos`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Logs are readable and helpful

## ✅ Documentation

- [ ] README.md complete with quickstart
- [ ] DEPLOYMENT.md with all options
- [ ] RENDER_DEPLOYMENT.md with step-by-step guide
- [ ] RAILWAY_DEPLOYMENT.md with step-by-step guide
- [ ] API endpoints documented in Swagger UI (`/docs`)
- [ ] CHANGELOG.md updated (optional but recommended)

## ✅ Git Repository

- [ ] Repository initialized and pushed to GitHub
- [ ] `.gitignore` configured (sensitive data excluded)
- [ ] LICENSE included (MIT or your choice)
- [ ] Main branch protected (GitHub Settings → Branches)
- [ ] Commit messages are descriptive and conventional

## ✅ GitHub Configuration

- [ ] Repository visibility set (Public/Private)
- [ ] Branch protection enabled for `main`
- [ ] Webhook configured for CI/CD (GitHub Actions)
- [ ] Repository description and topics updated

## ✅ Data Handling

- [ ] `laudos_completos.xlsx` is .gitignored
- [ ] Excel file location documented
- [ ] `LAUDOS_DATA_FILE` environment variable documented
- [ ] Backup strategy for data file planned

## ✅ Security

- [ ] No API keys/passwords in code
- [ ] `.env` file is .gitignored
- [ ] `.env.example` shows required variables
- [ ] CORS configured appropriately (if needed)
- [ ] Rate limiting considered for production

## ✅ Choose Your Platform

### If using Render:
- [ ] Render account created and configured
- [ ] Repository connected to Render
- [ ] `render.yaml` configured
- [ ] Environment variables added in dashboard
- [ ] Data file uploaded to Render
- [ ] Deploy button clicked
- [ ] Health check passes on production URL
- [ ] Swagger UI accessible at production URL

### If using Railway:
- [ ] Railway account created and configured
- [ ] Repository connected to Railway
- [ ] `railway.json` configured
- [ ] Environment variables added
- [ ] Volume storage configured
- [ ] Data file uploaded
- [ ] Deployment triggered
- [ ] Health check passes on production URL
- [ ] Logs show no errors

## ✅ Post-Deployment

- [ ] Production health check passes: `curl https://your-api.com/health`
- [ ] Swagger UI works: `https://your-api.com/docs`
- [ ] Sample endpoints tested with real data
- [ ] Response times acceptable
- [ ] No errors in logs
- [ ] Monitoring/alerts configured

## ✅ CI/CD Pipeline

- [ ] GitHub Actions workflow created (`.github/workflows/ci-cd.yml`)
- [ ] Tests run automatically on push
- [ ] Deploy only after tests pass
- [ ] Notifications configured (optional)
- [ ] Secrets stored in GitHub Secrets (not in code)

## ✅ Performance & Optimization

- [ ] Docker image size reasonable (~200-300 MB)
- [ ] Startup time < 30 seconds
- [ ] Response times < 200ms for simple queries
- [ ] Memory usage stable
- [ ] No memory leaks observed

## ✅ Monitoring & Logging

- [ ] Application logs visible in production
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Uptime monitoring configured (optional)
- [ ] Alerting configured for critical issues
- [ ] Regular log review scheduled

## 🔄 Regular Maintenance

- [ ] Weekly: Check logs for errors
- [ ] Monthly: Review performance metrics
- [ ] Monthly: Update dependencies (`pip list --outdated`)
- [ ] Quarterly: Security audit of code and dependencies
- [ ] Quarterly: Backup data file

## 🚀 Future Enhancements

- [ ] Migrate Excel to PostgreSQL database
- [ ] Add authentication (JWT/OAuth)
- [ ] Implement caching (Redis)
- [ ] Add rate limiting (slowapi)
- [ ] Set up webhooks for data updates
- [ ] Create mobile app SDK
- [ ] Add GraphQL endpoint
- [ ] Set up multi-region deployment

---

## Deployment Quick Reference

### Render
```bash
# 1. Push to GitHub
git push origin main

# 2. Go to render.com → New Web Service → Select repo
# 3. Upload laudos_completos.xlsx to Render Files
# 4. Set environment variable LAUDOS_DATA_FILE
# 5. Click Deploy
# ✅ Done! API at https://api-laudos.onrender.com
```

### Railway
```bash
# 1. Push to GitHub
git push origin main

# 2. Go to railway.app → New Project → Deploy from GitHub
# 3. Select api_laudos repo
# 4. Add environment variables
# 5. Upload data file to Volume
# ✅ Done! Auto-deploys to Railway domain
```

---

## Troubleshooting Deployment

| Problem | Solution |
|---------|----------|
| Build fails | Check Dockerfile syntax, ensure Python version is available |
| Container won't start | Review startup logs, verify data file path |
| Health check fails | Container is starting but app crashes - check application logs |
| High memory usage | Excel file loaded entirely in memory - migrate to DB or increase plan |
| Slow response times | Add caching, database indexing, or API pagination |

---

## Need Help?

- 📚 Read DEPLOYMENT.md for overview
- 🐳 Read RENDER_DEPLOYMENT.md for Render specifics
- 🚂 Read RAILWAY_DEPLOYMENT.md for Railway specifics
- 🐛 Check application logs in platform dashboard
- ✅ Run local tests: `pytest tests/ -v`
