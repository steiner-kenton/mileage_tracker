# Pre-Deployment Checklist

## ✅ Files Ready for Deployment

### Required Files
- [x] `app.py` - Main application entry point
- [x] `requirements.txt` - Python dependencies
- [x] `packages.txt` - System dependencies (Tesseract OCR)
- [x] `.gitignore` - Excludes secrets and cache files
- [x] `README.md` - Project documentation
- [x] All source files in `src/` and `pages/`

### Configuration Files
- [x] `.streamlit/config.toml` - Optional theme configuration
- [ ] `.streamlit/secrets.toml` - **DO NOT COMMIT** (add in Streamlit Cloud UI)

## 📋 Pre-Deployment Tasks

### 1. Code Cleanup
- [ ] Remove any debug print statements
- [ ] Remove unused imports
- [ ] Test all features locally
- [ ] Verify all pages load without errors

### 2. Git Repository
- [ ] Push latest code to GitHub
- [ ] Verify repository is public or accessible to Streamlit Cloud
- [ ] Check that `.gitignore` excludes secrets

### 3. Secrets Preparation
Prepare these values for Streamlit Cloud secrets:
- [ ] Google Maps API Key
- [ ] Supabase URL
- [ ] Supabase Anon Key
- [ ] Supabase Service Role Key

### 4. Supabase Configuration
- [ ] Database tables created (`mileage_dictionary`, `mileage_log`, `receipts`)
- [ ] RLS policies configured for authenticated users
- [ ] Authentication enabled (email/password)
- [ ] Test user account created

### 5. Google Cloud Configuration
- [ ] Google Maps API key created
- [ ] Distance Matrix API enabled
- [ ] Places API enabled (for address lookup)
- [ ] API restrictions set (optional but recommended)

## 🚀 Deployment Steps

### Step 1: Connect to Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"

### Step 2: Configure App
1. Select repository: `steiner-kenton/mileage_tracker`
2. Branch: `main`
3. Main file path: `app.py`
4. App URL: Choose a custom name

### Step 3: Add Secrets
Copy from your local `.streamlit/secrets.toml` and paste into Streamlit Cloud:
```toml
[google]
api_key = "YOUR_KEY_HERE"

[supabase]
SUPABASE_URL = "YOUR_URL_HERE"
SUPABASE_API = "YOUR_ANON_KEY_HERE"
SUPABASE_SERVICE_ROLE_KEY = "YOUR_SERVICE_ROLE_KEY_HERE"
```

### Step 4: Deploy
1. Click "Deploy!"
2. Wait for deployment (usually 2-5 minutes)
3. Monitor logs for any errors

### Step 5: Test Deployed App
- [ ] App loads successfully
- [ ] Login/Signup works
- [ ] Can add locations to Mileage Dictionary
- [ ] Can log trips
- [ ] Address lookup works
- [ ] Receipt OCR works
- [ ] Edit/Delete functions work
- [ ] Date filtering works
- [ ] CSV export works

## 🐛 Common Issues & Fixes

### Issue: "ModuleNotFoundError"
**Fix:** Check `requirements.txt` includes all dependencies

### Issue: "Tesseract not found"
**Fix:** Verify `packages.txt` exists with tesseract-ocr packages

### Issue: Authentication fails
**Fix:** Check Supabase credentials in secrets

### Issue: Google API errors
**Fix:** Verify API key and ensure APIs are enabled in Google Cloud Console

### Issue: App crashes on receipt upload
**Fix:** Check file size limits and Tesseract installation

## 📊 Post-Deployment Monitoring

### Check These Regularly
- [ ] Streamlit Cloud app logs
- [ ] Supabase dashboard (database usage)
- [ ] Google Cloud Console (API usage & billing)
- [ ] User feedback and error reports

### Performance Optimization
- Monitor response times
- Check for memory issues
- Review API call patterns
- Optimize database queries if needed

## 🔒 Security Checklist
- [ ] Secrets not committed to GitHub
- [ ] RLS policies enabled in Supabase
- [ ] API keys have restrictions
- [ ] Service role key only used where necessary
- [ ] Authentication required for all sensitive operations

## 📝 Documentation
- [ ] Update README.md with deployment URL
- [ ] Document any environment-specific configurations
- [ ] Create user guide if needed
- [ ] Document any known limitations

## ✨ Optional Enhancements
- [ ] Set up custom domain
- [ ] Add analytics tracking
- [ ] Set up error monitoring (e.g., Sentry)
- [ ] Add automated backups for Supabase
- [ ] Set up CI/CD pipeline

---

**Ready to Deploy?** Follow the steps in `DEPLOYMENT.md`!
