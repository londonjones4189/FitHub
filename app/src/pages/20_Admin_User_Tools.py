import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout="wide")

SideBarLinks()

API_BASE = "http://api:4000/a"

st.title("Admin: User Management")

# create 2 columns
col1, col2 = st.columns(2)


# UPDATE USER ROLE

with col1:
    st.subheader("Update User Role")

    user_id = st.number_input("User ID:", step=1, min_value=1)

    new_role = st.selectbox(
        "Select Role",
        ["admin", "user", "worker"]
    )

    if st.button("Update Role", use_container_width=True):
        logger.info(f"Updating role for user {user_id} → {new_role}")

        try:
            response = requests.put(
                f"{API_BASE}/users/{int(user_id)}/role",
                json={"role": new_role}
            )
            st.write(response.json())
        except:
            st.write("Error: Could not update role.")



# DEACTIVATE USER

with col2:
    st.subheader("Deactivate User")

    deactivate_user_id = st.number_input("User ID to Deactivate:", step=1, min_value=1)

    if st.button("Deactivate", use_container_width=True):
        logger.info(f"Deactivating user {deactivate_user_id}")

        try:
            response = requests.put(
                f"{API_BASE}/users/{int(deactivate_user_id)}/deactivate"
            )
            st.write(response.json())
        except:
            st.write("Error: Could not deactivate user.")
