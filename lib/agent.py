"""
Simple Agent Implementation
Direct tool calling without deprecated LangChain agent functions.
"""

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from lib.tools import get_all_tools
import streamlit as st
import json


def create_agent():
    """
    Create and configure the Groq LLM.
    
    Returns:
        Configured LLM instance and tools
    """
    # Get Groq API key from Streamlit secrets
    api_key = st.secrets.get("GROQ_API_KEY", "")
    
    if not api_key:
        st.error("Groq API key not found. Please configure in .streamlit/secrets.toml")
        return None
    
    # Initialize Groq LLM (FREE!)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=api_key
    )
    
    return llm


def run_agent(llm, user_input: str, chat_history: list = None) -> str:
    """
    Run the agent with user input using simple tool routing.
    
    Args:
        llm: Configured LLM instance
        user_input: User's message
        chat_history: Previous conversation messages
    
    Returns:
        Agent's response
    """
    try:
        # Get tools
        tools = get_all_tools()
        tool_map = {tool.name: tool for tool in tools}
        
        # Create system message with tool descriptions
        system_msg = """You are an AI assistant for Skylark Drones operations coordination.

Available tools and when to use them:
- query_pilots(skills, location, status): Find pilots by criteria. Use when asked about pilots, availability, or skills.
- query_drones(capabilities, location, status): Find drones by criteria. Use when asked about drones or equipment.
- update_pilot_status(pilot_id, new_status): Update pilot status. Use when changing pilot availability.
- update_drone_status(drone_id, new_status): Update drone status. Use when changing drone status.
- check_conflicts(pilot_id, drone_id, project_id): Check for conflicts. Use before assignments.
- assign_to_mission(pilot_id, drone_id, project_id): Assign resources. Use for new assignments.
- urgent_reassign(from_project, to_project, reason): Handle urgent reassignments.

For each request:
1. Determine which tool(s) to use
2. Call the appropriate tool(s)
3. Format the results clearly with emojis (✅ ⚠️ ❌)

Be concise and helpful."""
        
        # Determine which tool to call based on input
        lower_input = user_input.lower()
        
        # Simple keyword-based routing
        result = None
        
        if "pilot" in lower_input and ("show" in lower_input or "list" in lower_input or "available" in lower_input or "find" in lower_input):
            # Query pilots
            status = "Available" if "available" in lower_input else None
            result = tool_map["query_pilots"].func(skills=None, location=None, status=status)
            
        elif "drone" in lower_input and ("show" in lower_input or "list" in lower_input or "available" in lower_input or "find" in lower_input):
            # Query drones
            status = "Available" if "available" in lower_input else None
            result = tool_map["query_drones"].func(capabilities=None, location=None, status=status)
            
        elif "conflict" in lower_input or "check" in lower_input:
            # Check conflicts
            result = tool_map["check_conflicts"].func()
            
        elif "assign" in lower_input:
            # Let LLM handle assignment with context
            messages = [
                SystemMessage(content=system_msg),
                HumanMessage(content=f"{user_input}\n\nPlease guide me through making this assignment. What information do you need?")
            ]
            response = llm.invoke(messages)
            result = response.content
            
        else:
            # Use LLM for general queries
            messages = [
                SystemMessage(content=system_msg),
                HumanMessage(content=user_input)
            ]
            response = llm.invoke(messages)
            result = response.content
        
        return result if result else "I'm not sure how to help with that. Try asking about pilots, drones, or assignments."
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try rephrasing your request."
