import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from streamlit_extras.app_logo import add_logo
from modules .nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks()

API_BASE = "http://api:4000/d"

st.title(f"Welcome Taker, {st.session_state['first_name']}!")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Browse Available Listings',
             type = 'primary',
             use_container_width=True):
    st.switch_page('pages/40_Browse_Listings.py')

if st.button('View My Orders',
             type = 'primary',
             use_container_width=True):
    st.switch_page('pages/41_My_Orders.py')

if st.button('View Recommendations',
             type = 'primary',
             use_container_width=True):
    st.switch_page('pages/42_Recommendations.py')

if st.button('Track My Packages',
             type = 'primary',
             use_container_width=True):
    st.switch_page('pages/43_Track_Packages.py')
    
    