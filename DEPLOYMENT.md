# Streamlit Community Cloud Deployment Guide

## Prerequisites
- GitHub account
- Streamlit Community Cloud account (https://streamlit.io/cloud)
- Your Supabase credentials
- Your Google Maps API key

## Deployment Steps

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub repository
4. Select your repository: `steiner-kenton/mileage_tracker`
5. Set main file path: `app.py`
6. Click "Deploy"

### 3. Configure Secrets
In your Streamlit Cloud app settings, add these secrets:

```toml
# Google Maps API Configuration
[google]
api_key = "YOUR_GOOGLE_MAPS_API_KEY"

# Supabase Credentials
[supabase]
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_API = "YOUR_SUPABASE_ANON_KEY"
SUPABASE_SERVICE_ROLE_KEY = "YOUR_SERVICE_ROLE_KEY"
```

**Note:** You don't need the gspread_service credentials if you're only using Supabase.

### 4. Required Files for Deployment

#### ✅ `packages.txt` (System dependencies)
Already created! This installs Tesseract OCR on the server.

#### ✅ `requirements.txt` (Python dependencies)
Already exists! All your Python packages are listed.

#### ⚠️ Files to Exclude
Make sure you have a `.gitignore` file that excludes:
- `.streamlit/secrets.toml` (local secrets)
- `__pycache__/`
- `*.pyc`
- `.env`
- `venv/`

### 5. Supabase Configuration
Your Supabase database should already be configured with:
- Row Level Security (RLS) policies
- User authentication enabled
- Tables: `mileage_dictionary`, `mileage_log`, `receipts`

### 6. Testing After Deployment
1. Visit your deployed app URL
2. Test authentication (signup/login)
3. Test all CRUD operations
4. Test receipt OCR upload
5. Test Google Maps address lookup

## Potential Issues & Solutions

### Issue 1: Tesseract OCR Not Working
- **Solution:** The `packages.txt` file should handle this
- **Fallback:** If issues persist, you may need to modify OCR settings or use a different OCR service

### Issue 2: Secrets Not Loading
- **Solution:** Double-check secrets format in Streamlit Cloud dashboard
- **Common mistake:** Extra quotes or incorrect TOML syntax

### Issue 3: Module Import Errors
- **Solution:** Ensure all imports use relative paths: `from src.utils import ...`
- **Check:** All `__init__.py` files exist in folders

### Issue 4: Authentication Issues
- **Solution:** Verify Supabase URL and API keys are correct
- **Check:** RLS policies allow authenticated user access

### Issue 5: Google API Rate Limits
- **Solution:** Monitor your Google Maps API usage
- **Tip:** The app already caches results to minimize API calls

## Post-Deployment

### Monitor Your App
- Check Streamlit Cloud logs for errors
- Monitor Supabase dashboard for database activity
- Check Google Cloud Console for API usage

### Update Your App
Any push to your `main` branch will automatically redeploy the app!

### Sharing Your App
Your app will have a URL like: `https://your-app-name.streamlit.app`
Share this with users who need access.

## Environment Variables (Optional)
Instead of secrets, you can use environment variables in Streamlit Cloud settings if needed.

## Resources
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Supabase Documentation](https://supabase.com/docs)
- [Google Maps API Documentation](https://developers.google.com/maps/documentation)
