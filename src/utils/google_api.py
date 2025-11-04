"""
Google API utilities for address lookup and distance calculations
"""
import requests
import streamlit as st
from functools import lru_cache
from config.config import google_api_key

# Caching the Google Address lookup to avoid redundant API calls
@lru_cache(maxsize=100)
def get_google_address(address):
    """Get formatted address from Google Places API"""
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={address}&key={google_api_key}"

    # Make the API request
    response = requests.get(url)
    results = response.json()

    if response.status_code == 200 and "results" in results and len(results["results"]) > 0:
        # Use the first result to get the address
        google_location_address = results["results"][0]["formatted_address"]
        return google_location_address
    else:
        return None  # Return None if no result is found

def get_mileage(start_location_address, end_location_address, start_location_name, end_location_name, current_data_log):
    """Calculate mileage between two locations using Google Distance Matrix API"""
    # Check if the trip route already exists in the Mileage Log (to reuse cached distance)
    if trip_exists(start_location_name, end_location_name, current_data_log):
        # Find the existing mileage for this trip route
        existing_mileage = current_data_log[
            (current_data_log['start_location'] == start_location_name) & 
            (current_data_log['end_location'] == end_location_name)
        ]['distance'].values
        if existing_mileage.size > 0:
            # Return the existing mileage without showing a message (allows same route on different dates)
            return existing_mileage[0]

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": start_location_address,
        "destinations": end_location_address,
        "key": google_api_key
    }

    # Make the API request
    response = requests.get(url, params=params)
    
    if response.status_code == 200:  # Check if the request was successful
        response_json = response.json()
        rows = response_json.get("rows", [])
        
        if rows:
            elements = rows[0].get("elements", [])
            
            if elements and elements[0].get("status") == "OK":
                # Extract the distance in meters and convert to miles
                distance = elements[0].get("distance", {}).get("value", 0)
                if distance:
                    return round(distance / 1609.34)  # Convert to miles
                else:
                    st.error("Distance value is missing.")
            else:
                st.error(f"Error in response: {elements[0].get('status')}")
        else:
            st.error("No elements found in the API response.")
    else:
        st.error(f"API request failed with status code: {response.status_code}")
    
    return 0  # Return 0 miles if there was any error

def trip_exists(start_location_name, end_location_name, current_data_log):
    """Check if a trip already exists in the Mileage Log dataframe"""
    # Check if the trip exists in the current data log (compare both directions)
    return (
        (current_data_log['start_location'] == start_location_name) & 
        (current_data_log['end_location'] == end_location_name)
    ).any() or (
        (current_data_log['start_location'] == end_location_name) & 
        (current_data_log['end_location'] == start_location_name)
    ).any()
