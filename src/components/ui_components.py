"""
UI components for the Mileage Manager application
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from src.utils.google_api import get_google_address, get_mileage
from src.utils.ocr_utils import process_receipt_ocr
from src.utils.supabase_utils import add_data

def parse_ocr_date(date_string):
    """
    Parse various date formats that OCR might extract
    """
    if not date_string:
        return datetime.today().date()
    
    # Common date formats from OCR
    date_formats = [
        "%m/%d/%y",      # 7/22/25
        "%m/%d/%Y",      # 7/22/2025
        "%m-%d-%y",      # 7-22-25
        "%m-%d-%Y",      # 7-22-2025
        "%Y-%m-%d",      # 2025-07-22
        "%d/%m/%y",      # 22/7/25
        "%d/%m/%Y",      # 22/7/2025
        "%B %d, %Y",     # July 22, 2025
        "%b %d, %Y",     # Jul 22, 2025
        "%B %d %Y",      # July 22 2025
        "%b %d %Y",      # Jul 22 2025
    ]
    
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date_string.strip(), date_format)
            
            # If year is 2-digit and less than 50, assume 20xx, otherwise 19xx
            if parsed_date.year < 50:
                parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
            elif parsed_date.year < 100:
                parsed_date = parsed_date.replace(year=parsed_date.year + 1900)
                
            return parsed_date.date()
        except ValueError:
            continue
    
    # If no format matches, return today's date
    return datetime.today().date()

def render_trip_form(current_data_dict, current_data_log):
    """Render the form for adding new trips"""
    st.subheader("Add New Trip to Mileage Log")
    
    if not current_data_dict.empty:
        # Initialize session state for location swap
        if 'swap_locations' not in st.session_state:
            st.session_state.swap_locations = False
        if 'start_location_index' not in st.session_state:
            st.session_state.start_location_index = 0
        if 'end_location_index' not in st.session_state:
            st.session_state.end_location_index = 0
            
        # Get locations list
        locations = current_data_dict['location_name'].tolist()
        
        # Start of form to add a new trip
        with st.form(key='mileage_log_form'):
            # Location selection with swap button
            loc_col1, swap_col, loc_col2 = st.columns([5, 1, 5])
            
            with loc_col1:
                start_location_name = st.selectbox(
                    "Select Start Location", 
                    ["Select a location"] + locations,
                    index=st.session_state.start_location_index,
                    key="start_loc_select"
                )
            
            with swap_col:
                # Add some vertical spacing to align with selectbox
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("↔", help="Swap start and end locations", use_container_width=True):
                    # Swap the indices
                    st.session_state.start_location_index, st.session_state.end_location_index = \
                        st.session_state.end_location_index, st.session_state.start_location_index
                    st.rerun()
            
            with loc_col2:
                end_location_name = st.selectbox(
                    "Select End Location", 
                    ["Select a location"] + locations,
                    index=st.session_state.end_location_index,
                    key="end_loc_select"
                )

            # Input for trip_date with no default value
            trip_date = st.date_input("Enter Trip Date", max_value=datetime.today())

            # Submit button inside the form
            submit_button = st.form_submit_button(label="Add Trip")

            # Add trip to entries list when form is submitted
            if submit_button:
                if start_location_name != "Select a location" and end_location_name != "Select a location":
                    # Update session state indices for next time
                    st.session_state.start_location_index = (["Select a location"] + locations).index(start_location_name)
                    st.session_state.end_location_index = (["Select a location"] + locations).index(end_location_name)
                    
                    # Get the address for start and end location names
                    start_location_address = current_data_dict[current_data_dict['location_name'] == start_location_name]['location_address'].values[0]
                    end_location_address = current_data_dict[current_data_dict['location_name'] == end_location_name]['location_address'].values[0]
                    
                    # Calculate mileage between start_location_name and end_location_name
                    total_mileage = get_mileage(start_location_address, end_location_address, start_location_name, end_location_name, current_data_log)

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
            entries_log_df = pd.DataFrame(st.session_state.entries_mileage_log, columns=["trip_date", "start_location_name", "start_location_address", "end_location_name","end_location_address", "total_mileage"])
            st.dataframe(entries_log_df, hide_index=True, height=200)

        # Submit Changes to Database
        if st.button("Submit Changes to Mileage Log"):
            if st.session_state.entries_mileage_log:
                new_data_log = pd.DataFrame(st.session_state.entries_mileage_log, columns=["trip_date", "start_location_name", "start_location_address", "end_location_name","end_location_address", "total_mileage"])
                add_data(new_data_log, "mileage_log")
                st.session_state.entries_mileage_log = []
                st.rerun()
    else:
        st.warning("Please add locations to the Mileage Dictionary first!")

def render_location_form(current_data_dict):
    """Render the form for adding new locations"""
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

    # Mileage Dictionary Form
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
                
                # Check if the location_name already exists in the current dictionary
                location_names_in_existing_dict = current_data_dict["location_name"].tolist()
                
                if location_name in location_names_in_entries or location_name in location_names_in_existing_dict:
                    st.error(f"Location '{location_name}' already exists in the Mileage Dictionary.")
                else:
                    # Add the new location to session state (or database)
                    st.session_state.entries_mileage_dict.append([location_name, st.session_state["google_location_address"]])
                    st.success(f"Location added: {location_name} - {st.session_state['google_location_address']}")
            else:
                st.error("Please enter both location name and address!")

    # Display new locations added (but not yet submitted to database)
    if st.session_state.entries_mileage_dict:
        st.write("### Locations to Submit to Mileage Dictionary")
        entries_dict_df = pd.DataFrame(st.session_state.entries_mileage_dict, columns=["Location Name", "Location Address"])
        st.dataframe(entries_dict_df, hide_index=True, height=200)
    
    # Submit Changes to Database
    if st.button("Submit Changes to Mileage Dictionary"):
        if st.session_state.entries_mileage_dict:
            new_data_dict = pd.DataFrame(st.session_state.entries_mileage_dict)
            add_data(new_data_dict, "Mileage_Dictionary")
            # Clear session state values (delete keys to reset form fields)
            if "google_location_address" in st.session_state:
                del st.session_state["google_location_address"]
            st.session_state.entries_mileage_dict = []
            st.rerun()

def render_receipt_section(current_receipts_df):
    """Render the receipt processing section"""
    st.header("Receipt Processing")

    # Create columns for receipt section
    receipt_col1, receipt_col2 = st.columns([1, 1], gap="medium")

    with receipt_col1:
        st.subheader("Upload Receipt for OCR Processing")
        
        # File uploader for receipt
        uploaded_file = st.file_uploader(
            "Choose a receipt image file", 
            type=['png', 'jpg', 'jpeg', 'pdf'],
            key="receipt_uploader"
        )
        
        if uploaded_file is not None:
            # Display the uploaded image
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="Uploaded Receipt", use_container_width=True)
            
            # Process OCR button
            if st.button("Process Receipt with OCR", key="process_ocr"):
                with st.spinner("Processing receipt with Tesseract OCR..."):
                    ocr_result = process_receipt_ocr(uploaded_file)
                    
                    if ocr_result["success"]:
                        st.success("Receipt processed successfully!")
                        
                        # Store OCR results in session state
                        st.session_state.ocr_result = {
                            "store_name": ocr_result["store_name"],
                            "date": ocr_result["date"],
                            "total": ocr_result["total"]
                        }
                        
                        # Show extracted text for debugging
                        with st.expander("View OCR Text (for debugging)"):
                            st.text(ocr_result["raw_text"])
                        
                        st.rerun()
                    else:
                        st.error(f"OCR processing failed: {ocr_result['error']}")

        # Manual entry form (in case OCR fails or for editing)
        st.subheader("Receipt Details")
        with st.form(key='receipt_form'):
            # Pre-populate with OCR results if available
            ocr_data = st.session_state.get("ocr_result", {})
            
            receipt_date = st.date_input(
                "Receipt Date", 
                value=parse_ocr_date(ocr_data.get("date", "")),
                max_value=datetime.today()
            )
            
            store_name = st.text_input(
                "Store Name", 
                value=ocr_data.get("store_name", ""),
                key="store_name_input"
            )
            
            total_amount = st.text_input(
                "Total Amount", 
                value=ocr_data.get("total", ""),
                key="total_amount_input",
                help="Enter amount like 25.99 (without $ sign)"
            )
            
            # Submit button
            add_receipt_button = st.form_submit_button(label="Add Receipt Entry")
            
            if add_receipt_button:
                if store_name and total_amount and receipt_date:
                    try:
                        # Validate total amount
                        float(total_amount.replace('$', '').replace(',', ''))
                        
                        # Add timestamp
                        upload_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Add to session state
                        st.session_state.entries_receipts.append([
                            receipt_date.strftime("%Y-%m-%d"),
                            store_name,
                            total_amount,
                            upload_timestamp
                        ])
                        
                        st.success(f"Receipt added: {store_name} - ${total_amount} on {receipt_date}")
                        
                        # Clear OCR result from session state
                        if "ocr_result" in st.session_state:
                            del st.session_state["ocr_result"]
                        
                    except ValueError:
                        st.error("Please enter a valid total amount (numbers only)")
                else:
                    st.error("Please fill in all fields!")

    with receipt_col2:
        st.subheader("Current Receipts")
        if not current_receipts_df.empty:
            st.dataframe(current_receipts_df, hide_index=True, height=300)
        else:
            st.info("No receipts found. Upload your first receipt!")
        
        # Display pending receipt entries
        if st.session_state.entries_receipts:
            st.write("### Receipt Entries to Submit")
            entries_receipts_df = pd.DataFrame(
                st.session_state.entries_receipts, 
                columns=["Date", "Store Name", "Total", "Upload Timestamp"]
            )
            st.dataframe(entries_receipts_df, hide_index=True, height=200)
            
            # Submit receipts to Database
            if st.button("Submit Receipts to Database", key="submit_receipts"):
                if st.session_state.entries_receipts:
                    new_receipts_data = pd.DataFrame(
                        st.session_state.entries_receipts,
                        columns=["date", "store_name", "total", "upload_timestamp"]
                    )
                    add_data(new_receipts_data, "Receipts")
                    st.session_state.entries_receipts = []
                    st.rerun()
