import pandas as pd
import streamlit as st
import requests
from datetime import datetime, date
from functools import lru_cache
import gspread
from google.oauth2 import service_account

st.set_page_config(page_title="Mileage Manager", layout="wide")

# Load secrets
secrets = st.secrets["gsheets"]
google_api_key = st.secrets["google"]["api_key"]
SPREADSHEET_ID = secrets["spreadsheet_id"]

# Define the scope for Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Load credentials
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gspread_service"], scopes=SCOPES
)

# Authenticate with gspread
client = gspread.authorize(creds)

# Caching the Google Address lookup to avoid redundant API calls
@lru_cache(maxsize=100)
def get_google_address(address):
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

# Function to check if a trip already exists in the Mileage Log dataframe
def trip_exists(start_location_name, end_location_name):
    # Check if the trip exists in the current data log (compare both directions)
    return (
        (current_data_log['start_location_name'] == start_location_name) & 
        (current_data_log['end_location_name'] == end_location_name)
    ).any() or (
        (current_data_log['start_location_name'] == end_location_name) & 
        (current_data_log['end_location_name'] == start_location_name)
    ).any()

def get_mileage(start_location_address, end_location_address, start_location_name, end_location_name):
    # Check if the trip already exists in the Mileage Log
    if trip_exists(start_location_name, end_location_name):
        # Find the existing mileage for this trip
        existing_mileage = current_data_log[
            (current_data_log['start_location_name'] == start_location_name) & 
            (current_data_log['end_location_name'] == end_location_name)
        ]['total_mileage'].values
        if existing_mileage.size > 0:
            st.success("Trip already exists in the Mileage Log!")
            return existing_mileage[0]  # Return the existing mileage if found

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

# Function to append new data to Google Sheets (Mileage_Dictionary and Mileage_Log)
def append_to_gsheet(new_data, sheet_name):
    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)

    for _, row in new_data.iterrows():
        worksheet.append_row(row.tolist())

    st.success(f"Changes successfully submitted to {sheet_name}!")

# Streamlit UI
st.title("Mileage Manager")

# Session state to store new entries for both sheets
if 'entries_mileage_log' not in st.session_state:
    st.session_state.entries_mileage_log = []
if 'entries_mileage_dict' not in st.session_state:
    st.session_state.entries_mileage_dict = []

# Read the current Google Sheet data for Mileage_Dictionary
current_data_dicitionary = client.open_by_key(SPREADSHEET_ID).worksheet("Mileage_Dictionary")
data = current_data_dicitionary.get_all_records()
current_data_dict = pd.DataFrame(data)

# Read the current Google Sheet data for Mileage_Log
current_data_log_ws = client.open_by_key(SPREADSHEET_ID).worksheet("mileage_log")
data = current_data_log_ws.get_all_records()
current_data_log = pd.DataFrame(data)

# Create a 2-column layout
col1, col2 = st.columns(2)

# Initialize session state if it doesn't exist
if 'entries_mileage_dict' not in st.session_state:
    st.session_state.entries_mileage_dict = []

# --- Mileage Dictionary in Column 1 ---
with col1:
    st.write("### Current Mileage Dictionary")
    st.dataframe(current_data_dict, hide_index=True)

    st.subheader("Add New Location to Mileage Dictionary")

    # Google Address Search (Outside the Form)
    location_address_search = st.text_input("Enter Address to Search", key="location_address_search")

    google_location_address = None
    search_button = st.button("Search Google Address")

    # Trigger Google Address Search when button is clicked
    if search_button:
        if location_address_search:
            google_location_address = get_google_address(location_address_search)
            if google_location_address:
                # Save the address to session state when found
                st.session_state.google_location_address = google_location_address
                st.success(f"Found Google Address: {google_location_address}")
            else:
                st.error("No matching address found.")
        else:
            st.error("Please enter an address to search.")

    # --- Mileage Dictionary Form ---
    with st.form(key='mileage_dictionary_form'):
        # Get user input for location name
        location_name = st.text_input("Enter Location Name", key="location_name")

        # Auto-populate location address field if Google address is found in session state
        location_address_result = st.text_input(
            "Location Address", 
            value=st.session_state.get("google_location_address", ""), 
            disabled=True, 
            key="location_address_result"
        )

        # Button to add the location to Mileage Dictionary (submit form)
        add_location_button = st.form_submit_button(label="Add Location")

        # Handle form submission only when "Add Location" button is clicked
        if add_location_button:
            if location_name and st.session_state.get("google_location_address"):
                # Check if the location_name already exists in the session state entries (pending locations)
                location_names_in_entries = [entry[0] for entry in st.session_state.entries_mileage_dict]
                
                # Check if the location_name already exists in the current dictionary (Google Sheets data)
                location_names_in_existing_dict = current_data_dict["location_name"].tolist()
                
                if location_name in location_names_in_entries or location_name in location_names_in_existing_dict:
                    st.error(f"Location '{location_name}' already exists in the Mileage Dictionary.")
                else:
                    # Add the new location to session state (or database)
                    st.session_state.entries_mileage_dict.append([location_name, st.session_state["google_location_address"]])
                    st.success(f"Location added: {location_name} - {st.session_state['google_location_address']}")
            else:
                st.error("Please enter both location name and address!")

    # Display new locations added (but not yet submitted to Google Sheets)
    if st.session_state.entries_mileage_dict:
        st.write("### Locations to Submit to Mileage Dictionary")
        entries_dict_df = pd.DataFrame(st.session_state.entries_mileage_dict, columns=["Location Name", "Location Address"])
        st.dataframe(entries_dict_df, hide_index=True)
    
    # --- Submit Changes to Google Sheets ---
    if st.button("Submit Changes to Mileage Dictionary"):
        if st.session_state.entries_mileage_dict:
            new_data_dict = pd.DataFrame(st.session_state.entries_mileage_dict)
            append_to_gsheet(new_data_dict, "Mileage_Dictionary")
            # Clear session state values (delete keys to reset form fields)
            del st.session_state["google_location_address"]

            st.session_state.entries_mileage_dict = []  # Clear dictionary entries
            st.rerun()  # Rerun the script to refresh the form fields

# Initialize session state if it doesn't exist
if 'entries_mileage_log' not in st.session_state:
    st.session_state.entries_mileage_log = []

# --- Mileage Log in Column 2 ---
with col2:
    st.write("### Current Mileage Log")
    st.dataframe(current_data_log, hide_index=True)

    st.subheader("Add New Trip to Mileage Log")
    if not current_data_dict.empty:
        # Start of form to add a new trip
        with st.form(key='mileage_log_form'):
            # Select locations from Mileage_Dictionary for start_location_name and end_location_name with placeholders
            locations = current_data_dict['location_name'].tolist()
            start_location_name = st.selectbox("Select Start Location", ["Select a location"] + locations)  # Adding placeholder
            end_location_name = st.selectbox("Select End Location", ["Select a location"] + locations)  # Adding placeholder

            # Input for trip_date with no default value
            trip_date = st.date_input("Enter Trip Date", max_value=datetime.today())

            # Submit button inside the form
            submit_button = st.form_submit_button(label="Add Trip")

            # Add trip to entries list when form is submitted
            if submit_button:
                if start_location_name != "Select a location" and end_location_name != "Select a location":
                    # Get the address for start and end location names
                    start_location_address = current_data_dict[current_data_dict['location_name'] == start_location_name]['location_address'].values[0]
                    end_location_address = current_data_dict[current_data_dict['location_name'] == end_location_name]['location_address'].values[0]
                    
                    # Calculate mileage between start_location_name and end_location_name
                    total_mileage = get_mileage(start_location_address, end_location_address, start_location_name, end_location_name)

                    if trip_date and total_mileage > 0:
                        # Convert trip_date to string
                        trip_date = trip_date.strftime("%Y-%m-%d")

                        # Add the new trip to the session state entries list
                        st.session_state.entries_mileage_log.append([trip_date, start_location_name, start_location_address, end_location_name, end_location_address, total_mileage])
                        st.success(f"Trip added: {trip_date} - {start_location_name} to {end_location_name} - {total_mileage} miles")
                    else:
                        st.error("Please enter a valid trip date with non-zero mileage!")
                else:
                    st.error("Please select both start and end locations!")

        # Display the current list of entries to be submitted (Mileage Log)
        if st.session_state.entries_mileage_log:
            st.write("### Trip Entries to Submit to Mileage Log")

            # Add the new trip to the session state entries dataframe
            entries_log_df = pd.DataFrame(st.session_state.entries_mileage_log, columns=["trip_date", "start_location_name", "start_location_address", "end_location_name","end_location_address", "total_mileage"])
            st.dataframe(entries_log_df, hide_index=True)

        # --- Submit Changes to Google Sheets ---
        if st.button("Submit Changes to Mileage Log"):
            if st.session_state.entries_mileage_log:
                new_data_log = pd.DataFrame(st.session_state.entries_mileage_log, columns=["trip_date", "start_location_name", "start_location_address", "end_location_name","end_location_address", "total_mileage"])
                append_to_gsheet(new_data_log, "mileage_log")
                st.session_state.entries_mileage_log = []  # Clear the session state entries after submission
                st.rerun()  # Rerun the script to refresh the form fields
    else:
        st.warning("Please add locations to the Mileage Dictionary first!")
