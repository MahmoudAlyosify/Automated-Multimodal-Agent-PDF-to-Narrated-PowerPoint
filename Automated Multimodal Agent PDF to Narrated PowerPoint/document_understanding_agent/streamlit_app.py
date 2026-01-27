"""
Streamlit GUI for Document Understanding Agent with LayoutLMv3 integration
Allows PDF upload and page range selection (max 10 pages)
"""

import streamlit as st
import json
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any
import time

from src.dua.agent import DocumentUnderstandingAgent
from src.dua.types import DUAInput
from src.dua.config import DUAConfig, Presets
from src.dua.modules.pdf_loader import PDFLoader
from src.dua.modules.layoutlmv3_analyzer import LayoutLMv3Analyzer


# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Document Understanding Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize LayoutLMv3 on first load
@st.cache_resource
def init_models():
    """Initialize AI models on first startup"""
    try:
        analyzer = LayoutLMv3Analyzer()
        return analyzer
    except Exception as e:
        st.warning(f"Could not initialize LayoutLMv3: {str(e)}")
        return None

_ = init_models()

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 500;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== UTILITY FUNCTIONS ====================
@st.cache_resource
def load_agent(preset_name: str = "accurate"):
    """Load the Document Understanding Agent with optimal config"""
    preset_func = getattr(Presets, preset_name)
    config = preset_func()
    return DocumentUnderstandingAgent(config)


def get_pdf_page_count(pdf_path: str) -> int:
    """Get total number of pages in PDF"""
    try:
        # Use PyMuPDF to quickly get page count
        try:
            import fitz
            doc = fitz.open(pdf_path)
            page_count = doc.page_count
            doc.close()
            return page_count
        except ImportError:
            # Fallback to pypdf
            try:
                from pypdf import PdfReader
                reader = PdfReader(pdf_path)
                return len(reader.pages)
            except ImportError:
                # Last resort: use DUA's PDF loader
                loader = PDFLoader()
                blocks = loader.load(pdf_path, start_page=0, end_page=9999)
                if blocks:
                    return max(int(b.page_number) for b in blocks) + 1
                return 100  # Default estimate
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return 100


def validate_page_range(start_page: int, end_page: int, total_pages: int) -> tuple[bool, str]:
    """
    Validate page range selection
    Returns: (is_valid, error_message)
    """
    # Check for negative pages
    if start_page < 0 or end_page < 0:
        return False, "❌ Page numbers cannot be negative"
    
    # Check for reversed range
    if end_page < start_page:
        return False, "❌ End page must be greater than or equal to start page"
    
    # Check for pages beyond PDF
    if start_page >= total_pages or end_page >= total_pages:
        return False, f"❌ Page numbers exceed PDF length ({total_pages} pages)"
    
    # Check for max 10 pages
    num_pages = end_page - start_page + 1
    if num_pages > 10:
        return False, f"⚠️ WARNING: You selected {num_pages} pages, but maximum is 10 pages!"
    
    return True, ""


def process_pdf(pdf_path: str, start_page: int, end_page: int, agent) -> Optional[Dict[str, Any]]:
    """Process PDF through Document Understanding Agent"""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Stage 1: PDF Loading
        status_text.text("📖 Loading PDF...")
        progress_bar.progress(15)
        time.sleep(0.3)
        
        # Stage 2: Layout Analysis
        status_text.text("📐 Analyzing layout...")
        progress_bar.progress(30)
        time.sleep(0.3)
        
        # Stage 3: Block Classification
        status_text.text("🏷️ Classifying blocks...")
        progress_bar.progress(45)
        time.sleep(0.3)
        
        # Stage 4: Semantic Labeling
        status_text.text("🧠 Semantic labeling...")
        progress_bar.progress(60)
        time.sleep(0.3)
        
        # Stage 5: Structure Building
        status_text.text("🏗️ Building document structure...")
        progress_bar.progress(75)
        time.sleep(0.3)
        
        # Stage 6: Confidence Estimation
        status_text.text("📊 Estimating confidence...")
        progress_bar.progress(90)
        
        # Process with DUA
        dua_input = DUAInput(
            pdf_path=pdf_path,
            start_page=start_page,
            end_page=end_page
        )
        
        output = agent.process(dua_input)
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
        
        return output.to_dict()
    
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None


def display_document_structure(output_dict: Dict[str, Any]):
    """Display document structure in a formatted way"""
    with st.expander("📑 Document Structure", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        metadata = output_dict.get("metadata", {})
        
        with col1:
            num_pages = metadata.get("num_pages", 0)
            st.metric("📄 Total Pages", num_pages)
        
        with col2:
            # Count total blocks
            sections = output_dict.get("document_tree", {}).get("sections", [])
            total_blocks = 0
            for section in sections:
                total_blocks += len(section.get("blocks", []))
            st.metric("📋 Total Blocks", total_blocks)
        
        with col3:
            confidence = metadata.get("confidence", 0)
            st.metric("🎯 Confidence", f"{confidence:.1%}")
    
    # Display sections
    with st.expander("📚 Document Sections", expanded=True):
        sections = output_dict.get("document_tree", {}).get("sections", [])
        
        if sections:
            for i, section in enumerate(sections, 1):
                st.subheader(f"Section {i}: {section['title']}")
                st.text(f"Level: {section['level']} | Blocks: {len(section.get('blocks', []))}")
                
                # Show first few blocks in this section
                blocks = section.get('blocks', [])
                if blocks:
                    st.caption("Preview of blocks in this section:")
                    for block in blocks[:3]:
                        st.write(f"• {block.get('text', '')[:100]}...")
        else:
            st.info("No sections detected in document")


def display_blocks(output_dict: Dict[str, Any]):
    """Display document blocks with filtering"""
    with st.expander("🔤 Document Blocks", expanded=False):
        # Collect all blocks from all sections
        sections = output_dict.get("document_tree", {}).get("sections", [])
        blocks = []
        
        def collect_blocks(sections_list):
            for section in sections_list:
                blocks.extend(section.get("blocks", []))
                # Recursively collect from subsections if any
                if "subsections" in section:
                    collect_blocks(section["subsections"])
        
        collect_blocks(sections)
        
        if blocks:
            # Filter by block type
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Total Blocks: {len(blocks)}**")
            
            with col2:
                search_text = st.text_input("🔍 Search blocks:")
            
            # Display blocks
            for idx, block in enumerate(blocks):
                # Safely get text - handle None values
                block_text = block.get("text") or ""
                block_text = str(block_text).strip()
                
                if search_text.lower() in block_text.lower():
                    with st.container():
                        st.markdown(f"**Block {idx+1}** | Type: `{block.get('type', 'UNKNOWN')}` | Confidence: `{block.get('confidence', 0):.1%}`")
                        st.write(f"Text: {block_text[:200]}...")
                        st.divider()
        else:
            st.info("No blocks extracted from document")


# ==================== MAIN APP ====================
def main():
    # Header
    st.title("📄 Document Understanding Agent")
    st.markdown("Transform PDFs into structured semantic documents with LayoutLMv3")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        config_preset = st.selectbox(
            "Select processing preset:",
            ["accurate", "fast", "academic", "business", "technical", "legal"],
            help="Choose a preset configuration for PDF processing"
        )
        
        st.divider()
        
        # Show LayoutLMv3 info
        st.subheader("🧠 AI Models")
        layoutlmv3 = LayoutLMv3Analyzer()
        model_info = layoutlmv3.get_model_info()
        
        if model_info["available"]:
            st.success("✓ LayoutLMv3 Active")
            st.caption(f"**{model_info['model_name']}**")
            st.info("""
            Microsoft LayoutLMv3 enables:
            - Visual layout understanding
            - Multimodal document analysis
            - Superior structure detection
            """)
        else:
            st.warning("⚠️ LayoutLMv3 Unavailable")
            st.caption("Using rule-based analysis")
        
        st.divider()
        st.subheader("📊 About")
        st.info("""
        This tool uses a 6-stage pipeline:
        1. PDF Loading
        2. Layout Analysis (LayoutLMv3)
        3. Block Classification
        4. Semantic Labeling
        5. Structure Building
        6. Confidence Estimation
        
        **Powered by:** LayoutLMv3 + PyMuPDF
        """)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "📊 Results", "ℹ️ Help"])
    
    # ==================== TAB 1: UPLOAD & PROCESS ====================
    with tab1:
        st.subheader("Step 1: Upload PDF File")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Select a PDF file to analyze (max 10 pages per run)"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                pdf_path = tmp_file.name
            
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Get page count
            total_pages = get_pdf_page_count(pdf_path)
            
            if total_pages > 0:
                st.markdown(f"**📑 Total Pages in PDF: {total_pages}**")
                
                # Page range selection
                st.subheader("Step 2: Select Page Range (Max 10 Pages)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    start_page = st.number_input(
                        "Start page:",
                        min_value=0,
                        max_value=total_pages - 1,
                        value=0,
                        help="First page to process (0-indexed)"
                    )
                
                with col2:
                    max_end = min(start_page + 9, total_pages - 1)
                    end_page = st.number_input(
                        "End page:",
                        min_value=start_page,
                        max_value=total_pages - 1,
                        value=max_end,
                        help="Last page to process (inclusive)"
                    )
                
                # Validation
                is_valid, error_msg = validate_page_range(start_page, end_page, total_pages)
                
                if is_valid:
                    num_pages = end_page - start_page + 1
                    st.markdown(f"""
                    <div class="success-box">
                    ✅ <b>Valid Range Selected:</b> Pages {start_page}-{end_page} ({num_pages} pages)
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="error-box">
                    {error_msg}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Process button
                st.subheader("Step 3: Process Document")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    process_button = st.button(
                        "🚀 Process PDF",
                        disabled=not is_valid,
                        use_container_width=True,
                        type="primary"
                    )
                
                # Process PDF
                if process_button:
                    agent = load_agent(config_preset)
                    result = process_pdf(pdf_path, start_page, end_page, agent)
                    
                    if result:
                        # Save to session state
                        st.session_state.processing_result = result
                        st.session_state.pdf_name = uploaded_file.name
                        st.success("✅ PDF processed successfully! Check the Results tab.")
                
                # Cleanup
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
    
    # ==================== TAB 2: RESULTS ====================
    with tab2:
        if "processing_result" in st.session_state:
            result = st.session_state.processing_result
            pdf_name = st.session_state.pdf_name
            
            st.subheader(f"📊 Results for: {pdf_name}")
            
            # Display structure
            display_document_structure(result)
            
            # Display blocks
            display_blocks(result)
            
            # JSON Export
            with st.expander("💾 Export Raw JSON", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.code(json.dumps(result, indent=2), language="json")
                
                with col2:
                    json_str = json.dumps(result, indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"output_{int(time.time())}.json",
                        mime="application/json",
                        use_container_width=True
                    )
        else:
            st.info("👈 Upload and process a PDF first to see results")
    
    # ==================== TAB 3: HELP ====================
    with tab3:
        st.subheader("How to Use")
        st.markdown("""
        ### 1️⃣ Upload PDF
        - Click "Choose a PDF file" in the Upload & Process tab
        - Select any PDF from your computer
        
        ### 2️⃣ Select Page Range
        - Choose starting page (0-indexed, 0 = first page)
        - Choose ending page (inclusive)
        - **Maximum 10 pages per run** to ensure fast processing
        
        ### 3️⃣ Process
        - Click "Process PDF" to analyze
        - The system will perform 6 stages of analysis:
          - PDF Loading
          - Layout Analysis
          - Block Classification
          - Semantic Labeling
          - Structure Building
          - Confidence Estimation
        
        ### 4️⃣ View Results
        - See document structure and sections
        - Browse extracted blocks
        - Export results as JSON
        
        ---
        
        ### 🔧 Configuration Presets
        
        | Preset | Best For | Speed | Accuracy |
        |--------|----------|-------|----------|
        | **accurate** | Detailed analysis | Slower | Highest |
        | **fast** | Quick processing | Fastest | Good |
        | **academic** | Research papers | Medium | High |
        | **business** | Reports & docs | Medium | High |
        | **technical** | Code & specs | Medium | High |
        | **legal** | Contracts & terms | Slower | Highest |
        
        ### 📊 Understanding Output
        
        **Confidence Score**: 0.0-1.0 indicating how well the system understood the document
        
        **Block Types**: 
        - HEADING, SUBHEADING, BODY_TEXT, BULLET_POINT
        - NUMBERED_ITEM, TABLE, FIGURE, CODE, QUOTE, FOOTNOTE, METADATA
        
        **Semantic Labels**:
        - EXPLANATION, DEFINITION, EXAMPLE, IMPORTANT, QUESTION, ANSWER
        - SUMMARY, INTRODUCTION, CONCLUSION, METADATA
        
        ---
        
        ### 🎯 Tips for Best Results
        1. Use clear, well-formatted PDFs
        2. Start with smaller page ranges (5-10 pages)
        3. Try different presets to find optimal results
        4. Check confidence scores to gauge reliability
        
        ### ⚠️ Limitations
        - Maximum 10 pages per analysis
        - Works best with text-based PDFs
        - Scanned/image-based PDFs may have lower accuracy
        """)


if __name__ == "__main__":
    main()
