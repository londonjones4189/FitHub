# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar of the app

import streamlit as st


#### ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")

#Admin Nav Micah
def ReportsManagementNav():
    st.sidebar.page_link("pages/10_Reports_Management.py", label="Reports Management")
def AdminUserToolsNav():
    st.sidebar.page_link("pages/10_Admin_User_Tools.py", label="Admin User Tools" )
def ItemCleanupNav():
    st.sidebar.page_link("pages/10_Item_Cleanup.py", label="Item Cleanup" )
def AdminHomeNav():
    st.sidebar.page_link("pages/00_AdminDash.py", label= "Admin Home")

def DataAnalystNav():
    st.sidebar.page_link("pages/00_DADash.py", label = "Data Analyst Home")
# --------------------------------Links Function -----------------------------------------------
def SideBarLinks(show_home=False):

    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """

    # add a logo to the sidebar always
    st.sidebar.image("assets/FitHublogo.png", width=150)

    # If there is no logged in user, redirect to the Home (Landing) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        # Show the Home page link (the landing page)
        HomeNav()

    # Show the other page navigators depending on the users' role.
    if st.session_state["authenticated"]:


        # If the user is an administrator, give them access to the administrator pages
        if st.session_state["role"] == "admin":
            AdminHomeNav()
            AdminUserToolsNav()
            ItemCleanupNav()
            ReportsManagementNav()
        #If the user is an data analyst, give them access to the data analyst pages
        if st.session_state["role"] == "data_analyst":
            DataAnalystNav()

    # Always show the About page at the bottom of the list of links
    AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout", key="logout_button"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")