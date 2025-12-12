"""
Supabase database utilities for the mileage tracker application
Replaces Google Sheets with Supabase PostgreSQL database
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from src.utils.auth import init_connection

def get_user_id():
    """Get the current authenticated user's ID"""
    if "user" in st.session_state:
        return st.session_state["user"].id
    return None

def get_mileage_dictionary():
    """
    Get all locations from Supabase mileage_dictionary table for current user
    Returns a pandas DataFrame
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return pd.DataFrame(columns=["location_name", "location_address"])
        
        supabase = init_connection()
        response = supabase.table('mileage_dictionary').select('*').eq('user_id', user_id).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Only return the columns we need for the UI
            return df[['location_name', 'location_address']]
        else:
            return pd.DataFrame(columns=["location_name", "location_address"])
    
    except Exception as e:
        st.error(f"Error loading locations: {str(e)}")
        return pd.DataFrame(columns=["location_name", "location_address"])

def add_location(location_name, location_address):
    """
    Add a new location to Supabase mileage_dictionary table
    """
    try:
        user_id = get_user_id()
        if not user_id:
            raise Exception("User not authenticated")
        
        supabase = init_connection()
        
        # Check if location already exists
        existing = supabase.table('mileage_dictionary').select('*').eq(
            'user_id', user_id
        ).eq(
            'location_name', location_name
        ).execute()
        
        if existing.data:
            raise Exception(f"Location '{location_name}' already exists")
        
        # Insert new location
        data = {
            "user_id": user_id,
            "location_name": location_name,
            "location_address": location_address
        }
        
        response = supabase.table('mileage_dictionary').insert(data).execute()
        return True
    
    except Exception as e:
        raise Exception(f"Error adding location: {str(e)}")

def update_location(location_id, location_name, location_address):
    """
    Update an existing location in Supabase mileage_dictionary table
    """
    try:
        user_id = get_user_id()
        if not user_id:
            raise Exception("User not authenticated")
        
        supabase = init_connection()
        
        # Update location
        data = {
            "location_name": location_name,
            "location_address": location_address
        }
        
        response = supabase.table('mileage_dictionary').update(data).eq(
            'id', location_id
        ).eq(
            'user_id', user_id
        ).execute()
        
        return True
    
    except Exception as e:
        raise Exception(f"Error updating location: {str(e)}")

def delete_location(location_id):
    """
    Delete a location from Supabase mileage_dictionary table
    """
    try:
        user_id = get_user_id()
        if not user_id:
            raise Exception("User not authenticated")
        
        supabase = init_connection()
        
        # Delete location
        response = supabase.table('mileage_dictionary').delete().eq(
            'id', location_id
        ).eq(
            'user_id', user_id
        ).execute()
        
        return True
    
    except Exception as e:
        raise Exception(f"Error deleting location: {str(e)}")

def get_mileage_log():
    """
    Get all trips from Supabase mileage_log table for current user
    Returns a pandas DataFrame sorted by date (newest first)
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return pd.DataFrame(columns=["date", "start_location", "start_address", 
                                        "end_location", "end_address", "distance"])
        
        supabase = init_connection()
        response = supabase.table('mileage_log').select('*').eq(
            'user_id', user_id
        ).order('date', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Only return the columns we need for the UI
            columns = ["date", "start_location", "start_address", 
                      "end_location", "end_address", "distance"]
            return df[columns]
        else:
            return pd.DataFrame(columns=["date", "start_location", "start_address", 
                                        "end_location", "end_address", "distance"])
    
    except Exception as e:
        st.error(f"Error loading trips: {str(e)}")
        return pd.DataFrame(columns=["date", "start_location", "start_address", 
                                    "end_location", "end_address", "distance"])

def add_trip(date, start_location, start_address, end_location, end_address, distance):
    """
    Add a new trip to Supabase mileage_log table
    """
    try:
        user_id = get_user_id()
        if not user_id:
            raise Exception("User not authenticated")
        
        supabase = init_connection()
        
        # Prepare data
        data = {
            "user_id": user_id,
            "date": str(date),
            "start_location": start_location,
            "start_address": start_address,
            "end_location": end_location,
            "end_address": end_address,
            "distance": float(distance) if distance else 0.0
        }
        
        response = supabase.table('mileage_log').insert(data).execute()
        return True
    
    except Exception as e:
        raise Exception(f"Error adding trip: {str(e)}")

def get_receipts():
    """
    Get all receipts from Supabase receipts table for current user
    Returns a pandas DataFrame sorted by date (newest first)
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return pd.DataFrame(columns=["date", "store_name", "total", "upload_timestamp"])
        
        supabase = init_connection()
        response = supabase.table('receipts').select('*').eq(
            'user_id', user_id
        ).order('date', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Only return the columns we need for the UI
            columns = ["date", "store_name", "total", "upload_timestamp"]
            return df[columns]
        else:
            return pd.DataFrame(columns=["date", "store_name", "total", "upload_timestamp"])
    
    except Exception as e:
        st.error(f"Error loading receipts: {str(e)}")
        return pd.DataFrame(columns=["date", "store_name", "total", "upload_timestamp"])

def add_receipt(date, store_name, total, ocr_raw_text=None):
    """
    Add a new receipt to Supabase receipts table
    """
    try:
        user_id = get_user_id()
        if not user_id:
            raise Exception("User not authenticated")
        
        supabase = init_connection()
        
        # Prepare data
        data = {
            "user_id": user_id,
            "date": str(date),
            "store_name": store_name,
            "total": float(total) if total else 0.0,
            "upload_timestamp": datetime.now().isoformat(),
            "ocr_raw_text": ocr_raw_text
        }
        
        response = supabase.table('receipts').insert(data).execute()
        return True
    
    except Exception as e:
        raise Exception(f"Error adding receipt: {str(e)}")

def get_data(table_name, create_if_missing=False, headers=None):
    """Get data from Supabase table"""
    supabase_client = init_connection()
    user_id = st.session_state.get("user").id if "user" in st.session_state else None
    
    if not user_id:
        return pd.DataFrame()
    
    try:
        # Map table names to Supabase tables
        if table_name == "Mileage_Dictionary":
            response = supabase_client.table("mileage_dictionary").select("*").eq("user_id", user_id).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                # Only return the columns we need for the UI
                return df[['location_name', 'location_address']]
            else:
                return pd.DataFrame(columns=["location_name", "location_address"])
        
        elif table_name == "mileage_log":
            response = supabase_client.table("mileage_log").select("*").eq("user_id", user_id).order("date", desc=True).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                # Only return the columns we need for the UI
                columns = ["date", "start_location", "start_address", 
                          "end_location", "end_address", "distance"]
                return df[columns]
            else:
                return pd.DataFrame(columns=["date", "start_location", "start_address", 
                                            "end_location", "end_address", "distance"])
        
        elif table_name == "Receipts":
            response = supabase_client.table("receipts").select("*").eq("user_id", user_id).order("date", desc=True).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                # Only return the columns we need for the UI
                columns = ["date", "store_name", "total", "upload_timestamp"]
                return df[columns]
            else:
                return pd.DataFrame(columns=["date", "store_name", "total", "upload_timestamp"])
        
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data from {table_name}: {str(e)}")
        return pd.DataFrame()

def add_data(data, table_name):
    """
    Add data to Supabase tables
    Handles both DataFrame and list/tuple data formats
    
    Args:
        data: DataFrame or list/tuple of values to insert
        table_name: Name of the table/data type ('Mileage_Dictionary', 'mileage_log', 'Receipts')
    """
    try:
        user_id = get_user_id()
        if not user_id:
            raise Exception("User not authenticated")
        
        supabase = init_connection()
        
        # Handle Mileage Dictionary
        if table_name == "Mileage_Dictionary":
            if isinstance(data, pd.DataFrame):
                # DataFrame format: batch insert
                for _, row in data.iterrows():
                    location_data = {
                        "user_id": user_id,
                        "location_name": row[0],  # First column
                        "location_address": row[1]  # Second column
                    }
                    supabase.table('mileage_dictionary').insert(location_data).execute()
            else:
                # List/tuple format: single insert
                location_data = {
                    "user_id": user_id,
                    "location_name": data[0],
                    "location_address": data[1]
                }
                supabase.table('mileage_dictionary').insert(location_data).execute()
            st.success("Location(s) added successfully!")
            
        # Handle Mileage Log
        elif table_name == "mileage_log":
            if isinstance(data, pd.DataFrame):
                # DataFrame format: batch insert
                for _, row in data.iterrows():
                    trip_data = {
                        "user_id": user_id,
                        "date": str(row[0]),
                        "start_location": row[1],
                        "start_address": row[2],
                        "end_location": row[3],
                        "end_address": row[4],
                        "distance": float(row[5])
                    }
                    supabase.table('mileage_log').insert(trip_data).execute()
            else:
                # List/tuple format: single insert
                trip_data = {
                    "user_id": user_id,
                    "date": str(data[0]),
                    "start_location": data[1],
                    "start_address": data[2],
                    "end_location": data[3],
                    "end_address": data[4],
                    "distance": float(data[5])
                }
                supabase.table('mileage_log').insert(trip_data).execute()
            st.success("Trip(s) added successfully!")
            
        # Handle Receipts
        elif table_name == "Receipts":
            if isinstance(data, pd.DataFrame):
                # DataFrame format: batch insert
                for _, row in data.iterrows():
                    receipt_data = {
                        "user_id": user_id,
                        "date": str(row[0]),
                        "store_name": row[1],
                        "total": float(row[2]) if row[2] else 0.0,
                        "upload_timestamp": row[3] if len(row) > 3 else datetime.now().isoformat()
                    }
                    supabase.table('receipts').insert(receipt_data).execute()
            else:
                # List/tuple format: single insert
                receipt_data = {
                    "user_id": user_id,
                    "date": str(data[0]),
                    "store_name": data[1],
                    "total": float(data[2]) if data[2] else 0.0,
                    "upload_timestamp": data[3] if len(data) > 3 else datetime.now().isoformat()
                }
                supabase.table('receipts').insert(receipt_data).execute()
            st.success("Receipt(s) added successfully!")
        else:
            st.warning(f"Unknown table name: {table_name}")
            
    except Exception as e:
        st.error(f"Error adding data to {table_name}: {str(e)}")
        raise

# Backward compatibility alias
def append_to_gsheet(data, sheet_name):
    """
    Legacy function name - calls add_data()
    Kept for backward compatibility with existing code
    """
    return add_data(data, sheet_name)
