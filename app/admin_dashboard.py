"""
Admin Dashboard for viewing and managing bookings.
"""
import streamlit as st
from db.database import Database
from typing import List, Dict


def render_admin_dashboard(database: Database):
    """Render the admin dashboard."""
    st.header("📊 Admin Dashboard")
    st.markdown("---")
    
    # Search and filter section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_name = st.text_input("Search by Name", key="admin_search_name")
    
    with col2:
        search_email = st.text_input("Search by Email", key="admin_search_email")
    
    with col3:
        search_date = st.text_input("Search by Date (YYYY-MM-DD)", key="admin_search_date")
    
    # Search button
    if st.button("🔍 Search", key="admin_search_btn"):
        st.session_state.admin_search_name = search_name
        st.session_state.admin_search_email = search_email
        st.session_state.admin_search_date = search_date
    
    # Get bookings
    try:
        if search_name or search_email or search_date:
            bookings = database.search_bookings(
                name=search_name if search_name else None,
                email=search_email if search_email else None,
                date=search_date if search_date else None
            )
        else:
            bookings = database.get_all_bookings()
        
        if not bookings:
            st.info("No bookings found.")
            return
        
        # Display bookings
        st.subheader(f"📋 Total Bookings: {len(bookings)}")
        st.markdown("---")
        
        # Display as table
        for idx, booking in enumerate(bookings):
            # Ensure customer_name is displayed correctly
            customer_name = booking.get('customer_name', 'Unknown')
            booking_type = booking.get('booking_type', 'N/A')
            
            with st.expander(f"Booking #{booking['id']} - {customer_name} ({booking_type})", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Booking ID:** {booking['id']}")
                    st.markdown(f"**Customer Name:** {customer_name}")
                    st.markdown(f"**Email:** {booking.get('customer_email', 'N/A')}")
                    st.markdown(f"**Phone:** {booking.get('customer_phone', 'N/A')}")
                    st.markdown(f"**Status:** {booking.get('status', 'N/A')}")
                
                with col2:
                    st.markdown(f"**Ticket Type:** {booking_type}")
                    st.markdown(f"**Date:** {booking.get('date', 'N/A')}")
                    st.markdown(f"**Time:** {booking.get('time', 'N/A')}")
                    st.markdown(f"**Created At:** {booking.get('created_at', 'N/A')}")
                    if booking.get('notes'):
                        st.markdown(f"**Notes:** {booking['notes']}")
        
        # Summary statistics
        st.markdown("---")
        st.subheader("📈 Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_bookings = len(bookings)
        confirmed = len([b for b in bookings if b['status'] == 'confirmed'])
        booking_types = {}
        for booking in bookings:
            btype = booking['booking_type']
            booking_types[btype] = booking_types.get(btype, 0) + 1
        
        with col1:
            st.metric("Total Bookings", total_bookings)
        
        with col2:
            st.metric("Confirmed", confirmed)
        
        with col3:
            st.metric("Unique Customers", len(set(b['customer_email'] for b in bookings)))
        
        with col4:
            most_common_type = max(booking_types.items(), key=lambda x: x[1])[0] if booking_types else "N/A"
            st.metric("Most Common Type", most_common_type)
        
        # Booking types breakdown
        if booking_types:
            st.markdown("### Booking Types Distribution")
            for btype, count in sorted(booking_types.items(), key=lambda x: x[1], reverse=True):
                st.progress(count / total_bookings, text=f"{btype}: {count}")
    
    except Exception as e:
        st.error(f"Error loading bookings: {str(e)}")

