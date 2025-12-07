import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

API_BASE = "http://api:4000/t"

st.title('📦 My Orders')
#I would assume we would hardcode user ID for the demo instead of session_state?
user_id = 3

left_col, right_col = st.columns([2,1])

with left_col:
    st.subheader("Active Orders")

    try:
        response = requests.get(f"{API_BASE}/track_package/{user_id}")
        orders = response.json()

        if orders:
            #Filter active orders (not yet shipped)
            active_orders = [order for order in orders if not o.get('DateArrived')]

            if active_orders:
                with st.container(height = 500, border = True):
                    for order in active_orders:
                        with st.expander(f"Order #{order['OrderID']} - {order['Title']}", expanded=False):
                            cols = st.columns([2, 1])
                            
                            with cols[0]:
                                st.write(f"**Item:** {order['Title']}")
                                st.write(f"**Requested:** {order['RequestDate']}")
                                if order.get('Carrier'):
                                    st.write(f"**Carrier:** {order['Carrier']}")
                                if order.get('TrackingNum'):
                                    st.write(f"**Tracking:** {order['TrackingNum']}")
                                
                                if order.get('DateShipped'):
                                    st.info(f"📦 Shipped on {order['DateShipped']}")
                                else:
                                    st.warning("⏳ Processing...")
                            
                            with cols[1]:
                                # Only allow cancel if not shipped yet
                                if not order.get('DateShipped'):
                                    if st.button("Cancel Order", key=f"cancel_{order['OrderID']}", type="secondary"):
                                        cancel_response = requests.delete(
                                            f"{API_BASE}/orders/{order['OrderID']}",
                                            params={'user_id': USER_ID}
                                        )
                                        if cancel_response.status_code == 200:
                                            st.success("✅ Order cancelled!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to cancel order")
            else:
                st.info("You have no active orders at the moment.")
        else:
            st.info("You have no orders at the moment.")

    except Exception as e:
        st.error(f"An error occurred while fetching your orders: {e}")

with right_col:
    st.subheader("📊 Order Summary")
    
    try:
        response = requests.get(f"{API_BASE}/track_package/{user_id}")
        orders = response.json()
        
        if orders:
            with st.container(border=True):
                total_orders = len(orders)
                delivered = len([o for o in orders if o.get('DateArrived')])
                in_transit = len([o for o in orders if o.get('DateShipped') and not o.get('DateArrived')])
                processing = len([o for o in orders if not o.get('DateShipped')])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Orders", total_orders)
                    st.metric("In Transit", in_transit)
                with col2:
                    st.metric("Delivered", delivered)
                    st.metric("Processing", processing)
        else:
            with st.container(border=True):
                st.info("No order data available")
                
    except Exception as e:
        st.error(f"Could not load order summary")
    
    st.divider()
    
    st.subheader("✅ Order History")
    
    try:
        response = requests.get(f"{API_BASE}/track_package/{user_id}")
        orders = response.json()
        
        if orders:
            delivered_orders = [o for o in orders if o.get('DateArrived')]
            
            with st.container(height=300, border=True):
                if delivered_orders:
                    for order in delivered_orders:
                        with st.container(border=True):
                            st.write(f"**{order['Title']}**")
                            st.write(f"Delivered: {order['DateArrived']}")
                else:
                    st.info("No delivered orders yet")
        
    except Exception as e:
        st.error("Could not load order history")