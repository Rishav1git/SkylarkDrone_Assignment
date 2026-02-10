"""
LangChain Agent Setup
Orchestrates the AI agent with Groq and custom tools.
"""

from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from lib.tools import get_all_tools
import streamlit as st


def create_agent():
    """
    Create and configure the LangChain agent with Groq and custom tools.
    
    Returns:
        Configured agent instance
    """
    # Get Groq API key from Streamlit secrets
    api_key = st.secrets.get("GROQ_API_KEY", "")
    
    if not api_key:
        st.error("Groq API key not found. Please configure in .streamlit/secrets.toml")
        return None
    
    # Initialize Groq LLM (FREE!)
    llm = ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0,
        api_key=api_key
    )
    
    # Get custom tools
    tools = get_all_tools()
    
    # System prompt prefix
    system_prefix = """You are an AI assistant for Skylark Drones operations coordination.

Your job is to help coordinate drone operations by:
- Managing pilot rosters and availability
- Tracking drone fleet inventory
- Matching pilots to missions based on skills, certifications, and location
- Detecting and preventing scheduling conflicts
- Handling urgent reassignments

**Important Guidelines:**
1. Always check for conflicts BEFORE making assignments
2. Be concise and actionable in your responses
3. Use emojis to make responses clearer (✅ for success, ⚠️ for warnings, ❌ for errors)
4. When conflicts are detected, explain them clearly and suggest alternatives
5. Confirm Google Sheets updates in your responses

Always verify data before making changes. Be helpful and professional."""
    
    # Create agent using simpler initialization (better Groq compatibility)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        agent_kwargs={
            "prefix": system_prefix
        }
    )
    
    return agent


def run_agent(agent, user_input: str, chat_history: list = None) -> str:
    """
    Run the agent with user input.
    
    Args:
        agent: Configured agent instance
        user_input: User's message
        chat_history: Previous conversation messages (not used with STRUCTURED_CHAT)
    
    Returns:
        Agent's response
    """
    try:
        result = agent.run(user_input)
        return result
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try rephrasing your request or check the configuration."
