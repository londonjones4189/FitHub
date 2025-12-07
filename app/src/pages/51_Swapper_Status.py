import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()
add_logo("assets/FitHublogo.png")

# Log swapper status access
logger.info(f"Swapper Status loaded by {st.session_state.get('first_name', 'Unknown')}")

API_BASE = "http://api:4000/s"

# CSS Styling
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    max-width: 95%;
}

.swapper-title {
    color: #328E6E;
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 30px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    background-color: #f0f2f6;
    border-radius: 8px;
    padding: 0 24px;
    font-size: 18px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background-color: #328E6E;
    color: white;
}

.section-subtitle {
    color: #000000;
    font-size: 28px;
    font-weight: bold;
    text-align: center;
    margin: 40px 0 30px 0;
}
</style>
""", unsafe_allow_html=True)

# Helper Functions
def render_trade_image(img_url, is_free=False):
    if img_url:
        return f'<div style="border: 2px solid #333; background-color: white; height: 150px; border-radius: 8px; overflow: hidden;"><img src="{img_url}" style="width: 100%; height: 100%; object-fit: cover;"></div>'
    elif is_free:
        return '<div style="border: 2px solid #333; background-color: white; height: 150px; display: flex; align-items: center; justify-content: center; border-radius: 8px;"><span style="font-size: 28px; font-weight: bold;">Free</span></div>'
    else:
        return '<div style="border: 2px solid #333; background-color: white; height: 150px; display: flex; align-items: center; justify-content: center; border-radius: 8px;"><span style="font-size: 20px; font-weight: bold;">IMG</span></div>'

def api_action(endpoint, success_msg, error_msg):
    try:
        response = requests.put(endpoint)
        if response.status_code == 200:
            st.success(success_msg)
            st.rerun()
        else:
            st.error(f"{error_msg}: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {e}")

# Main UI
st.markdown('<div class="swapper-title">Trade Status</div>', unsafe_allow_html=True)

trade_tab1, trade_tab2 = st.tabs(["Trades Ongoing", "Trades Completed"])

# TRADES ONGOING
with trade_tab1:
    try:
        user_id = st.session_state.get('user_id', 1)
        response = requests.get(f"{API_BASE}/trades/ongoing/{user_id}")
        ongoing_trades = response.json() if response.status_code == 200 else []
        
        if not ongoing_trades:
            st.info("No ongoing trades at the moment.")
        
        for trade in ongoing_trades:
            st.markdown('<div style="background-color: #f8f9fa; border: 2px solid #333; border-radius: 20px; padding: 25px; margin-bottom: 20px;">', unsafe_allow_html=True)
            
            col_title, col_msg = st.columns([3, 1])
            with col_title:
                trade_type = "Incoming Request" if trade["type"] == "incoming" else "Outgoing Request" if trade["type"] == "outgoing" else "Confirmed Take" if not trade.get("their_item_img") else "Confirmed Trade"
                st.markdown(f"### {trade_type} @{trade['username']}")
            with col_msg:
                st.button("Message", key=f"msg_{trade['username']}", use_container_width=True)
            
            c1, c2, c3, c4 = st.columns([2, 1, 2, 2])
            
            with c1:
                st.markdown(render_trade_image(trade.get("your_item_img")), unsafe_allow_html=True)
            with c2:
                st.markdown('<div style="display: flex; align-items: center; justify-content: center; height: 150px;"><span style="font-size: 48px; font-weight: bold;">→</span></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(render_trade_image(trade.get("their_item_img"), trade.get("is_free")), unsafe_allow_html=True)
            with c4:
                if trade["type"] == "incoming":
                    st.markdown('<div style="display: flex; gap: 10px; align-items: center; height: 150px;">', unsafe_allow_html=True)
                    acc, rej = st.columns(2)
                    with acc:
                        st.markdown('<div style="background-color: #90EE90; border: 2px solid #333; border-radius: 12px; height: 100px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 48px; font-weight: bold;">✓</span></div>', unsafe_allow_html=True)
                    with rej:
                        st.markdown('<div style="background-color: #FFB6C1; border: 2px solid #333; border-radius: 12px; height: 100px; display: flex; align-items: center; justify-content: center;"><span style="font-size: 48px; font-weight: bold;">✕</span></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    ac, rc = st.columns(2)
                    with ac:
                        if st.button("Accept", key=f"accept_{trade['username']}", use_container_width=True, type="secondary"):
                            api_action(f"{API_BASE}/trades/{trade.get('trade_id', 0)}/accept", f"Trade with @{trade['username']} accepted!", "Failed to accept trade")
                    with rc:
                        if st.button("Reject", key=f"reject_{trade['username']}", use_container_width=True, type="secondary"):
                            api_action(f"{API_BASE}/trades/{trade.get('trade_id', 0)}/reject", f"Trade with @{trade['username']} rejected!", "Failed to reject trade")
                
                elif trade["type"] == "outgoing":
                    st.markdown(f'<div style="display: flex; align-items: center; height: 150px;"><span style="font-size: 18px; font-weight: bold;">Status: {trade["status"]}</span></div>', unsafe_allow_html=True)
                
                else:
                    st.markdown(f'<div style="font-size: 16px; margin-top: 10px;"><strong>Status:</strong> {trade["status"]}<br><strong>Location:</strong> {trade["location"]}<br><strong>Date:</strong> {trade["date"]}</div>', unsafe_allow_html=True)
                    st.write("")
                    if st.button("Cancel Trade", key=f"cancel_{trade['username']}", use_container_width=True):
                        api_action(f"{API_BASE}/trades/{trade.get('trade_id', 0)}/cancel", f"Trade with @{trade['username']} cancelled!", "Failed to cancel trade")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    except requests.exceptions.RequestException as e:
        st.error("Unable to connect to the server.")

# TRADES COMPLETED
with trade_tab2:
    try:
        response = requests.get(f"{API_BASE}/trades/completed/{st.session_state.get('user_id', 1)}")
        completed_trades = response.json() if response.status_code == 200 else []
        
        if not completed_trades:
            st.info("No completed trades yet.")
        else:
            for trade in completed_trades:
                st.markdown('<div style="background-color: #f8f9fa; border: 2px solid #333; border-radius: 20px; padding: 25px; margin-bottom: 20px;">', unsafe_allow_html=True)
                st.markdown(f"### Trade with @{trade.get('username', 'Unknown')}")
                
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1:
                    st.markdown(render_trade_image(trade.get("your_item_img")), unsafe_allow_html=True)
                with c2:
                    st.markdown('<div style="display: flex; align-items: center; justify-content: center; height: 150px;"><span style="font-size: 48px; font-weight: bold;">→</span></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(render_trade_image(trade.get("their_item_img"), not trade.get("their_item_img")), unsafe_allow_html=True)
                
                st.markdown(f'<div style="margin-top: 20px; font-size: 16px;"><strong>Completed:</strong> {trade.get("completed_date", "N/A")}<br><strong>Location:</strong> {trade.get("location", "N/A")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    except requests.exceptions.RequestException as e:
        st.error("Unable to connect to the server.")
