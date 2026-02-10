# Decision Log - Drone Operations AI Agent

**Project**: Skylark Drones Assignment | **Date**: February 2026 | **Timeline**: 6 hours

---

## Executive Summary

Built an AI-powered conversational assistant for drone operations coordination using Python, Streamlit, LangChain, and Groq LLM. The agent manages pilot rosters, drone inventory, mission assignments, and automated conflict detection with real-time Google Sheets synchronization.

---

## Key Technology Decisions

### 1. ✅ Python + Streamlit (Not React/Next.js)
**Why**: Rapid prototyping in single language, built-in chat UI, free deployment, 6-hour timeline constraint.  
**Trade-off**: Less UI customization, but **saved 3 hours** on frontend development.

### 2. ✅ Groq LLM (Initially OpenAI, Switched for Cost)
**Initial Choice**: OpenAI GPT-4o for best function calling reliability.  
**Final Choice**: Groq `llama-3.3-70b-versatile` (100% FREE, no credit card).  
**Why Switch**: Assignment demo doesn't justify API costs; Groq provides unlimited free tier.  
**Implementation**: Simplified agent with keyword-based tool routing instead of complex LangChain agents due to API compatibility.  
**Trade-off**: Less sophisticated reasoning, but **$0 cost** for unlimited usage.

### 3. ✅ Google Sheets via gspread (Not Database)
**Why**: Required by assignment, Python library simpler than REST API.  
**Trade-off**: Slower than database, but **saved 2 hours** on infrastructure setup.

### 4. ✅ Real-time Sync (Not Batched)
**Why**: Better UX for prototype demonstration, immediate feedback.  
**Trade-off**: More API calls, but **better for evaluation**.

---

## Critical Assumptions

### 1. Google Sheets Structure
**Assumption**: One spreadsheet with 3 worksheets: Pilots, Drones, Missions.  
**Rationale**: Assignment specifies Google Sheets; single source of truth avoids database complexity.

### 2. Date Format: YYYY-MM-DD
**Assumption**: All date fields use ISO 8601 format.  
**Impact**: Simplifies pandas parsing; users must follow this format.

### 3. Service Account Authentication
**Assumption**: Users can create Google Cloud Project and configure service account.  
**Rationale**: Enables headless deployment to Streamlit Cloud without OAuth flows.

### 4. Comma-Separated Multi-Value Fields
**Assumption**: Skills/certifications stored as "Mapping, Survey, Inspection".  
**Impact**: Parsing logic converts to Python lists for matching.

---

## Urgent Reassignment Interpretation

**Definition**: When high-priority mission needs immediate resources, propose reallocating from lower-priority missions.

**Implementation**: `urgent_reassign` tool that:
1. Identifies resources assigned to source project
2. Analyzes target mission requirements (skills, location)
3. Generates impact report (delays, affected projects)
4. **Requires user confirmation** before execution

**Why This Approach**:
- **Safety**: No automatic swapping without human approval
- **Transparency**: Shows full impact before changes
- **Flexibility**: Agent suggests, human decides

**Alternative Rejected**: Fully automated swapping → Too risky without human oversight.

---

## Edge Case Handling

| Edge Case | Detection | Action | Severity |
|-----------|-----------|--------|----------|
| **Double Booking** | `status == 'Assigned'` and `current_assignment != '–'` | Block assignment, suggest alternatives | **CRITICAL** |
| **Skill Mismatch** | Missing required skills | Show warning, allow override | **WARNING** |
| **Cert Mismatch** | Missing required certifications | Block assignment | **CRITICAL** |
| **Drone Maintenance** | `status == 'Maintenance'` OR `maintenance_due < start + 7 days` | Block if in maintenance, warn if due soon | **CRITICAL / WARNING** |
| **Location Mismatch** | `pilot.location != mission.location` | Show warning (requires travel) | **WARNING** |

---

## Deployment Challenges & Solutions

### Challenge 1: LangChain Version Conflicts
**Problem**: Streamlit Cloud installed newer LangChain that deprecated `initialize_agent`.  
**Solution**: Rewrote agent with simple keyword-based tool routing, removed dependency on deprecated functions.  
**Lesson**: Pin critical dependencies; avoid deprecated APIs in cloud environments.

### Challenge 2: GitHub Secret Scanning
**Problem**: Accidentally committed Google Cloud credentials JSON, push blocked.  
**Solution**: `git reset`, added `*.json` to `.gitignore`, removed from tracking.  
**Lesson**: Always configure `.gitignore` before first commit.

### Challenge 3: Google Drive API Disabled
**Problem**: Sheets API requires Drive API to be enabled in Google Cloud Console.  
**Solution**: Enabled Drive API via provided console link, waited 30s for propagation.  
**Lesson**: Document all required Google Cloud APIs in setup guide.

---

## Future Improvements (Given More Time)

| Feature | Time | Benefit |
|---------|------|---------|
| Hungarian algorithm for optimal assignment | 3h | Automated optimization vs manual matching |
| WebSocket real-time updates | 2h | Multi-user collaboration without polling |
| pytest unit test suite | 3h | Regression prevention for conflict logic |
| Redis caching layer | 1h | 5x faster queries, reduced API quota |
| Audit log (separate Sheet) | 2h | Track changes, compliance, rollback |
| Better NLU with few-shot prompts | 2h | More reliable query parsing |

---

## Requirements Validation

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Conversational Interface | Streamlit chat UI + Groq LLM | ✅ |
| Roster Management | `query_pilots`, `update_pilot_status` | ✅ |
| Assignment Tracking | `assign_to_mission` with conflict checks | ✅ |
| Drone Inventory | `query_drones`, `update_drone_status` | ✅ |
| Conflict Detection | 4 edge cases handled | ✅ |
| Google Sheets Sync | gspread read/write operations | ✅ |
| Urgent Reassignments | `urgent_reassign` with impact analysis | ✅ |
| Hosted Prototype | Streamlit Cloud deployment | ✅ |
| Decision Log | This document (2 pages) | ✅ |
| Source Code | GitHub repo with clean commits | ✅ |

---

## Conclusion

Successfully delivered a functional AI agent within the 6-hour timeline by prioritizing:
1. **Free tools** (Groq LLM, Streamlit Cloud) for zero-cost demo
2. **Rapid prototyping** (Python stack) over production architecture
3. **Essential features** (conflict detection) over nice-to-haves (caching)

**Key Success**: Switching to Groq saved ~$50 in API costs while maintaining functionality.  
**Biggest Challenge**: LangChain deprecation during deployment → Fixed with simplified agent.  
**Learning**: For prototypes, optimize for demo-ability and cost over scalability.
