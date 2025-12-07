import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
from datetime import datetime

st.set_page_config(layout="wide")
SideBarLinks()

API_BASE = "http://api:4000/admin"

st.markdown('<div class="page-title">📢 Announcements</div>', unsafe_allow_html=True)

# Create Announcement Section
st.subheader("📝 Create New Announcement")

announcer_id = 1

with st.container(border=True):
    message = st.text_area(
        "Message",
        placeholder="Enter your announcement message here...",
        height=150,
        help="This message will be sent to all active users"
    )

    # Submit button
    if st.button("📤 Send Announcement", type="primary", use_container_width=True):
        if message.strip():
            try:
                # Create announcement via API
                response = requests.post(
                    f"{API_BASE}/create_announcements",
                    json={
                        "announcer_id": announcer_id,
                        "message": message
                    }
                )

                if response.status_code == 201:
                    result = response.json()
                    st.success(f"✅ Announcement created successfully! ID: {result.get('data', {}).get('announcement_id')}")
                    st.balloons()
                    # Clear the message after successful submission
                    st.rerun()
                else:
                    error_msg = response.json().get('message', 'Unknown error')
                    st.error(f"❌ Failed to create announcement: {error_msg}")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Could not connect to API: {str(e)}")
        else:
            st.warning("⚠️ Please enter a message before sending")

# Past Announcements Section
st.divider()
st.subheader("🗓️ Past Announcements")

with st.container(border=True):
    try:
        announcements_response = requests.get(f"{API_BASE}/announcements")
        if announcements_response.status_code == 200:
            announcements_data = announcements_response.json()
            announcements = announcements_data.get('data', [])

            if announcements:
                for announcement in announcements:
                    with st.expander(
                            f"📢 {announcement.get('message', 'No message')[:50]}... - {announcement.get('announced_at', 'Unknown date')}",
                            expanded=False
                    ):
                        st.write(f"**Announcer:** {announcement.get('announcer_name', 'Unknown')}")
                        st.write(f"**Date:** {announcement.get('announced_at', 'Unknown')}")
                        st.write(f"**Message:** {announcement.get('message', 'No message')}")
            else:
                st.info("No announcements found")
        else:
            st.warning("Could not fetch announcements")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to API: {str(e)}")
