# Drone Operations Coordinator AI Agent

AI-powered conversational assistant for managing drone operations, pilot assignments, and conflict detection with Google Sheets integration.

## 🎯 Features

- 🤖 **Conversational AI Interface** - Chat naturally to manage operations
- 👨‍✈️ **Pilot Roster Management** - Query availability, skills, certifications
- 🚁 **Drone Inventory Tracking** - Monitor fleet status, capabilities, maintenance
- 📋 **Assignment Coordination** - Match pilots to missions automatically
- ⚠️ **Conflict Detection** - Catch double-bookings, skill mismatches, equipment issues
- 🔄 **Google Sheets 2-Way Sync** - Real-time updates to your spreadsheets
- 🚨 **Urgent Reassignments** - Priority-based resource reallocation

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **UI**: Streamlit
- **AI**: Groq (Llama 3.1 70B) - **100% FREE!**
- **Orchestration**: LangChain
- **Database**: Google Sheets (via gspread)
- **Deployment**: Streamlit Cloud

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/skylark-drone-coordinator.git
cd skylark-drone-coordinator

# Install dependencies
pip install -r requirements.txt

# Set up Google Sheets credentials
# 1. Create Google Cloud Project
# 2. Enable Google Sheets API
# 3. Create Service Account
# 4. Download credentials.json
# 5. Share your Google Sheets with service account email

# Set up environment variables
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your API keys
```

## 🚀 Quick Start

```bash
streamlit run app.py
```

Open browser at `http://localhost:8501`

## 💬 Usage Examples

```
User: "Show me available pilots in Bangalore"
Agent: Found 2 pilots:
       - Arjun (Mapping, Survey | DGCA, Night Ops)
       - Rohit (Inspection, Mapping | DGCA)

User: "Assign Arjun and drone D001 to Project PRJ001"
Agent: ✅ Assignment successful! Updated Google Sheet.

User: "Check conflicts for Neha"
Agent: ⚠️ Neha is already assigned to Project-A
```

## 📁 Project Structure

```
skylark-drone-coordinator/
├── app.py                 # Main Streamlit application
├── lib/
│   ├── sheets.py         # Google Sheets integration
│   ├── agent.py          # LangChain agent setup
│   ├── conflicts.py      # Conflict detection logic
│   └── tools.py          # Custom LangChain tools
├── data/
│   ├── pilot_roster.csv
│   ├── drone_fleet.csv
│   └── missions.csv
├── docs/
│   ├── DECISION_LOG.md
│   └── ARCHITECTURE.md
├── requirements.txt
└── README.md
```

## 🔑 Environment Variables

Create `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "sk-..."

[GOOGLE_SHEETS_CREDENTIALS]
type = "service_account"
project_id = "your-project"
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
# ... rest of credentials
```

## 📊 Google Sheets Setup

1. Create a Google Sheet named "Skylark Drone Operations"
2. Create 3 worksheets: "Pilots", "Drones", "Missions"
3. Upload data from CSV files
4. Share with service account email (found in credentials.json)

## 🧪 Testing

Run the agent locally and test:
- ✅ Query pilots by skill/location
- ✅ Update pilot status (verify Sheet changes)
- ✅ Assign pilot to mission
- ✅ Conflict detection (all 4 edge cases)
- ✅ Urgent reassignment workflow

## 🌐 Live Demo

[Deployment URL will be added after Streamlit Cloud deployment]

## 📝 Documentation

- [Decision Log](docs/DECISION_LOG.md) - Key assumptions and trade-offs
- [Architecture](docs/ARCHITECTURE.md) - System design overview

## 👨‍💻 Author

Built for Skylark Drones Assignment

## 📄 License

MIT License
