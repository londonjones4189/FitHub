import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import time
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()
add_logo("assets/FitHublogo.png")

# Log swapper feed access
logger.info(f"Swapper Feed loaded by {st.session_state.get('first_name', 'Unknown')}")

API_BASE = "http://api:4000/s"

st.title("👕 Browse Available Swap Listings")

#FILTERS
st.subheader("Filter Listings")
with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        category_filter = st.selectbox(
            "Select Category",
            options=["All", "shoes", "t-shirt", "jacket", "dress", "jeans", "sweater", "coat", "skirt", "hoodie", "shirt", "blouse", "pants", "shorts", "top", "vest", "blazer", "tank top"]
        )

    with col2:
        size_filter = st.selectbox(
            "Select Size",
            options=["All", "XS", "S", "M", "L", "XL", "XXL"]
        )

    with col3:
        condition_filter = st.multiselect(
            "Select Condition(s)",
            options=["Excellent", "Very good", "Good", "Fair"]
        )

    with col4:
        tags_filter = st.multiselect(
            "Select Tags",
            options=["Y2K", "Chic", "Bohemian", "Preppy", "Retro", "Eclectic", "Sporty", "Edgy", "Minimalist", "Sophisticated", "Urban"]
        )

params = {}
if category_filter != "All":
    params['category'] = category_filter
if size_filter != "All":
    params['size'] = size_filter
if condition_filter:
    params['condition'] = ','.join(condition_filter)
if tags_filter:
    params['tags'] = ','.join(tags_filter)

if params:
    response = requests.get(f"{API_BASE}/listings/filter", params=params)
else:
    response = requests.get(f"{API_BASE}/listings/up_for_swap")

listings = response.json() if response.status_code == 200 else []

if listings:
    st.success(f"Found {len(listings)} listings matching your criteria.")

    # Category emoji mapping
    category_emojis = {
        'shoes': '👟',
        't-shirt': '👕',
        'jacket': '🧥',
        'dress': '👗',
        'jeans': '👖',
        'sweater': '🧶',
        'coat': '🧥',
        'skirt': '👗',
        'hoodie': '🧥',
        'shirt': '👔',
        'blouse': '👔',
        'pants': '👖',
        'shorts': '🩳',
        'top': '👚',
        'vest': '🎽',
        'blazer': '👔',
        'tank top': '👕'
    }
    
    def get_category_emoji(category):
        if category:
            category_lower = str(category).lower()
            return category_emojis.get(category_lower, '👕')
        return '👕'

    with st.container(height = 600, border = True):
        for item in listings:
            category = item.get('Category', '')
            emoji = get_category_emoji(category)
            with st.expander(f"{emoji} {item.get('Title', 'Item')}", expanded=False):
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

                item_id = item.get('ItemID')
                user_id = st.session_state.get('user_id', 1)
                
                # For swapper, we might want to initiate a swap request instead of just requesting
                # This would need to be implemented based on your swap logic
                if st.button(f"Initiate Swap", key=f"swap_{item_id}", type="primary"):
                    # TODO: Implement swap initiation logic
                    # This might involve selecting an item to swap, or just initiating a swap request
                    st.toast(f"Swap initiated for: {item['Title']}", icon="✅")
                    time.sleep(1.5)
                    st.rerun()

else:
    st.info("No listings found matching your criteria.")
