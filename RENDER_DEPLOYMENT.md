# Deploy on Render.com (Free Demo)

## Prerequisites
- GitHub account with your code repository
- Render.com account (sign up at https://render.com - **free tier available**)

---

## Option 1: Deploy Using render.yaml (Recommended - 5 minutes)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Connect to Render
1. Go to [render.com](https://render.com)
2. Sign in → Click **"New +"** → Select **"Blueprint"**
3. Connect your GitHub account
4. Search for your repository
5. Click **"Connect"**

### Step 3: Deploy Automatically
- Render reads `render.yaml` and deploys both services
- Wait 5-10 minutes for build completion

### Step 4: Access Your App
- Frontend URL: `https://your-app-frontend.onrender.com`
- Backend URL: `https://your-app-backend.onrender.com`

---

## Option 2: Manual Deployment (Without render.yaml)

### Deploy Backend
1. Go to Render Dashboard → Click **"New +"** → Select **"Web Service"**
2. Choose **"Deploy from GitHub"** → Select your repository
3. Fill in:
   - **Name**: `upi-mule-backend`
   - **Runtime**: Docker
   - **Build Command**: (Leave empty - Render auto-detects)
   - **Start Command**: (Leave empty - uses Dockerfile)
   - **Port**: 8000

4. Under **"Environment"**, add:
   ```
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   PORT=8000
   ```

5. Click **"Create Web Service"** → Wait for deployment ✅

### Deploy Frontend
1. Click **"New +"** → Select **"Web Service"** again
2. Choose **"Deploy from GitHub"** → Same repository
3. Fill in:
   - **Name**: `upi-mule-frontend`
   - **Runtime**: Docker
   - **Publish directory**: `dist` (nginx serves this)

4. Under **"Environment"**, add:
   ```
   VITE_API_BASE_URL=https://upi-mule-backend.onrender.com
   NODE_ENV=production
   ```
   *(Replace `upi-mule-backend.onrender.com` with your actual backend URL)*

5. Click **"Create Web Service"** → Wait for deployment ✅

---

## ⚙️ Important Configuration

### Frontend - Update API Base URL
After backend deploys, update **frontend** environment variable:
- Edit service → **"Environment"**
- Set `VITE_API_BASE_URL` to your backend URL

### Example:
```
VITE_API_BASE_URL=https://upi-mule-backend.onrender.com
```

---

## 🔗 CORS Configuration (If Needed)

Update `backend/app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.onrender.com",
        "http://localhost:3000"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Render Free Tier Benefits
- ✅ 2 free web services
- ✅ 100 GB/month bandwidth
- ✅ Auto deploys on git push
- ✅ Email notifications
- ✅ Basic monitoring
- ⏱️ **Note**: Services sleep after 15 minutes of inactivity (free tier)
  - First request after sleep takes 30 seconds to wake up
  - **Upgrade to paid ($7+/month) to prevent sleeping**

---

## 🚀 After Deployment

### Test Endpoints
```bash
# Backend health
curl https://your-app-backend.onrender.com/health

# Frontend
Visit https://your-app-frontend.onrender.com
```

### View Logs
Render dashboard → Your service → **"Logs"** (real-time)

### Redeploy
- Automatic: Git push triggers rebuild
- Manual: Render dashboard → **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## ❌ Troubleshooting

### Frontend shows 404
- ✅ Check `VITE_API_BASE_URL` environment variable
- ✅ Ensure backend is running (`curl` its `/health` endpoint)

### Backend fails to deploy
- Check logs: Render dashboard → **"Logs"**
- Ensure `requirements.txt` exists
- Check Dockerfile exists and is valid

### Services can't communicate
- Frontend must use full HTTPS URL to backend (not localhost)
- Set `VITE_API_BASE_URL=https://your-backend-url` (not HTTP)

### Cold start is slow
- This is free tier behavior (services sleep)
- Upgrade plan to keep services warm

---

## 📱 Monitoring & Analytics
- View in Render dashboard:
  - CPU/Memory usage
  - Request rates
  - Error rates
  - Deployment history

## 💡 Tips
- Keep **render.yaml** in root of repo for easy multi-service deployments
- Use Render's built-in **environment groups** to manage secrets
- Set up **email alerts** for deployment failures
- Monitor logs daily in first week

---

**Your app is now live! 🎉**
