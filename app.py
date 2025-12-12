import pandas as pd
import streamlit as st
from src.utils.supabase_utils import get_sheet_data
from src.utils.auth import init_connection, login_or_signup, check_session

# Configure Streamlit page (must be first Streamlit command)
st.set_page_config(
    page_title="Tax Expense Tracker",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Auth Connection to Supabase
supabase = init_connection()

# Check authentication
if check_session():
    st.sidebar.success(f"{st.session_state['user'].email}")
    
    # Add logout button to sidebar
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.pop("user", None)
        st.session_state.pop("auth_session", None)
        st.rerun()
else:
    login_or_signup()
    st.stop()  # Stop app until login

def initialize_session_state():
    """Initialize session state variables"""
    if 'entries_mileage_log' not in st.session_state:
        st.session_state.entries_mileage_log = []
    if 'entries_mileage_dict' not in st.session_state:
        st.session_state.entries_mileage_dict = []
    if 'entries_receipts' not in st.session_state:
        st.session_state.entries_receipts = []

def main():
    """Main application function - Dashboard/Home page"""
    # Initialize session state
    initialize_session_state()
    
    # App title with icon
    st.title("Tax Expense Tracker")
    st.markdown("### Welcome to your Mileage Manager Dashboard")
    
    st.markdown("""
    Track your business expenses, mileage, and receipts all in one place. Use the navigation above to get started!
    """)
    
    # Show quick stats
    st.header("Quick Overview")
    
    try:
        # Load data from Supabase
        current_data_dict = get_sheet_data("Mileage_Dictionary")
        current_data_log = get_sheet_data("mileage_log")
        current_receipts_df = get_sheet_data("Receipts", create_if_missing=True, 
                                           headers=["date", "store_name", "total", "upload_timestamp"])
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Saved Locations", len(current_data_dict))
        
        with col2:
            st.metric("Total Trips", len(current_data_log))
        
        with col3:
            st.metric("Receipts Stored", len(current_receipts_df))
        
        # Recent activity
        st.header("Recent Activity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent Trips")
            if len(current_data_log) > 0:
                st.dataframe(current_data_log.head(5), hide_index=True)
            else:
                st.info("No trips logged yet. Visit the Mileage Log page to add your first trip!")
        
        with col2:
            st.subheader("Recent Receipts")
            if len(current_receipts_df) > 0:
                st.dataframe(current_receipts_df.head(5), hide_index=True)
            else:
                st.info("No receipts uploaded yet. Visit the Receipt Tracker page to add your first receipt!")
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    main()
