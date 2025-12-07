import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks()
API_BASE = "http://api:4000/d"


st.title(f"Welcome, {st.session_state['first_name']}!")

left_col, right_col = st.columns([2, 1])

with left_col:
    #Get all listings
    st.subheader("📦 All Listings")
    get_listings = requests.get(f"{API_BASE}/listings")
    try:
        listings = get_listings.json()

        if listings:
            with st.container(height=400, border=True):
                for listing in listings:
                    with st.expander(f"🏷️ {listing.get('name', listing.get('ListingID', 'Item'))}", expanded=False):
                        cols = st.columns(2)

                        items = list(listing.items())
                        mid = len(items) // 2
                        with cols[0]:
                            for key, value in items[:mid]:
                                st.write(f"**{key}:** {value}")
                        with cols[1]:
                            for key, value in items[mid:]:
                                st.write(f"**{key}:** {value}")
    except:
        st.write("Could not connect to database to get listings")

    st.divider()

    # Category Stock
    st.subheader("👕 Category Stock")
    get_listings_category = requests.get(f"{API_BASE}/listings/category")
    try:
        category_data = get_listings_category.json()

        if category_data:
            if isinstance(category_data, list):
                df = pd.DataFrame(category_data)
            elif isinstance(category_data, dict):
                df = pd.DataFrame([category_data])
            else:
                df = pd.DataFrame()

            if not df.empty:
                with st.container(height=300, border=True):
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No category data available")
        else:
            st.info("No category data available")
    except:
        st.write("Could not connect to database to get category stock")

    st.divider()

    # Get User growth
    st.subheader("👥 User Growth by Demographics")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female"])
        with col2:
            age_min = st.number_input("Min Age", min_value=0, max_value=110, value=0)
        with col3:
            age_max = st.number_input("Max Age", min_value=0, max_value=110, value=0)

        if st.button("Enter", type="primary"):
            get_users_demo = requests.get(f"{API_BASE}/users/{gender}/{age_min}/{age_max}")
            try:
                users_data = get_users_demo.json()

                if users_data:
                    st.success(f"Found {len(users_data)} users")

                    df = pd.DataFrame(users_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    if 'Age' in df.columns:
                        st.caption("Age Distribution")
                        age_counts = df['Age'].value_counts().sort_index()
                        st.bar_chart(age_counts, height=200)
                else:
                    st.info("No users found")

            except:
                st.error("Could not connect to database to get user demographic information")

with right_col:
    # Late Shipments Alert
    st.subheader("🚨 Late Shipments")

    get_late_shipments = requests.get(f"{API_BASE}/listings/category")
    try:
        late_shipments_data = get_late_shipments.json()

        with st.container(height=300, border=True):
            if late_shipments_data:
                if isinstance(late_shipments_data, list):
                    st.error(f"**{len(late_shipments_data)} shipments are overdue!**")

                    for shipment in late_shipments_data:
                        with st.container(border=True):
                            for key, value in shipment.items():
                                st.write(f"**{key}:** {value}")
                else:
                    st.write(late_shipments_data)
            else:
                st.success("No late shipments")

    except:
        st.write("Could not connect to database to get late shipments")

    st.divider()


    # Get all users
    st.subheader("👤Users")
    get_users = requests.get(f"{API_BASE}/users")
    try:
        users_data = get_users.json()

        with st.container(height=300, border=True):
            if users_data:
                for user in users_data:
                    with st.expander(f"👤 {user.get('Name', 'User')}", expanded=False):
                        cols = st.columns(2)

                        with cols[0]:
                            st.write(f"**User ID:** {user.get('UserID', 'N/A')}")
                            st.write(f"**Email:** {user.get('Email', 'N/A')}")
                            st.write(f"**Phone:** {user.get('Phone', 'N/A')}")
                            st.write(f"**Gender:** {user.get('Gender', 'N/A')}")

                        with cols[1]:
                            st.write(f"**Address:** {user.get('Address', 'N/A')}")
                            st.write(f"**DOB:** {user.get('DOB', 'N/A')}")
            else:
                st.info("No users found")

    except:
        st.write("Could not connect to database to get users")

    st.divider()

    # Engagement Metrics
    st.subheader("📊 Engagement")
    get_engagement = requests.get(f"{API_BASE}/users/engagement")
    try:
        engagement_data = get_engagement.json()

        with st.container(border=True):
            if engagement_data:
                df = pd.DataFrame(engagement_data)
                col1, col2,= st.columns(2)
                with col1:
                    st.metric("Total Received", int(df['OrdersReceived'].sum()))
                with col2:
                    st.metric("Total Given", int(df['OrdersGiven'].sum()))
                st.divider()
                st.caption("Most Engaged Users")
                df['TotalOrders'] = df['OrdersReceived'] + df['OrdersGiven']
                top_users = df.nlargest(5, 'TotalOrders')
                chart_data = top_users[['OrdersReceived', 'OrdersGiven']].set_index(top_users['UserID'])
                st.bar_chart(chart_data, height=250)
            else:
                st.info("No engagement data available")
    except:
        st.write("Could not connect to database to engagement metrics")