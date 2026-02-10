"""
LangChain Agent Setup
Orchestrates the AI agent with OpenAI and custom tools.
"""

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from lib.tools import get_all_tools
import streamlit as st


def create_agent() -> AgentExecutor:
    """
    Create and configure the LangChain agent with OpenAI and custom tools.
    
    Returns:
        Configured AgentExecutor instance
    """
    # Get OpenAI API key from Streamlit secrets
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    
    if not api_key:
        st.error("OpenAI API key not found. Please configure in .streamlit/secrets.toml")
        return None
    
    # Initialize OpenAI LLM
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=api_key
    )
    
    # System prompt
    system_message = """You are an AI assistant for Skylark Drones operations coordination.

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

**Available Tools:**
- query_pilots: Find pilots by skills, location, or status
- query_drones: Find drones by capabilities, location, or status
- update_pilot_status_tool: Change pilot status (syncs to Google Sheets)
- update_drone_status_tool: Change drone status (syncs to Google Sheets)
- check_conflicts_tool: Detect scheduling conflicts and skill mismatches
- assign_to_mission_tool: Assign pilot and drone to mission (with conflict checking)
- urgent_reassign_tool: Handle priority-based resource reallocation

Always verify data before making changes. Be helpful and professional."""
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_message),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Get custom tools
    tools = get_all_tools()
    
    # Create agent
    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return agent_executor


def run_agent(agent_executor: AgentExecutor, user_input: str, chat_history: list = None) -> str:
    """
    Run the agent with user input and chat history.
    
    Args:
        agent_executor: Configured AgentExecutor
        user_input: User's message
        chat_history: Previous conversation messages
    
    Returns:
        Agent's response
    """
    try:
        result = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history or []
        })
        
        return result.get("output", "Sorry, I couldn't process that request.")
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try rephrasing your request or check the configuration."
