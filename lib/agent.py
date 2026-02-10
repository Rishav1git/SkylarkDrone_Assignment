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
    Run the agent with user input using intelligent tool routing.
    
    Args:
        llm: Configured LLM instance
        user_input: User's message
        chat_history: Previous conversation messages
    
    Returns:
        Agent's response
    """
    try:
        from lib.sheets import load_all_data
        
        # Get tools
        tools = get_all_tools()
        tool_map = {tool.name: tool for tool in tools}
        
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
            # Smart assignment - parse names and execute
            pilots_df, drones_df, missions_df = load_all_data()
            
            # Try to extract pilot name (look for common names in input)
            pilot_id = None
            pilot_name = None
            for _, pilot in pilots_df.iterrows():
                name_lower = pilot['name'].lower()
                if name_lower in lower_input or pilot['pilot_id'].lower() in lower_input:
                    pilot_id = pilot['pilot_id']
                    pilot_name = pilot['name']
                    break
            
            # Try to extract project (look for "client" or "project" or "PRJ")
            project_id = None
            project_name = None
            for _, mission in missions_df.iterrows():
                proj_lower = mission['project_id'].lower()
                client_lower = mission.get('client', '').lower() if 'client' in mission else ''
                
                if proj_lower in lower_input or client_lower in lower_input:
                    project_id = mission['project_id']
                    project_name = mission.get('client', mission['project_id'])
                    break
            
            # Find available drone
            available_drones = drones_df[drones_df['status'] == 'Available']
            drone_id = available_drones.iloc[0]['drone_id'] if not available_drones.empty else None
            
            if pilot_id and project_id and drone_id:
                # Execute assignment
                result = tool_map["assign_to_mission"].func(
                    pilot_id=pilot_id,
                    drone_id=drone_id,
                    project_id=project_id
                )
            elif pilot_id and project_id:
                result = f"❌ Found pilot {pilot_name} ({pilot_id}) and project {project_name} ({project_id}), but no available drones!"
            elif pilot_id:
                result = f"❌ Found pilot {pilot_name} ({pilot_id}), but couldn't identify the project. Available projects:\n"
                for _, m in missions_df.head(3).iterrows():
                    result += f"• {m['project_id']}: {m.get('client', 'N/A')}\n"
            else:
                result = f"❌ Couldn't identify pilot in the query. Try using their name or ID. Available pilots:\n"
                for _, p in pilots_df[pilots_df['status'] == 'Available'].head(3).iterrows():
                    result += f"• {p['pilot_id']}: {p['name']}\n"
        
        else:
            # Use LLM for general queries
            system_msg = """You are a helpful AI assistant for drone operations. 
            Answer questions about pilot/drone management briefly and clearly."""
            
            messages = [
                SystemMessage(content=system_msg),
                HumanMessage(content=user_input)
            ]
            response = llm.invoke(messages)
            result = response.content
        
        return result if result else "I'm not sure how to help with that. Try asking about pilots, drones, or assignments."
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try rephrasing your request."
