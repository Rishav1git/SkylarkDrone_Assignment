"""
Google Sheets Integration Module
Handles 2-way sync with Google Sheets for pilot roster, drone fleet, and missions data.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple


@st.cache_resource
def get_gspread_client():
    """
    Authenticate and return gspread client (cached for performance).
    Uses Streamlit secrets in production, local file for development.
    """
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        # Try Streamlit secrets first (for deployed app)
        if hasattr(st, 'secrets') and 'GOOGLE_SHEETS_CREDENTIALS' in st.secrets:
            creds_dict = dict(st.secrets['GOOGLE_SHEETS_CREDENTIALS'])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # Fall back to local credentials file (for development)
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'credentials.json', scope
            )
        
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Failed to authenticate with Google Sheets: {e}")
        return None


@st.cache_data(ttl=60)  # Cache for 60 seconds to avoid API quota limits
def load_pilot_roster() -> pd.DataFrame:
    """
    Load pilot roster from Google Sheets and return as pandas DataFrame.
    Parses comma-separated skills and certifications into lists.
    """
    try:
        client = get_gspread_client()
        if not client:
            return pd.DataFrame()
        
        sheet = client.open("Skylark Drone Operations").worksheet("Pilots")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Parse comma-separated fields into lists
        if not df.empty:
            df['skills'] = df['skills'].apply(
                lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
            )
            df['certifications'] = df['certifications'].apply(
                lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
            )
        
        return df
    except Exception as e:
        st.error(f"Failed to load pilot roster: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)  # Cache for 60 seconds to avoid API quota limits
def load_drone_fleet() -> pd.DataFrame:
    """
    Load drone fleet from Google Sheets and return as pandas DataFrame.
    Parses comma-separated capabilities into lists.
    """
    try:
        client = get_gspread_client()
        if not client:
            return pd.DataFrame()
        
        sheet = client.open("Skylark Drone Operations").worksheet("Drones")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Parse comma-separated capabilities
        if not df.empty:
            df['capabilities'] = df['capabilities'].apply(
                lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
            )
        
        return df
    except Exception as e:
        st.error(f"Failed to load drone fleet: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)  # Cache for 60 seconds to avoid API quota limits
def load_missions() -> pd.DataFrame:
    """
    Load missions from Google Sheets and return as pandas DataFrame.
    Parses comma-separated skills/certs and dates.
    """
    try:
        client = get_gspread_client()
        if not client:
            return pd.DataFrame()
        
        sheet = client.open("Skylark Drone Operations").worksheet("Missions")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Parse comma-separated fields
        if not df.empty:
            df['required_skills'] = df['required_skills'].apply(
                lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
            )
            df['required_certs'] = df['required_certs'].apply(
                lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
            )
            
            # Parse dates
            df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
            df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Failed to load missions: {e}")
        return pd.DataFrame()


def load_all_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all data from Google Sheets.
    Returns: (pilots_df, drones_df, missions_df)
    """
    pilots = load_pilot_roster()
    drones = load_drone_fleet()
    missions = load_missions()
    return pilots, drones, missions


def update_pilot_status(pilot_id: str, new_status: str, assignment: str = "–") -> bool:
    """
    Update pilot status in Google Sheet (WRITE operation).
    
    Args:
        pilot_id: Pilot identifier (e.g., 'P001')
        new_status: New status ('Available', 'Assigned', 'On Leave')
        assignment: Project assignment (default: '–' for no assignment)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_gspread_client()
        if not client:
            return False
        
        sheet = client.open("Skylark Drone Operations").worksheet("Pilots")
        
        # Find pilot row
        cell = sheet.find(pilot_id)
        if not cell:
            st.error(f"Pilot {pilot_id} not found in sheet")
            return False
        
        row = cell.row
        
        # Update status (column 6) and assignment (column 7)
        # Assuming: pilot_id, name, skills, certifications, location, status, current_assignment, available_from
        sheet.update_cell(row, 6, new_status)
        sheet.update_cell(row, 7, assignment)
        
        # Clear cache to reload fresh data
        st.cache_resource.clear()
        
        return True
    except Exception as e:
        st.error(f"Failed to update pilot status: {e}")
        return False


def update_drone_status(drone_id: str, new_status: str, assignment: str = "–") -> bool:
    """
    Update drone status in Google Sheet (WRITE operation).
    
    Args:
        drone_id: Drone identifier (e.g., 'D001')
        new_status: New status ('Available', 'Maintenance', 'Assigned')
        assignment: Project assignment (default: '–' for no assignment)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_gspread_client()
        if not client:
            return False
        
        sheet = client.open("Skylark Drone Operations").worksheet("Drones")
        
        # Find drone row
        cell = sheet.find(drone_id)
        if not cell:
            st.error(f"Drone {drone_id} not found in sheet")
            return False
        
        row = cell.row
        
        # Update status (column 4) and assignment (column 6)
        # Assuming: drone_id, model, capabilities, status, location, current_assignment, maintenance_due
        sheet.update_cell(row, 4, new_status)
        sheet.update_cell(row, 6, assignment)
        
        # Clear cache to reload fresh data
        st.cache_resource.clear()
        
        return True
    except Exception as e:
        st.error(f"Failed to update drone status: {e}")
        return False


def get_sheet_url() -> str:
    """
    Get the URL of the Google Sheet for reference.
    """
    try:
        client = get_gspread_client()
        if not client:
            return ""
        
        sheet = client.open("Skylark Drone Operations")
        return sheet.url
    except:
        return ""
