import logging
logger = logging.getLogger(__name__)
import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import requests

SideBarLinks()

# add the logo
add_logo("src/assets/logo.png", height=300)

# Log swapper dashboard access
logger.info(f"Swapper Dashboard loaded by {st.session_state.get('first_name', 'Unknown')}")

st.markdown("# Swapper Dashboard")
st.sidebar.header("Swapper Dashboard")
st.write("""Welcome to the Swapper Dashboard!""")

st.markdown("---")

# Navigation buttons for Swapper features
st.markdown("### Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("📦 Browse Items", use_container_width=True):
        logger.info("Navigating to Browse Items")
        st.session_state.view = "browse"

    if st.button("📤 Upload New Listing", use_container_width=True):
        logger.info("Navigating to Upload Listing")
        st.session_state.view = "upload"

with col2:
    if st.button("🔄 My Swap Requests", use_container_width=True):
        logger.info("Navigating to Swap Requests")
        st.session_state.view = "requests"
    
    if st.button("📍 Track Shipments", use_container_width=True):
        logger.info("Navigating to Track Shipments")
        st.session_state.view = "shipments"

st.markdown("---")

# Initialize view state
if 'view' not in st.session_state:
    st.session_state.view = "browse"

# Browse Items View
if st.session_state.view == "browse":
    st.markdown("## Browse Available Items")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Filter: Size")
        size_filter = st.selectbox(
            "Select Size",
            ["All", "XS", "S", "M", "L", "XL", "XXL", "6", "7", "8", "9", "10", "11", "12"],
            label_visibility="collapsed"
        )

    with col2:
        st.subheader("Condition")
        condition_filter = st.selectbox(
            "Select Condition",
            ["All", "Excellent", "Good", "Fair", "Like New"],
            label_visibility="collapsed"
        )

    with col3:
        st.subheader("Posted Date")
        date_filter = st.selectbox(
            "Select Date Range",
            ["All Time", "Today", "This Week", "This Month"],
            label_visibility="collapsed"
        )

    st.markdown("---")

    # Function to fetch listings from your API
    def fetch_listings(size, condition):
        try:
            if size == "All":
                size = "M"
            if condition == "All":
                condition = "Good"
            
            url = f"http://localhost:4000/listings/{size}/{condition}/Vintage"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.warning(f"API returned status code: {response.status_code}")
                return []
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Cannot connect to API. Make sure your Flask server is running on port 4000!")
            return []
        except Exception as e:
            st.error(f"Error fetching listings: {e}")
            return []

    # Fetch listings based on filters
    with st.spinner("Loading items..."):
        listings = fetch_listings(size_filter, condition_filter)

    # Display items in a grid
    if listings:
        num_cols = 4
        rows = [listings[i:i + num_cols] for i in range(0, len(listings), num_cols)]
        
        for row in rows:
            cols = st.columns(num_cols)
            for idx, item in enumerate(row):
                with cols[idx]:
                    with st.container():
                        st.image("https://via.placeholder.com/200x200?text=Item+Image", use_container_width=True)
                        
                        st.markdown(f"### {item.get('Title', 'Item')}")
                        st.write(f"**Size:** {item.get('Size', 'N/A')}")
                        st.write(f"**Condition:** {item.get('Condition', 'N/A')}")
                        st.write(f"**Category:** {item.get('Category', 'N/A')}")
                        st.write(f"**Owner:** {item.get('OwnerName', 'Unknown')}")
                        
                        if st.button(f"View Details", key=f"btn_{item.get('ItemID')}"):
                            st.session_state.selected_item = item.get('ItemID')
                            st.info(f"Selected Item ID: {item.get('ItemID')}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("📦 No items found matching your filters. Try adjusting your search criteria or make sure the API is running.")
        
        if st.button("Show Sample Data (for testing)"):
            sample_data = [
                {"ItemID": 1, "Title": "Nike Air Force 1", "Size": "9", "Condition": "Excellent", "Category": "shoes", "OwnerName": "John Doe"},
                {"ItemID": 2, "Title": "Vintage Levi's Jeans", "Size": "32", "Condition": "Good", "Category": "pants", "OwnerName": "Jane Smith"},
                {"ItemID": 3, "Title": "Supreme Hoodie", "Size": "L", "Condition": "Like New", "Category": "tops", "OwnerName": "Mike Johnson"},
                {"ItemID": 4, "Title": "Adidas Sneakers", "Size": "10", "Condition": "Fair", "Category": "shoes", "OwnerName": "Sarah Lee"}
            ]
            
            cols = st.columns(4)
            for idx, item in enumerate(sample_data):
                with cols[idx]:
                    st.image("https://via.placeholder.com/200x200?text=Sample+Item", use_container_width=True)
                    st.markdown(f"### {item['Title']}")
                    st.write(f"**Size:** {item['Size']}")
                    st.write(f"**Condition:** {item['Condition']}")
                    st.write(f"**Owner:** {item['OwnerName']}")
                    if st.button(f"View Details", key=f"sample_btn_{item['ItemID']}"):
                        st.success(f"Selected: {item['Title']}")

# Upload Listing View
elif st.session_state.view == "upload":
    st.markdown("## Upload New Listing")
    
    with st.form("upload_listing_form"):
        title = st.text_input("Title*", placeholder="e.g., Nike Air Force 1")
        category = st.selectbox("Category*", ["shoes", "tops", "bottoms", "outerwear", "accessories"])
        description = st.text_area("Description*", placeholder="Describe your item...")
        size = st.selectbox("Size*", ["XS", "S", "M", "L", "XL", "XXL", "6", "7", "8", "9", "10", "11", "12"])
        item_type = st.radio("Type*", ["Swap", "Take"])
        condition = st.selectbox("Condition*", ["Excellent", "Good", "Fair", "Like New"])
        tags = st.multiselect("Tags", ["Streetwear", "Vintage", "Basic", "Designer", "Athletic"])
        
        submitted = st.form_submit_button("Upload Listing", use_container_width=True)
        
        if submitted:
            if title and category and description and size and condition:
                try:
                    response = requests.post(
                        "http://localhost:4000/upload_listing",
                        json={
                            "Title": title,
                            "Category": category,
                            "Description": description,
                            "Size": size,
                            "Type": item_type,
                            "Condition": condition,
                            "OwnerID": st.session_state.get('user_id', 1),
                            "Tags": tags
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 201:
                        st.success("✅ Listing uploaded successfully!")
                        logger.info(f"New listing created: {title}")
                    else:
                        st.error(f"Error uploading listing: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please fill in all required fields!")

# Swap Requests View
elif st.session_state.view == "requests":
    st.markdown("## My Swap Requests")
    st.info("Coming soon! View and manage your swap requests here.")

# Track Shipments View
elif st.session_state.view == "shipments":
    st.markdown("## Track Shipments")
    
    user_id = st.session_state.get('user_id', 1)
    
    try:
        response = requests.get(f"http://localhost:4000/track_swap/{user_id}", timeout=5)
        
        if response.status_code == 200:
            shipments = response.json()
            
            if shipments:
                for shipment in shipments:
                    with st.container():
                        st.markdown(f"### Order #{shipment['OrderID']}")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Direction:** {shipment['SwapDirection']}")
                            st.write(f"**Carrier:** {shipment.get('Carrier', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Tracking #:** {shipment.get('TrackingNum', 'N/A')}")
                            st.write(f"**Status:** {shipment['Status']}")
                        
                        with col3:
                            st.write(f"**Shipped:** {shipment.get('DateShipped', 'Not yet')}")
                            st.write(f"**Arrived:** {shipment.get('DateArrived', 'In transit')}")
                        
                        st.markdown("---")
            else:
                st.info("No shipments to track yet.")
        else:
            st.error("Could not load shipments")
    except Exception as e:
        st.error(f"Error loading shipments: {e}")

# Custom CSS
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    h3 {
        color: #2c3e50;
        font-size: 1.2em;
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<br><center>DistinctDevs ©2025</center>", unsafe_allow_html=True)