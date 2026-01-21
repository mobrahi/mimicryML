import streamlit as st
import requests
from PIL import Image
import io
import time
from pathlib import Path
import uuid

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Page configuration
st.set_page_config(
    page_title="mimicryML | AI Style Transfer Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    h1 {
        color: white;
        text-align: center;
        padding: 20px;
    }
    .uploadedFile {
        border: 2px dashed white;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'current_job_id' not in st.session_state:
    st.session_state.current_job_id = None

if 'processing' not in st.session_state:
    st.session_state.processing = False

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/paint-palette.png", width=150)
    st.title("🎨 Navigation")
    
    page = st.radio(
        "Select Page",
        ["Transform", "History", "Gallery"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # API Status Check
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend Online")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    Transform your photos into artistic masterpieces using deep learning.
    
    **Tech Stack:**
    - FastAPI
    - TensorFlow
    - SQLite
    - Streamlit
    """)

# Helper Functions
def get_available_styles():
    """Fetch available styles from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/styles")
        if response.status_code == 200:
            return response.json()["styles"]
        return {}
    except:
        return {}

def upload_and_transform(image_file, style):
    """Upload image and start transformation"""
    try:
        files = {"file": ("image.jpg", image_file, "image/jpeg")}
        params = {
            "style": style,
            "session_id": st.session_state.session_id
        }
        
        response = requests.post(
            f"{API_BASE_URL}/transform",
            files=files,
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def check_status(job_id):
    """Check transformation status"""
    try:
        response = requests.get(f"{API_BASE_URL}/status/{job_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_result(job_id):
    """Download result image"""
    try:
        response = requests.get(f"{API_BASE_URL}/result/{job_id}")
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        return None
    except:
        return None

def get_history(session_id):
    """Get transformation history"""
    try:
        response = requests.get(f"{API_BASE_URL}/history/{session_id}")
        if response.status_code == 200:
            return response.json()["transformations"]
        return []
    except:
        return []

def get_gallery(limit=20):
    """Get gallery transformations"""
    try:
        response = requests.get(f"{API_BASE_URL}/gallery?limit={limit}")
        if response.status_code == 200:
            return response.json()["transformations"]
        return []
    except:
        return []

# ============================================
# PAGE: TRANSFORM
# ============================================
if page == "Transform":
    st.title("🎨 mimicryML | AI Style Transfer Studio")
    st.markdown("### Transform your photos into artistic masterpieces")
    
    # Get available styles
    styles = get_available_styles()
    
    if not styles:
        st.error("Could not load styles from backend. Is the server running?")
        st.stop()
    
    # Image Upload Section
    st.markdown("---")
    st.subheader("📸 Step 1: Upload Your Photo")
    
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a photo you want to transform"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Original Photo", use_container_width=True)
    
    # Style Selection
    st.markdown("---")
    st.subheader("🎨 Step 2: Choose Artistic Style")
    
    # Display styles in a grid
    cols = st.columns(4)
    selected_style = None
    
    style_names = list(styles.keys())
    for idx, style_key in enumerate(style_names):
        with cols[idx % 4]:
            style_info = styles[style_key]
            
            # Create a styled button
            if st.button(
                f"🎨 {style_info['name'].split(' - ')[0]}",
                key=f"style_{style_key}",
                use_container_width=True
            ):
                selected_style = style_key
            
            st.caption(style_info['description'])
    
    # Store selected style in session state
    if selected_style:
        st.session_state.selected_style = selected_style
    
    # Transform Button
    st.markdown("---")
    
    if uploaded_file and 'selected_style' in st.session_state:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✨ Transform My Image", type="primary", use_container_width=True):
                with st.spinner("Uploading and starting transformation..."):
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    result = upload_and_transform(
                        uploaded_file,
                        st.session_state.selected_style
                    )
                    
                    if result:
                        st.session_state.current_job_id = result['job_id']
                        st.session_state.processing = True
                        st.success(f"✅ Job started! ID: {result['job_id']}")
                        st.rerun()
    
    # Processing Status
    if st.session_state.processing and st.session_state.current_job_id:
        st.markdown("---")
        st.subheader("⏳ Processing Your Image...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        max_checks = 60  # 60 seconds timeout
        for i in range(max_checks):
            status = check_status(st.session_state.current_job_id)
            
            if status:
                current_status = status['status']
                
                if current_status == 'completed':
                    progress_bar.progress(100)
                    status_text.success(f"✅ Completed in {status.get('processing_time', 'N/A'):.1f}s")
                    
                    # Display result
                    st.markdown("---")
                    st.subheader("🎉 Your Artistic Masterpiece!")
                    
                    result_image = get_result(st.session_state.current_job_id)
                    
                    if result_image:
                        # Side by side comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Original")
                            st.image(image, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### Stylized")
                            st.image(result_image, use_container_width=True)
                        
                        # Download button
                        buf = io.BytesIO()
                        result_image.save(buf, format='JPEG')
                        btn = st.download_button(
                            label="💾 Download Stylized Image",
                            data=buf.getvalue(),
                            file_name=f"stylized_{st.session_state.selected_style}.jpg",
                            mime="image/jpeg",
                            use_container_width=True
                        )
                    
                    st.session_state.processing = False
                    break
                
                elif current_status == 'failed':
                    progress_bar.progress(100)
                    status_text.error(f"❌ Failed: {status.get('error_message', 'Unknown error')}")
                    st.session_state.processing = False
                    break
                
                elif current_status == 'processing':
                    progress = min((i + 1) * 100 // max_checks, 95)
                    progress_bar.progress(progress)
                    status_text.info(f"🔄 Processing... ({i+1}s)")
                
                else:  # pending
                    progress_bar.progress(10)
                    status_text.info("⏳ Waiting to start...")
            
            time.sleep(1)
        
        if st.session_state.processing:
            st.warning("⏱️ Processing is taking longer than expected. Check History page later.")
            st.session_state.processing = False

# ============================================
# PAGE: HISTORY
# ============================================
elif page == "History":
    st.title("📜 Your Transformation History")
    
    history = get_history(st.session_state.session_id)
    
    if not history:
        st.info("No transformations yet. Go to Transform page to create your first masterpiece!")
    else:
        st.success(f"Found {len(history)} transformation(s)")
        
        # Statistics
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Transformations", len(history))
        
        with col2:
            completed = len([h for h in history if h['status'] == 'completed'])
            st.metric("Completed", completed)
        
        with col3:
            avg_time = sum([h.get('processing_time', 0) or 0 for h in history if h.get('processing_time')]) / max(completed, 1)
            st.metric("Avg Time", f"{avg_time:.1f}s")
        
        st.markdown("---")
        
        # Display history items
        for item in history:
            with st.expander(f"🎨 {item['style_name'].title()} - {item['created_at']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Job ID:** `{item['job_id']}`")
                    st.write(f"**Status:** {item['status'].upper()}")
                    st.write(f"**Created:** {item['created_at']}")
                    
                    if item['status'] == 'completed':
                        st.write(f"**Processing Time:** {item.get('processing_time', 'N/A'):.1f}s")
                
                with col2:
                    if item['status'] == 'completed':
                        if st.button(f"View Result", key=f"view_{item['job_id']}"):
                            result_img = get_result(item['job_id'])
                            if result_img:
                                st.image(result_img, caption="Result", use_container_width=True)

# ============================================
# PAGE: GALLERY
# ============================================
elif page == "Gallery":
    st.title("🖼️ Community Gallery")
    st.markdown("### Explore amazing transformations from all users")
    
    gallery_items = get_gallery(limit=30)
    
    if not gallery_items:
        st.info("Gallery is empty. Be the first to create a transformation!")
    else:
        st.success(f"Showing {len(gallery_items)} recent transformation(s)")
        
        # Display in grid
        cols_per_row = 3
        
        for i in range(0, len(gallery_items), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j in range(cols_per_row):
                idx = i + j
                if idx < len(gallery_items):
                    item = gallery_items[idx]
                    
                    with cols[j]:
                        st.markdown(f"**{item['style_name'].title()}**")
                        st.caption(f"{item['created_at']}")
                        
                        # Try to load and display image
                        try:
                            result_img = get_result(item['job_id'])
                            if result_img:
                                st.image(result_img, use_container_width=True)
                        except:
                            st.info("Image not available")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: white; padding: 20px;'>
        <p>🎨 mimicryML | AI Style Transfer Studio | Built with FastAPI, TensorFlow & Streamlit</p>
        <p style='font-size: 0.8em;'>Python Bootcamp JomHack Cohort4 Final Project © 2026</p>
    </div>
""", unsafe_allow_html=True)