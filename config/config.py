"""
Configuration and constants for the Mileage Manager application
"""
import streamlit as st
import gspread
from google.oauth2 import service_account

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
