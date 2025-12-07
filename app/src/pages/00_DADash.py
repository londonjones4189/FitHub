import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
st.set_page_config(layout="wide")
SideBarLinks()

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()
API_BASE = "http://api:4000/d"

st.title(f"Welcome Data Analyst, {st.session_state['first_name']}.")
st.write('')
st.write('')

st.write("### View All Listings")
get_listings = requests.get(f"{API_BASE}/listings")
try:
    st.write(get_listings.json())
except:
    st.write("Could not connect to Database to get all listings.")
