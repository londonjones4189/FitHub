import logging
logger = logging.getLogger(__name__)

import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
st.set_page_config(layout = 'wide')
# Load sidebar navigation (includes admin links if authenticated)
SideBarLinks()

# Add logo to sidebar
add_logo("assets/FitHublogo.png")

# Log admin dashboard access
logger.info(f"Admin Dashboard loaded by {st.session_state.get('first_name', 'Unknown')}")

# Title
st.title("Admin Dashboard")

st.markdown("### ")

if st.button('Manage Reports',
             type='primary',
             use_container_width=True):
  st.switch_page('pages/10_Reports_Management.py')
if st.button("User Roles", use_container_width=True):
    logger.info("Navigating to User Roles page")
    st.switch_page("pages/20_Admin_User_Tools.py")


if st.button("Item Cleanup Tools", use_container_width=True):
    logger.info("Navigating to Item Cleanup Tools")
    st.switch_page("pages/30_Item_Cleanup.py")

