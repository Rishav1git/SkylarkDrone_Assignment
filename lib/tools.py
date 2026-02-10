"""
LangChain Custom Tools
Defines custom tools for the AI agent to interact with drone operations data.
"""

from langchain.tools import tool
from typing import Optional
import pandas as pd
from lib.sheets import update_pilot_status as sheets_update_pilot, update_drone_status as sheets_update_drone, load_all_data
from lib.conflicts import detect_all_conflicts, get_conflict_summary, can_proceed_with_assignment


@tool
def query_pilots(skills: Optional[str] = None, location: Optional[str] = None, status: Optional[str] = None) -> str:
    """
    Query pilots by skills, location, or status.
    
    Args:
        skills: Required skill (e.g., 'Mapping', 'Inspection')
        location: Location filter (e.g., 'Bangalore', 'Mumbai')
        status: Status filter ('Available', 'Assigned', 'On Leave')
    
    Returns:
        Formatted string with matching pilots
    """
    pilots_df, _, _ = load_all_data()
    
    if pilots_df.empty:
        return "❌ No pilot data available"
    
    # Apply filters
    filtered = pilots_df.copy()
    
    if skills:
        filtered = filtered[filtered['skills'].apply(
            lambda x: any(skills.lower() in s.lower() for s in x) if isinstance(x, list) else False
        )]
    
    if location:
        filtered = filtered[filtered['location'].str.lower() == location.lower()]
    
    if status:
        filtered = filtered[filtered['status'].str.lower() == status.lower()]
    
    if filtered.empty:
        return f"No pilots found matching criteria: skills={skills}, location={location}, status={status}"
    
    # Format results
    results = []
    results.append(f"Found {len(filtered)} pilot(s):\n")
    
    for _, pilot in filtered.iterrows():
        skills_str = ', '.join(pilot['skills']) if isinstance(pilot['skills'], list) else str(pilot['skills'])
        certs_str = ', '.join(pilot['certifications']) if isinstance(pilot['certifications'], list) else str(pilot['certifications'])
        
        results.append(
            f"• **{pilot['pilot_id']}** - {pilot['name']}\n"
            f"  Skills: {skills_str}\n"
            f"  Certifications: {certs_str}\n"
            f"  Location: {pilot['location']}\n"
            f"  Status: {pilot['status']}\n"
            f"  Current assignment: {pilot['current_assignment']}\n"
        )
    
    return "\n".join(results)


@tool
def query_drones(capabilities: Optional[str] = None, location: Optional[str] = None, status: Optional[str] = None) -> str:
    """
    Query drones by capabilities, location, or status.
    
    Args:
        capabilities: Required capability (e.g., 'Thermal', 'LiDAR', 'RGB')
        location: Location filter (e.g., 'Bangalore', 'Mumbai')
        status: Status filter ('Available', 'Maintenance', 'Assigned')
    
    Returns:
        Formatted string with matching drones
    """
    _, drones_df, _ = load_all_data()
    
    if drones_df.empty:
        return "❌ No drone data available"
    
    # Apply filters
    filtered = drones_df.copy()
    
    if capabilities:
        filtered = filtered[filtered['capabilities'].apply(
            lambda x: any(capabilities.lower() in c.lower() for c in x) if isinstance(x, list) else False
        )]
    
    if location:
        filtered = filtered[filtered['location'].str.lower() == location.lower()]
    
    if status:
        filtered = filtered[filtered['status'].str.lower() == status.lower()]
    
    if filtered.empty:
        return f"No drones found matching criteria: capabilities={capabilities}, location={location}, status={status}"
    
    # Format results
    results = []
    results.append(f"Found {len(filtered)} drone(s):\n")
    
    for _, drone in filtered.iterrows():
        caps_str = ', '.join(drone['capabilities']) if isinstance(drone['capabilities'], list) else str(drone['capabilities'])
        
        results.append(
            f"• **{drone['drone_id']}** - {drone['model']}\n"
            f"  Capabilities: {caps_str}\n"
            f"  Location: {drone['location']}\n"
            f"  Status: {drone['status']}\n"
            f"  Current assignment: {drone['current_assignment']}\n"
            f"  Maintenance due: {drone['maintenance_due']}\n"
        )
    
    return "\n".join(results)


@tool
def update_pilot_status(pilot_id: str, new_status: str) -> str:
    """
    Update pilot status in Google Sheets.
    
    Args:
        pilot_id: Pilot ID (e.g., 'P001')
        new_status: New status ('Available', 'Assigned', 'On Leave')
    
    Returns:
        Confirmation message
    """
    valid_statuses = ['Available', 'Assigned', 'On Leave']
    
    if new_status not in valid_statuses:
        return f"❌ Invalid status. Must be one of: {', '.join(valid_statuses)}"
    
    # If setting to Available or On Leave, clear assignment
    assignment = "–" if new_status in ['Available', 'On Leave'] else None
    
    success = sheets_update_pilot(pilot_id, new_status, assignment or "–")
    
    if success:
        return f"✅ Updated {pilot_id} status to '{new_status}'. Google Sheet synced."
    else:
        return f"❌ Failed to update {pilot_id} status. Check if pilot exists."


@tool
def update_drone_status(drone_id: str, new_status: str) -> str:
    """
    Update drone status in Google Sheets.
    
    Args:
        drone_id: Drone ID (e.g., 'D001')
        new_status: New status ('Available', 'Maintenance', 'Assigned')
    
    Returns:
        Confirmation message
    """
    valid_statuses = ['Available', 'Maintenance', 'Assigned']
    
    if new_status not in valid_statuses:
        return f"❌ Invalid status. Must be one of: {', '.join(valid_statuses)}"
    
    assignment = "–" if new_status in ['Available', 'Maintenance'] else None
    
    success = sheets_update_drone(drone_id, new_status, assignment or "–")
    
    if success:
        return f"✅ Updated {drone_id} status to '{new_status}'. Google Sheet synced."
    else:
        return f"❌ Failed to update {drone_id} status. Check if drone exists."


@tool
def check_conflicts(pilot_id: Optional[str] = None, drone_id: Optional[str] = None, project_id: Optional[str] = None) -> str:
    """
    Check for scheduling conflicts, skill mismatches, and equipment issues.
    
    Args:
        pilot_id: Pilot ID to check (optional)
        drone_id: Drone ID to check (optional)
        project_id: Project ID to check against (optional)
    
    Returns:
        Conflict report
    """
    pilots_df, drones_df, missions_df = load_all_data()
    
    conflicts = detect_all_conflicts(
        pilot_id=pilot_id,
        drone_id=drone_id,
        project_id=project_id,
        pilots_df=pilots_df,
        drones_df=drones_df,
        missions_df=missions_df
    )
    
    return get_conflict_summary(conflicts)


@tool
def assign_to_mission(pilot_id: str, drone_id: str, project_id: str) -> str:
    """
    Assign pilot and drone to a mission after checking conflicts.
    
    Args:
        pilot_id: Pilot ID (e.g., 'P001')
        drone_id: Drone ID (e.g., 'D001')
        project_id: Project ID (e.g., 'PRJ001')
    
    Returns:
        Assignment result with conflict warnings
    """
    # Load data
    pilots_df, drones_df, missions_df = load_all_data()
    
    # Check if entities exist
    if pilots_df[pilots_df['pilot_id'] == pilot_id].empty:
        return f"❌ Pilot {pilot_id} not found"
    
    if drones_df[drones_df['drone_id'] == drone_id].empty:
        return f"❌ Drone {drone_id} not found"
    
    if missions_df[missions_df['project_id'] == project_id].empty:
        return f"❌ Project {project_id} not found"
    
    # Detect conflicts
    conflicts = detect_all_conflicts(
        pilot_id=pilot_id,
        drone_id=drone_id,
        project_id=project_id,
        pilots_df=pilots_df,
        drones_df=drones_df,
        missions_df=missions_df
    )
    
    # Check if can proceed
    if not can_proceed_with_assignment(conflicts):
        return f"❌ **Cannot assign due to CRITICAL conflicts:**\n\n{get_conflict_summary(conflicts)}"
    
    # Proceed with assignment
    pilot_updated = sheets_update_pilot(pilot_id, 'Assigned', project_id)
    drone_updated = sheets_update_drone(drone_id, 'Assigned', project_id)
    
    if pilot_updated and drone_updated:
        result = f"✅ **Assignment successful!**\n\n"
        result += f"• Pilot {pilot_id} assigned to {project_id}\n"
        result += f"• Drone {drone_id} assigned to {project_id}\n"
        result += f"• Google Sheets updated\n"
        
        if conflicts:
            result += f"\n⚠️ **Warnings:**\n{get_conflict_summary(conflicts)}"
        
        return result
    else:
        return f"❌ Assignment failed during Google Sheets update"


@tool
def urgent_reassign(from_project: str, to_project: str, reason: str = "Urgent priority") -> str:
    """
    Handle urgent reassignment of resources from lower to higher priority mission.
    
    Args:
        from_project: Source project ID to take resources from
        to_project: Destination project ID (urgent)
        reason: Reason for reassignment
    
    Returns:
        Reassignment plan and impact analysis
    """
    pilots_df, drones_df, missions_df = load_all_data()
    
    # Find current assignments for from_project
    assigned_pilots = pilots_df[pilots_df['current_assignment'] == from_project]
    assigned_drones = drones_df[drones_df['current_assignment'] == from_project]
    
    if assigned_pilots.empty and assigned_drones.empty:
        return f"❌ No resources currently assigned to {from_project}"
    
    # Get mission details
    to_mission_rows = missions_df[missions_df['project_id'] == to_project]
    if to_mission_rows.empty:
        return f"❌ Project {to_project} not found"
    
    to_mission = to_mission_rows.iloc[0]
    
    result = f"🚨 **URGENT REASSIGNMENT PLAN**\n\n"
    result += f"**From:** {from_project}\n"
    result += f"**To:** {to_project} (Priority: {to_mission['priority']})\n"
    result += f"**Reason:** {reason}\n\n"
    
    result += "**Resources to reassign:**\n"
    
    if not assigned_pilots.empty:
        for _, pilot in assigned_pilots.iterrows():
            result += f"• Pilot {pilot['pilot_id']} ({pilot['name']})\n"
    
    if not assigned_drones.empty:
        for _, drone in assigned_drones.iterrows():
            result += f"• Drone {drone['drone_id']} ({drone['model']})\n"
    
    result += f"\n**Impact:**\n"
    result += f"• {from_project} will need replacement resources\n"
    result += f"• {to_project} can start immediately after reassignment\n\n"
    
    result += "⚠️ **Note:** Execute assignment using `assign_to_mission` to complete reassignment."
    
    return result


def get_all_tools():
    """Return list of all custom tools for the agent."""
    return [
        query_pilots,
        query_drones,
        update_pilot_status,
        update_drone_status,
        check_conflicts,
        assign_to_mission,
        urgent_reassign
    ]
