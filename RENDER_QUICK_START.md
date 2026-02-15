# 🚀 Render Deploy in 5 Minutes

## TL;DR - Just 3 Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for Render"
git push
```

### 2. Go to Render.com
- Sign Up at https://render.com (free)
- Dashboard → **New +** → **Blueprint**
- Connect GitHub & select your repo
- Click **Next** & **Deploy**

### 3. Get Live URLs
After ~5-10 minutes:
- **Frontend**: `https://xxx.onrender.com`
- **Backend**: `https://xxx.onrender.com`

---

## That's it! Your app is LIVE! 🎉

### Troubleshooting
- Backend not responding? → Update Frontend's VITE_API_BASE_URL env var
- After 15 min of no traffic, it sleeps (free tier) - refresh to wake up
- Check Logs in Render dashboard for errors

### Full Guide
See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for detailed setup
