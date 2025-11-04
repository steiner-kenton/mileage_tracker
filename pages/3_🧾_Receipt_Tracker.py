"""
Receipt Tracker Page - Upload and manage receipts
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.utils.supabase_utils import get_sheet_data
from src.utils.auth import init_connection, check_session
from src.components.ui_components import render_receipt_section

# Configure page
st.set_page_config(page_title="Receipt Tracker", page_icon="🧾", layout="wide")

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
st.title("🧾 Receipt Tracker")
st.markdown("Upload and manage your business expense receipts with automatic OCR extraction.")

# Load receipts data
current_receipts_df = get_sheet_data("Receipts", create_if_missing=True, 
                                   headers=["date", "store_name", "total", "upload_timestamp"])

# Receipt upload section
st.header("📤 Upload New Receipt")
render_receipt_section(current_receipts_df)

st.divider()

# Receipt history
st.header("📋 Receipt History")

# Add filters
col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    # Date range filter
    date_filter = st.selectbox(
        "Filter by date",
        ["All Time", "Last 7 Days", "Last 30 Days", "This Month", "Custom Range"]
    )

with col_filter2:
    # Search filter
    search = st.text_input("🔍 Search receipts", placeholder="Search by store name...")

with col_filter3:
    # Sort option
    sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Total (High-Low)", "Total (Low-High)"])

# Apply filters
filtered_receipts = current_receipts_df.copy()

if len(filtered_receipts) > 0:
    # Apply date filter if date column exists
    if 'date' in filtered_receipts.columns:
        # Ensure date column is datetime
        filtered_receipts['date'] = pd.to_datetime(filtered_receipts['date'])
        
        if date_filter == "Last 7 Days":
            cutoff_date = datetime.now() - timedelta(days=7)
            filtered_receipts = filtered_receipts[filtered_receipts['date'] >= cutoff_date]
        elif date_filter == "Last 30 Days":
            cutoff_date = datetime.now() - timedelta(days=30)
            filtered_receipts = filtered_receipts[filtered_receipts['date'] >= cutoff_date]
        elif date_filter == "This Month":
            current_month = datetime.now().month
            current_year = datetime.now().year
            filtered_receipts = filtered_receipts[
                (filtered_receipts['date'].dt.month == current_month) & 
                (filtered_receipts['date'].dt.year == current_year)
            ]
        elif date_filter == "Custom Range":
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
            with col_date2:
                end_date = st.date_input("End Date", value=datetime.now())
            
            filtered_receipts = filtered_receipts[
                (filtered_receipts['date'] >= pd.Timestamp(start_date)) & 
                (filtered_receipts['date'] <= pd.Timestamp(end_date))
            ]
    
    # Apply search filter
    if search:
        filtered_receipts = filtered_receipts[
            filtered_receipts.apply(lambda row: search.lower() in str(row).lower(), axis=1)
        ]
    
    # Apply sorting
    if 'date' in filtered_receipts.columns:
        if sort_by == "Date (Newest)":
            filtered_receipts = filtered_receipts.sort_values('date', ascending=False)
        elif sort_by == "Date (Oldest)":
            filtered_receipts = filtered_receipts.sort_values('date', ascending=True)
    
    if 'total' in filtered_receipts.columns:
        # Convert total to numeric for sorting
        filtered_receipts['total_numeric'] = pd.to_numeric(filtered_receipts['total'], errors='coerce')
        
        if sort_by == "Total (High-Low)":
            filtered_receipts = filtered_receipts.sort_values('total_numeric', ascending=False)
        elif sort_by == "Total (Low-High)":
            filtered_receipts = filtered_receipts.sort_values('total_numeric', ascending=True)
        
        # Drop the temporary column
        filtered_receipts = filtered_receipts.drop(columns=['total_numeric'])
    
    # Display summary stats
    if len(filtered_receipts) > 0:
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Total Receipts", len(filtered_receipts))
        
        with col_stat2:
            if 'total' in filtered_receipts.columns:
                total_amount = pd.to_numeric(filtered_receipts['total'], errors='coerce').sum()
                st.metric("Total Amount", f"${total_amount:.2f}")
            else:
                st.metric("Total Amount", "N/A")
        
        with col_stat3:
            if 'date' in filtered_receipts.columns:
                avg_per_receipt = pd.to_numeric(filtered_receipts['total'], errors='coerce').mean()
                st.metric("Avg per Receipt", f"${avg_per_receipt:.2f}")
            else:
                st.metric("Avg per Receipt", "N/A")
        
        st.divider()
        
        # Display the dataframe
        st.dataframe(
            filtered_receipts,
            hide_index=True,
            use_container_width=True,
            height=400
        )
        
        st.caption(f"Showing {len(filtered_receipts)} of {len(current_receipts_df)} receipts")
        
        # Download button
        csv = filtered_receipts.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"receipts_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        if search or date_filter != "All Time":
            st.info("No receipts match your filters. Try adjusting the filters above.")
        else:
            st.info("No receipts uploaded yet. Upload your first receipt using the form above!")
else:
    st.info("No receipts uploaded yet. Upload your first receipt using the form above!")

# Add helpful tips
with st.expander("💡 Tips for Managing Receipts"):
    st.markdown("""
    - **Upload receipts promptly** after making purchases
    - **Take clear photos** for best OCR results
    - **Verify OCR data** before saving to ensure accuracy
    - **Rotate images** if needed - the system will auto-correct orientation
    - **Keep originals** for at least 3 years for tax purposes
    - Download your receipt log regularly as a backup
    """)

# Add OCR tips
with st.expander("📸 Tips for Better OCR Results"):
    st.markdown("""
    - **Good lighting** - Avoid shadows and glare
    - **Flat surface** - Lay receipt flat, don't fold
    - **High resolution** - Use your phone's camera, not screenshots
    - **Clear focus** - Make sure text is sharp and readable
    - **Full receipt** - Capture the entire receipt including top and bottom
    """)
