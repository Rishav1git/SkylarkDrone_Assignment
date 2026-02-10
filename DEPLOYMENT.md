# Deployment Guide - Skylark Drone Coordinator

## 🎯 Current Status

✅ **Code Complete** - All modules implemented  
✅ **8 Git Commits** - Clean development history  
⏳ **Ready for Deployment** - Needs configuration

---

## 📋 Prerequisites

1. **Google Cloud Account** (for Sheets API)
2. **OpenAI API Account** (for GPT-4o)
3. **GitHub Account** (for version control)
4. **Streamlit Cloud Account** (for hosting)

---

## 🚀 Step-by-Step Deployment

### Step 1: Set Up Google Sheets API (15 minutes)

#### 1.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Skylark Drone Operations"
3. Enable **Google Sheets API**:
   - APIs & Services → Enable APIs and Services
   - Search "Google Sheets API" → Enable

#### 1.2 Create Service Account
1. IAM & Admin → Service Accounts → Create Service Account
2. Name: `drone-coordinator-bot`
3. Grant role: **Editor**
4. Create Key → JSON → Download `credentials.json`

#### 1.3 Create Google Sheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create new spreadsheet: "Skylark Drone Operations"
3. Create 3 worksheets:
   - **Pilots** (copy data from `pilot_roster.csv`)
   - **Drones** (copy data from `drone_fleet.csv`)
   - **Missions** (copy data from `missions.csv`)
4. **Share** the sheet with service account email (from credentials.json):
   - `drone-coordinator-bot@your-project.iam.gserviceaccount.com`
   - Give **Editor** access

---

### Step 2: Get OpenAI API Key (5 minutes)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy the key (starts with `sk-...`)
4. **Important**: Add billing method if not already done

---

### Step 3: Configure Local Environment (5 minutes)

#### 3.1 Create Secrets File
```bash
cd SkylarkDrone_Assignment
mkdir .streamlit
New-Item .streamlit\secrets.toml
```

#### 3.2 Edit `.streamlit/secrets.toml`
```toml
OPENAI_API_KEY = "sk-your-actual-openai-key-here"

[GOOGLE_SHEETS_CREDENTIALS]
# Paste contents of credentials.json here
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id-here"
private_key = "-----BEGIN PRIVATE KEY-----\nYour\nPrivate\nKey\nHere\n-----END PRIVATE KEY-----\n"
client_email = "drone-coordinator-bot@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

---

### Step 4: Test Locally (10 minutes)

#### 4.1 Install Dependencies
```powershell
pip install -r requirements.txt
```

#### 4.2 Run Application
```powershell
streamlit run app.py
```

#### 4.3 Test Scenarios
Open browser at `http://localhost:8501` and test:

1. **✅ Query Test**:
   - "Show me available pilots in Bangalore"
   - Expected: Lists Arjun and Sneha (if available)

2. **✅ Update Test**:
   - "Mark pilot P004 as Available"
   - Expected: Status updates, check Google Sheet cell changes

3. **✅ Assignment Test**:
   - "Assign Arjun and D001 to Project PRJ001"
   - Expected: Conflict check → Assignment confirmation

4. **✅ Conflict Test**:
   - Try assigning P002 (Neha) who's already assigned
   - Expected: "❌ CRITICAL: Neha already assigned to Project-A"

---

### Step 5: Push to GitHub (5 minutes)

#### 5.1 Create GitHub Repository
1. Go to [github.com/new](https://github.com/new)
2. Repository name: `skylark-drone-coordinator`
3. **Don't initialize** with README (we already have one)
4. Create repository

#### 5.2 Connect and Push
```powershell
git remote add origin https://github.com/YOUR_USERNAME/skylark-drone-coordinator.git
git branch -M main
git push -u origin main
```

All 8 commits will be pushed with clean history!

---

### Step 6: Deploy to Streamlit Cloud (10 minutes)

#### 6.1 Connect to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `skylark-drone-coordinator`
5. Main file path: `app.py`
6. Click "Advanced settings"

#### 6.2 Add Secrets
Paste the same content from local `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-..."

[GOOGLE_SHEETS_CREDENTIALS]
type = "service_account"
...
```

#### 6.3 Deploy
1. Click "Deploy!"
2. Wait 2-3 minutes for build
3. Get public URL: `https://YOUR-APP-NAME.streamlit.app`

---

### Step 7: Verify Deployment (5 minutes)

Test the live URL:
1. ✅ Chat interface loads
2. ✅ Query pilots works
3. ✅ Update status syncs to Sheet
4. ✅ Conflict detection works
5. ✅ Assignment flow complete

---

## 📦 Prepare Submission (10 minutes)

### 1. Create ZIP File
```powershell
# Compress entire folder
Compress-Archive -Path * -DestinationPath skylark-drone-coordinator.zip
```

**Exclude** in ZIP:
- `.git/`
- `credentials.json`
- `.streamlit/secrets.toml`
- `__pycache__/`

### 2. Submit via Form
Go to [Google Form](https://forms.gle/CzC7VgAMbFC3Tqhs7) and submit:
- ✅ Hosted app URL
- ✅ GitHub repository URL
- ✅ Decision Log (docs/DECISION_LOG.md)
- ✅ Source code ZIP

---

## 🔧 Troubleshooting

### Issue: "OpenAI API key not found"
**Fix**: Check `.streamlit/secrets.toml` has correct format with no extra spaces

### Issue: "Failed to load pilot roster"
**Fix**: 
1. Verify service account email has Editor access to Sheet
2. Check Sheet name is exactly "Skylark Drone Operations"
3. Verify worksheet names: "Pilots", "Drones", "Missions"

### Issue: "Module not found"
**Fix**: Run `pip install -r requirements.txt` again

### Issue: Streamlit Cloud build fails
**Fix**: Check `requirements.txt` has no version conflicts. Use exact versions provided.

---

## 📊 What You've Built

- **Lines of Code**: ~1,200
- **Git Commits**: 8 meaningful commits
- **Modules**: 5 (sheets, conflicts, tools, agent, app)
- **Features**: 7 LangChain tools + conversational UI
- **Edge Cases**: 4 conflict types handled
- **Documentation**: 2-page Decision Log + README

**Total Development Time**: ~4-5 hours (within 6-hour limit!)

---

## 🎉 You're Done!

Your AI agent is:
- ✅ Fully functional
- ✅ Deployed and accessible
- ✅ Syncing with Google Sheets
- ✅ Handling all edge cases
- ✅ Ready for submission

**Good luck with the evaluation! 🚀**
