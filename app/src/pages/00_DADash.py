import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

st.title(f"Welcome Data Analyst, {st.session_state['first_name']}!")
st.write('')
st.write('')
st.write('### What would you like to analyze today?')

if st.button('📦 View Listings & Category Stock', 
             type='primary',
             use_container_width=True):
    st.switch_page('pages/01_DA_Listings.py')

if st.button('🚨 Check Late Shipments', 
             type='primary',
             use_container_width=True):
    st.switch_page('pages/02_DA_Shipments.py')

if st.button('👥 Analyze User Metrics', 
             type='primary',
             use_container_width=True):
    st.switch_page('pages/03_DA_User_Metrics.py')