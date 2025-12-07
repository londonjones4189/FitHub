import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

API_BASE = "http://api:4000/t"

st.title("👕 Browse Available Listings")

#FILTERS
st.subheader("Filter Listings")
with st.container(border=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        size_filter = st.selectbox(
            "Select Size",
            options=["All", "S", "M", "L", "XL", "XXL"] #idk how many sizes we want or how to do numeric sizes
        )

    with col2:
        condition_filter = st.multiselect(
            "Select Condition(s)",
            options=["New", "Like New", "Good", "Fair", "Poor"]
        )

    with col3:
        tags_filter = st.multiselect(
            "Select Tags",
            options=["Vintage", "Casual", "Y2K", "Formal", "Sport"]
        )

        st.divider()

#GET LISTINGS
try:
    params = {}
    if size_filter != "All":
        params['size'] = size_filter
    if condition_filter:
        params['condition'] = ','.join(condition_filter)
    if tags_filter:
        params['tags'] = ','.join(tags_filter)

    if params:
        response = requests.get(f"{API_BASE}/listings/filter", params=params)
    else:
        response = requests.get(f"{API_BASE}/listings/up_for_grabs")

    listings = response.json()

    if listings:
        st.success(f"Found {len(listings)} listings matching your criteria.")

        with st.container(height = 600, border = True):
            for item in listings:
                with st.expander(f"🏷️ {item.get('Title', 'Item')}", expanded=False):
                    cols = st.columns(2)
                    with cols[0]:
                        st.write(f"**Category:** {item.get('Category', 'N/A')}")
                        st.write(f"**Description:** {item.get('Description', 'N/A')}")
                        st.write(f"**Size:** {item.get('Size', 'N/A')}")
                        st.write(f"**Condition:** {item.get('Condition', 'N/A')}")
                    with cols[1]:
                        st.write(f"**Owner:** {item.get('OwnerName', 'N/A')}")
                        st.write(f"**Tags:** {item.get('Tags', 'N/A')}")
                        st.write(f"**Listed At:** {item.get('ListedAt', 'N/A')}")
                st.write(f"**Description:** {item.get('Description', 'N/A')}")

                if st.button(f"Request Item: {item.get('Title', 'Item')}", key=item.get('ItemID')):
                    st.success(f"✅ Request sent for {item['Title']}!")

    else:
        st.info("No listings found matching your criteria.")

except Exception as e:
    logger.error(f"Error fetching listings: {e}")
    st.error("An error occurred while fetching listings. Please try again later.")