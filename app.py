import streamlit as st
import requests
from PIL import Image
import io

"""
Phase 4: Multi-Modal Cold Case Intelligence Platform - Investigative Dashboard
A high-fidelity Streamlit interface for forensic analysts to interact with 
the ColdSync AI backend, visualize cross-modality matches, and review AI synthesis.
"""

# ---------------------------------------------------------
# 1. Page Configuration & Professional Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="ColdSync AI | Investigative Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main Title Header
st.title("🔍 ColdSync AI: Multi-Modal Cold Case Intelligence")
st.markdown("---")

# ---------------------------------------------------------
# 2. Sidebar: The Investigative Input Zone
# ---------------------------------------------------------
st.sidebar.header("Investigation Input")
st.sidebar.markdown("Enter details of the current case to cross-reference the historical database.")

# Case Text Input
new_case_summary = st.sidebar.text_area(
    "New Case M.O. / Summary", 
    placeholder="Describe the crime scene, suspect behavior, or entry method...",
    height=150
)

# Multi-Image Evidence Input
uploaded_files = st.sidebar.file_uploader(
    "Upload Crime Scene Photos (Select multiple)", 
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# Process Button
run_button = st.sidebar.button("Run ColdSync AI", type="primary", use_container_width=True)

# ---------------------------------------------------------
# 3. Main Dashboard: The Results Zone
# ---------------------------------------------------------
if run_button:
    if not new_case_summary or not uploaded_files:
        st.error("Please provide both a text summary and at least one crime scene photo to proceed.")
    else:
        with st.spinner("Cross-referencing multimodal database and generating forensic synthesis..."):
            try:
                # Prepare data for API request
                # Multi-image list for 'scene_images' key
                files = [("scene_images", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                # Form data dictionary
                data = {"text_summary": new_case_summary}
                
                # POST request to FastAPI backend
                backend_url = "http://127.0.0.1:8000/analyze"
                response = requests.post(backend_url, data=data, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # ---------------------------------------------------------
                    # 4. AI Forensic Synthesis Section
                    # ---------------------------------------------------------
                    st.subheader("🤖 AI Forensic Synthesis")
                    st.info(result.get("forensic_synthesis", "Synthesis could not be generated."))
                    
                    # ---------------------------------------------------------
                    # 5. Iterating through Top Matches
                    # ---------------------------------------------------------
                    st.subheader("📊 Top Historical Matches")
                    
                    top_matches = result.get("top_matches", [])
                    
                    if not top_matches or len(top_matches) == 0:
                        st.info("No confident historical matches found for this evidence. The AI rejected all low-probability connections.")
                    else:
                        for match in top_matches:
                            st.divider()
                            
                            # Match Header: Case ID and Fused Score
                            case_id = match.get("case_id")
                            combined_score = match.get("combined_score", 0.0)
                            
                            st.markdown(f"### Case ID: {case_id} | :green[Combined Score: {combined_score}%]")
                            
                            # CRITICAL UI ELEMENT: Divergence Flag Alert
                            if match.get("divergence_flag"):
                                st.error("🚨 **DIVERGENCE FLAG TRIGGERED**: Visual evidence severely conflicts with textual M.O. High probability of staged scene or copycat.")
                            
                            # 3-Column Evidence Display
                            col1, col2, col3 = st.columns([1, 1, 1.2])
                            
                            with col1:
                                st.markdown("**New Case Evidence**")
                                # Display only the first image from the upload list to save UI space
                                st.image(uploaded_files[0], use_column_width=True, caption=f"New Case Evidence (1 of {len(uploaded_files)})")
                                
                            with col2:
                                st.markdown("**Historical Match Evidence**")
                                # Display the matched historical image from local path
                                img_path = match.get("image_path")
                                if img_path and img_path != "":
                                    try:
                                        st.image(img_path, use_column_width=True, caption=f"Archived Case: {case_id}")
                                    except Exception:
                                        st.warning("Visual evidence corrupted on disk.")
                                else:
                                    st.warning("Visual record not found (Text-Only Match).")
                                    
                            with col3:
                                st.markdown("**Match Details & Metrics**")
                                # Display historical summary
                                st.write(f"**Historical M.O. Summary:** {match.get('text_summary')}")
                                
                                # Metrics Breakdown
                                m_col1, m_col2 = st.columns(2)
                                m_col1.metric("Textual Score", f"{match.get('text_score')}%")
                                m_col2.metric("Visual Score", f"{match.get('visual_score')}%")
                                
                                # Additional Analysis Data
                                st.caption(f"Divergence Delta: {match.get('divergence_delta')}%")

                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Connection Error: Could not connect to the ColdSync AI backend at http://127.0.0.1:8000. Is main.py running?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

else:
    # Initial State View
    st.markdown("""
    ### Welcome, Investigator.
    Please use the sidebar to upload case data. 
    1. **Text Summary:** Enter details about the entry point, weapon, or signature.
    2. **Evidence Image:** Upload high-resolution crime scene photography.
    
    ColdSync AI will then perform a **fused multi-modal search** to identify patterns across our historical database.
    """)

# Footer Styling
st.sidebar.markdown("---")
st.sidebar.caption("ColdSync AI v1.0 | Hackathon Prototype")
