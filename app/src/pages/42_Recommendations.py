import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

API_BASE = "http://api:4000/t"

st.title('✨ Personalized Recommendations')
st.caption("Items posted in the last 24 hours that match your preferences")

#Still assuming user ID is hardcoded for demo purposes
user_id = 3

#SIZE PREFERENCE
with st.container(border=True):
    size_pref = st.selectbox(
        "Select Your Preferred Size",
        options=["S", "M", "L", "XL", "XXL"] #idk how many sizes we want or how to do numeric sizes
    )
st.divider()

try:
    response = requests.get(f"{API_BASE}/recommendations/{user_id}", params={'size': size_pref})
    recommendations = response.json()
    
    if recommendations:
        st.success(f"**🎉 Found {len(recommendations)} new items for you!**")
        
        with st.container(height=600, border=True):
            for item in recommendations:
                with st.expander(f"✨ {item.get('Title', 'Item')}", expanded=False):
                    cols = st.columns([2, 1])
                    
                    with cols[0]:
                        st.write(f"**Item ID:** {item.get('ItemID', 'N/A')}")
                        st.write(f"**Category:** {item.get('Category', 'N/A')}")
                        st.write(f"**Size:** {item.get('Size', 'N/A')}")
                        st.write(f"**Owner:** {item.get('OwnerName', 'N/A')}")
                        st.write(f"**Posted:** {item.get('ListedAt', 'N/A')}")
                    
                    with cols[1]:
                        if st.button("Request Item", key=f"rec_{item['ItemID']}", type="primary"):
                            st.success(f"✅ Request sent for {item['Title']}!")
    else:
        st.info(f"No new items in size {size_pref} posted in the last 24 hours. Check back later!")
        
except Exception as e:
    st.error(f"Could not connect to database to get recommendations: {str(e)}")