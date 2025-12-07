"""
Swapper Dashboard Page

This page displays available items for swapping and tracks user's trade activity.

API Endpoints Expected:
-----------------------

1. GET /items
   Query Parameters: size, condition, posted_date (optional)
   Response: List of item objects
   Example:
   [
     {
       "id": 1,
       "name": "Item Name",
       "size": "M",
       "condition": "Like New",
       "image_url": "http://...",
       "posted_date": "2025-12-01"
     }
   ]

2. GET /trades/ongoing/{user_id}
   Response: List of ongoing trade objects
   Example:
   [
     {
       "type": "incoming",  // or "outgoing" or "confirmed"
       "username": "username",
       "your_item_img": "http://...",  // URL to your item image
       "their_item_img": "http://...",  // URL to their item image (null for free items)
       "is_free": false,  // true if it's a free giveaway
       "status": "pending",  // or "PENDING", "Scheduled", "Unscheduled"
       "location": "Curry Center",  // for confirmed trades
       "date": "12-03-2025 6 pm"  // for confirmed trades
     }
   ]

3. GET /trades/completed/{user_id}
   Response: List of completed trade objects
   Example:
   [
     {
       "username": "username",
       "your_item_img": "http://...",
       "their_item_img": "http://...",
       "completed_date": "12-01-2025",
       "location": "Curry Center"
     }
   ]
"""

import logging
import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

# API base URL
API_URL = "http://localhost:4000"

# Page config
st.set_page_config(layout="wide")

# Sidebar with logo
SideBarLinks()
add_logo("assets/FitHublogo.png")

# Log swapper dashboard access
logger.info(f"Swapper Dashboard loaded by {st.session_state.get('first_name', 'Unknown')}")


# CSS Styling
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    max-width: 95%;
}

/* Page title */
.swapper-title {
    color: #328E6E;
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 30px;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    background-color: #f0f2f6;
    border-radius: 8px;
    padding: 0 24px;
    font-size: 18px;
    font-weight: 600;
    color: #666;
}

.stTabs [aria-selected="true"] {
    background-color: #328E6E;
    color: white;
}

/* Filter section */
.filter-container {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 30px;
}

.filter-label {
    color: #000000;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 15px;
}

/* Section subtitle */
.section-subtitle {
    color: #000000;
    font-size: 28px;
    font-weight: bold;
    text-align: center;
    margin: 40px 0 30px 0;
}

/* Item cards */
.item-card {
    background-color: #D3D3D3;
    padding: 40px 20px;
    border-radius: 12px;
    text-align: center;
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
}

.item-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.item-name {
    color: #000000;
    font-size: 32px;
    font-weight: bold;
}

/* Dropdown styling */
div[data-baseweb="select"] {
    font-size: 18px;
}

/* Center columns */
[data-testid="column"] {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

/* Custom button styling for accept/reject */
div.stButton > button[kind="primary"] {
    background-color: #90EE90 !important;
    color: black !important;
    font-size: 32px !important;
    font-weight: bold !important;
    height: 80px !important;
    border: 2px solid #333 !important;
}

div.stButton > button[kind="secondary"] {
    background-color: #FFB6C1 !important;
    color: black !important;
    font-size: 32px !important;
    font-weight: bold !important;
    height: 80px !important;
    border: 2px solid #333 !important;
}

</style>
""", unsafe_allow_html=True)


# Helper Functions
def fetch_items(size_filter=None, condition_filter=None, posted_date_filter=None):
    """Fetch items from the API with optional filters"""
    try:
        params = {}
        if size_filter and size_filter != "All":
            params['size'] = size_filter
        if condition_filter and condition_filter != "All":
            params['condition'] = condition_filter
        if posted_date_filter and posted_date_filter != "All":
            params['posted_date'] = posted_date_filter
        
        response = requests.get(f"{API_URL}/items", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch items: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error fetching items: {str(e)}")
        st.error("Unable to connect to the server. Please try again later.")
        return []


def display_item_card(item, col):
    """Display an item card in the specified column"""
    with col:
        st.markdown(f"""
        <div class="item-card">
            <div class="item-name">{item.get('name', 'Unknown Item')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add click functionality
        if st.button(f"View Details", key=f"item_{item.get('id', 0)}", use_container_width=True):
            st.session_state['selected_item'] = item
            st.switch_page("pages/Item_Details.py")


# Main UI
st.markdown('<div class="swapper-title">Swapper Dashboard</div>', unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["Feed", "Status"])

# TAB 1: FEED
with tab1:
    # Filter Section
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        st.markdown('<div class="filter-label">Filter: Size</div>', unsafe_allow_html=True)
        size_options = ["All", "XS", "S", "M", "L", "XL", "XXL"]
        size_filter = st.selectbox(
            "Size",
            options=size_options,
            label_visibility="collapsed",
            key="size_filter"
        )

    with filter_col2:
        st.markdown('<div class="filter-label">Condition</div>', unsafe_allow_html=True)
        condition_options = ["All", "New", "Like New", "Good", "Fair", "Well-Worn"]
        condition_filter = st.selectbox(
            "Condition",
            options=condition_options,
            label_visibility="collapsed",
            key="condition_filter"
        )

    with filter_col3:
        st.markdown('<div class="filter-label">Posted Date</div>', unsafe_allow_html=True)
        posted_date_options = ["All", "Today", "Last 7 Days", "Last 30 Days", "Last 3 Months"]
        posted_date_filter = st.selectbox(
            "Posted Date",
            options=posted_date_options,
            label_visibility="collapsed",
            key="posted_date_filter"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Fetch items based on filters
    items = fetch_items(size_filter, condition_filter, posted_date_filter)

    # Display section
    st.markdown('<div class="section-subtitle">Current Available items</div>', unsafe_allow_html=True)

    # Display items in a grid
    if items:
        # Display 4 items per row
        for i in range(0, len(items), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(items):
                    display_item_card(items[i + j], cols[j])
    else:
        st.info("No items available matching your filters. Try adjusting your search criteria.")

    # Add spacing
    st.write("")
    st.write("")

    # Optional: Add refresh button
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        if st.button("Refresh Items", use_container_width=True):
            st.rerun()

# TAB 2: STATUS (TRADE PAGE)
with tab2:
    st.markdown('<div class="section-subtitle">TRADE PAGE</div>', unsafe_allow_html=True)
    
    # Sub-tabs for Trades Ongoing and Trades Completed
    trade_tab1, trade_tab2 = st.tabs(["Trades Ongoing", "Trades Completed"])
    
    # TRADES ONGOING
    with trade_tab1:
        st.write("")
        
        # Fetch ongoing trades from API
        try:
            user_id = st.session_state.get('user_id', 1)  # Get actual user_id from session
            response = requests.get(f"{API_URL}/trades/ongoing/{user_id}")
            
            if response.status_code == 200:
                ongoing_trades = response.json()
                
                if not ongoing_trades:
                    st.info("No ongoing trades at the moment.")
            else:
                st.error(f"Failed to fetch ongoing trades. Status code: {response.status_code}")
                ongoing_trades = []
        except Exception as e:
            logger.error(f"Error fetching ongoing trades: {str(e)}")
            st.error("Unable to connect to the server. Please try again later.")
            ongoing_trades = []
        
        # Display trades from API
        for trade in ongoing_trades:
            # Trade card container
            st.markdown(f"""
            <div style="background-color: #f8f9fa; border: 2px solid #333; border-radius: 20px; 
                        padding: 25px; margin-bottom: 20px;">
            """, unsafe_allow_html=True)
            
            # Header row with title and message button
            col_title, col_msg = st.columns([3, 1])
            
            with col_title:
                if trade["type"] == "incoming":
                    st.markdown(f"### Incoming Request @{trade['username']}")
                elif trade["type"] == "outgoing":
                    st.markdown(f"### Outgoing Request @{trade['username']}")
                else:
                    if trade.get("their_item_img"):
                        st.markdown(f"### Confirmed Trade @{trade['username']}")
                    else:
                        st.markdown(f"### Confirmed Take @{trade['username']}")
            
            with col_msg:
                if st.button("Message", key=f"msg_{trade['username']}", use_container_width=True):
                    st.info(f"Opening message with @{trade['username']}")
            
            # Trade items and actions row
            trade_col1, trade_col2, trade_col3, trade_col4 = st.columns([2, 1, 2, 2])
            
            with trade_col1:
                # Your item image - display actual image if URL provided, otherwise show placeholder
                if trade.get("your_item_img"):
                    st.markdown(f"""
                    <div style="border: 2px solid #333; background-color: white; height: 150px; 
                                border-radius: 8px; overflow: hidden;">
                        <img src="{trade['your_item_img']}" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="border: 2px solid #333; background-color: white; height: 150px; 
                                display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                        <span style="font-size: 20px; font-weight: bold;">IMG</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with trade_col2:
                # Arrow
                st.markdown("""
                <div style="display: flex; align-items: center; justify-content: center; height: 150px;">
                    <span style="font-size: 48px; font-weight: bold;">→</span>
                </div>
                """, unsafe_allow_html=True)
            
            with trade_col3:
                # Their item image - display actual image, "Free", or placeholder
                if trade.get("their_item_img"):
                    st.markdown(f"""
                    <div style="border: 2px solid #333; background-color: white; height: 150px; 
                                border-radius: 8px; overflow: hidden;">
                        <img src="{trade['their_item_img']}" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    """, unsafe_allow_html=True)
                elif trade.get("is_free") or trade["type"] == "confirmed" and not trade.get("their_item_img"):
                    st.markdown("""
                    <div style="border: 2px solid #333; background-color: white; height: 150px; 
                                display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                        <span style="font-size: 28px; font-weight: bold;">Free</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="border: 2px solid #333; background-color: white; height: 150px; 
                                display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                        <span style="font-size: 20px; font-weight: bold;">IMG</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with trade_col4:
                # Action buttons or status info
                if trade["type"] == "incoming":
                    # Accept/Reject buttons with custom styling
                    st.markdown("""
                    <div style="display: flex; gap: 10px; align-items: center; height: 150px;">
                    """, unsafe_allow_html=True)
                    
                    accept_col, reject_col = st.columns(2)
                    with accept_col:
                        st.markdown("""
                        <div style="background-color: #90EE90; border: 2px solid #333; border-radius: 12px; 
                                    height: 100px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
                            <span style="font-size: 48px; font-weight: bold;">✓</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with reject_col:
                        st.markdown("""
                        <div style="background-color: #FFB6C1; border: 2px solid #333; border-radius: 12px; 
                                    height: 100px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
                            <span style="font-size: 48px; font-weight: bold;">✕</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Hidden buttons for functionality
                    acc_col, rej_col = st.columns(2)
                    with acc_col:
                        if st.button("Accept", key=f"accept_{trade['username']}", 
                                   use_container_width=True, type="secondary"):
                            st.success(f"Trade with @{trade['username']} accepted!")
                    with rej_col:
                        if st.button("Reject", key=f"reject_{trade['username']}", 
                                   use_container_width=True, type="secondary"):
                            st.error(f"Trade with @{trade['username']} rejected!")
                
                elif trade["type"] == "outgoing":
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; height: 150px;">
                        <span style="font-size: 18px; font-weight: bold;">Status: {trade['status']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                else:  # confirmed trades
                    st.markdown(f"""
                    <div style="font-size: 16px; margin-top: 10px;">
                        <strong>Status:</strong> {trade['status']}<br>
                        <strong>Location:</strong> {trade['location']}<br>
                        <strong>Date:</strong> {trade['date']}
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
                    if st.button("Cancel Trade", key=f"cancel_{trade['username']}", use_container_width=True):
                        st.warning(f"Trade with @{trade['username']} cancelled!")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TRADES COMPLETED
    with trade_tab2:
        st.write("")
        
        # Fetch completed trades from API
        try:
            user_id = st.session_state.get('user_id', 1)
            response = requests.get(f"{API_URL}/trades/completed/{user_id}")
            
            if response.status_code == 200:
                completed_trades = response.json()
                
                if not completed_trades:
                    st.info("No completed trades yet.")
                else:
                    for trade in completed_trades:
                        # Trade card container
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; border: 2px solid #333; border-radius: 20px; 
                                    padding: 25px; margin-bottom: 20px;">
                        """, unsafe_allow_html=True)
                        
                        # Header
                        st.markdown(f"### Trade with @{trade.get('username', 'Unknown')}")
                        
                        # Trade details in columns
                        detail_col1, detail_col2, detail_col3 = st.columns([2, 1, 2])
                        
                        with detail_col1:
                            # Your item
                            if trade.get("your_item_img"):
                                st.markdown(f"""
                                <div style="border: 2px solid #333; background-color: white; height: 150px; 
                                            border-radius: 8px; overflow: hidden;">
                                    <img src="{trade['your_item_img']}" style="width: 100%; height: 100%; object-fit: cover;">
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="border: 2px solid #333; background-color: white; height: 150px; 
                                            display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                                    <span style="font-size: 20px; font-weight: bold;">IMG</span>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with detail_col2:
                            st.markdown("""
                            <div style="display: flex; align-items: center; justify-content: center; height: 150px;">
                                <span style="font-size: 48px; font-weight: bold;">→</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with detail_col3:
                            # Their item
                            if trade.get("their_item_img"):
                                st.markdown(f"""
                                <div style="border: 2px solid #333; background-color: white; height: 150px; 
                                            border-radius: 8px; overflow: hidden;">
                                    <img src="{trade['their_item_img']}" style="width: 100%; height: 100%; object-fit: cover;">
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="border: 2px solid #333; background-color: white; height: 150px; 
                                            display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                                    <span style="font-size: 28px; font-weight: bold;">Free</span>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Trade info
                        st.markdown(f"""
                        <div style="margin-top: 20px; font-size: 16px;">
                            <strong>Completed:</strong> {trade.get('completed_date', 'N/A')}<br>
                            <strong>Location:</strong> {trade.get('location', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error(f"Failed to fetch completed trades. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching completed trades: {str(e)}")
            st.error("Unable to connect to the server. Please try again later.")