# ✅ 100% FREE Setup Guide - Groq API

## Quick Start (5 minutes)

### 1. Get Groq API Key (FREE - No Credit Card!)

1. Visit: https://console.groq.com/
2. Click "Sign Up" (use Google/GitHub for faster signup)
3. Once logged in, go to "API Keys" in left sidebar
4. Click "Create API Key"
5. Give it a name: "Drone Coordinator"
6. Copy the key (starts with `gsk_...`)

**Important**: Save this key somewhere safe! You can't see it again.

---

### 2. Configure Secrets

Create `.streamlit/secrets.toml` file:

```toml
GROQ_API_KEY = "gsk_paste_your_key_here"

[GOOGLE_SHEETS_CREDENTIALS]
# Your Google service account JSON here
# (See main DEPLOYMENT.md for Google Sheets setup)
```

---

### 3. Test Locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` and type:
- "Show me available pilots"

If it works → You're all set! ✅

---

## Why Groq is Perfect for This Assignment

✅ **100% FREE** - No credit card, no billing  
✅ **Fast** - Responses in ~1 second  
✅ **Generous Limits** - 30 requests/minute (more than enough)  
✅ **Good Quality** - Uses Meta's Llama 3.1 70B model  

---

## Groq vs OpenAI Comparison

| Feature | Groq (FREE) | OpenAI GPT-4o |
|---------|-------------|---------------|
| Cost | $0.00 | $0.50-$5 for testing |
| Credit Card | Not needed | Required |
| Speed | Very fast (~1s) | Fast (~2s) |
| Quality | Excellent | Slightly better |
| Free Tier | Unlimited (with rate limits) | $5 credit expires |

**For this assignment**: Groq is the **perfect choice**! 🎯

---

## Troubleshooting

**Error: "Groq API key not found"**
- Make sure `.streamlit/secrets.toml` exists
- Check that key starts with `gsk_`
- No extra spaces around the key

**Error: "Rate limit exceeded"**
- Wait 1 minute and try again
- Free tier: 30 requests/minute

**Error: "Import error: langchain_groq"**
- Run: `pip install -r requirements.txt` again
- Make sure you have internet connection

---

## Next Steps

Once Groq is working:
1. ✅ Set up Google Sheets (see main DEPLOYMENT.md)
2. ✅ Test all features locally
3. ✅ Push to GitHub
4. ✅ Deploy to Streamlit Cloud

**You're using a completely FREE stack! 🎉**
