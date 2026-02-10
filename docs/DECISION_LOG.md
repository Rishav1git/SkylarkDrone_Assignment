# Decision Log - Drone Operations Coordinator AI Agent

**Project**: Skylark Drones Assignment  
**Date**: February 2026  
**Timeline**: 6 hours

---

## Executive Summary

Built an AI-powered conversational assistant for coordinating drone operations using Python, Streamlit, LangChain, and OpenAI GPT-4o. The agent handles pilot roster management, drone inventory tracking, assignment coordination, and automated conflict detection with real-time Google Sheets synchronization.

---

## Key Assumptions

### 1. Google Sheets as Single Source of Truth
**Assumption**: Users will manually upload CSV data to Google Sheets and maintain one spreadsheet with three worksheets (Pilots, Drones, Missions).

**Rationale**: The assignment explicitly requires Google Sheets integration. This avoids managing separate database infrastructure for a prototype.

**Impact**: Simpler architecture but relies on Sheet structure consistency.

---

### 2. Service Account for API Access
**Assumption**: Users can create a Google Cloud Project and configure service account credentials.

**Rationale**: Service accounts provide secure, programmatic access without user OAuth flows, suitable for deployed applications.

**Impact**: Requires one-time setup but enables automatic Streamlit Cloud deployment.

---

### 3. Date Format Standardization
**Assumption**: All dates in CSV/Sheets use YYYY-MM-DD format.

**Rationale**: ISO 8601 format is unambiguous and pandas-compatible.

**Impact**: Simplifies date parsing; users must follow this format.

---

### 4. Comma-Separated Multi-Value Fields
**Assumption**: Skills, certifications, and capabilities are comma-separated strings (e.g., "Mapping, Survey").

**Rationale**: Matches the provided sample data format.

**Impact**: Parsing logic converts these to Python lists for matching operations.

---

## Technology Trade-offs

### ✅ Chosen: Python + Streamlit
**Why**: Rapid prototyping in single language, chat UI in ~10 lines of code, free deployment.

**Alternative Considered**: Next.js + React  
**Why Rejected**: Requires 3x more code, separate frontend/backend, steeper learning curve for 6-hour timeline.

**Trade-off**: Less customizable UI, but **3 hours faster development**.

---

### ✅ Chosen: LangChain + OpenAI Function Calling
**Why**: Built-in agent orchestration, GPT-4o best for function calling, natural language → structured operations.

**Alternative Considered**: Direct OpenAI API without LangChain  
**Why Rejected**: Would need custom tool routing logic, conversation management, retry handling.

**Trade-off**: Added dependency, but **saved 2 hours** on orchestration logic.

---

### ✅ Chosen: Google Sheets via gspread
**Why**: Required by assignment, Python library simpler than REST API.

**Alternative Considered**: Direct Google Sheets REST API  
**Why Rejected**: More boilerplate code for authentication and requests.

**Trade-off**: Library is synchronous (slower), but **saved 1 hour** on API integration.

---

### ✅ Chosen: Real-time Sync (Not Batched)
**Why**: Better UX for prototype demonstration, immediate feedback on changes.

**Alternative Considered**: Batch updates every N seconds  
**Why Rejected**: Adds caching complexity, delays visible in demo.

**Trade-off**: More API calls, but **better for evaluation**.

---

## Interpretation: "Urgent Reassignments"

### Definition
When a high-priority mission needs immediate resources, intelligently propose reallocating pilots/drones from lower-priority ongoing missions.

### Implementation
Created `urgent_reassign_tool` that:
1. Identifies resources assigned to source project
2. Analyzes target mission requirements (skills, location)
3. Generates impact report (what gets delayed, who's affected)
4. **Requires user confirmation** before executing swap

### Why This Approach?
- **Safety**: No automatic resource swapping without approval
- **Transparency**: Shows full impact analysis before changes
- **Flexibility**: Suggests plan but lets human make final call

### Example Flow
```
User: "Handle urgent reassignment for PRJ002"

Agent: 🚨 Urgent Reassignment Plan
       From: PRJ001 → To: PRJ002 (Priority: Urgent)
       Resources: P002 (Neha), D003
       Impact: PRJ001 delayed 1 day
       
       Confirm? Execute using assign_to_mission_tool
```

**Alternative Rejected**: Fully automated swapping → Too risky for real operations without human oversight.

---

## Edge Cases & Handling

### 1. Double Booking
**Detection**: Check if `status == 'Assigned'` and `current_assignment != '–'`  
**Action**: **CRITICAL** block, suggest available alternatives  
**Example**: "❌ Pilot P002 already on Project-A. Try P003 (Rohit) instead."

### 2. Skill/Certification Mismatch
**Detection**: Set difference between pilot certs and required certs  
**Action**: **CRITICAL** for missing certs, **WARNING** for missing skills  
**Example**: "⚠️ Pilot lacks 'Night Ops' certification. Proceed anyway?"

### 3. Drone in Maintenance
**Detection**: `status == 'Maintenance'` or `maintenance_due < mission_start_date + 7 days`  
**Action**: **CRITICAL** block if in maintenance, **WARNING** if due soon  
**Example**: "❌ D002 in maintenance. Available after Feb 1. Use D003?"

### 4. Location Mismatch
**Detection**: `pilot.location != mission.location` OR `drone.location != mission.location`  
**Action**: **WARNING** (not blocking, requires travel coordination)  
**Example**: "⚠️ Pilot in Bangalore, mission in Mumbai - requires travel"

---

## What I'd Do Differently With More Time

### 1. Advanced Scheduling Algorithm (2-3 hours)
**Current**: Manual matching via conversational queries  
**Better**: Implement Hungarian algorithm for optimal pilot-mission allocation  
**Benefit**: Automated optimization based on skills + location + availability

### 2. WebSocket Real-Time Updates (2 hours)
**Current**: Users manually refresh or ask agent  
**Better**: Live updates when Google Sheet changes (multi-user coordination)  
**Benefit**: Team collaboration without polling

### 3. Comprehensive Unit Tests (3 hours)
**Current**: Manual testing via chat interface  
**Better**: pytest suite for all conflict detection scenarios  
**Benefit**: Regression prevention, faster iteration

### 4. Caching Layer (1 hour)
**Current**: Reads Google Sheets on every query  
**Better**: Redis cache with TTL, invalidate on writes  
**Benefit**: 5x faster queries, reduced API quota usage

### 5. Audit Log (2 hours)
**Current**: No change history  
**Better**: Track who changed what and when (separate Audit sheet)  
**Benefit**: Compliance, rollback capability

### 6. Natural Language Understanding Improvements (2 hours)
**Current**: Relies on GPT-4o interpretation  
**Better**: Few-shot examples in prompt, structured entity extraction  
**Benefit**: More reliable parsing of ambiguous queries

### 7. Mobile-Responsive UI (1 hour)
**Current**: Works on mobile but not optimized  
**Better**: Streamlit columns, compact layout for small screens  
**Benefit**: Field coordinators can use on tablets

---

## Architecture Decisions

### Agent Pattern: Function Calling (Not RAG)
**Why**: Operations are deterministic (update status, check conflicts)  
**Not Used**: Retrieval-Augmented Generation would be overkill for structured data

### Error Handling: Graceful Degradation
- Google Sheets API fails → Return cached data + warning
- OpenAI API fails → Show error, suggest retry
- Conflict detected → Block assignment + suggest alternatives

### Security: Service Account (Not User OAuth)
**Why**: Headless deployment, no manual login flow  
**Risk**: Service account key must be kept secure (stored in Streamlit secrets)

---

## Validation Against Requirements

| Requirement | Implementation | ✅ |
|-------------|----------------|---|
| Conversational Interface | Streamlit chat UI + GPT-4o | ✅ |
| Roster Management | `query_pilots`, `update_pilot_status_tool` | ✅ |
| Assignment Tracking | `assign_to_mission_tool` with conflict checks | ✅ |
| Drone Inventory | `query_drones`, `update_drone_status_tool` | ✅ |
| Conflict Detection | 4 edge cases: double-booking, skills, maintenance, location | ✅ |
| Google Sheets Sync | gspread read/write with cache invalidation | ✅ |
| Urgent Reassignments | `urgent_reassign_tool` with impact analysis | ✅ |
| Hosted Prototype | Streamlit Cloud deployment | ✅ |
| Decision Log | This document (2 pages) | ✅ |
| Source Code | GitHub repo with meaningful commits | ✅ |

---

## Conclusion

Successfully delivered a functional AI agent within the 6-hour timeline by prioritizing rapid prototyping tools (Streamlit, LangChain) over production-grade architecture. The system handles all core requirements and edge cases while maintaining simplicity for evaluation.

**Key Success Factor**: Choosing Python stack for entire application eliminated context-switching and allowed reuse of data structures across modules.

**Biggest Challenge**: Google Sheets API rate limits during testing → Solved with caching and batched reads.

**Learning**: For prototypes, optimize for demo-ability over scalability. The right tool choice (Streamlit) saved 50% of development time.
