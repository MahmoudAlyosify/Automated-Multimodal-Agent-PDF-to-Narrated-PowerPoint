#!/usr/bin/env python3
"""Streamlit GUI for PDF-to-Narrated-PowerPoint System"""

import streamlit as st
import sys
import json
import tempfile
from pathlib import Path
import os
from dotenv import load_dotenv

st.set_page_config(
    page_title="PDF to PowerPoint Converter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

root_dir = Path(__file__).parent.absolute()
dua_dir = root_dir / "document_understanding_agent"
ppt_dir = root_dir / "JSON To PPT"

sys.path.insert(0, str(dua_dir / "src"))
sys.path.insert(0, str(ppt_dir))

try:
    from dua import DocumentUnderstandingAgent
    from dua.types import DUAInput
    from main import build
    has_agents = True
except ImportError as e:
    st.error(f"❌ Failed to import agents: {e}")
    has_agents = False

with st.sidebar:
    st.title("⚙️ Settings")
    
    domain = st.selectbox(
        "Document Domain",
        ["general", "academic", "business", "technical", "legal"],
        help="Select the type of document being processed"
    )
    
    language = st.text_input("Language Code", "en", help="Language code (en, es, fr, etc.)")
    
    st.subheader("Page Range")
    col1, col2 = st.columns(2)
    with col1:
        start_page = st.number_input("Start Page", min_value=0, value=0)
    with col2:
        end_page = st.number_input("End Page", min_value=-1, value=-1, help="-1 = all pages")
    
    st.subheader("API Configuration")
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key:
        st.success("✓ Mistral API Key: Configured")
    else:
        st.warning("⚠️ Mistral API Key: Not configured")

st.title("📊 PDF to PowerPoint Converter")
st.markdown("Convert your PDF documents into professional PowerPoint presentations")

if not has_agents:
    st.error("❌ System components not properly initialized. Please check the installation.")
    st.stop()

# Create tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "📋 Preview", "📥 Download"])

# ============================================================================
# TAB 1: UPLOAD & PROCESS
# ============================================================================

with tab1:
    st.subheader("Step 1: Upload PDF")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to convert to PowerPoint"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_pdf_path = tmp_file.name
        
        st.success(f"✓ File uploaded: {uploaded_file.name}")
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col2:
            # Get page count
            try:
                import pymupdf
                doc = pymupdf.open(tmp_pdf_path)
                page_count = len(doc)
                doc.close()
                st.metric("Total Pages", page_count)
            except:
                st.metric("Total Pages", "N/A")
        with col3:
            st.metric("Format", "PDF")
        
        st.divider()
        st.subheader("Step 2: Process Document")
        
        # Processing button
        if st.button("🔄 Process PDF", use_container_width=True, type="primary"):
            
            with st.spinner("📖 Extracting content from PDF..."):
                try:
                    # Initialize DUA
                    agent = DocumentUnderstandingAgent(use_ml=False, log_level='WARNING')
                    
                    # Determine end page
                    end_page_param = None if end_page == -1 else end_page
                    
                    # Create input
                    input_data = DUAInput(
                        pdf_path=tmp_pdf_path,
                        start_page=int(start_page),
                        end_page=end_page_param,
                        domain=domain,
                        language=language
                    )
                    
                    # Process
                    result = agent.process(input_data)
                    
                    # Store in session state
                    st.session_state.dua_result = result
                    st.session_state.uploaded_filename = uploaded_file.name
                    
                    st.success("✓ Content extracted successfully!")
                    
                    # Show extraction summary
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Pages Processed", result.metadata.num_pages)
                    with col2:
                        st.metric("Content Blocks", len(result.document_tree.sections[0].blocks) if result.document_tree.sections else 0)
                    with col3:
                        st.metric("Confidence", f"{result.metadata.confidence:.1%}")
                    with col4:
                        st.metric("Has Tables", "Yes" if result.metadata.has_tables else "No")
                    
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
                    logger.error(f"DUA Error: {e}", exc_info=True)
            
            st.divider()
            st.subheader("Step 3: Generate PowerPoint")
            
            # Generate PPT button
            if st.button("⚡ Generate PowerPoint", use_container_width=True, type="primary"):
                
                if "dua_result" not in st.session_state:
                    st.error("❌ Please process the PDF first!")
                else:
                    with st.spinner("🎨 Creating PowerPoint presentation..."):
                        try:
                            # Create presentation structure
                            ppt_data = {
                                "ppt": {
                                    "size": {"width": 960, "height": 540, "unit": "px"},
                                    "defaultUnit": "px",
                                    "slides": []
                                }
                            }
                            
                            # Add title slide
                            title_text = uploaded_file.name.replace('.pdf', '').replace('_', ' ')
                            ppt_data["ppt"]["slides"].append({
                                "title": "Cover",
                                "elements": [
                                    {
                                        "type": "text",
                                        "text": title_text,
                                        "box": {"x": 50, "y": 150, "w": 860, "h": 100},
                                        "style": {"fontSize": 44, "bold": True, "align": "center"}
                                    },
                                    {
                                        "type": "text",
                                        "text": "Generated by PDF-to-PowerPoint Converter",
                                        "box": {"x": 50, "y": 280, "w": 860, "h": 50},
                                        "style": {"fontSize": 16, "align": "center"}
                                    }
                                ]
                            })
                            
                            # Add content slides from extracted data
                            result = st.session_state.dua_result
                            sections = result.document_tree.sections
                            
                            if sections:
                                for i, section in enumerate(sections[:10]):  # Limit to 10 slides
                                    slide = {
                                        "title": section.title or f"Slide {i+1}",
                                        "elements": []
                                    }
                                    
                                    # Add section title
                                    slide["elements"].append({
                                        "type": "text",
                                        "text": section.title or f"Content {i+1}",
                                        "box": {"x": 50, "y": 30, "w": 860, "h": 60},
                                        "style": {"fontSize": 28, "bold": True}
                                    })
                                    
                                    # Add block content
                                    y_pos = 110
                                    for block in section.blocks[:5]:  # Limit blocks per slide
                                        if y_pos < 480:
                                            slide["elements"].append({
                                                "type": "text",
                                                "text": block.text[:200] if len(block.text) > 200 else block.text,  # Limit text
                                                "box": {"x": 50, "y": y_pos, "w": 860, "h": 80},
                                                "style": {"fontSize": 12}
                                            })
                                            y_pos += 90
                                    
                                    ppt_data["ppt"]["slides"].append(slide)
                            
                            # Build PowerPoint
                            prs, slide_count = build(ppt_data)
                            
                            # Save to bytes
                            pptx_bytes = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
                            prs.save(pptx_bytes.name)
                            
                            # Store in session
                            with open(pptx_bytes.name, 'rb') as f:
                                st.session_state.pptx_data = f.read()
                            st.session_state.pptx_filename = f"{uploaded_file.name.replace('.pdf', '')}_presentation.pptx"
                            
                            os.unlink(pptx_bytes.name)
                            
                            st.success(f"✓ PowerPoint created successfully!")
                            st.info(f"📊 Generated {slide_count} slides")
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"❌ Error generating PowerPoint: {str(e)}")
                            logger.error(f"PPT Error: {e}", exc_info=True)

# ============================================================================
# TAB 2: PREVIEW
# ============================================================================

with tab2:
    st.subheader("Extracted Content Preview")
    
    if "dua_result" in st.session_state:
        result = st.session_state.dua_result
        
        # Display metadata
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pages", result.metadata.num_pages)
        with col2:
            st.metric("Confidence", f"{result.metadata.confidence:.1%}")
        with col3:
            st.metric("Tables", "Yes" if result.metadata.has_tables else "No")
        with col4:
            st.metric("Images", "Yes" if result.metadata.has_images else "No")
        
        st.divider()
        
        # Display sections
        if result.document_tree.sections:
            st.subheader("Document Structure")
            
            for i, section in enumerate(result.document_tree.sections):
                with st.expander(f"📑 {section.title or f'Section {i+1}'}", expanded=(i==0)):
                    
                    # Section info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"Level: {section.level}")
                    with col2:
                        st.caption(f"Blocks: {len(section.blocks)}")
                    
                    # Blocks
                    for j, block in enumerate(section.blocks[:10]):  # Limit preview
                        st.markdown(f"**Block {j+1}** ({block.type})")
                        if block.text:
                            st.write(block.text[:500])  # Limit text
                        else:
                            st.caption("(No text content)")
                        
                        with st.expander("Details"):
                            st.json({
                                "type": block.type,
                                "semantic_label": block.semantic_label,
                                "importance": block.importance,
                                "caption": block.caption
                            })
                        
                        st.divider()
        
        # Raw JSON view
        with st.expander("📋 Raw JSON Data"):
            st.json(result.to_dict())
    
    else:
        st.info("📤 Upload and process a PDF to see the preview")

# ============================================================================
# TAB 3: DOWNLOAD
# ============================================================================

with tab3:
    st.subheader("Download Results")
    
    col1, col2 = st.columns(2)
    
    # Download PowerPoint
    with col1:
        st.markdown("### 📊 PowerPoint Presentation")
        if "pptx_data" in st.session_state:
            st.download_button(
                label="📥 Download PowerPoint",
                data=st.session_state.pptx_data,
                file_name=st.session_state.pptx_filename,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )
            st.success(f"✓ Ready to download: {st.session_state.pptx_filename}")
        else:
            st.info("⚠️ Generate a PowerPoint first")
    
    # Download extracted content
    with col2:
        st.markdown("### 📄 Extracted Content (JSON)")
        if "dua_result" in st.session_state:
            json_data = json.dumps(st.session_state.dua_result.to_dict(), indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"{st.session_state.uploaded_filename.replace('.pdf', '')}_content.json",
                mime="application/json",
                use_container_width=True
            )
            st.success("✓ Ready to download")
        else:
            st.info("⚠️ Process a PDF first")
    
    st.divider()
    
    # Processing summary
    if "dua_result" in st.session_state or "pptx_data" in st.session_state:
        st.subheader("📊 Processing Summary")
        
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            if "uploaded_filename" in st.session_state:
                st.markdown(f"**Input:** {st.session_state.uploaded_filename}")
            if "dua_result" in st.session_state:
                st.markdown(f"**Pages Processed:** {st.session_state.dua_result.metadata.num_pages}")
        
        with summary_col2:
            if "pptx_filename" in st.session_state:
                st.markdown(f"**Output:** {st.session_state.pptx_filename}")
            if "dua_result" in st.session_state:
                st.markdown(f"**Confidence:** {st.session_state.dua_result.metadata.confidence:.1%}")
    
    else:
        st.info("👈 Use the 'Upload & Process' tab to get started")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("📖 [Documentation](https://github.com)")

with col2:
    st.caption("🐛 [Report Issues](https://github.com)")

with col3:
    st.caption("⭐ [Star on GitHub](https://github.com)")

st.caption("*PDF-to-Narrated-PowerPoint System v1.0*")
