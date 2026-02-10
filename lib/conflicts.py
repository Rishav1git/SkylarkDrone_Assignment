"""
Conflict Detection Engine
Handles all edge case detection for pilot and drone assignments.
"""

from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional


def detect_all_conflicts(
    pilot_id: Optional[str] = None,
    drone_id: Optional[str] = None,
    project_id: Optional[str] = None,
    pilots_df: Optional[pd.DataFrame] = None,
    drones_df: Optional[pd.DataFrame] = None,
    missions_df: Optional[pd.DataFrame] = None
) -> List[Dict]:
    """
    Run all conflict detection checks.
    
    Returns:
        List of conflict dictionaries with 'type', 'severity', and 'message' keys
    """
    conflicts = []
    
    if pilot_id and pilots_df is not None:
        conflicts.extend(check_pilot_conflicts(pilot_id, pilots_df, missions_df))
    
    if drone_id and drones_df is not None:
        conflicts.extend(check_drone_conflicts(drone_id, drones_df))
    
    if pilot_id and project_id and all([pilots_df is not None, missions_df is not None]):
        conflicts.extend(check_skill_mismatch(pilot_id, project_id, pilots_df, missions_df))
    
    if all([pilot_id, drone_id, project_id, pilots_df is not None, drones_df is not None, missions_df is not None]):
        conflicts.extend(check_location_mismatch(pilot_id, drone_id, project_id, pilots_df, drones_df, missions_df))
    
    return conflicts


def check_pilot_conflicts(
    pilot_id: str,
    pilots_df: pd.DataFrame,
    missions_df: Optional[pd.DataFrame] = None
) -> List[Dict]:
    """
    Check for pilot-related conflicts:
    1. Double booking (already assigned)
    2. Unavailability (on leave)
    """
    conflicts = []
    
    # Find pilot
    pilot_rows = pilots_df[pilots_df['pilot_id'] == pilot_id]
    if pilot_rows.empty:
        conflicts.append({
            'type': 'NOT_FOUND',
            'severity': 'CRITICAL',
            'message': f"Pilot {pilot_id} not found in roster"
        })
        return conflicts
    
    pilot = pilot_rows.iloc[0]
    
    # 1. Double Booking Check
    if pilot['status'] == 'Assigned' and str(pilot['current_assignment']) != '–':
        conflicts.append({
            'type': 'DOUBLE_BOOKING',
            'severity': 'CRITICAL',
            'message': f"Pilot {pilot_id} ({pilot['name']}) already assigned to {pilot['current_assignment']}"
        })
    
    # 2. Availability Check
    if pilot['status'] == 'On Leave':
        conflicts.append({
            'type': 'UNAVAILABLE',
            'severity': 'CRITICAL',
            'message': f"Pilot {pilot_id} is on leave until {pilot['available_from']}"
        })
    
    return conflicts


def check_skill_mismatch(
    pilot_id: str,
    project_id: str,
    pilots_df: pd.DataFrame,
    missions_df: pd.DataFrame
) -> List[Dict]:
    """
    Check if pilot has required skills and certifications for the mission.
    """
    conflicts = []
    
    # Find pilot and mission
    pilot_rows = pilots_df[pilots_df['pilot_id'] == pilot_id]
    mission_rows = missions_df[missions_df['project_id'] == project_id]
    
    if pilot_rows.empty or mission_rows.empty:
        return conflicts
    
    pilot = pilot_rows.iloc[0]
    mission = mission_rows.iloc[0]
    
    # Get skills and certifications as sets
    pilot_skills = set(pilot['skills']) if isinstance(pilot['skills'], list) else set()
    required_skills = set(mission['required_skills']) if isinstance(mission['required_skills'], list) else set()
    
    pilot_certs = set(pilot['certifications']) if isinstance(pilot['certifications'], list) else set()
    required_certs = set(mission['required_certs']) if isinstance(mission['required_certs'], list) else set()
    
    # Find missing skills and certs
    missing_skills = required_skills - pilot_skills
    missing_certs = required_certs - pilot_certs
    
    if missing_skills:
        conflicts.append({
            'type': 'SKILL_MISMATCH',
            'severity': 'HIGH',
            'message': f"Pilot {pilot_id} lacks required skills: {', '.join(missing_skills)}"
        })
    
    if missing_certs:
        conflicts.append({
            'type': 'CERTIFICATION_MISMATCH',
            'severity': 'CRITICAL',
            'message': f"Pilot {pilot_id} lacks required certifications: {', '.join(missing_certs)}"
        })
    
    return conflicts


def check_drone_conflicts(
    drone_id: str,
    drones_df: pd.DataFrame
) -> List[Dict]:
    """
    Check for drone-related conflicts:
    1. Drone in maintenance
    2. Maintenance due soon
    3. Double booking
    """
    conflicts = []
    
    # Find drone
    drone_rows = drones_df[drones_df['drone_id'] == drone_id]
    if drone_rows.empty:
        conflicts.append({
            'type': 'NOT_FOUND',
            'severity': 'CRITICAL',
            'message': f"Drone {drone_id} not found in fleet"
        })
        return conflicts
    
    drone = drone_rows.iloc[0]
    
    # 1. Maintenance Status Check
    if drone['status'] == 'Maintenance':
        conflicts.append({
            'type': 'MAINTENANCE_CONFLICT',
            'severity': 'CRITICAL',
            'message': f"Drone {drone_id} is currently in maintenance"
        })
    
    # 2. Maintenance Due Check (within next 7 days)
    try:
        maintenance_due = pd.to_datetime(drone['maintenance_due'])
        days_until_maintenance = (maintenance_due - datetime.now()).days
        
        if 0 <= days_until_maintenance <= 7:
            conflicts.append({
                'type': 'MAINTENANCE_DUE',
                'severity': 'WARNING',
                'message': f"Drone {drone_id} maintenance due on {maintenance_due.date()} ({days_until_maintenance} days)"
            })
    except:
        pass  # Skip if maintenance_due is not a valid date
    
    # 3. Double Booking Check
    if drone['status'] == 'Assigned' and str(drone['current_assignment']) != '–':
        conflicts.append({
            'type': 'DOUBLE_BOOKING',
            'severity': 'CRITICAL',
            'message': f"Drone {drone_id} already assigned to {drone['current_assignment']}"
        })
    
    return conflicts


def check_location_mismatch(
    pilot_id: str,
    drone_id: str,
    project_id: str,
    pilots_df: pd.DataFrame,
    drones_df: pd.DataFrame,
    missions_df: pd.DataFrame
) -> List[Dict]:
    """
    Check if pilot, drone, and mission are in compatible locations.
    """
    conflicts = []
    
    # Find all entities
    pilot_rows = pilots_df[pilots_df['pilot_id'] == pilot_id]
    drone_rows = drones_df[drones_df['drone_id'] == drone_id]
    mission_rows = missions_df[missions_df['project_id'] == project_id]
    
    if pilot_rows.empty or drone_rows.empty or mission_rows.empty:
        return conflicts
    
    pilot = pilot_rows.iloc[0]
    drone = drone_rows.iloc[0]
    mission = mission_rows.iloc[0]
    
    pilot_location = str(pilot['location']).strip()
    drone_location = str(drone['location']).strip()
    mission_location = str(mission['location']).strip()
    
    # Check pilot-mission location mismatch
    if pilot_location != mission_location:
        conflicts.append({
            'type': 'LOCATION_MISMATCH',
            'severity': 'WARNING',
            'message': f"Pilot in {pilot_location}, mission in {mission_location} - requires travel coordination"
        })
    
    # Check drone-mission location mismatch
    if drone_location != mission_location:
        conflicts.append({
            'type': 'LOCATION_MISMATCH',
            'severity': 'WARNING',
            'message': f"Drone in {drone_location}, mission in {mission_location} - requires transport"
        })
    
    return conflicts


def get_conflict_summary(conflicts: List[Dict]) -> str:
    """
    Generate a formatted summary of conflicts.
    """
    if not conflicts:
        return "✅ No conflicts detected"
    
    # Group by severity
    critical = [c for c in conflicts if c['severity'] == 'CRITICAL']
    high = [c for c in conflicts if c['severity'] == 'HIGH']
    warnings = [c for c in conflicts if c['severity'] == 'WARNING']
    
    summary_lines = []
    
    if critical:
        summary_lines.append(f"🚫 **{len(critical)} CRITICAL** issue(s):")
        for c in critical:
            summary_lines.append(f"   - {c['message']}")
    
    if high:
        summary_lines.append(f"\n⚠️ **{len(high)} HIGH** priority warning(s):")
        for c in high:
            summary_lines.append(f"   - {c['message']}")
    
    if warnings:
        summary_lines.append(f"\nℹ️ **{len(warnings)} WARNING**(s):")
        for c in warnings:
            summary_lines.append(f"   - {c['message']}")
    
    return "\n".join(summary_lines)


def can_proceed_with_assignment(conflicts: List[Dict]) -> bool:
    """
    Determine if assignment can proceed despite conflicts.
    CRITICAL conflicts block the assignment.
    """
    return not any(c['severity'] == 'CRITICAL' for c in conflicts)
