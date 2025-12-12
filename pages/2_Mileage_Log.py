"""
Mileage Log Page - Track and log trips
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.utils.supabase_utils import get_sheet_data, get_mileage_log, get_user_id
from src.utils.auth import init_connection, check_session
from src.components.ui_components import render_trip_form

# Configure page
st.set_page_config(page_title="Mileage Log", layout="wide")

# Check authentication
supabase = init_connection()

if check_session():
    st.sidebar.success(f"Logged in as {st.session_state['user'].email}")
    
    if st.sidebar.button("Logout"):
        st.session_state.pop("user", None)
        st.session_state.pop("auth_session", None)
        st.rerun()
else:
    st.warning("Please log in from the home page")
    st.stop()

# Page content
st.title("Mileage Log")
st.markdown("Track your business trips and mileage for tax deductions.")

# Initialize session state for editing
if 'editing_trip' not in st.session_state:
    st.session_state.editing_trip = False
if 'trip_to_edit' not in st.session_state:
    st.session_state.trip_to_edit = None
if 'deleting_trip' not in st.session_state:
    st.session_state.deleting_trip = False
if 'trip_to_delete' not in st.session_state:
    st.session_state.trip_to_delete = None

# Load data
current_data_dict = get_sheet_data("Mileage_Dictionary")
current_data_log = get_mileage_log()

# Two column layout
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.header("Log New Trip")
    render_trip_form(current_data_dict, current_data_log)

with col2:
    st.header("Trip History")
    
    # Add filters
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        # Date range filter
        date_filter = st.selectbox(
            "Filter by date",
            ["All Time", "Last 7 Days", "Last 30 Days", "This Month", "Custom Range"]
        )
    
    with col_filter2:
        # Search filter
        search = st.text_input("Search trips", placeholder="Type to filter...")
    
    # Apply date filter
    filtered_log = current_data_log.copy()
    
    if len(filtered_log) > 0 and 'date' in filtered_log.columns:
        # Ensure date column is datetime
        filtered_log['date'] = pd.to_datetime(filtered_log['date'])
        
        if date_filter == "Last 7 Days":
            cutoff_date = datetime.now() - timedelta(days=7)
            filtered_log = filtered_log[filtered_log['date'] >= cutoff_date]
        elif date_filter == "Last 30 Days":
            cutoff_date = datetime.now() - timedelta(days=30)
            filtered_log = filtered_log[filtered_log['date'] >= cutoff_date]
        elif date_filter == "This Month":
            current_month = datetime.now().month
            current_year = datetime.now().year
            filtered_log = filtered_log[
                (filtered_log['date'].dt.month == current_month) & 
                (filtered_log['date'].dt.year == current_year)
            ]
        elif date_filter == "Custom Range":
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
            with col_date2:
                end_date = st.date_input("End Date", value=datetime.now())
            
            filtered_log = filtered_log[
                (filtered_log['date'] >= pd.Timestamp(start_date)) & 
                (filtered_log['date'] <= pd.Timestamp(end_date))
            ]
    
    # Apply search filter
    if search and len(filtered_log) > 0:
        filtered_log = filtered_log[
            filtered_log.apply(lambda row: search.lower() in str(row).lower(), axis=1)
        ]
    
    # Display summary stats
    if len(filtered_log) > 0:
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Total Trips", len(filtered_log))
        
        with col_stat2:
            if 'distance' in filtered_log.columns:
                total_miles = filtered_log['distance'].sum()
                st.metric("Total Miles", f"{total_miles:.2f}")
            else:
                st.metric("Total Miles", "N/A")
        
        with col_stat3:
            if 'distance' in filtered_log.columns:
                # IRS mileage rate for 2025 (example - update as needed)
                mileage_rate = 0.67  # $0.67 per mile
                estimated_deduction = total_miles * mileage_rate
                st.metric("Est. Deduction", f"${estimated_deduction:.2f}")
            else:
                st.metric("Est. Deduction", "N/A")
        
        st.divider()
        
        # Format date column to show only dates (not timestamps)
        display_log = filtered_log.copy()
        if 'date' in display_log.columns:
            display_log['date'] = pd.to_datetime(display_log['date']).dt.strftime('%Y-%m-%d')
        
        # Display the dataframe
        st.dataframe(
            display_log.sort_values('date', ascending=False) if 'date' in display_log.columns else display_log,
            hide_index=True,
            use_container_width=True,
            height=400
        )
        
        st.caption(f"Showing {len(filtered_log)} of {len(current_data_log)} trips")
        
        # Download button
        csv = filtered_log.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"mileage_log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Edit/Delete section
        st.divider()
        st.subheader("Manage Trips")
        
        # Get full trip data with IDs from database
        supabase = init_connection()
        user_id = get_user_id()
        response = supabase.table('mileage_log').select('*').eq('user_id', user_id).order('date', desc=True).execute()
        
        if response.data:
            trips_with_ids = pd.DataFrame(response.data)
            
            # Create dropdown options with readable format
            trip_options = []
            for _, trip in trips_with_ids.iterrows():
                trip_date = pd.to_datetime(trip['date']).strftime('%Y-%m-%d')
                option_label = f"{trip_date}: {trip['start_location']} → {trip['end_location']} ({trip['distance']} mi)"
                trip_options.append(option_label)
            
            selected_trip_label = st.selectbox(
                "Select trip to edit or delete:",
                ["Select a trip..."] + trip_options,
                key="trip_selector"
            )
            
            # Action buttons
            action_col1, action_col2 = st.columns(2)
            
            with action_col1:
                if st.button("Edit Trip", disabled=(selected_trip_label == "Select a trip...")):
                    selected_idx = trip_options.index(selected_trip_label)
                    st.session_state.trip_to_edit = trips_with_ids.iloc[selected_idx].to_dict()
                    st.session_state.editing_trip = True
                    st.session_state.deleting_trip = False
                    st.rerun()
            
            with action_col2:
                if st.button("Delete Trip", disabled=(selected_trip_label == "Select a trip...")):
                    selected_idx = trip_options.index(selected_trip_label)
                    st.session_state.trip_to_delete = trips_with_ids.iloc[selected_idx].to_dict()
                    st.session_state.deleting_trip = True
                    st.session_state.editing_trip = False
                    st.rerun()
            
            # Edit form
            if st.session_state.editing_trip and st.session_state.trip_to_edit:
                st.divider()
                st.subheader("Edit Trip")
                trip = st.session_state.trip_to_edit
                
                with st.form("edit_trip_form"):
                    edit_date = st.date_input(
                        "Trip Date",
                        value=pd.to_datetime(trip['date']).date()
                    )
                    
                    locations = current_data_dict['location_name'].tolist() if not current_data_dict.empty else []
                    
                    edit_start = st.selectbox(
                        "Start Location",
                        locations,
                        index=locations.index(trip['start_location']) if trip['start_location'] in locations else 0
                    )
                    
                    edit_end = st.selectbox(
                        "End Location",
                        locations,
                        index=locations.index(trip['end_location']) if trip['end_location'] in locations else 0
                    )
                    
                    edit_distance = st.number_input(
                        "Distance (miles)",
                        value=float(trip['distance']),
                        min_value=0.0,
                        step=0.1
                    )
                    
                    submit_col1, submit_col2 = st.columns(2)
                    
                    with submit_col1:
                        save_button = st.form_submit_button("Save Changes", use_container_width=True)
                    
                    with submit_col2:
                        cancel_button = st.form_submit_button("Cancel", use_container_width=True)
                    
                    if save_button:
                        try:
                            # Get addresses from dictionary
                            start_address = current_data_dict[current_data_dict['location_name'] == edit_start]['location_address'].values[0] if not current_data_dict.empty else ""
                            end_address = current_data_dict[current_data_dict['location_name'] == edit_end]['location_address'].values[0] if not current_data_dict.empty else ""
                            
                            update_data = {
                                'date': str(edit_date),
                                'start_location': edit_start,
                                'start_address': start_address,
                                'end_location': edit_end,
                                'end_address': end_address,
                                'distance': float(edit_distance)
                            }
                            
                            supabase.table('mileage_log').update(update_data).eq(
                                'id', trip['id']
                            ).eq(
                                'user_id', user_id
                            ).execute()
                            
                            st.success("Trip updated successfully!")
                            st.session_state.editing_trip = False
                            st.session_state.trip_to_edit = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating trip: {str(e)}")
                    
                    if cancel_button:
                        st.session_state.editing_trip = False
                        st.session_state.trip_to_edit = None
                        st.rerun()
            
            # Delete confirmation
            if st.session_state.deleting_trip and st.session_state.trip_to_delete:
                st.divider()
                st.subheader("Confirm Deletion")
                trip = st.session_state.trip_to_delete
                trip_date = pd.to_datetime(trip['date']).strftime('%Y-%m-%d')
                st.warning(f"Are you sure you want to delete this trip?\n\n**{trip_date}: {trip['start_location']} → {trip['end_location']} ({trip['distance']} mi)**")
                
                conf_col1, conf_col2 = st.columns(2)
                
                with conf_col1:
                    if st.button("Yes, Delete", use_container_width=True):
                        try:
                            supabase.table('mileage_log').delete().eq(
                                'id', trip['id']
                            ).eq(
                                'user_id', user_id
                            ).execute()
                            
                            st.success("Trip deleted successfully!")
                            st.session_state.deleting_trip = False
                            st.session_state.trip_to_delete = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting trip: {str(e)}")
                
                with conf_col2:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.deleting_trip = False
                        st.session_state.trip_to_delete = None
                        st.rerun()
    else:
        st.info("No trips logged yet. Add your first trip using the form on the left!")

# Add helpful tips
with st.expander("Tips for Logging Trips"):
    st.markdown("""
    - **Log trips promptly** to ensure accuracy
    - **Use saved locations** from the Mileage Dictionary for consistency
    - **Keep records** for at least 3 years for tax purposes
    - **Note the purpose** of each trip for tax documentation
    - Download your log regularly as a backup
    """)
