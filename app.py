"""
Drone Operations Coordinator AI Agent
Main Streamlit application with chat interface.
"""

import streamlit as st
from lib.agent import create_agent, run_agent
from lib.sheets import get_sheet_url

# Page configuration
st.set_page_config(
    page_title="Drone Operations Coordinator",
    page_icon="🚁",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1F77B4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🚁 Drone Operations Coordinator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered assistant for managing pilots, drones, and missions</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️  About")
    st.info(
        "This AI agent helps coordinate drone operations by:\n\n"
        "• Managing pilot rosters\n"
        "• Tracking drone inventory\n"
        "• Matching pilots to missions\n"
        "• Detecting conflicts automatically\n"
        "• Syncing with Google Sheets"
    )
    
    st.header("💡 Quick Actions")
    
    if st.button("📋 Show All Pilots"):
        st.session_state.quick_query = "Show me all available pilots"
    
    if st.button("🚁 Show All Drones"):
        st.session_state.quick_query = "Show me all available drones"
    
    if st.button("⚠️ Check All Conflicts"):
        st.session_state.quick_query = "Check for any conflicts in current assignments"
    
    st.header("🔗 Links")
    sheet_url = get_sheet_url()
    if sheet_url:
        st.markdown(f"[Open Google Sheet]({sheet_url})")
    
    st.markdown("---")
    st.caption("Built with Streamlit + LangChain + OpenAI")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.agent = None

if "quick_query" not in st.session_state:
    st.session_state.quick_query = None

# Initialize agent (cached)
if st.session_state.agent is None:
    with st.spinner("Initializing AI agent..."):
        st.session_state.agent = create_agent()
        
        if st.session_state.agent:
            # Add welcome message
            welcome_msg = """👋 **Welcome!** I'm your Drone Operations Coordinator AI assistant.

I can help you with:
- ✈️ Finding available pilots and drones
- 📝 Updating pilot/drone status
- 🎯 Assigning resources to missions
- ⚠️ Detecting conflicts and issues
- 🚨 Handling urgent reassignments

**Try asking:**
- "Show me available pilots in Bangalore"
- "Assign Arjun and D001 to Project PRJ001"
- "Check if Neha has any conflicts"
- "Mark pilot P004 as Available"

All changes sync automatically with Google Sheets! 🔄"""
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": welcome_msg
            })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle quick action queries
if st.session_state.quick_query:
    prompt = st.session_state.quick_query
    st.session_state.quick_query = None
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            if st.session_state.agent:
                response = run_agent(
                    st.session_state.agent,
                    prompt,
                    st.session_state.messages[:-1]  # Exclude current message
                )
            else:
                response = "❌ Agent not initialized. Please check your API keys configuration."
            
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask about pilots, drones, or missions..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            if st.session_state.agent:
                response = run_agent(
                    st.session_state.agent,
                    prompt,
                    st.session_state.messages[:-1]  # Exclude current message
                )
            else:
                response = "❌ Agent not initialized. Please check your API keys configuration."
            
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🔒 Data syncs with Google Sheets")

with col2:
    st.caption("🤖 Powered by OpenAI GPT-4o")

with col3:
    st.caption("⚡ Real-time conflict detection")
