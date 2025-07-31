"""
Mileage Manager - Main Application
A Streamlit application for tracking mileage and processing receipts
"""
import pandas as pd
import streamlit as st
from src.utils.sheets_utils import get_sheet_data
from src.components.ui_components import render_trip_form, render_location_form, render_receipt_section

# Configure Streamlit page
st.set_page_config(page_title="Mileage Manager", layout="wide")

def initialize_session_state():
    """Initialize session state variables"""
    if 'entries_mileage_log' not in st.session_state:
        st.session_state.entries_mileage_log = []
    if 'entries_mileage_dict' not in st.session_state:
        st.session_state.entries_mileage_dict = []
    if 'entries_receipts' not in st.session_state:
        st.session_state.entries_receipts = []

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # App title
    st.title("Mileage Manager")

    # Load data from Google Sheets
    current_data_dict = get_sheet_data("Mileage_Dictionary")
    current_data_log = get_sheet_data("mileage_log")
    current_receipts_df = get_sheet_data("Receipts", create_if_missing=True, 
                                       headers=["date", "store_name", "total", "upload_timestamp"])

    # Create a 2-column layout with fixed sizing
    col1, col2 = st.columns([1, 1], gap="medium")

    # Column 1: Add New Trip (first), Add New Location (second)
    with col1:
        render_trip_form(current_data_dict, current_data_log)
        st.divider()  # Add visual separator
        render_location_form(current_data_dict)

    # Column 2: Current Location Dictionary (first), Current Mileage Log (second)
    with col2:
        # Current Mileage Dictionary
        st.write("### Current Mileage Dictionary")
        st.dataframe(current_data_dict, hide_index=True, height=300)

        st.divider()  # Add visual separator

        # Current Mileage Log
        st.write("### Current Mileage Log")
        st.dataframe(current_data_log, hide_index=True, height=300)

    # Receipt Upload Section (Full Width at Bottom)
    st.divider()
    render_receipt_section(current_receipts_df)

if __name__ == "__main__":
    main()
