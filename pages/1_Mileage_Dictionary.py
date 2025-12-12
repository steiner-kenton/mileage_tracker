"""
Mileage Dictionary Page - Manage saved locations
"""
import streamlit as st
import pandas as pd
from src.utils.supabase_utils import get_sheet_data
from src.utils.auth import init_connection, check_session
from src.components.ui_components import render_location_form

# Configure page
st.set_page_config(page_title="Mileage Dictionary", layout="wide")

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
st.title("Mileage Dictionary")
st.markdown("Manage your saved locations for quick access when logging trips.")

# Load current dictionary data
current_data_dict = get_sheet_data("Mileage_Dictionary")

# Two column layout
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.header("Add New Location")
    render_location_form(current_data_dict)

with col2:
    st.header("Saved Locations")
    
    # Add search/filter
    search = st.text_input("Search locations", placeholder="Type to filter...")
    
    # Get all locations with IDs from Supabase
    from src.utils.auth import init_connection
    supabase = init_connection()
    user_id = st.session_state.get("user").id if "user" in st.session_state else None
    
    if user_id:
        response = supabase.table('mileage_dictionary').select('*').eq('user_id', user_id).execute()
        all_locations = response.data if response.data else []
    else:
        all_locations = []
    
    # Filter locations if search is provided
    if search:
        filtered_locations = [
            loc for loc in all_locations 
            if search.lower() in loc['location_name'].lower() or 
               search.lower() in loc['location_address'].lower()
        ]
    else:
        filtered_locations = all_locations
    
    # Display locations with edit/delete buttons
    if len(filtered_locations) > 0:
        # Check if any location is being edited or deleted
        editing_any = any(st.session_state.get(f"editing_{loc['id']}", False) for loc in filtered_locations)
        deleting_any = any(st.session_state.get(f"confirm_delete_{loc['id']}", False) for loc in filtered_locations)
        
        if not editing_any and not deleting_any:
            # Show compact table view
            import pandas as pd
            
            # Create display dataframe with action buttons
            display_data = []
            for loc in filtered_locations:
                display_data.append({
                    'Location Name': loc['location_name'],
                    'Address': loc['location_address'],
                    'id': loc['id']
                })
            
            df_display = pd.DataFrame(display_data)
            
            # Show the dataframe without the id column
            st.dataframe(
                df_display[['Location Name', 'Address']], 
                hide_index=True, 
                use_container_width=True,
                height=400
            )
            
            st.caption(f"Showing {len(filtered_locations)} of {len(all_locations)} locations")
            
            # Action buttons in a compact row
            st.write("**Actions:**")
            cols = st.columns([3, 1, 1])
            
            with cols[0]:
                selected_location = st.selectbox(
                    "Select location to edit/delete",
                    options=[loc['location_name'] for loc in filtered_locations],
                    key="location_selector"
                )
            
            with cols[1]:
                if st.button("Edit", use_container_width=True):
                    # Find the selected location
                    selected = next((loc for loc in filtered_locations if loc['location_name'] == selected_location), None)
                    if selected:
                        st.session_state[f"editing_{selected['id']}"] = True
                        st.rerun()
            
            with cols[2]:
                if st.button("Delete", use_container_width=True):
                    # Find the selected location
                    selected = next((loc for loc in filtered_locations if loc['location_name'] == selected_location), None)
                    if selected:
                        st.session_state[f"confirm_delete_{selected['id']}"] = True
                        st.rerun()
        else:
            # Show edit/delete forms
            for loc in filtered_locations:
                # Show edit form if editing
                if st.session_state.get(f"editing_{loc['id']}", False):
                    with st.form(key=f"edit_form_{loc['id']}"):
                        st.subheader(f"Edit: {loc['location_name']}")
                        new_name = st.text_input("Location Name", value=loc['location_name'])
                        new_address = st.text_input("Location Address", value=loc['location_address'])
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("Save Changes", use_container_width=True):
                                try:
                                    supabase.table('mileage_dictionary').update({
                                        'location_name': new_name,
                                        'location_address': new_address
                                    }).eq('id', loc['id']).execute()
                                    
                                    st.success(f"Updated '{new_name}'!")
                                    del st.session_state[f"editing_{loc['id']}"]
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating location: {str(e)}")
                        
                        with col_cancel:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                del st.session_state[f"editing_{loc['id']}"]
                                st.rerun()
                
                # Show delete confirmation
                if st.session_state.get(f"confirm_delete_{loc['id']}", False):
                    st.warning(f"Delete **{loc['location_name']}**?")
                    st.caption(loc['location_address'])
                    col_confirm, col_cancel = st.columns(2)
                    
                    with col_confirm:
                        if st.button("Yes, Delete", key=f"confirm_yes_{loc['id']}", use_container_width=True):
                            try:
                                supabase.table('mileage_dictionary').delete().eq('id', loc['id']).execute()
                                st.success(f"Deleted '{loc['location_name']}'")
                                del st.session_state[f"confirm_delete_{loc['id']}"]
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting location: {str(e)}")
                    
                    with col_cancel:
                        if st.button("Cancel", key=f"confirm_no_{loc['id']}", use_container_width=True):
                            del st.session_state[f"confirm_delete_{loc['id']}"]
                            st.rerun()
    else:
        st.info("No locations saved yet. Add your first location using the form on the left!")

# Add some helpful tips
with st.expander("Tips for Managing Locations"):
    st.markdown("""
    - **Save frequently visited places** to speed up trip logging
    - **Use descriptive names** like "Home", "Office", "Client Site A"
    - **Keep addresses accurate** for precise mileage calculations
    - Locations can be reused across multiple trips
    """)
