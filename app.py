import streamlit as st
import os
from file_type_detector import FileTypeDetector  # Your detector class
from PIL import Image
import io

# Configure page
st.set_page_config(
    page_title="Magic File Detector",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .header {
        font-size: 2.5em;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5em;
    }
    .subheader {
        font-size: 1.2em;
        color: #7f8c8d;
        margin-bottom: 2em;
    }
    .upload-box {
        border: 2px dashed #3498db;
        border-radius: 10px;
        padding: 3em;
        text-align: center;
        margin-bottom: 2em;
        background-color: #f8f9fa;
    }
    .result-card {
        border-radius: 10px;
        padding: 1.5em;
        margin-bottom: 1.5em;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .file-info {
        background-color: #e8f4fc;
    }
    .detection-result {
        background-color: #e8f8f0;
    }
    .file-preview {
        background-color: #f9f9f9;
    }
    .icon {
        font-size: 1.5em;
        margin-right: 0.5em;
        vertical-align: middle;
    }
    .metric-value {
        font-size: 1.4em !important;
        font-weight: 600 !important;
    }
    .stProgress > div > div > div > div {
        background-color: #3498db;
    }
    footer {
        text-align: center;
        padding: 1em;
        margin-top: 2em;
        color: #7f8c8d;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown('<div class="header">🔮 Magic File Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Discover the true nature of your files beyond their extensions</div>', unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # File upload section
    st.markdown("### 📤 Upload Your File")
    with st.container():
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drag and drop any file here",
            type=None,
            label_visibility="collapsed",
            help="Supported formats: Images, Documents, Spreadsheets, Presentations, Archives"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        # Process the file
        with st.spinner('Analyzing your file...'):
            temp_file_path = os.path.join("/tmp", uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                category, mime_type = FileTypeDetector.detect_file_type(temp_file_path, return_mime=True)
                
                # Display results
                st.markdown("## 🔍 Detection Results")
                
                # File info card
                with st.container():
                    st.markdown('<div class="result-card file-info">', unsafe_allow_html=True)
                    st.markdown("### 📄 File Information")
                    
                    info_col1, info_col2 = st.columns(2)
                    with info_col1:
                        st.metric("File Name", uploaded_file.name)
                        st.metric("File Size", f"{len(uploaded_file.getvalue()) / 1024:.2f} KB")
                    
                    with info_col2:
                        st.metric("Category", category.capitalize())
                        st.metric("MIME Type", mime_type)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # File preview section
                with st.container():
                    st.markdown('<div class="result-card file-preview">', unsafe_allow_html=True)
                    st.markdown("### 👀 File Preview")
                    
                    if category == "image":
                        try:
                            image = Image.open(io.BytesIO(uploaded_file.getvalue()))
                            st.image(image, caption="Image Preview", use_column_width=True)
                        except:
                            st.warning("Could not display image preview")
                    elif category == "pdf":
                        st.info("PDF preview would be displayed here with additional libraries")
                    elif category in ["word", "excel", "powerpoint"]:
                        st.info(f"This appears to be a {category} document")
                    elif category == "mixed":
                        st.warning("Archive contents would be listed here with additional libraries")
                    else:
                        st.warning("No preview available for this file type")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Technical details
                with st.expander("🛠 Technical Details"):
                    st.markdown("""
                    **How we detected this file type:**
                    - Magic bytes (file signature) analysis
                    - Internal structure examination
                    - Content type verification
                    """)
                    
                    st.markdown("### File Header (first 128 bytes in hex)")
                    with open(temp_file_path, "rb") as f:
                        header = f.read(128)
                        st.code(header.hex(" ", 1))
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

with col2:
    # Sidebar with information
    st.markdown("## ℹ️ About This Tool")
    st.markdown("""
    This advanced file detector examines the actual content of your files to determine their true type, regardless of their extension.
    
    **How it works:**
    - Analyzes file signatures (magic bytes)
    - Examines internal file structures
    - Verifies content types
    - Supports dozens of file formats
    """)
    
    st.markdown("### 📋 Supported Formats")
    st.markdown("""
    - **Images:** JPEG, PNG, GIF, BMP, TIFF
    - **Documents:** DOC, DOCX, PDF, ODT
    - **Spreadsheets:** XLS, XLSX, ODS
    - **Presentations:** PPT, PPTX, ODP
    - **Archives:** ZIP, RAR, 7Z, TAR
    - **And many more...**
    """)
    
    st.markdown("### 💡 Pro Tip")
    st.markdown("""
    This tool is especially useful when:
    - You receive files with missing extensions
    - You suspect a file has been mislabeled
    - You need to verify a file's true type for security purposes
    """)

# Footer
st.markdown("---")
st.markdown("""
<footer>
    Magic File Detector • Powered by Streamlit • Uses advanced file signature analysis
</footer>
""", unsafe_allow_html=True)