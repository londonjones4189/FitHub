import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

SideBarLinks()

st.write("# Accessing a REST API from Within Streamlit")
"""


Simply retrieving data from a REST api running in a separate Docker Container.

If the container isn't running, this will be very unhappy.  But the Streamlit app 
should not totally die. 


data = {} 
try:
  data = requests.get('http://web-api:4000/data').json()
except:
  st.write("**Important**: Could not connect to sample api, so using dummy data.")
  data = {"a":{"b": "123", "c": "hello"}, "z": {"b": "456", "c": "goodbye"}}

st.dataframe(data)
"""


# ============================
# USER STORY 1 — View Pending Reports
# ============================
st.write("### View Pending Reports")
get_pending_reports = requests.get("http://api:4000/a/reports/pending")
try:
    st.write(get_pending_reports.json())
except:
    st.write("Could not connect to database to get pending reports.")



# ============================
# USER STORY 1 — Resolve Report
# ============================
st.write("### Resolve Report (example: report_id = 1)")
resolve_report = requests.put("http://api:4000/a/reports/1/resolve")
try:
    st.write(resolve_report.json())
except:
    st.write("Could not resolve report.")



# ============================
# USER STORY 2 — Update User Role
# ============================
st.write("### Update User Role (example: user_id = 1)")
update_user_role = requests.put(
    "http://api:4000/a/users/1/role",
    json={"role": "admin"}
)
try:
    st.write(update_user_role.json())
except:
    st.write("Could not update user role.")



# ============================
# USER STORY 3 — Deactivate User
# ============================
st.write("### Deactivate User (example: user_id = 1)")
deactivate_user = requests.put("http://api:4000/a/users/1/deactivate")
try:
    st.write(deactivate_user.json())
except:
    st.write("Could not deactivate user.")



# ============================
# USER STORY 4 — Create Announcement
# ============================
st.write("### Create Announcement")
create_announcement = requests.post(
    "http://api:4000/a/announcements",
    json={"announcer_id": 1, "message": "Test announcement"}
)
try:
    st.write(create_announcement.json())
except:
    st.write("Could not create announcement.")



# ============================
# USER STORY 5 — Analytics Summary
# ============================
st.write("### Analytics Summary")
analytics_summary = requests.get("http://api:4000/a/analytics/summary")
try:
    st.write(analytics_summary.json())
except:
    st.write("Could not load analytics summary.")



# ============================
# USER STORY 6 — Delete Duplicate Items
# ============================
st.write("### Delete Duplicate Items")
delete_duplicates = requests.delete("http://api:4000/a/items/duplicates")
try:
    st.write(delete_duplicates.json())
except:
    st.write("Could not delete duplicate items.")



# ============================
# USER STORY 6+1 — Delete Specific Item
# ============================
st.write("### Delete Specific Item (example: item_id = 1)")
delete_item = requests.delete("http://api:4000/a/items/1")
try:
    st.write(delete_item.json())
except:
    st.write("Could not delete item.")
